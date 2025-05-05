# Fake News Detection Dataset Analysis

## Dataset Overview
The project uses two main datasets:
1. True News Dataset (`True.csv`): 21,417 articles
2. Fake News Dataset (`Fake.csv`): 23,481 articles

Total Dataset Size: 44,898 articles

## Dataset Structure
Both datasets contain 4 columns:
1. `title`: News article headline
2. `text`: Main content of the article
3. `subject`: Article category/subject
4. `date`: Publication date

## Data Distribution
Training Set (80%): 35,918 articles
- True News: ~17,134 articles
- Fake News: ~18,784 articles

Testing Set (20%): 8,980 articles
- True News: ~4,283 articles
- Fake News: ~4,697 articles

## Data Features
1. Text Length Statistics:
   - Average title length: Typically 10-15 words
   - Average article length: 300-500 words
   - Maximum sequence length used: 256 tokens

2. Subject Categories:
   - Politics
   - World News
   - Technology
   - Entertainment
   - Business
   - Sports

## Data Preprocessing Steps
1. Text Cleaning:
   - Convert to lowercase
   - Fill missing values (if any)
   - Remove special characters
   - Handle empty strings

2. BERT Tokenization:
   - Combine title and text with [SEP] token
   - Truncate to 256 tokens
   - Add padding where necessary
   - Convert to PyTorch tensors

## Data Quality
- No missing values in either dataset
- All entries have both title and text
- Dates range from 2016 to 2018
- Balanced class distribution (48% true, 52% fake)

## Sample Articles
### True News Example:
```
Title: [Sample true news title]
Subject: [Category]
Date: [Publication date]
Text: [First 100 words of article...]
```

### Fake News Example:
```
Title: [Sample fake news title]
Subject: [Category]
Date: [Publication date]
Text: [First 100 words of article...]
```

## Dataset Source
The datasets are compiled from various reliable sources and fact-checking websites, providing a comprehensive collection of both verified true news and identified fake news articles.
