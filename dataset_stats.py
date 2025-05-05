import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Create visualizations directory
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

# Load datasets
print("Loading datasets...")
true_df = pd.read_csv('Dataset/True.csv')
fake_df = pd.read_csv('Dataset/Fake.csv')

# Add labels
true_df['label'] = 'True'
fake_df['label'] = 'Fake'

# Combine datasets
combined_df = pd.concat([true_df, fake_df], ignore_index=True)

# Calculate text lengths
combined_df['title_length'] = combined_df['title'].str.len()
combined_df['text_length'] = combined_df['text'].str.len()

# 1. Basic Statistics
print("\nGenerating statistics...")
stats_file = 'visualizations/dataset_statistics.txt'
with open(stats_file, 'w') as f:
    f.write("FAKE NEWS DETECTION DATASET STATISTICS\n")
    f.write("====================================\n\n")
    
    f.write("1. Dataset Size\n")
    f.write("--------------\n")
    f.write(f"True News Articles: {len(true_df):,}\n")
    f.write(f"Fake News Articles: {len(fake_df):,}\n")
    f.write(f"Total Articles: {len(combined_df):,}\n\n")
    
    f.write("2. Subject Distribution\n")
    f.write("---------------------\n")
    subject_dist = combined_df.groupby(['subject', 'label']).size().unstack(fill_value=0)
    f.write(subject_dist.to_string())
    f.write("\n\n")
    
    f.write("3. Text Length Statistics\n")
    f.write("----------------------\n")
    f.write("Title Length (characters):\n")
    title_stats = combined_df.groupby('label')['title_length'].describe()
    f.write(title_stats.to_string())
    f.write("\n\nArticle Length (characters):\n")
    text_stats = combined_df.groupby('label')['text_length'].describe()
    f.write(text_stats.to_string())

# 2. Create visualizations
print("Creating visualizations...")

# Dataset distribution
plt.figure(figsize=(10, 6))
sns.countplot(data=combined_df, x='label')
plt.title('Distribution of True vs Fake News Articles')
plt.savefig('visualizations/class_distribution.png')
plt.close()

# Subject distribution
plt.figure(figsize=(12, 6))
sns.countplot(data=combined_df, x='subject', hue='label')
plt.xticks(rotation=45)
plt.title('Articles by Subject Category')
plt.tight_layout()
plt.savefig('visualizations/subject_distribution.png')
plt.close()

# Text length distributions
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

sns.boxplot(data=combined_df, x='label', y='title_length', ax=ax1)
ax1.set_title('Title Length Distribution')

sns.boxplot(data=combined_df, x='label', y='text_length', ax=ax2)
ax2.set_title('Article Length Distribution')

plt.tight_layout()
plt.savefig('visualizations/length_distributions.png')
plt.close()

print("\nDataset analysis completed! Files created in 'visualizations' directory:")
print("1. dataset_statistics.txt - Detailed statistics")
print("2. class_distribution.png - True vs Fake distribution")
print("3. subject_distribution.png - Subject category distribution")
print("4. length_distributions.png - Text length analysis")
