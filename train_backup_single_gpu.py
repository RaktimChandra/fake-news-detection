"""
================================================================================
FAKE NEWS DETECTION - BACKUP TRAINING SCRIPT (Single GPU)
================================================================================
Purpose: Fallback training if DGX A100 is not available
Dataset: 425,986 articles (world_class_master_dataset.csv)
Hardware: Works on single GPU (GTX 1080, RTX 3060, etc.)
Expected: 98-99% accuracy (slightly lower than DGX ensemble)
Time: 12-18 hours on consumer GPU
================================================================================
"""

import pandas as pd
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader
from transformers import BertTokenizer, BertForSequenceClassification, AdamW, get_linear_schedule_with_warmup
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, classification_report
from tqdm import tqdm
import random
import json
from datetime import datetime

# ============================================================================
# CONFIGURATION - OPTIMIZED FOR SINGLE GPU
# ============================================================================
CONFIG = {
    'dataset_path': 'world_class_dataset/world_class_master_dataset.csv',
    'model_name': 'bert-base-uncased',  # Smaller than BERT-large for memory
    'max_length': 256,  # Reduced from 512 to save memory
    'batch_size': 16,  # Smaller batch for single GPU
    'epochs': 4,  # Fewer epochs but still effective
    'learning_rate': 2e-5,
    'warmup_steps': 500,
    'save_path': 'model_backup_single_gpu.pt',
    'augmentation_factor': 1.5,  # 1.5x augmentation (lighter than 2x)
    'sample_size': None,  # None = use all data, or set to 100000 for faster testing
}

print("=" * 80)
print("🔥 FAKE NEWS DETECTION - BACKUP TRAINING (Single GPU)")
print("=" * 80)
print(f"Dataset: {CONFIG['dataset_path']}")
print(f"Model: {CONFIG['model_name']}")
print(f"Hardware: Single GPU (if available) or CPU")
print(f"Expected Time: 12-18 hours")
print(f"Expected Accuracy: 98-99%")
print("=" * 80)

# ============================================================================
# DATA AUGMENTATION
# ============================================================================
def augment_text(text, augmentation_prob=0.15):
    """Light data augmentation for text"""
    words = text.split()
    if len(words) < 3:
        return text
    
    # Random word deletion (10% chance)
    if random.random() < augmentation_prob:
        words = [w for w in words if random.random() > 0.1]
    
    # Random word swap (10% chance)
    if random.random() < augmentation_prob and len(words) > 1:
        idx1, idx2 = random.sample(range(len(words)), 2)
        words[idx1], words[idx2] = words[idx2], words[idx1]
    
    return ' '.join(words) if words else text

# ============================================================================
# DATASET CLASS
# ============================================================================
class FakeNewsDataset(Dataset):
    def __init__(self, texts, labels, tokenizer, max_length, augment=False):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.augment = augment
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        
        # Apply augmentation during training
        if self.augment:
            text = augment_text(text)
        
        encoding = self.tokenizer.encode_plus(
            text,
            add_special_tokens=True,
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_attention_mask=True,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'label': torch.tensor(self.labels[idx], dtype=torch.long)
        }

# ============================================================================
# LOAD AND PREPARE DATA
# ============================================================================
print("\n📂 Loading dataset...")
df = pd.read_csv(CONFIG['dataset_path'])
print(f"   ✅ Loaded: {len(df):,} articles")

# Sample if specified (for quick testing)
if CONFIG['sample_size'] and CONFIG['sample_size'] < len(df):
    print(f"   ⚠️  Sampling {CONFIG['sample_size']:,} articles for quick testing")
    df = df.sample(n=CONFIG['sample_size'], random_state=42)

print(f"\n📊 Dataset Statistics:")
print(f"   Total: {len(df):,} articles")
print(f"   Fake: {(df['label'] == 1).sum():,} ({(df['label'] == 1).sum() / len(df) * 100:.1f}%)")
print(f"   Real: {(df['label'] == 0).sum():,} ({(df['label'] == 0).sum() / len(df) * 100:.1f}%)")

# Prepare text and labels
texts = df['text'].values
labels = df['label'].values

