import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
import re
import nltk
from nltk.tokenize import sent_tokenize
import torch
nltk.download('punkt')

class DataPreparator:
    def __init__(self):
        # Croatian patterns for question generation
        self.patterns = [
            # Location patterns
            (r'([^,\.]+) (?:se nalazi|je smješten[a]?) ([^,\.]+)',
             lambda m: f"Gdje se nalazi {m.group(1)}?",
             lambda m: f"{m.group(1)} {m.group(2)}"),
            
            # Description patterns
            (r'([^,\.]+) je ([^,\.]+)',
             lambda m: f"Što je {m.group(1)}?",
             lambda m: f"{m.group(1)} je {m.group(2)}"),
            
            # Feature patterns
            (r'([^,\.]+) (?:ima|sadrži|uključuje) ([^,\.]+)',
             lambda m: f"Što {m.group(1)} ima?",
             lambda m: f"{m.group(1)} ima {m.group(2)}"),
            
            # Time/period patterns
            (r'([^,\.]+) (?:se održava|traje) ([^,\.]+)',
             lambda m: f"Kada se održava {m.group(1)}?",
             lambda m: f"{m.group(1)} se održava {m.group(2)}"),
            
            # Characteristic patterns
            (r'([^,\.]+) (?:poznat[a]? je|poznat[a]? po|karakterizira[ju]?) ([^,\.]+)',
             lambda m: f"Po čemu je poznato {m.group(1)}?",
             lambda m: f"{m.group(1)} je poznato po {m.group(2)}"),
            
            # Number patterns
            (r'([^,\.]+) (?:broji|ima|sadrži) (\d+[^,\.]+)',
             lambda m: f"Koliko {m.group(2)} ima {m.group(1)}?",
             lambda m: f"{m.group(1)} ima {m.group(2)}")
        ]
        
        # Additional patterns for answer validation
        self.invalid_starts = ['i', 'ili', 'te', 'a', 'ali', 'no', 'dok']
        self.min_answer_words = 3
        self.max_answer_words = 50

    def custom_sentence_split(self, text):
        """Enhanced sentence splitting for Croatian text"""
        # Pre-process to handle common abbreviations
        text = re.sub(r'(?<=\d)\s*\.\s*(?=\d)', '<DECIMAL>', text)  # Save decimal points
        text = re.sub(r'(?<=\w)\s*\.\s*(?=[A-ZČĆĐŠŽ])', '.<SPLIT>', text)  # Mark sentence boundaries
        
        # Split sentences
        sentences = [s.strip() for s in text.split('<SPLIT>')]
        
        # Post-process to restore decimal points
        sentences = [s.replace('<DECIMAL>', '.') for s in sentences]
        
        return [s for s in sentences if len(s.split()) >= 3]  # Filter very short sentences

    def is_valid_answer(self, answer):
        """Check if the answer is valid"""
        # Remove leading/trailing punctuation and whitespace
        answer = answer.strip('.,;: ')
        
        # Check length
        words = answer.split()
        if len(words) < self.min_answer_words or len(words) > self.max_answer_words:
            return False
        
        # Check if starts with invalid words
        if words[0].lower() in self.invalid_starts:
            return False
        
        # Check if contains question words
        if any(q in answer.lower() for q in ['što', 'gdje', 'kada', 'tko', 'kako', 'zašto', 'koliko']):
            return False
        
        return True

    def create_qa_pairs(self, text):
        """Generate question-answer pairs from text"""
        sentences = self.custom_sentence_split(text)
        qa_pairs = []
        
        for i, sentence in enumerate(sentences):
            # Create context from surrounding sentences
            start_idx = max(0, i - 1)
            end_idx = min(len(sentences), i + 2)
            context = ' '.join(sentences[start_idx:end_idx])
            
            # Generate QA pairs using patterns
            if len(sentence.split()) >= 5:  # Skip very short sentences
                for pattern, q_gen, a_gen in self.patterns:
                    matches = list(re.finditer(pattern, sentence))
                    
                    for match in matches:
                        try:
                            question = q_gen(match)
                            answer = a_gen(match)
                            
                            # Validate the generated QA pair
                            if (self.is_valid_answer(answer) and
                                len(question.split()) >= 3 and
                                answer not in [pair['answer'] for pair in qa_pairs]):
                                
                                qa_pairs.append({
                                    'question': question,
                                    'answer': answer,
                                    'context': context
                                })
                        except Exception as e:
                            print(f"Error generating QA pair: {str(e)}")
                            continue
        
        return qa_pairs

    def prepare_tourism_data(self, csv_path, test_size=0.2, val_size=0.1):
        """Prepare dataset for training"""
        try:
            # Load and validate data
            df = pd.read_csv(csv_path)
            if 'text' not in df.columns:
                raise ValueError("CSV must contain a 'text' column")
            
            # Create QA pairs from all texts
            all_qa_pairs = []
            for text in df['text']:
                if isinstance(text, str) and text.strip():
                    qa_pairs = self.create_qa_pairs(text)
                    all_qa_pairs.extend(qa_pairs)
            
            if not all_qa_pairs:
                raise ValueError("No valid QA pairs generated from the texts")
            
            # Convert to DataFrame
            qa_df = pd.DataFrame(all_qa_pairs)
            
            # Shuffle the data
            qa_df = qa_df.sample(frac=1, random_state=42).reset_index(drop=True)
            
            # Split into train, validation, and test sets
            train_size = 1 - test_size - val_size
            
            # First split: separate training data
            train_df, temp_df = train_test_split(
                qa_df,
                test_size=(test_size + val_size),
                random_state=42
            )
            
            # Second split: separate validation and test data
            val_df, test_df = train_test_split(
                temp_df,
                test_size=test_size/(test_size + val_size),
                random_state=42
            )
            
            print(f"Dataset splits created:")
            print(f"Training samples: {len(train_df)}")
            print(f"Validation samples: {len(val_df)}")
            print(f"Test samples: {len(test_df)}")
            
            return train_df, val_df, test_df
            
        except Exception as e:
            print(f"Error preparing tourism data: {str(e)}")
            return None, None, None