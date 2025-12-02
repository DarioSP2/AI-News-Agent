# AI Controversy Monitoring Agent

## 1. Introduction

This project is an automated AI agent designed to monitor a portfolio of companies for ESG (Environmental, Social, Governance), legal, and financial controversies. It runs weekly, scans global news in multiple languages, and uses advanced Large Language Models (LLMs) to analyze risks.

**Key Features:**
*   **Automated Surveillance:** Scans news for the last 7 days.
*   **Bilingual Search:** Searches in English and the company's local language.
*   **AI Analysis:** Uses Google Gemini or OpenAI GPT-4 to filter noise, classify incidents, and score severity.
*   **Reporting:** Generates a JSON data file, a CSV for spreadsheets, and an HTML email summary.

## 2. Getting Started

Follow these instructions to set up and run the bot on your machine.

### 2.1. Prerequisites

*   **Python 3.10 or higher**: [Download Here](https://www.python.org/downloads/)
*   **Git** (Optional, for cloning): [Download Here](https://git-scm.com/downloads)

### 2.2. Installation

#### Step 1: Download the Code
You can clone the repository using Git or download the ZIP file.

**Using Git:**
```bash
git clone <repository-url>
cd <repository-folder>
```

#### Step 2: Create a Virtual Environment (Recommended)
This isolates the project dependencies from your system.

*   **MacOS / Linux:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

*   **Windows (Command Prompt):**
    ```cmd
    python -m venv venv
    venv\Scripts\activate.bat
    ```

*   **Windows (PowerShell):**
    ```powershell
    python -m venv venv
    .\venv\Scripts\Activate.ps1
    ```

#### Step 3: Install Dependencies
Run the following command to install the required libraries:
```bash
pip install -r requirements.txt
```

### 2.3. Configuration

The bot is configured using a `.env` file. This file holds your API keys and settings.

1.  **Create the file:**
    *   Copy the example file provided in the repository.
    *   **MacOS / Linux:** `cp .env.example .env`
    *   **Windows:** Copy `.env.example`, rename the copy to `.env`.

2.  **Edit the `.env` file:**
    Open the `.env` file in a text editor (Notepad, TextEdit, VS Code) and fill in the following details.

    **A. Choose your AI Provider (`LLM_PROVIDER`)**
    You can choose between Google Gemini (cheaper/free tier available) or OpenAI GPT-4.

    *   **Option 1: Google Gemini (Recommended for simplicity)**
        *   Set `LLM_PROVIDER="google"`
        *   Get an API Key from [Google AI Studio](https://aistudio.google.com/).
        *   Paste it into `GOOGLE_API_KEY`.
        *   *Note: This mode uses Google's internal search, so you don't need a separate News API key.*

    *   **Option 2: OpenAI GPT-4**
        *   Set `LLM_PROVIDER="openai"`
        *   Get an API Key from [OpenAI Platform](https://platform.openai.com/).
        *   Paste it into `OPENAI_API_KEY`.
        *   **Required:** You also need a GNews API key for news fetching. Get it from [GNews.io](https://gnews.io/).
        *   Paste it into `NEWS_API_KEY`.

    **B. Email Settings (Optional)**
    To receive the weekly email report:
    *   Set `SENDGRID_API_KEY` (Get one from [SendGrid](https://sendgrid.com/)).
    *   Set `SENDGRID_FROM_EMAIL` (The email address validated in SendGrid).
    *   Set `RESPONSIBLE_EMAIL` (The recipient's email address).

### 2.4. Running the Bot

Once everything is set up, run the bot using the following command from the project root folder:

*   **MacOS / Linux:**
    ```bash
    python3 -m src.main
    ```

*   **Windows:**
    ```cmd
    python -m src.main
    ```

**What happens next?**
1.  The bot reads the portfolio from `data/enriched_portfolio.csv`.
2.  It searches for news for each company.
3.  It analyzes the news for controversies.
4.  It saves reports to the `output/` folder (`report.json`, `incidents.csv`).
5.  It saves the run history to `reports/` for trend comparison next week.
6.  It sends an email summary to the configured address.

## 3. Project Structure

For developers or curious users, here is how the code is organized:

*   `data/`: Contains the portfolio CSV file.
*   `output/`: Where the generated reports (JSON, CSV, HTML) are saved.
*   `reports/`: Stores historical state for week-over-week comparison.
*   `src/`: The source code.
    *   `main.py`: The brain of the operation.
    *   `llm_analyzer.py`: Handles the AI logic (Gemini/OpenAI).
    *   `news_api.py`: Fetches news (used for OpenAI mode).
    *   `email_sender.py`: Sends the emails.
*   `tests/`: Unit tests to ensure the code works correctly.

## 4. Troubleshooting

*   **ModuleNotFoundError**: Make sure you activated your virtual environment (Step 2) and installed requirements (Step 3). Also, ensure you run the command as `python -m src.main`, not just `python src/main.py`.
*   **API Errors**: Double-check your API keys in the `.env` file. Ensure there are no extra spaces or quotes around the keys unless necessary.
