# Weekly Controversy Monitoring Agent

## 1. Project Overview

### 1.1. Goal

The objective of this project is to provide an automated, serverless pipeline that runs weekly to monitor a portfolio of companies for new controversies. The system is designed to scan multi-lingual news sources, leverage a Large Language Model (LLM) for sophisticated analysis, and produce a clear, actionable weekly report for stakeholders. The final outputs include an email summary, a machine-readable JSON report, and a CSV file for archival and Business Intelligence (BI) purposes.

### 1.2. Core Functionality

- **Ingest**: Reads a static CSV file defining the company portfolio.
- **Schedule**: Designed to be triggered on a weekly schedule (e.g., every Friday at 09:00).
- **Search**: For each company, it searches for relevant news articles from the last 7 days using a dedicated News/Search API, supporting both English and the company's local language.
- **Analyze**: Utilizes an LLM to perform advanced analysis on the search results, including:
    - Deduplication of stories about the same incident.
    - Classification of incidents into predefined categories.
    - Severity scoring of each incident on a 1-5 scale.
    - Summarization of incidents in English.
    - Extraction of source evidence (quotes, URLs).
- **Compare**: Loads the previous week's results to calculate week-over-week (WoW) deltas for key risk metrics.
- **Report**: Generates and delivers three distinct outputs: an HTML email, a `report.json` file, and an `incidents.csv` file.

## 2. System Architecture

This system is designed for a serverless architecture to ensure cost-efficiency and low management overhead. The primary technology stack is Python 3.10+, intended for deployment on a cloud platform like Google Cloud Platform (GCP) or Amazon Web Services (AWS).

### 2.1. Components

- **Scheduler (The "Clock")**: A cloud-native scheduler (e.g., Google Cloud Scheduler, Amazon EventBridge) triggers the main orchestration function on a fixed weekly schedule.
- **Orchestrator (The "Worker")**: A serverless function (e.g., Google Cloud Function, AWS Lambda) that contains the core Python script. This function orchestrates the entire data flow from data ingestion to final delivery.
- **Memory (The "Database")**: A cloud storage bucket (e.g., Google Cloud Storage, Amazon S3) is used to persist the state between runs. It stores the `report-{WEEK_KEY}.json` file each week, which is then loaded by the next week's run to perform the WoW comparison.
- **Tools (External APIs)**:
    - **News/Search API**: A required external API for fetching news articles (e.g., NewsAPI.org, Meltwater, Google Custom Search API).
    - **LLM API**: A required API for the analysis task (e.g., Google Gemini, OpenAI GPT).
    - **Email API**: A required API for reliable email delivery (e.g., SendGrid, Mailgun, Amazon SES).

## 3. How to Set Up and Run

### 3.1. Prerequisites

- Python 3.10+
- `pip` for package management

### 3.2. Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd <repository-name>
    ```

2.  **Install dependencies:**
    It is highly recommended to use a virtual environment.
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

### 3.3. Configuration

The application requires several environment variables to be set. You can create a `.env` file in the project root and the application will load it, or set them directly in your shell.

**User-Provided Variables:**

- `PORTFOLIO_NAME`: The name of the portfolio being monitored (e.g., "EM Consumer 30").
- `RESPONSIBLE_NAME`: The name of the person receiving the report (e.g., "Dario").
- `RESPONSIBLE_EMAIL`: The email address to send the report to.

**Programmer-Provisioned Keys:**

- `NEWS_API_KEY`: Your API key for the chosen News/Search API.
- `LLM_API_KEY`: Your API key for the chosen LLM API.
- `EMAIL_API_KEY`: Your API key for the chosen Email API.
- `GCS_BUCKET_NAME`: The name of the GCS/S3 bucket for state storage.

### 3.4. Local Execution

To run the pipeline locally, execute the main script as a module from the project root:

```bash
python3 -m src.main
```

This will run the entire pipeline using the configuration from your environment variables or `.env` file. The output files will be generated in the `output/` directory, and the state file will be saved in the `reports/` directory.

**Note**: The current implementation uses mock services for the News and LLM APIs, so it can be run without actual API keys. The mock data is hardcoded in `src/news_api.py` and `src/llm_analyzer.py`.

### 3.5. Running Tests

To run the suite of unit tests, use the following command from the project root:

```bash
python3 -m unittest discover tests
```

## 4. Project Structure

```
.
├── data/
│   └── enriched_portfolio.csv  # Input CSV with company data
├── output/                     # Generated output files (gitignored)
├── reports/                    # Weekly state JSON files (gitignored)
├── src/
│   ├── __init__.py
│   ├── email_sender.py         # Module for sending emails
│   ├── llm_analyzer.py         # Module for LLM analysis
│   ├── main.py                 # Main orchestration script
│   ├── news_api.py             # Module for fetching news
│   ├── output_generator.py     # Module for creating output files
│   └── state_manager.py        # Module for loading/saving state
├── tests/
│   ├── __init__.py
│   ├── test_output_generator.py
│   └── test_state_manager.py
├── .gitignore
├── README.md
└── requirements.txt
```

## 5. Input and Output Schemas

### 5.1. Input CSV (`data/enriched_portfolio.csv`)

The input CSV must contain the following columns: `name`, `ticker`, `isin`, `hq_country`, `primary_language`, `local_language`, `aliases`.

### 5.2. Output JSON (`report.json`)

The main JSON output follows a nested structure containing a portfolio summary and a list of companies with their respective incidents and metrics. For the full schema, please refer to the technical specification document.

### 5.3. Output CSV (`incidents.csv`)

A flattened CSV containing all incidents found during the week. The columns are: `incident_id`, `company_name`, `ticker`, `category`, `severity`, `confidence`, `summary_en`, `key_quote`, `first_seen_date`, `language`, `source_url`, `source_outlet`.