# Train/validation split
print("\n🔀 Splitting data...")
train_texts, val_texts, train_labels, val_labels = train_test_split(
    texts, labels, test_size=0.1, random_state=42, stratify=labels
)
print(f"   Training: {len(train_texts):,} articles")
print(f"   Validation: {len(val_texts):,} articles")

# Apply augmentation to training set
if CONFIG['augmentation_factor'] > 1:
    print(f"\n🔄 Applying {CONFIG['augmentation_factor']}x data augmentation...")
    aug_factor = int((CONFIG['augmentation_factor'] - 1) * len(train_texts))
    aug_indices = np.random.choice(len(train_texts), aug_factor, replace=True)
    
    aug_texts = [augment_text(train_texts[i]) for i in aug_indices]
    aug_labels = [train_labels[i] for i in aug_indices]
    
    train_texts = np.concatenate([train_texts, aug_texts])
    train_labels = np.concatenate([train_labels, aug_labels])
    
    print(f"   ✅ Training samples after augmentation: {len(train_texts):,}")

# ============================================================================
# TOKENIZER AND DATASETS
# ============================================================================
print(f"\n🔤 Loading tokenizer: {CONFIG['model_name']}...")
tokenizer = BertTokenizer.from_pretrained(CONFIG['model_name'])

print("\n📦 Creating datasets...")
train_dataset = FakeNewsDataset(train_texts, train_labels, tokenizer, CONFIG['max_length'], augment=False)
val_dataset = FakeNewsDataset(val_texts, val_labels, tokenizer, CONFIG['max_length'], augment=False)

train_loader = DataLoader(train_dataset, batch_size=CONFIG['batch_size'], shuffle=True, num_workers=0)
val_loader = DataLoader(val_dataset, batch_size=CONFIG['batch_size'], shuffle=False, num_workers=0)

print(f"   ✅ Training batches: {len(train_loader)}")
print(f"   ✅ Validation batches: {len(val_loader)}")

# ============================================================================
# MODEL SETUP
# ============================================================================
print(f"\n🤖 Loading model: {CONFIG['model_name']}...")
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
print(f"   Device: {device}")

model = BertForSequenceClassification.from_pretrained(
    CONFIG['model_name'],
    num_labels=2
)
model = model.to(device)

# Optimizer and scheduler
optimizer = AdamW(model.parameters(), lr=CONFIG['learning_rate'], eps=1e-8)
total_steps = len(train_loader) * CONFIG['epochs']
scheduler = get_linear_schedule_with_warmup(
    optimizer,
    num_warmup_steps=CONFIG['warmup_steps'],
    num_training_steps=total_steps
)

print(f"   ✅ Model loaded")
print(f"   Total training steps: {total_steps:,}")

# ============================================================================
# TRAINING FUNCTIONS
# ============================================================================
def train_epoch(model, data_loader, optimizer, scheduler, device):
    model.train()
    total_loss = 0
    predictions = []
    true_labels = []
    
    progress_bar = tqdm(data_loader, desc='Training')
    for batch in progress_bar:
        optimizer.zero_grad()
        
        input_ids = batch['input_ids'].to(device)
        attention_mask = batch['attention_mask'].to(device)
        labels = batch['label'].to(device)
        
        outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
        loss = outputs.loss
        logits = outputs.logits
        
        loss.backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        scheduler.step()
        
        total_loss += loss.item()
        
        preds = torch.argmax(logits, dim=1)
        predictions.extend(preds.cpu().numpy())
        true_labels.extend(labels.cpu().numpy())
        
        progress_bar.set_postfix({'loss': loss.item()})
    
    avg_loss = total_loss / len(data_loader)
    accuracy = accuracy_score(true_labels, predictions)
    
    return avg_loss, accuracy

