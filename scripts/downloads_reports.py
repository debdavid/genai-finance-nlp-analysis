import requests
import os
from urllib.parse import unquote

# Define the URL (2025 AI/FS reports)
reports = {
    'McKinsey_State': 'https://www.mckinsey.com/~/media/mckinsey/business%20functions/quantumblack/our%20insights/the%20state%20of%20ai/2025/the-state-of-ai-how-organizations-are-rewiring-to-capture-value_final.pdf',
    'BCG_Reckoning': 'https://web-assets.bcg.com/3e/6f/9dfa63434eb7a00e1cf1cdcb3754/for-banks-the-ai-reckoning-is-here-may-2025.pdf',
    'KPMG_Insights': 'https://assets.kpmg.com/content/dam/kpmg/ae/pdf-2025/03/global-tech-report-financial-services-insights.pdf',
    'EY_FPA': 'https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/services/consulting/documents/ey-gl-how-ai-is-transforming-fpa-06-2025.pdf',
    'McKinsey_Bank': 'https://www.mckinsey.com/~/media/mckinsey/industries/financial%20services/our%20insights/building%20the%20ai%20bank%20of%20the%20future/building-the-ai-bank-of-the-future.pdf'
}

# Output directory
REPORT_DIR = 'data/reports'
os.makedirs(REPORT_DIR, exist_ok=True)

def download_file(url, filename):
    """Download PDF from URL and save to filename. Why? Automates data collection."""
    try:
        response = requests.get(url, stream=True, timeout=60)
        if response.status_code == 200:
            decoded_url = unquote(url)
            save_path = os.path.join(REPORT_DIR, filename)
            bytes_written = 0
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        bytes_written += len(chunk)
            print(f"Downloaded {filename} ({bytes_written} bytes)")
        else:
            print(f"Failed to download {filename}: Status {response.status_code}")
    except Exception as e:
        print(f"Error downloading {filename}: {e}")
    
def main():
    """Download all reports."""
    for name, url in reports.items():
        filename = f"{name}.pdf"
        print(f"Starting download: {filename} from {url}")
        download_file(url, filename)

if __name__ == "__main__":
    main()

                    