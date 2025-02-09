from transformers import AutoTokenizer, AutoModelForQuestionAnswering, Trainer, TrainingArguments
import torch
from torch.utils.data import Dataset
import os
import gc
from tqdm import tqdm
import numpy as np
import re
from nltk.corpus import stopwords
import nltk

nltk.download('stopwords')

class QADataset(Dataset):
    def __init__(self, data, tokenizer, max_length=384):
        self.data = data
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.max_answer_length = 100
        self.stopwords = set(stopwords.words('english'))
    
    def clean_text(self, text):
        """Clean text for better processing"""
        text = text.strip()
        text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
        text = text.replace('##', '')  # Remove BERT artifacts
        return text
    
    def find_answer_span(self, context, answer):
        """Find the best concise answer span in context"""
        # Clean both texts
        context = self.clean_text(context.lower())
        answer = self.clean_text(answer.lower())
        
        # Try exact match first
        start = context.find(answer)
        if start != -1:
            return start, start + len(answer)
        
        # Try to find the most concise answer that contains the key information
        answer_words = set(answer.split())
        key_words = {word for word in answer_words 
                    if len(word) > 3 and word not in self.stopwords}
        
        best_start = -1
        best_end = -1
        best_score = 0
        min_length = float('inf')
        
        # Sliding window approach
        words = context.split()
        for i in range(len(words)):
            for j in range(i + 1, min(i + 15, len(words))):  # Limit to 15 words max
                span = ' '.join(words[i:j])
                span_words = set(span.split())
                
                # Calculate matching score
                matches = len(key_words & span_words)
                span_length = j - i
                
                # Prefer shorter spans with more key word matches
                score = matches / (span_length ** 0.5)  # Penalize length
                
                if (matches >= len(key_words) * 0.5 and  # At least 50% key words
                    (score > best_score or 
                     (score == best_score and span_length < min_length))):
                    span_start = context.find(span)
                    if span_start != -1:
                        best_score = score
                        min_length = span_length
                        best_start = span_start
                        best_end = span_start + len(span)
        
        return (best_start, best_end) if best_start != -1 else (0, 1)
    
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        item = self.data.iloc[idx]
        question = self.clean_text(item['question'])
        context = self.clean_text(item['context'])
        answer = self.clean_text(item['answer'])
        
        # Tokenize inputs
        encoding = self.tokenizer(
            question,
            context,
            max_length=self.max_length,
            padding='max_length',
            truncation='only_second',
            return_tensors='pt',
            return_offsets_mapping=True,
            stride=128
        )
        
        # Find answer span in context
        answer_start, answer_end = self.find_answer_span(context, answer)
        
        # Convert character positions to token positions
        offset_mapping = encoding.offset_mapping[0].numpy()
        start_token = 0
        end_token = 0
        
        for idx, (start, end) in enumerate(offset_mapping):
            if start <= answer_start <= end:
                start_token = idx
            if start <= answer_end <= end:
                end_token = idx
                break
        
        # Remove offset mapping
        encoding.pop("offset_mapping")
        
        # Prepare final encoding
        encoding = {key: val.squeeze(0) for key, val in encoding.items()}
        encoding['start_positions'] = torch.tensor(start_token, dtype=torch.long)
        encoding['end_positions'] = torch.tensor(end_token, dtype=torch.long)
        
        return encoding

class ModelManager:
    def __init__(self):
        self.models = {}
        self.tokenizers = {}
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Using device: {self.device}")
        
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
            gc.collect()
    
    def initialize_models(self):
        """Initialize models with memory-efficient settings"""
        model_configs = {
            'BERT': 'bert-base-uncased',
            'RoBERTa': 'roberta-base',
            'DistilBERT': 'distilbert-base-uncased',
            'ALBERT': 'albert-base-v2',
            'DeBERTa': 'microsoft/deberta-base'
        }
        
        for name, path in model_configs.items():
            try:
                print(f"Loading model {name}...")
                
                # Load tokenizer
                self.tokenizers[name] = AutoTokenizer.from_pretrained(path)
                
                # Load model in eval mode first
                with torch.no_grad():
                    model = AutoModelForQuestionAnswering.from_pretrained(
                        path,
                        low_cpu_mem_usage=True
                    )
                    model.eval()  # Set to eval mode initially
                    
                    # Move to GPU if available
                    model = model.to(self.device)
                    
                    # Enable gradient checkpointing for memory efficiency
                    model.gradient_checkpointing_enable()
                    
                self.models[name] = model
                print(f"Successfully loaded model: {name}")
                
            except Exception as e:
                print(f"Error loading model {name}: {str(e)}")
    
    def train_model(self, model_name, train_data, val_data, output_dir):
        if model_name not in self.models:
            print(f"Model {model_name} not found!")
            return None
            
        try:
            model = self.models[model_name]
            tokenizer = self.tokenizers[model_name]
            
            # Set model to train mode
            model.train()
            
            # Create datasets
            train_dataset = QADataset(train_data, tokenizer)
            val_dataset = QADataset(val_data, tokenizer)
            
            # Model-specific batch sizes and settings
            if model_name in ['DeBERTa', 'RoBERTa']:
                batch_size = 8
                grad_accum = 4
            else:
                batch_size = 16
                grad_accum = 2
            
            # Training arguments with better memory management
            training_args = TrainingArguments(
                output_dir=output_dir,
                num_train_epochs=3,
                per_device_train_batch_size=batch_size,
                per_device_eval_batch_size=batch_size,
                gradient_accumulation_steps=grad_accum,
                learning_rate=2e-5,
                warmup_ratio=0.1,
                weight_decay=0.01,
                logging_dir='./logs',
                logging_steps=50,
                eval_steps=100,
                save_steps=100,
                evaluation_strategy="steps",
                save_strategy="steps",
                load_best_model_at_end=True,
                save_total_limit=2,
                report_to="none",
                remove_unused_columns=False,
                fp16=True if torch.cuda.is_available() else False,
                gradient_checkpointing=True,
                dataloader_num_workers=4,
                dataloader_pin_memory=True,
                metric_for_best_model="eval_loss",
                greater_is_better=False,
                max_grad_norm=1.0,
                optim="adamw_torch"
            )
            
            # Clear cache before training
            if torch.cuda.is_available():
                torch.cuda.empty_cache()
                gc.collect()
            
            print(f"Starting training for model {model_name}...")
            trainer = Trainer(
                model=model,
                args=training_args,
                train_dataset=train_dataset,
                eval_dataset=val_dataset,
                tokenizer=tokenizer
            )
            
            trainer.train()
            
            print(f"Training completed. Saving model...")
            model_save_path = os.path.join(output_dir, f"best_{model_name}")
            trainer.save_model(model_save_path)
            tokenizer.save_pretrained(model_save_path)
            
            return trainer
            
        except Exception as e:
            print(f"Error during training model {model_name}: {str(e)}")
            return None

    def cleanup(self):
        """Clean up GPU memory"""
        for model in self.models.values():
            model.cpu()
        self.models.clear()
        self.tokenizers.clear()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        gc.collect()