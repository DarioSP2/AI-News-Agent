# Setup Guide: AI Controversy Monitoring Agent

This guide explains how to configure and run the AI Controversy Monitoring Agent, specifically how to switch between LLM providers (Google Gemini vs. OpenAI GPT-4).

## 1. Prerequisites

Ensure you have the dependencies installed:
```bash
pip install -r requirements.txt
```

## 2. Configuration (.env)

The behavior of the agent is controlled by the `.env` file. You can start by copying the example:

```bash
cp .env.example .env
```

### Toggle LLM Provider

To switch between providers, modify the `LLM_PROVIDER` variable in `.env`.

**Option A: Google Gemini (Grounding)**
Uses Google Gemini with built-in Search Grounding. It fetches news directly.

```ini
LLM_PROVIDER="google"
GOOGLE_API_KEY="AIzaSy..."  # Your Google Gemini API Key
```

**Option B: OpenAI GPT-4 + GNews**
Uses GNews.io to fetch articles and GPT-4 to analyze them.

```ini
LLM_PROVIDER="openai"
OPENAI_API_KEY="sk-..."     # Your OpenAI API Key
NEWS_API_KEY="e1188..."     # Your GNews.io API Key
```

### Email Configuration
To enable email reporting, configure the SendGrid settings:

```ini
SENDGRID_FROM_EMAIL="sender@example.com"
RESPONSIBLE_EMAIL="receiver1@example.com, receiver2@example.com" # Comma separated
SENDGRID_API_KEY="SG..."
```

## 3. Running the Agent

Run the main module from the project root:

```bash
python3 -m src.main
```

The agent will:
1. Load the portfolio.
2. Search for controversies (method depends on `LLM_PROVIDER`).
3. Generate reports in `output/` (JSON, CSV, HTML).
4. Save state for trend analysis in `reports/`.
5. Send an email summary if configured.