def evaluate(model, data_loader, device):
    model.eval()
    total_loss = 0
    predictions = []
    true_labels = []
    
    with torch.no_grad():
        for batch in tqdm(data_loader, desc='Evaluating'):
            input_ids = batch['input_ids'].to(device)
            attention_mask = batch['attention_mask'].to(device)
            labels = batch['label'].to(device)
            
            outputs = model(input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            logits = outputs.logits
            
            total_loss += loss.item()
            
            preds = torch.argmax(logits, dim=1)
            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
    
    avg_loss = total_loss / len(data_loader)
    accuracy = accuracy_score(true_labels, predictions)
    precision, recall, f1, _ = precision_recall_fscore_support(
        true_labels, predictions, average='binary', zero_division=0
    )
    
    return avg_loss, accuracy, precision, recall, f1, predictions, true_labels

# ============================================================================
# TRAINING LOOP
# ============================================================================
print("\n" + "=" * 80)
print("🚀 STARTING TRAINING")
print("=" * 80)

best_accuracy = 0
training_history = []
start_time = datetime.now()

for epoch in range(CONFIG['epochs']):
    print(f"\n📊 Epoch {epoch + 1}/{CONFIG['epochs']}")
    print("-" * 80)
    
    # Train
    train_loss, train_acc = train_epoch(model, train_loader, optimizer, scheduler, device)
    
    # Evaluate
    val_loss, val_acc, val_precision, val_recall, val_f1, _, _ = evaluate(model, val_loader, device)
    
    # Save history
    history_entry = {
        'epoch': epoch + 1,
        'train_loss': train_loss,
        'train_accuracy': train_acc,
        'val_loss': val_loss,
        'val_accuracy': val_acc,
        'val_precision': val_precision,
        'val_recall': val_recall,
        'val_f1': val_f1
    }
    training_history.append(history_entry)
    
    # Print results
    print(f"\n📈 Results:")
    print(f"   Training   - Loss: {train_loss:.4f}, Accuracy: {train_acc:.4f}")
    print(f"   Validation - Loss: {val_loss:.4f}, Accuracy: {val_acc:.4f}")
    print(f"   Precision: {val_precision:.4f}, Recall: {val_recall:.4f}, F1: {val_f1:.4f}")
    
    # Save best model
    if val_acc > best_accuracy:
        best_accuracy = val_acc
        print(f"\n   ✅ New best accuracy: {best_accuracy:.4f}! Saving model...")
        torch.save({
            'epoch': epoch + 1,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'accuracy': best_accuracy,
            'config': CONFIG
        }, CONFIG['save_path'])

end_time = datetime.now()
training_duration = end_time - start_time

# ============================================================================
# FINAL EVALUATION
# ============================================================================
print("\n" + "=" * 80)
print("📊 FINAL EVALUATION")
print("=" * 80)

# Load best model
checkpoint = torch.load(CONFIG['save_path'])
model.load_state_dict(checkpoint['model_state_dict'])

val_loss, val_acc, val_precision, val_recall, val_f1, predictions, true_labels = evaluate(
    model, val_loader, device
)

print(f"\n🎯 Best Model Performance:")
print(f"   Accuracy:  {val_acc:.4f} ({val_acc * 100:.2f}%)")
print(f"   Precision: {val_precision:.4f}")
print(f"   Recall:    {val_recall:.4f}")
print(f"   F1-Score:  {val_f1:.4f}")

print(f"\n⏱️  Training Time: {training_duration}")

# Classification report
print("\n📋 Classification Report:")
print(classification_report(true_labels, predictions, target_names=['Real', 'Fake']))

# ============================================================================
# SAVE RESULTS
# ============================================================================
results = {
    'config': CONFIG,
    'best_accuracy': float(val_acc),
    'precision': float(val_precision),
    'recall': float(val_recall),
    'f1_score': float(val_f1),
    'training_duration': str(training_duration),
    'training_history': training_history,
    'dataset_size': len(df),
    'training_samples': len(train_texts),
    'validation_samples': len(val_texts)
}

with open('training_results_backup.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\n✅ Results saved to: training_results_backup.json")
print(f"✅ Model saved to: {CONFIG['save_path']}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "=" * 80)
print("🎊 TRAINING COMPLETE!")
print("=" * 80)
print(f"\n📊 Final Results:")
print(f"   Dataset: {len(df):,} articles")
print(f"   Accuracy: {val_acc * 100:.2f}%")
print(f"   Training Time: {training_duration}")
print(f"   Model: {CONFIG['save_path']}")
print(f"\n🎯 Next Steps:")
print(f"   1. Update app_realtime.py to load this model")
print(f"   2. Test with new articles")
print(f"   3. Deploy with {val_acc * 100:.1f}% accuracy!")
print("\n" + "=" * 80)
