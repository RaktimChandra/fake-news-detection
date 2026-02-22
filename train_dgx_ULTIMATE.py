"""
ULTIMATE DGX A100 Training Script
With: Data Augmentation + Ensemble Support + All Optimizations
Target: 99.5%+ Accuracy
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from transformers import (
    RobertaTokenizer, RobertaForSequenceClassification,
    BertTokenizer, BertForSequenceClassification,
    get_linear_schedule_with_warmup
)
from torch.utils.data import DataLoader, TensorDataset
import torch
import torch.nn as nn
from torch.optim import AdamW
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report, confusion_matrix
import time
import os
from tqdm import tqdm
import json
import random

class DataAugmenter:
    """Data augmentation for text"""
    
    @staticmethod
    def synonym_replacement(text, n=2):
        """Replace n words with synonyms"""
        words = text.split()
        if len(words) < 5:
            return text
        
        # Simple synonym replacement (in production, use nltk wordnet)
        for _ in range(min(n, len(words))):
            idx = random.randint(0, len(words)-1)
            # Placeholder for actual synonym replacement
        
        return text
    
    @staticmethod
    def random_deletion(text, p=0.1):
        """Randomly delete words with probability p"""
        words = text.split()
        if len(words) == 1:
            return text
        
        new_words = [w for w in words if random.random() > p]
        
        if len(new_words) == 0:
            return random.choice(words)
        
        return ' '.join(new_words)
    
    @staticmethod
    def random_swap(text, n=2):
        """Randomly swap n pairs of words"""
        words = text.split()
        if len(words) < 2:
            return text
        
        for _ in range(n):
            idx1, idx2 = random.sample(range(len(words)), 2)
            words[idx1], words[idx2] = words[idx2], words[idx1]
        
        return ' '.join(words)
    
    @staticmethod
    def augment(text, label):
        """Apply random augmentation"""
        techniques = [
            lambda t: DataAugmenter.random_deletion(t, 0.1),
            lambda t: DataAugmenter.random_swap(t, 2),
            lambda t: t  # No change (original)
        ]
        
        aug_func = random.choice(techniques)
        return aug_func(text), label


class UltimateDGXTrainer:
    def __init__(self, data_path='world_class_dataset/world_class_master_dataset.csv'):
        self.data_path = data_path
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.num_gpus = torch.cuda.device_count()
        
        print("="*80)
        print("🚀 ULTIMATE DGX A100 TRAINER")
        print("="*80)
        print(f"Features: Data Augmentation + Multi-Model + All Optimizations")
        print(f"Target: 99.5%+ Accuracy")
        print(f"GPUs: {self.num_gpus}")
        print("="*80)
        
        self.augmenter = DataAugmenter()
        self.models = {}
        self.histories = {}
    
    def load_data(self, augmentation_factor=2):
        """Load data with augmentation"""
        print(f"\n📁 Loading dataset from {self.data_path}...")
        
        df = pd.read_csv(self.data_path)
        print(f"✅ Loaded {len(df):,} articles")
        
        # Original data
        X_orig = df['text'].fillna('').astype(str)
        y_orig = df['label'].values
        
        # Apply data augmentation
        if augmentation_factor > 1:
            print(f"\n🔄 Applying {augmentation_factor}x data augmentation...")
            
            X_aug = []
            y_aug = []
            
            for text, label in tqdm(zip(X_orig, y_orig), total=len(X_orig), desc="Augmenting"):
                # Add original
                X_aug.append(text)
                y_aug.append(label)
                
                # Add augmented versions
                for _ in range(augmentation_factor - 1):
                    aug_text, aug_label = self.augmenter.augment(text, label)
                    X_aug.append(aug_text)
                    y_aug.append(aug_label)
            
            X = np.array(X_aug)
            y = np.array(y_aug)
            
            print(f"✅ Augmented: {len(X_orig):,} → {len(X):,} articles ({augmentation_factor}x)")
        else:
            X = X_orig.values
            y = y_orig
        
        # Stats
        fake_count = (y == 0).sum()
        real_count = (y == 1).sum()
        print(f"\n📊 Dataset: {fake_count:,} fake / {real_count:,} real")
        
        self.X = X
        self.y = y
        return True
    
    def prepare_data(self, model_name='roberta-large', test_size=0.15, val_size=0.1, max_length=512):
        """Prepare data for training"""
        print(f"\n🔄 Preparing data for {model_name}...")
        
        # Tokenizer
        if 'roberta' in model_name:
            tokenizer = RobertaTokenizer.from_pretrained(model_name)
        else:
            tokenizer = BertTokenizer.from_pretrained(model_name)
        
        # Splits
        X_train, X_test, y_train, y_test = train_test_split(
            self.X, self.y, test_size=test_size, random_state=42, stratify=self.y
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_train, y_train, test_size=val_size/(1-test_size),
            random_state=42, stratify=y_train
        )
        
        print(f"   Train: {len(X_train):,}")
        print(f"   Val: {len(X_val):,}")
        print(f"   Test: {len(X_test):,}")
        
        # Tokenize
        print(f"\n🔤 Tokenizing (max_length={max_length})...")
        
        train_encodings = tokenizer(
            list(X_train), truncation=True, padding=True,
            max_length=max_length, return_tensors='pt'
        )
        
        val_encodings = tokenizer(
            list(X_val), truncation=True, padding=True,
            max_length=max_length, return_tensors='pt'
        )
        
        test_encodings = tokenizer(
            list(X_test), truncation=True, padding=True,
            max_length=max_length, return_tensors='pt'
        )
        
        # Datasets
        train_dataset = TensorDataset(
            train_encodings['input_ids'],
            train_encodings['attention_mask'],
            torch.tensor(y_train)
        )
        
        val_dataset = TensorDataset(
            val_encodings['input_ids'],
            val_encodings['attention_mask'],
            torch.tensor(y_val)
        )
        
        test_dataset = TensorDataset(
            test_encodings['input_ids'],
            test_encodings['attention_mask'],
            torch.tensor(y_test)
        )
        
        print("✅ Data preparation complete!")
        
        return {
            'train': train_dataset,
            'val': val_dataset,
            'test': test_dataset,
            'y_test': y_test
        }
    
    def train_model(self, model_name='roberta-large', epochs=6, batch_size=32, learning_rate=2e-5):
        """Train a single model"""
        
        print("\n" + "="*80)
        print(f"🎓 TRAINING: {model_name}")
        print("="*80)
        
        # Prepare data
        datasets = self.prepare_data(model_name)
        
        # Initialize model
        if 'roberta' in model_name:
            model = RobertaForSequenceClassification.from_pretrained(model_name, num_labels=2)
        else:
            model = BertForSequenceClassification.from_pretrained(model_name, num_labels=2)
        
        # Multi-GPU
        if self.num_gpus > 1:
            model = nn.DataParallel(model)
        
        model.to(self.device)
        
        # Data loaders
        train_loader = DataLoader(
            datasets['train'],
            batch_size=batch_size,
            shuffle=True,
            num_workers=8,
            pin_memory=True
        )
        
        val_loader = DataLoader(
            datasets['val'],
            batch_size=batch_size * 2,
            num_workers=8,
            pin_memory=True
        )
        
        # Optimizer & Scheduler
        optimizer = AdamW(model.parameters(), lr=learning_rate, weight_decay=0.01)
        
        total_steps = len(train_loader) * epochs
        scheduler = get_linear_schedule_with_warmup(
            optimizer,
            num_warmup_steps=int(total_steps * 0.1),
            num_training_steps=total_steps
        )
        
        # Training
        best_val_acc = 0
        history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}
        
        for epoch in range(epochs):
            print(f"\n{'='*80}")
            print(f"📅 EPOCH {epoch + 1}/{epochs}")
            print('='*80)
            
            # Train
            model.train()
            train_loss = 0
            train_correct = 0
            train_total = 0
            
            for batch in tqdm(train_loader, desc='Training'):
                input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                
                optimizer.zero_grad()
                outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                
                loss = outputs.loss
                if loss.dim() > 0:
                    loss = loss.mean()
                
                train_loss += loss.item()
                
                predictions = torch.argmax(outputs.logits, dim=1)
                train_correct += (predictions == labels).sum().item()
                train_total += labels.size(0)
                
                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
                optimizer.step()
                scheduler.step()
            
            avg_train_loss = train_loss / len(train_loader)
            train_accuracy = train_correct / train_total
            
            # Validation
            model.eval()
            val_loss = 0
            val_correct = 0
            val_total = 0
            
            with torch.no_grad():
                for batch in tqdm(val_loader, desc='Validation'):
                    input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
                    
                    loss = outputs.loss
                    if loss.dim() > 0:
                        loss = loss.mean()
                    
                    val_loss += loss.item()
                    predictions = torch.argmax(outputs.logits, dim=1)
                    val_correct += (predictions == labels).sum().item()
                    val_total += labels.size(0)
            
            avg_val_loss = val_loss / len(val_loader)
            val_accuracy = val_correct / val_total
            
            # History
            history['train_loss'].append(avg_train_loss)
            history['train_acc'].append(train_accuracy)
            history['val_loss'].append(avg_val_loss)
            history['val_acc'].append(val_accuracy)
            
            print(f"\n📊 Epoch {epoch + 1} Results:")
            print(f"   Train Loss: {avg_train_loss:.4f} | Train Acc: {train_accuracy*100:.2f}%")
            print(f"   Val Loss: {avg_val_loss:.4f} | Val Acc: {val_accuracy*100:.2f}%")
            
            # Save best
            if val_accuracy > best_val_acc:
                best_val_acc = val_accuracy
                print(f"   🌟 New best! Saving...")
                model_to_save = model.module if hasattr(model, 'module') else model
                
                save_path = f'world_class_dataset/{model_name.replace("/", "_")}_best.pt'
                torch.save({
                    'model_state_dict': model_to_save.state_dict(),
                    'history': history,
                    'val_acc': val_accuracy
                }, save_path)
        
        self.models[model_name] = model
        self.histories[model_name] = history
        
        return model, datasets, best_val_acc
    
    def train_ensemble(self):
        """Train multiple models for ensemble"""
        print("\n" + "="*80)
        print("🎯 ENSEMBLE TRAINING")
        print("="*80)
        
        models_to_train = [
            'roberta-large',
            'bert-large-uncased',
        ]
        
        results = {}
        
        for model_name in models_to_train:
            print(f"\n\n{'='*80}")
            print(f"Training model {len(results)+1}/{len(models_to_train)}: {model_name}")
            print('='*80)
            
            model, datasets, best_val_acc = self.train_model(model_name)
            results[model_name] = {
                'model': model,
                'datasets': datasets,
                'val_acc': best_val_acc
            }
            
            print(f"\n✅ {model_name}: {best_val_acc*100:.2f}%")
        
        return results
    
    def evaluate_ensemble(self, results):
        """Evaluate ensemble predictions"""
        print("\n" + "="*80)
        print("🎯 ENSEMBLE EVALUATION")
        print("="*80)
        
        # Use test set from first model
        first_model_name = list(results.keys())[0]
        test_loader = DataLoader(
            results[first_model_name]['datasets']['test'],
            batch_size=64,
            num_workers=8,
            pin_memory=True
        )
        
        all_predictions = {name: [] for name in results.keys()}
        all_labels = []
        
        # Get predictions from each model
        for model_name, result in results.items():
            print(f"\n📊 Getting predictions from {model_name}...")
            model = result['model']
            model.eval()
            
            with torch.no_grad():
                for batch in tqdm(test_loader, desc=f'  {model_name}'):
                    input_ids, attention_mask, labels = [b.to(self.device) for b in batch]
                    outputs = model(input_ids=input_ids, attention_mask=attention_mask)
                    
                    probs = torch.softmax(outputs.logits, dim=1)
                    all_predictions[model_name].extend(probs.cpu().numpy())
                    
                    if model_name == first_model_name:
                        all_labels.extend(labels.cpu().numpy())
        
        # Ensemble by averaging probabilities
        print("\n🔗 Computing ensemble predictions...")
        ensemble_probs = np.mean([np.array(preds) for preds in all_predictions.values()], axis=0)
        ensemble_preds = np.argmax(ensemble_probs, axis=1)
        
        # Individual model accuracies
        print("\n📊 Individual Model Accuracies:")
        for model_name, preds in all_predictions.items():
            individual_preds = np.argmax(np.array(preds), axis=1)
            acc = accuracy_score(all_labels, individual_preds)
            print(f"   {model_name}: {acc*100:.2f}%")
        
        # Ensemble accuracy
        ensemble_acc = accuracy_score(all_labels, ensemble_preds)
        ensemble_precision = precision_score(all_labels, ensemble_preds, average='weighted')
        ensemble_recall = recall_score(all_labels, ensemble_preds, average='weighted')
        ensemble_f1 = f1_score(all_labels, ensemble_preds, average='weighted')
        
        print("\n" + "="*80)
        print("🎊 ENSEMBLE RESULTS:")
        print("="*80)
        print(f"   Accuracy:  {ensemble_acc*100:.2f}%")
        print(f"   Precision: {ensemble_precision*100:.2f}%")
        print(f"   Recall:    {ensemble_recall*100:.2f}%")
        print(f"   F1-Score:  {ensemble_f1*100:.2f}%")
        
        print("\n📋 Classification Report:")
        print(classification_report(all_labels, ensemble_preds, target_names=['Fake', 'Real'], digits=4))
        
        # Save ensemble results
        ensemble_results = {
            'accuracy': ensemble_acc,
            'precision': ensemble_precision,
            'recall': ensemble_recall,
            'f1_score': ensemble_f1
        }
        
        with open('world_class_dataset/ensemble_results.json', 'w') as f:
            json.dump(ensemble_results, f, indent=2)
        
        return ensemble_results


if __name__ == '__main__':
    print("="*80)
    print("🚀 ULTIMATE DGX A100 TRAINING - ALL OPTIMIZATIONS")
    print("="*80)
    
    trainer = UltimateDGXTrainer()
    
    # Load with data augmentation (2x)
    trainer.load_data(augmentation_factor=2)
    
    # Train ensemble
    results = trainer.train_ensemble()
    
    # Evaluate ensemble
    ensemble_results = trainer.evaluate_ensemble(results)
    
    print("\n" + "="*80)
    print("🎊 ULTIMATE TRAINING COMPLETE!")
    print("="*80)
    print(f"Ensemble Accuracy: {ensemble_results['accuracy']*100:.2f}%")
    print("Models saved in: world_class_dataset/")
