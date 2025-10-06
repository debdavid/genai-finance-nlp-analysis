import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from gensim import corpora
from gensim.models.ldamodel import LdaModel
from sklearn.feature_extraction.text import TfidfVectorizer
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import os

# Download NLTK resources
nltk.download('punkt')
nltk.download('stopwords')

# Paths
METADATA_PATH = "data/processed/metadata.csv"
OUTPUT_PATH = "data/processed/analysis_results.csv"
os.makedirs("data/processed", exist_ok=True)

# Load data
df = pd.read_csv(METADATA_PATH)
stop_words = set(stopwords.words('english'))

def preprocess_text(text):
    """Preprocess text for analysis."""
    tokens = word_tokenize(text.lower())
    tokens = [t for t in tokens if t.isalpha() and t not in stop_words]
    return " ".join(tokens)

# Apply preprocessing
df["processed_text"] = df["text"].apply(preprocess_text)

# TF-IDF
vectorizer = TfidfVectorizer(max_features=1000)
tfidf_matrix = vectorizer.fit_transform(df["processed_text"])
feature_names = vectorizer.get_feature_names_out()
df["top_keywords"] = [
    "|".join([feature_names[i] for i in tfidf_matrix[row].toarray()[0].argsort()[-5:][::-1]])
    for row in range(tfidf_matrix.shape[0])
]

# LDA
texts = [text.split() for text in df["processed_text"]]
dictionary = corpora.Dictionary(texts)
corpus = [dictionary.doc2bow(text) for text in texts]
lda = LdaModel(corpus, num_topics=5, id2word=dictionary, passes=10)
df["topics"] = ["|".join([f"Topic {topic[0]}" for topic in lda[doc]]) for doc in corpus]

# Sentiment Analysis
analyzer = SentimentIntensityAnalyzer()
df["vader_sentiment"] = df["text"].apply(lambda x: analyzer.polarity_scores(x)["compound"])
df["textblob_sentiment"] = df["text"].apply(lambda x: TextBlob(x).sentiment.polarity)

# Save results
df.to_csv(OUTPUT_PATH, index=False)
print(f"Analysis completed, saved to {OUTPUT_PATH}")