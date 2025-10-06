import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
import pdfplumber
import os
import nltk
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from nltk.probability import FreqDist
from heapq import nlargest

nltk.download('punkt')
nltk.download('stopwords')

# Directories
PROCESSED_DIR = 'data/processed'
ANALYSIS_PATH = os.path.join(PROCESSED_DIR, 'analysis_results.csv')

# Text cleaning function
def clean_text(text):
    # Remove boilerplate (e.g., copyright, document classification)
    boilerplate_patterns = [
        r'22002244 KKPPMMGG LLLLPP.*?\. AAllll rriigghhttss rreesseerrvveedd\.',
        r'Document Classification KPMG Public',
        r'The KPMG name and logo are trademarks.*?\.',
        r'\b[A-Z]{2,}\b \b[A-Z]{2,}\b',  # Remove repeated uppercase words (e.g., KKPPMMGG LLLLPP)
        r'\b\d{6,}\b',  # Remove large numbers (e.g., 22002244)
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    # Fix repeated characters (e.g., KKPPMMGG → KPMG)
    text = re.sub(r'([A-Z])\1+', r'\1', text)
    # Remove extra spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Load data with error handling
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(ANALYSIS_PATH)
        required_columns = ["report", "firm", "year", "industry", "vader_sentiment", "textblob_sentiment", "text", "top_keywords", "topics"]
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            st.error(f"Missing columns in analysis_results.csv: {missing_cols}")
            return pd.DataFrame()
        # Handle NaN values
        df = df.fillna({"firm": "Unknown", "year": 0, "industry": "Unknown", "topics": "", "top_keywords": "", "text": ""})
        return df
    except FileNotFoundError:
        st.error("analysis_results.csv not found. Please run analyze_texts.py.")
        return pd.DataFrame()

df = load_data()
if df.empty:
    st.warning("No data available. Please check data/processed/analysis_results.csv.")
    st.stop()

# Sidebar Filters
st.sidebar.header("Filters")
firm_options = sorted(df["firm"].unique())
year_options = sorted(df["year"].astype(str).unique())
industry_options = sorted(df["industry"].unique())
firm = st.sidebar.multiselect("Firm", options=firm_options, default=firm_options)
year = st.sidebar.multiselect("Year", options=year_options, default=year_options)
industry = st.sidebar.multiselect("Industry", options=industry_options, default=industry_options)

# Filter data
filtered_df = df[df["firm"].isin(firm) & df["year"].astype(str).isin(year) & df["industry"].isin(industry)]
if filtered_df.empty:
    st.warning("No data matches the selected filters. Please adjust filters.")
    st.stop()

# Report Selection for Summary
st.subheader("Select Report for Summary")
report_options = sorted(filtered_df["report"].unique())
selected_report = st.selectbox("Choose a report", report_options)
if selected_report:
    report_df = filtered_df[filtered_df["report"] == selected_report]
    full_text = " ".join(report_df["text"])
    # Clean text
    full_text = clean_text(full_text)
    sentences = sent_tokenize(full_text)
    if sentences:
        # Use top_keywords for scoring
        keywords = set("|".join(report_df["top_keywords"]).split("|"))
        keywords = {kw.lower() for kw in keywords if kw.strip() and kw.lower() not in stopwords.words('english')}
        # Score sentences based on keyword presence
        summary_sentences = nlargest(2, sentences, key=lambda s: sum(1 for w in word_tokenize(s.lower()) if w in keywords))
        summary = "\n- ".join(summary_sentences)
        st.write("**Summary of selected report:**")
        st.write(f"- {summary}" if summary else "- No meaningful sentences found.")
    else:
        st.write("No text available for summary.")

# Sentiment Plot (by report, averaged across chunks)
st.subheader("Average Sentiment by Report")
sentiment_df = filtered_df.groupby("report").agg({
    "vader_sentiment": "mean",
    "firm": "first"
}).reset_index()
if not sentiment_df.empty:
    fig, ax = plt.subplots(figsize=(10, max(4, len(sentiment_df)*0.3)))
    sns.barplot(data=sentiment_df, x="vader_sentiment", y="report", hue="firm", ax=ax, palette="tab10")
    ax.set_xlabel("VADER Sentiment Score")
    ax.set_ylabel("Report")
    ax.legend(title="Firm", loc="best")
    st.pyplot(fig)
else:
    st.warning("No sentiment data available for the selected filters.")

# Topic Distribution Bar Chart
st.subheader("Topic Distribution")
topics = filtered_df["topics"].str.split("|").explode().value_counts()
if not topics.empty:
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=topics.values, y=topics.index, ax=ax, palette="viridis")
    ax.set_xlabel("Chunk Count")
    ax.set_ylabel("Topics")
    ax.set_title("Distribution of Topics Across Filtered Reports")
    st.pyplot(fig)
else:
    st.warning("No topics available for the selected filters.")

# Keyword Word Cloud (unique per report)
st.subheader("Top Keywords Word Cloud")
generic_terms = {'report', 'use', 'ai', 'university', 'melbourne', 'kpmg', 'rights', 'international', 'entities', 'copyright'}
keywords_per_report = filtered_df.groupby('report')['top_keywords'].apply(lambda x: set('|'.join(x).split('|')) - generic_terms)
keywords_freq = {}
for report, keywords in keywords_per_report.items():
    for kw in keywords:
        if kw.strip():
            keywords_freq[kw] = keywords_freq.get(kw, 0) + 1
if keywords_freq:
    wordcloud = WordCloud(width=800, height=400, background_color="white").generate_from_frequencies(keywords_freq)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud, interpolation="bilinear")
    ax.axis("off")
    st.pyplot(fig)
else:
    st.warning("No keywords available for the selected filters.")

# Top 10 Keywords Table
st.subheader("Top 10 Keywords")
if keywords_freq:
    keywords_df = pd.DataFrame(list(keywords_freq.items()), columns=['Keyword', 'Frequency']).sort_values(by='Frequency', ascending=False).head(10)
    st.table(keywords_df)
else:
    st.warning("No keywords available for the selected filters.")

# PDF Upload
st.subheader("Upload New PDF")
uploaded_file = st.file_uploader("Choose a PDF", type="pdf")
if uploaded_file:
    with pdfplumber.open(uploaded_file) as pdf:
        text = "".join(page.extract_text() or "" for page in pdf.pages)
    st.write("**Extracted text (preview):**")
    st.write(text[:500] + "...")