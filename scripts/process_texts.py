import pdfplumber
import pandas as pd
import os
import re

# Directories
RAW_DIR = 'data/reports'
PROCESSED_DIR = 'data/processed'
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Text cleaning function
def clean_text(text):
    # Remove boilerplate
    boilerplate_patterns = [
        r'22002244 KKPPMMGG LLLLPP.*?\. AAllll rriigghhttss rreesseerrvveedd\.',
        r'Document Classification KPMG Public',
        r'The KPMG name and logo are trademarks.*?\.',
        r'\b[A-Z]{2,}\b \b[A-Z]{2,}\b',
        r'\b\d{6,}\b',
    ]
    for pattern in boilerplate_patterns:
        text = re.sub(pattern, '', text, flags=re.IGNORECASE | re.DOTALL)
    # Fix repeated characters
    text = re.sub(r'([A-Z])\1+', r'\1', text)
    # Remove extra spaces and newlines
    text = re.sub(r'\s+', ' ', text).strip()
    return text

# Process PDFs
data = []
for pdf_file in os.listdir(RAW_DIR):
    if pdf_file.endswith('.pdf'):
        pdf_path = os.path.join(RAW_DIR, pdf_file)
        try:
            with pdfplumber.open(pdf_path) as pdf:
                text = "".join(page.extract_text() or "" for page in pdf.pages)
                text = clean_text(text)
                # Chunk text (~1000 words)
                words = text.split()
                chunk_size = 1000
                for i in range(0, len(words), chunk_size):
                    chunk = " ".join(words[i:i+chunk_size])
                    data.append({
                        'report': pdf_file,
                        'firm': pdf_file.split('_')[0],
                        'year': pdf_file.split('_')[1][:4],
                        'industry': '_'.join(pdf_file.split('_')[2:]).replace('.pdf', ''),
                        'chunk_id': i // chunk_size,
                        'text': chunk
                    })
        except Exception as e:
            print(f"Error processing {pdf_file}: {e}")

# Save to CSV
df = pd.DataFrame(data)
df.to_csv(os.path.join(PROCESSED_DIR, 'metadata.csv'), index=False)
print(f"Saved {len(df)} chunks to metadata.csv")