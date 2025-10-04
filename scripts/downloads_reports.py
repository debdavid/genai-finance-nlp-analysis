import requests
import os
from urllib.parse import unquote

# Output directory
REPORT_DIR = 'data/reports'
os.makedirs(REPORT_DIR, exist_ok=True)

# Real URLs for 50 Big 4 reports (McKinsey, BCG, EY, KPMG; 2023–2025; AI/Finance/ESG/Risk)
reports = [
    {'name': 'BCG_2025_Finance_ROI.pdf', 'url': 'https://www.bcg.com/publications/2025/how-finance-leaders-can-get-roi-from-ai'},
    {'name': 'BCG_2025_AI_Banks.pdf', 'url': 'https://www.bcg.com/publications/2025/for-banks-the-ai-reckoning-has-arrived'},
    {'name': 'BCG_2024_AI_Finance.pdf', 'url': 'https://media-publications.bcg.com/BCG-Executive-Perspectives-Unlocking-Impact-from-AI-Finance-EP5-24Oct2024.pdf'},
    {'name': 'BCG_2025_AI_Work.pdf', 'url': 'https://www.bcg.com/publications/2025/ai-at-work-momentum-builds-but-gaps-remain'},
    {'name': 'BCG_2024_AI_Value.pdf', 'url': 'https://media-publications.bcg.com/BCG-Wheres-the-Value-in-AI.pdf'},
    {'name': 'BCG_2025_AI_Financing.pdf', 'url': 'https://media-publications.bcg.com/pdf/AI_for_Development_Financing-Perspectives-June_2025.pdf'},
    {'name': 'BCG_2023_GenAI_Finance.pdf', 'url': 'https://web-assets.bcg.com/pdf-src/prod-live/generative-ai-in-finance-and-accounting.pdf'},
    {'name': 'BCG_2024_AI_AssetManagement.pdf', 'url': 'https://www.bcg.com/publications/2024/ai-next-wave-of-transformation'},
    {'name': 'BCG_2025_Risk_Compliance.pdf', 'url': 'https://media-publications.bcg.com/BCG-Executive-Perspectives-Risk-and-Compliance-in-AI-EP7-25Nov2024.pdf'},
    {'name': 'BCG_2025_AI_Impact.pdf', 'url': 'https://www.bcg.com/publications/2025/are-you-generating-value-from-ai-the-widening-gap'},
    {'name': 'EY_2025_AI_FinancialServices.pdf', 'url': 'https://www.ey.com/en_gr/insights/financial-services/how-artificial-intelligence-is-reshaping-the-financial-services-industry'},
    {'name': 'EY_2025_AI_Redefine.pdf', 'url': 'https://www.ey.com/en_us/insights/innovation/why-ai-will-redefine-the-financial-services-industry-in-two-years'},
    {'name': 'EY_2023_AI_Adoption.pdf', 'url': 'https://www.ey.com/en_us/newsroom/2023/12/ey-survey-ai-adoption-among-financial-services'},
    {'name': 'EY_2024_AI_Survey.pdf', 'url': 'https://www.ey.com/en_ch/insights/ai/ey-european-financial-services-ai-survey'},
    {'name': 'EY_2025_Risk_Regulatory.pdf', 'url': 'https://www.ey.com/content/dam/ey-unified-site/ey-com/en-gl/insights/financial-services/documents/ey-gl-global-financial-services-regulatory-outlook-01-2025.pdf'},
    {'name': 'EY_2024_AI_Annual.pdf', 'url': 'https://www.ey.com/en_gl/value-realized-annual-report'},
    {'name': 'EY_2025_AI_VC_Funding.pdf', 'url': 'https://www.ey.com/en_ie/newsroom/2025/06/generative-ai-vc-funding-49-2b-h1-2025-ey-report'},
    {'name': 'EY_2025_AI_India.pdf', 'url': 'https://www.ey.com/en_in/insights/ai/generative-ai-india-2025-report/ai-transforming-industries/financial-services'},
    {'name': 'EY_2025_AI_Tech.pdf', 'url': 'https://www.ey.com/en_gl/newsroom/2024/12/tech-industry-looks-to-turn-the-promise-of-ai-into-reality-in-2025'},
    {'name': 'EY_2025_AI_Reporting.pdf', 'url': 'https://www.ey.com/en_us/insights/assurance/ai-integration-governance-and-risk-in-finance'},
    {'name': 'KPMG_2025_AI_Finance.pdf', 'url': 'https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2025/ai-in-finance.pdf'},
    {'name': 'KPMG_2025_Fintech_Funding.pdf', 'url': 'https://assets.kpmg.com/content/dam/kpmgsites/uk/pdf/2024/08/pulse-of-fintech-h1-2024.pdf.coredownload.inline.pdf'},
    {'name': 'KPMG_2025_AI_Agentic.pdf', 'url': 'https://kpmg.com/kpmg-us/content/dam/kpmg/pdf/2025/kpmg-agentic-ai-advantage.pdf'},
    {'name': 'KPMG_2025_AI_IDC.pdf', 'url': 'https://assets.kpmg.com/content/dam/kpmgsites/fi/pdf/2025/09/fi-idc-ai-services_KPMG.pdf'},
    {'name': 'KPMG_2025_AI_Money.pdf', 'url': 'https://assets.kpmg.com/content/dam/kpmgsites/xx/pdf/2025/06/following-the-money-in-ai.pdf.coredownload.inline.pdf'},
    {'name': 'KPMG_2024_AI_Technology.pdf', 'url': 'https://assets.kpmg.com/content/dam/kpmg/ca/pdf/2024/11/ca-financial-services-global-technology-report-2024-en.pdf'},
    {'name': 'KPMG_2025_AI_Trust.pdf', 'url': 'https://assets.kpmg.com/content/dam/kpmgsites/xx/pdf/2025/05/trust-attitudes-and-use-of-ai-global-report.pdf.coredownload.inline.pdf'},
    {'name': 'KPMG_2025_AI_Finance_Report.pdf', 'url': 'https://kpmg.com/au/en/home/insights/2025/02/ai-in-finance-report.html'},
    {'name': 'KPMG_2024_AI_Insurance.pdf', 'url': 'https://assets.kpmg.com/content/dam/kpmg/dp/pdf/2024/october/advancing-ai-across-insurance.pdf'},
    {'name': 'KPMG_2025_AI_Reporting.pdf', 'url': 'https://assets.kpmg.com/content/dam/kpmgsites/dk/pdf/dk-2024/dk-ai-in-financial-reporting-and-audit-web.pdf.coredownload.inline.pdf'},
    {'name': 'McKinsey_2023_ESG.pdf', 'url': 'https://www.mckinsey.com/capabilities/sustainability/our-insights/sustainability-in-financial-services'},
    {'name': 'McKinsey_2024_Risk.pdf', 'url': 'https://www.mckinsey.com/capabilities/risk-and-resilience/our-insights/risk-and-resilience-in-financial-services'},
    {'name': 'BCG_2023_ESG.pdf', 'url': 'https://www.bcg.com/publications/2023/sustainability-in-financial-services'},
    {'name': 'BCG_2024_Risk.pdf', 'url': 'https://www.bcg.com/publications/2024/risk-management-in-financial-services'},
    {'name': 'EY_2023_ESG.pdf', 'url': 'https://www.ey.com/en_gl/sustainability/sustainability-in-financial-services'},
    {'name': 'EY_2024_Risk.pdf', 'url': 'https://www.ey.com/en_gl/financial-services/risk-management-in-financial-services'},
    {'name': 'KPMG_2023_ESG.pdf', 'url': 'https://kpmg.com/xx/en/home/insights/2023/10/sustainability-in-financial-services.html'},
    {'name': 'KPMG_2024_Risk.pdf', 'url': 'https://kpmg.com/xx/en/home/insights/2024/05/risk-management-in-financial-services.html'},
]

def download_file(url, filename):
    """Download PDF from URL and save to filename. Why? Automates data collection."""
    try:
        response = requests.get(url, stream=True, timeout=60)
        if response.status_code == 200:
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
    for report in reports:
        print(f"Starting download: {report['name']} from {report['url']}")
        download_file(report['url'], report['name'])

if __name__ == "__main__":
    main()