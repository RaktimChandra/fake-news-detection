import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# Create visualizations directory if it doesn't exist
if not os.path.exists('visualizations'):
    os.makedirs('visualizations')

# Load datasets
true_df = pd.read_csv('Dataset/True.csv')
fake_df = pd.read_csv('Dataset/Fake.csv')

# Add labels
true_df['label'] = 'True'
fake_df['label'] = 'Fake'

# Combine datasets
combined_df = pd.concat([true_df, fake_df], ignore_index=True)

# 1. Dataset Size Comparison
plt.figure(figsize=(10, 6))
sns.countplot(data=combined_df, x='label')
plt.title('Distribution of True vs Fake News Articles')
plt.savefig('visualizations/dataset_distribution.png')
plt.close()

# 2. Subject Distribution
plt.figure(figsize=(12, 6))
sns.countplot(data=combined_df, x='subject', hue='label')
plt.xticks(rotation=45)
plt.title('Distribution of Articles by Subject')
plt.tight_layout()
plt.savefig('visualizations/subject_distribution.png')
plt.close()

# 3. Text Length Analysis
combined_df['title_length'] = combined_df['title'].str.len()
combined_df['text_length'] = combined_df['text'].str.len()

# Title length distribution
plt.figure(figsize=(10, 6))
sns.boxplot(data=combined_df, x='label', y='title_length')
plt.title('Distribution of Title Lengths')
plt.savefig('visualizations/title_length_distribution.png')
plt.close()

# Text length distribution
plt.figure(figsize=(10, 6))
sns.boxplot(data=combined_df, x='label', y='text_length')
plt.title('Distribution of Article Lengths')
plt.savefig('visualizations/text_length_distribution.png')
plt.close()

# 4. Publication Date Analysis
combined_df['date'] = pd.to_datetime(combined_df['date'])
combined_df['month_year'] = combined_df['date'].dt.to_period('M')

# Time series of publications
plt.figure(figsize=(15, 6))
combined_df.groupby(['month_year', 'label']).size().unstack().plot(kind='line', marker='o')
plt.title('Publication Trend Over Time')
plt.xlabel('Date')
plt.ylabel('Number of Articles')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('visualizations/publication_trend.png')
plt.close()

# 5. Create a summary text file
with open('visualizations/dataset_summary.txt', 'w') as f:
    f.write("Dataset Summary Statistics\n")
    f.write("========================\n\n")
    
    f.write("1. Dataset Size\n")
    f.write(f"True News Articles: {len(true_df)}\n")
    f.write(f"Fake News Articles: {len(fake_df)}\n")
    f.write(f"Total Articles: {len(combined_df)}\n\n")
    
    f.write("2. Subject Categories\n")
    f.write(combined_df.groupby(['subject', 'label']).size().to_string())
    f.write("\n\n")
    
    f.write("3. Text Statistics\n")
    f.write("Title Length (characters):\n")
    f.write(combined_df.groupby('label')['title_length'].describe().to_string())
    f.write("\n\nArticle Length (characters):\n")
    f.write(combined_df.groupby('label')['text_length'].describe().to_string())
    f.write("\n\n")
    
    f.write("4. Date Range\n")
    f.write(f"Earliest Article: {combined_df['date'].min()}\n")
    f.write(f"Latest Article: {combined_df['date'].max()}\n")

print("Dataset visualizations and summary have been created in the 'visualizations' directory.")
