import evaluate
from tqdm import tqdm
import torch
import re
import numpy as np
from nltk.tokenize import word_tokenize
from nltk.translate.bleu_score import sentence_bleu
import nltk
from typing import Dict, List, Union
import string

nltk.download('punkt')
nltk.download('stopwords')
from nltk.corpus import stopwords

class Evaluator:
    def __init__(self):
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Evaluator using device: {self.device}")
        
        # English stopwords from NLTK
        self.stopwords = set(stopwords.words('english'))
        
        # Tourism-related keywords for relevance scoring
        self.tourism_keywords = {
            'hotel', 'restaurant', 'museum', 'beach', 'landmark', 'attraction', 'tour',
            'excursion', 'accommodation', 'transport', 'city', 'island', 'park', 'lake',
            'sea', 'mountain', 'church', 'cathedral', 'palace', 'fortress', 'castle',
            'festival', 'culture', 'history', 'architecture', 'tourists', 'visitors',
            'national', 'park', 'monument', 'gallery', 'square', 'street', 'promenade',
            'nature', 'heritage', 'tradition', 'food', 'wine', 'lodging', 'guide',
            'sightseeing', 'view', 'historic', 'ancient', 'medieval', 'modern',
            'experience', 'destination', 'travel', 'vacation', 'holiday', 'scenic',
            'UNESCO', 'heritage', 'site', 'traditional', 'local', 'authentic'
        }

    def find_best_answer(self, start_logits: torch.Tensor, end_logits: torch.Tensor, 
                        input_ids: torch.Tensor, tokenizer, max_answer_length: int = 50) -> str:
        """Find the best answer span from model outputs"""
        # Convert to numpy for easier handling
        start_logits = start_logits[0].cpu().numpy()
        end_logits = end_logits[0].cpu().numpy()
        
        # Get the top start and end positions
        start_idx = np.argsort(start_logits)[-20:][::-1]  # Top 20 starts
        end_idx = np.argsort(end_logits)[-20:][::-1]  # Top 20 ends
        
        best_score = float('-inf')
        best_answer = ""
        
        # Try all valid combinations of start and end positions
        for start in start_idx:
            for end in end_idx:
                if start > end or end - start + 1 > max_answer_length:
                    continue
                    
                # Skip answers starting with special tokens
                if start == 0:
                    continue
                    
                score = start_logits[start] + end_logits[end]
                if score > best_score:
                    tokens = input_ids[0][start:end + 1]
                    answer = tokenizer.decode(tokens, skip_special_tokens=True).strip()
                    
                    # Validate answer quality
                    if (len(answer.split()) >= 2 and  # At least 2 words
                        not answer.startswith('?') and  # Not a question
                        not any(answer.lower().startswith(w) for w in ['what', 'where', 'when', 'who', 'how', 'why'])):
                        
                        best_score = score
                        best_answer = answer
        
        return best_answer.strip()

    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison"""
        # Convert to lowercase and remove punctuation
        text = text.lower()
        text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Remove stopwords
        words = text.split()
        words = [w for w in words if w not in self.stopwords]
        
        return ' '.join(words)

    def compute_metrics(self, prediction: str, reference: str) -> Dict[str, float]:
        """Compute evaluation metrics for a single prediction"""
        try:
            # Normalize texts
            pred_norm = self.normalize_text(prediction)
            ref_norm = self.normalize_text(reference)
            
            # Tokenize
            pred_tokens = word_tokenize(pred_norm)
            ref_tokens = word_tokenize(ref_norm)
            
            # Exact match (after normalization)
            exact_match = float(pred_norm == ref_norm)
            
            # F1 score
            pred_set = set(pred_tokens)
            ref_set = set(ref_tokens)
            
            if not pred_set or not ref_set:
                f1 = 0.0
            else:
                intersection = pred_set & ref_set
                precision = len(intersection) / len(pred_set)
                recall = len(intersection) / len(ref_set)
                f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0
            
            # BLEU score
            try:
                bleu = sentence_bleu([ref_tokens], pred_tokens, weights=(0.5, 0.5, 0, 0))
            except:
                bleu = 0.0
            
            # Tourism relevance
            tourism_relevance = self.evaluate_tourism_relevance(prediction, reference)
            
            # Factual accuracy
            factual_accuracy = self.evaluate_factual_accuracy(prediction, reference)
            
            return {
                'exact_match': exact_match,
                'f1': f1,
                'bleu': bleu,
                'tourism_relevance': tourism_relevance,
                'factual_accuracy': factual_accuracy
            }
            
        except Exception as e:
            print(f"\nError computing metrics:")
            print(f"Prediction: {prediction}")
            print(f"Reference: {reference}")
            print(f"Error: {str(e)}")
            return {
                'exact_match': 0.0,
                'f1': 0.0,
                'bleu': 0.0,
                'tourism_relevance': 0.0,
                'factual_accuracy': 0.0
            }

    def evaluate_tourism_relevance(self, prediction: str, reference: str) -> float:
        """Evaluate how relevant the answer is to tourism domain"""
        try:
            # Get tourism keywords from both texts
            pred_keywords = set(word.lower() for word in prediction.split() 
                              if word.lower() in self.tourism_keywords)
            ref_keywords = set(word.lower() for word in reference.split() 
                             if word.lower() in self.tourism_keywords)
            
            if not ref_keywords:
                return 1.0 if not pred_keywords else 0.0
                
            # Calculate overlap
            overlap = len(pred_keywords & ref_keywords)
            return overlap / len(ref_keywords)
            
        except Exception:
            return 0.0

    def evaluate_factual_accuracy(self, prediction: str, reference: str) -> float:
        """Evaluate factual accuracy by comparing numbers, dates, and named entities"""
        try:
            # Extract numbers
            pred_numbers = set(re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', prediction))
            ref_numbers = set(re.findall(r'\d+(?:,\d+)*(?:\.\d+)?', reference))
            
            # Extract capitalized words (potential named entities)
            pred_entities = set(re.findall(r'[A-Z][a-z]+', prediction))
            ref_entities = set(re.findall(r'[A-Z][a-z]+', reference))
            
            # Calculate accuracy scores
            number_accuracy = (len(pred_numbers & ref_numbers) / len(ref_numbers) 
                             if ref_numbers else 1.0)
            entity_accuracy = (len(pred_entities & ref_entities) / len(ref_entities) 
                             if ref_entities else 1.0)
            
            return (number_accuracy + entity_accuracy) / 2
            
        except Exception:
            return 0.0

    def evaluate_model(self, model, tokenizer, test_data):
        """Evaluate model on test set"""
        print("\nStarting model evaluation...")
        model.eval()
        model.to(self.device)
        
        all_metrics = []
        detailed_results = []
        
        for _, row in tqdm(test_data.iterrows(), total=len(test_data)):
            try:
                # Prepare input
                inputs = tokenizer(
                    row['question'],
                    row['context'],
                    max_length=384,
                    truncation=True,
                    padding='max_length',
                    return_tensors='pt'
                )
                
                # Move to GPU
                inputs = {k: v.to(self.device) for k, v in inputs.items()}
                
                # Generate prediction
                with torch.no_grad():
                    outputs = model(**inputs)
                
                # Get best answer
                prediction = self.find_best_answer(
                    outputs.start_logits,
                    outputs.end_logits,
                    inputs['input_ids'],
                    tokenizer
                )
                
                # Clean prediction
                prediction = self.clean_prediction(prediction)
                
                # Store results
                detailed_results.append({
                    'question': row['question'],
                    'prediction': prediction,
                    'reference': row['answer']
                })
                
                # Print example
                print(f"\nQuestion: {row['question']}")
                print(f"Predicted: {prediction}")
                print(f"Reference: {row['answer']}")
                
                # Compute metrics
                metrics = self.compute_metrics(prediction, row['answer'])
                all_metrics.append(metrics)
                
            except Exception as e:
                print(f"Error evaluating example: {str(e)}")
                continue
        
        # Calculate final metrics
        final_results = {}
        for metric in ['exact_match', 'f1', 'bleu', 'tourism_relevance', 'factual_accuracy']:
            values = [m[metric] for m in all_metrics]
            final_results[metric] = np.mean(values) if values else 0.0
        
        print("\nEvaluation results:")
        for metric, value in final_results.items():
            print(f"{metric}: {value:.4f}")
        
        return final_results, detailed_results

    def clean_prediction(self, pred: str) -> str:
        """Clean the predicted answer"""
        if not isinstance(pred, str):
            return ""
        
        # Remove special tokens
        pred = re.sub(r'<s>|</s>|\[CLS\]|\[SEP\]|\[PAD\]', '', pred)
        
        # Remove the question if it was included in the answer
        pred = re.sub(r'^(What|Where|When|Who|How|Why).*\?', '', pred)
        
        # Clean up whitespace
        pred = ' '.join(pred.split())
        
        # Remove quotes
        pred = pred.strip('"\'')
        
        return pred.strip()