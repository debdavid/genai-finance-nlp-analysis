import streamlit as st
import pandas as pd
import PyPDF2
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import matplotlib.pyplot as plt

# Set NLTK data path
nltk_data_dir = '/workspaces/genai-finance-nlp-analysis/nltk_data'  # Why: Use same NLTK data path as notebook
import nltk
nltk.data.path.append(nltk_data_dir)  # Why: Ensure NLTK finds punkt, stopwords, wordnet

def extract_text_from_pdf(pdf_file):
    """Extract text from PDF."""
    text = ''
    try:
        reader = PyPDF2.PdfReader(pdf_file)  # Why: Read PDF file
        if reader.is_encrypted:
            reader.decrypt('')  # Why: Handle encrypted PDFs (e.g., KPMG)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + '\n'
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {e}")  # Why: Show error in app
        return ''

lemmatizer = WordNetLemmatizer()
stop_words = set(stopwords.words('english'))

def clean_text(text):
    """Clean text for NLP."""
    try:
        text = re.sub(r'[^a-zA-Z\s]', '', text.lower())  # Why: Remove non-letters
        tokens = word_tokenize(text)  # Why: Tokenize with NLTK
    except LookupError:
        tokens = text.split()  # Why: Fallback if punkt fails
    cleaned = [lemmatizer.lemmatize(token) for token in tokens if token not in stop_words and len(token) > 3]  # Why: Lemmatize, filter stops
    return ' '.join(cleaned)

st.title("🧠 ConsultAI Insights: AI in FS")  # Why: App title
st.write("Upload a report to compare sentiment.")  # Why: User instructions

# Load benchmark data
df = pd.read_csv('data/cleaned_texts.csv')  # Why: Load preprocessed data with sentiments

# Sidebar: Show benchmark sentiments
st.sidebar.header("Benchmark Reports")  # Why: Organize benchmark info
selected_firm = st.sidebar.selectbox("View Firm", df['Firm_Report'].tolist())  # Why: Let user select report
st.sidebar.write(f"Sentiment: {df[df['Firm_Report']==selected_firm]['Sentiment'].iloc[0]:.2f}")  # Why: Show sentiment

# Upload new PDF
uploaded_file = st.file_uploader("Upload PDF", type='pdf')  # Why: Allow PDF upload
if uploaded_file:
    raw_text = extract_text_from_pdf(uploaded_file)  # Why: Extract text from uploaded PDF
    cleaned = clean_text(raw_text)  # Why: Clean text for analysis
    analyzer = SentimentIntensityAnalyzer()
    sent = analyzer.polarity_scores(cleaned)['compound']  # Why: Calculate sentiment
    st.subheader("New Report")
    st.write(f"Sentiment: {sent:.2f} (Positive >0.05, Negative <0)")  # Why: Display result

    # Plot comparison
    st.subheader("Sentiment Comparison")  # Why: Section for visualization
    fig, ax = plt.subplots(figsize=(8, 5))
    sentiments = list(df['Sentiment']) + [sent]  # Why: Combine benchmark and new sentiment
    ax.bar(range(len(sentiments)), sentiments)  # Why: Plot bar chart
    ax.set_xticks(range(len(sentiments)), list(df['Firm_Report']) + ['New'])  # Why: Label x-axis
    ax.set_title('Sentiment Comparison')
    ax.set_ylabel('VADER Sentiment Score')
    st.pyplot(fig)  # Why: Display in app

# Benchmark visualization
st.subheader("Benchmark Insights")  # Why: Section for benchmark plot
fig_bench, ax_bench = plt.subplots(figsize=(8, 5))
df.groupby('Firm_Report')['Sentiment'].mean().plot(kind='bar', ax=ax_bench)  # Why: Plot benchmark sentiments
ax_bench.set_title('Sentiment Across Firms')
ax_bench.set_ylabel('VADER Sentiment Score')
st.pyplot(fig_bench)  # Why: Display in app