import pandas as pd
import textwrap

def display_article(title, text, subject, date):
    print("=" * 80)
    print("TITLE:", title)
    print("-" * 80)
    print("SUBJECT:", subject)
    print("DATE:", date)
    print("-" * 80)
    print("TEXT:")
    # Wrap text to 80 characters for readability
    wrapped_text = textwrap.fill(text[:500], width=80)
    print(wrapped_text)
    if len(text) > 500:
        print("... [text truncated]")
    print("=" * 80 + "\n")

# Load datasets
true_df = pd.read_csv('Dataset/True.csv')
fake_df = pd.read_csv('Dataset/Fake.csv')

print("\nTRUE NEWS EXAMPLES (First 3 articles)")
print("====================================")
for _, row in true_df.head(3).iterrows():
    display_article(row['title'], row['text'], row['subject'], row['date'])

print("\nFAKE NEWS EXAMPLES (First 3 articles)")
print("====================================")
for _, row in fake_df.head(3).iterrows():
    display_article(row['title'], row['text'], row['subject'], row['date'])

# Display dataset statistics
print("\nDATASET STATISTICS")
print("=================")
print(f"True News Articles: {len(true_df):,}")
print(f"Fake News Articles: {len(fake_df):,}")
print("\nSubject Distribution in True News:")
print(true_df['subject'].value_counts())
print("\nSubject Distribution in Fake News:")
print(fake_df['subject'].value_counts())
