import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from transformers import BertTokenizer, BertForSequenceClassification
from torch.utils.data import DataLoader, TensorDataset
import torch
from torch.optim import AdamW
from sklearn.metrics import accuracy_score, classification_report
import time
import os
from tqdm import tqdm

class EnhancedFakeNewsDetector:
    def __init__(self):
        self.bert_tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
        self.bert_model = BertForSequenceClassification.from_pretrained('bert-base-uncased', num_labels=2)
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.bert_model.to(self.device)
        
    def prepare_existing_datasets(self):
        """Prepare existing datasets"""
        print('Loading True and Fake datasets...')
        try:
            # Load only first 1000 rows from each dataset for quick testing
            true_df = pd.read_csv('Dataset/True.csv', nrows=1000)
            fake_df = pd.read_csv('Dataset/Fake.csv', nrows=1000)
            print('Successfully loaded True and Fake datasets')
            
            # Add labels
            true_df['label'] = 1  # True news
            fake_df['label'] = 0  # Fake news
            
            # Combine datasets
            combined_df = pd.concat([true_df, fake_df], ignore_index=True)
            
            # Shuffle the data
            combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
            
            # Split into train and test (80-20 split)
            train_size = int(0.8 * len(combined_df))
            train_df = combined_df[:train_size]
            test_df = combined_df[train_size:]
            
            print(f'Dataset split: {len(train_df)} training samples, {len(test_df)} test samples')
            return train_df, test_df
            
        except Exception as e:
            print(f'Error loading datasets: {e}')
            raise

    def load_and_preprocess_data(self):
        """Load and preprocess all available datasets"""
        # Load existing datasets
        train_df, test_df = self.prepare_existing_datasets()
        
        # Clean and preprocess
        for df in [train_df, test_df]:
            text_col = 'text' if 'text' in df.columns else 'title'
            df[text_col] = df[text_col].fillna('')
            df[text_col] = df[text_col].str.lower()
        
        self.train_data = train_df
        self.test_data = test_df
        return train_df, test_df

    def prepare_bert_features(self, titles, texts):
        """Prepare features for BERT model by combining title and text"""
        # Combine title and text with [SEP] token
        combined_texts = [f"{title} [SEP] {text}" for title, text in zip(titles, texts)]
        
        encodings = self.bert_tokenizer(combined_texts,
                                      truncation=True,
                                      padding=True,
                                      max_length=256,
                                      return_tensors='pt')
        return encodings

    def train_model(self, epochs=2, batch_size=8):
        """Train the enhanced model with smaller batches and fewer epochs for testing"""
        print("Preparing training data...")
        
        # Prepare data
        X_train_title = self.train_data['title'].fillna('')
        X_train_text = self.train_data['text'].fillna('')
        y_train = self.train_data['label'].astype(int)
        
        X_test_title = self.test_data['title'].fillna('')
        X_test_text = self.test_data['text'].fillna('')
        y_test = self.test_data['label'].astype(int)
        
        print(f"Training samples: {len(y_train)}, Test samples: {len(y_test)}")
        
        # Prepare BERT features
        print("Encoding training data...")
        train_encodings = self.prepare_bert_features(X_train_title, X_train_text)
        test_encodings = self.prepare_bert_features(X_test_title, X_test_text)
        
        # Create dataloaders
        train_dataset = TensorDataset(
            train_encodings['input_ids'],
            train_encodings['attention_mask'],
            torch.tensor(y_train.values)
        )
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        
        # Initialize optimizer with a smaller learning rate
        optimizer = AdamW(self.bert_model.parameters(), lr=2e-5)
        
        # Record start time
        start_time = time.time()
        
        # Training loop
        self.bert_model.train()
        for epoch in range(epochs):
            total_loss = 0
            progress_bar = tqdm(train_loader, desc=f'Epoch {epoch + 1}/{epochs}')
            
            for batch in progress_bar:
                # Move batch to device
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                
                # Clear gradients
                optimizer.zero_grad()
                
                # Forward pass
                outputs = self.bert_model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    labels=labels
                )
                
                # Calculate loss
                loss = outputs.loss
                total_loss += loss.item()
                
                # Backward pass
                loss.backward()
                
                # Update weights
                optimizer.step()
                
                # Update progress bar
                progress_bar.set_postfix({'loss': f'{loss.item():.4f}'})
            
            # Calculate average loss for the epoch
            avg_loss = total_loss / len(train_loader)
            print(f'Epoch {epoch + 1} average loss: {avg_loss:.4f}')
            
            # Quick evaluation after each epoch
            self.bert_model.eval()
            with torch.no_grad():
                correct = 0
                total = 0
                for batch in train_loader:
                    input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                    outputs = self.bert_model(input_ids=input_ids, attention_mask=attention_mask)
                    _, predicted = torch.max(outputs.logits, 1)
                    total += labels.size(0)
                    correct += (predicted == labels).sum().item()
                print(f'Training accuracy: {100 * correct / total:.2f}%')
            self.bert_model.train()
        
        # Save the enhanced model
        print('Saving model...')
        torch.save({
            'epoch': epochs,
            'model_state_dict': self.bert_model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
        }, 'enhanced_model.pt')
        
        training_time = time.time() - start_time
        print(f"Training completed in {training_time:.2f} seconds")
        
        # Final evaluation
        print('\nEvaluating on test set...')
        test_features = self.prepare_bert_features(X_test_title, X_test_text)
        self.evaluate_model(test_features, y_test)

    def evaluate_model(self, test_features, y_test):
        """Evaluate the model on test data"""
        test_dataset = TensorDataset(
            test_features['input_ids'],
            test_features['attention_mask'],
            torch.tensor(y_test.values)
        )
        test_loader = DataLoader(test_dataset, batch_size=16)
        
        predictions = []
        self.bert_model.eval()
        with torch.no_grad():
            for batch in tqdm(test_loader, desc='Evaluating'):
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                outputs = self.bert_model(input_ids=input_ids, attention_mask=attention_mask)
                preds = torch.argmax(outputs.logits, dim=1)
                predictions.extend(preds.cpu().numpy())
        
        # Print evaluation metrics
        print('\nModel Evaluation:')
        print(classification_report(y_test, predictions))

    def predict(self, text):
        """Make predictions on new text"""
        self.bert_model.eval()
        encoding = self.prepare_bert_features(pd.Series([text]))
        
        with torch.no_grad():
            input_ids = encoding['input_ids'].to(self.device)
            attention_mask = encoding['attention_mask'].to(self.device)
            outputs = self.bert_model(input_ids=input_ids, attention_mask=attention_mask)
            prediction = torch.argmax(outputs.logits, dim=1)
        
        return 'REAL' if prediction.item() == 1 else 'FAKE'

if __name__ == '__main__':
    # Initialize and train enhanced model
    detector = EnhancedFakeNewsDetector()
    
    # Load and preprocess data
    print("Loading and preprocessing data...")
    train_df, test_df = detector.load_and_preprocess_data()
    
    # Train the enhanced model
    print("Training enhanced model...")
    detector.train_model()
    
    # Save the trained model
    print("Saving model...")
    torch.save(detector.bert_model.state_dict(), 'enhanced_model.pt')
    
    print("Enhancement complete! The new model has been saved.")
