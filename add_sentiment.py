import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# Load cleaned texts
df = pd.read_csv('data/cleaned_texts.csv')  # Load existing CSV with Firm_Report, Text

# Initialize VADER
analyzer = SentimentIntensityAnalyzer()  # Create VADER analyzer instance

# Calculate sentiment scores
df['Sentiment'] = df['Text'].apply(lambda x: analyzer.polarity_scores(x)['compound'])  # Compute VADER compound score (-1 to +1)

# Verify
print(df[['Firm_Report', 'Sentiment']])  # Check Firm_Report and Sentiment columns

# Save updated CSV
df.to_csv('data/cleaned_texts.csv', index=False)  # Overwrite CSV with Sentiment column