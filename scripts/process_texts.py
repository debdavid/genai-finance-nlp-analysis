import os
import re
import pandas as pd
import pickle
import pdfplumber
from nltk.tokenize import sent_tokenize
import nltk
import magic  # For file type checking

# Download NLTK data
nltk.download('punkt')
nltk.download('punkt_tab')

# Directories
REPORT_DIR = 'data/reports'
PROCESSED_DIR = 'data/processed'
CACHE_DIR = 'cache'
os.makedirs(PROCESSED_DIR, exist_ok=True)
os.makedirs(CACHE_DIR, exist_ok=True)

def is_valid_pdf(file_path):
    """Check if file is a valid PDF. Why? Skip non-PDFs or corrupted files."""
    try:
        mime = magic.Magic(mime=True)
        file_type = mime.from_file(file_path)
        return file_type == 'application/pdf'
    except Exception as e:
        print(f"Error checking file type for {file_path}: {e}")
        return False

def clean_text(text):
    """Clean text by removing boilerplate and special characters. Why? Improve NLP quality."""
    text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
    text = re.sub(r'[^\w\s.,-]', '', text)  # Remove special chars
    return text.strip()

def chunk_text(text, max_words=1000):
    """Chunk text into ~1000-word segments. Why? Manageable for NLP."""
    try:
        sentences = sent_tokenize(text)
        chunks, current_chunk, word_count = [], [], 0
        for sentence in sentences:
            words = len(sentence.split())
            if word_count + words > max_words:
                chunks.append(' '.join(current_chunk))
                current_chunk, word_count = [sentence], words
            else:
                current_chunk.append(sentence)
                word_count += words
        if current_chunk:
            chunks.append(' '.join(current_chunk))
        return chunks
    except Exception as e:
        print(f"Error chunking text: {e}")
        return []

def process_pdf(pdf_path):
    """Extract and chunk text from PDF. Why? Convert PDFs to structured data."""
    if not is_valid_pdf(pdf_path):
        print(f"Skipping {pdf_path}: Not a valid PDF")
        return []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            text = ''
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text
            text = clean_text(text)
            return chunk_text(text)
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return []

def main():
    """Process all PDFs and save metadata/cache. Why? Automate data prep."""
    metadata = []
    processed_files = set()  # Track processed files to avoid duplicates
    for filename in os.listdir(REPORT_DIR):
        if filename.endswith('.pdf') and filename not in processed_files:
            pdf_path = os.path.join(REPORT_DIR, filename)
            parts = filename.replace('.pdf', '').split('_')
            if len(parts) < 3:
                print(f"Skipping {filename}: Invalid format (expected Firm_Year_Industry.pdf)")
                continue
            firm, year = parts[0], parts[1]
            industry = '_'.join(parts[2:])  # Join remaining parts for industry
            chunks = process_pdf(pdf_path)
            if chunks:  # Only add if chunks exist
                for i, chunk in enumerate(chunks):
                    metadata.append({
                        'report': filename,
                        'firm': firm,
                        'year': year,
                        'industry': industry,
                        'chunk_id': i,
                        'text': chunk
                    })
                    # Cache chunk
                    cache_path = os.path.join(CACHE_DIR, f"{filename}_{i}.pkl")
                    with open(cache_path, 'wb') as f:
                        pickle.dump(chunk, f)
                print(f"Processed {filename}: {len(chunks)} chunks")
                processed_files.add(filename)  # Mark as processed
    # Save metadata
    if metadata:
        df = pd.DataFrame(metadata)
        df.to_csv(os.path.join(PROCESSED_DIR, 'metadata.csv'), index=False)
        print(f"Saved metadata to {PROCESSED_DIR}/metadata.csv")
    else:
        print("No valid PDFs processed.")

if __name__ == "__main__":
    main()