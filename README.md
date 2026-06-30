# Fed Data Chatbot

> 🏆 **KCU 2026 — Best Project Award · 1st Place** *(University of Wisconsin-Madison)*

An AI chatbot for analyzing U.S. Federal Reserve economic data, built with FRED API and RAG.

[![Launch App](https://img.shields.io/badge/Launch%20App-kcu--fed.onrender.com-2563eb?style=for-the-badge&logo=render&logoColor=white)](https://kcu-fed.onrender.com/)

> Cold start: Initial load may take up to 30 seconds on the free Render tier.

---

[![Technical Report (EN)](https://img.shields.io/badge/Technical%20Report%20(EN)-View%20PDF-1B2A4A?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](https://github.com/yhwang55/fed-data-chatbot/blob/main/technical_report_EN.pdf)&nbsp;&nbsp;[![Project Report (KR)](https://img.shields.io/badge/Project%20Report%20(KR)-View%20PDF-6B7280?style=for-the-badge&logo=adobeacrobatreader&logoColor=white)](https://github.com/yhwang55/fed-data-chatbot/blob/main/kcu_fed_report.pdf)

---

## Overview

Ask questions in natural language and get instant analysis of Federal Reserve economic data.  
Real-time indicators are fetched via the FRED API, while Fed speeches, FOMC meeting minutes, and SEP documents are connected through a RAG pipeline — delivering numbers, context, and forward projections in a single response.

---

## Screenshots

![Main Screen](assets/main.png)

<p align="center">
  <img src="assets/language.png" width="49%"/>
  <img src="assets/indicators.png" width="49%"/>
</p>

<p align="center">
  <img src="assets/scatter.png" width="100%"/>
</p>

---

## Features

- **Interactive Charts** — Visualize 10+ indicators including Fed Funds Rate, CPI, Unemployment, and GDP (Plotly.js)
- **RAG-Powered Answers** — Responses grounded strictly in retrieved Fed documents and FRED API data; the model is explicitly prevented from using general LLM knowledge to avoid hallucination
- **SEP Forecast Overlay** — Official Fed economic projections plotted as a dotted overlay; automatically suppressed for historical date-range queries
- **Auto-Update Pipeline** — APScheduler crawls and indexes the latest Fed documents daily at 4 AM
- **Multilingual** — English / Korean / Spanish with full localization across UI, charts, and axis labels
- **Responsive UI** — Mobile-friendly layout

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Python 3.11, Flask, LangChain, ChromaDB |
| AI/LLM | OpenAI GPT-4o-mini, text-embedding-3-small |
| Data | FRED API, BeautifulSoup, pypdf |
| Frontend | HTML/CSS/JS, Plotly.js |
| Infra | Render, APScheduler |

---

## System Architecture

![Architecture](assets/architecture.svg)

---

## My Contributions

**Role: Project Lead Engineer**

- **SEP End-to-End Pipeline** — Designed and implemented the full pipeline: PDF crawling (`sep_crawler.py`) → data structuring (`sep_structurer.py`) → CSV storage → GPT prompt injection → chart overlay
- **Backend Architecture** — Built Flask API (`/api/chat`, `/api/chart`) and RAG pipeline with LangChain + ChromaDB
- **Dual-Endpoint API Design** — Separated text answers and chart data into independent endpoints to optimize frontend rendering performance
- **NL → FRED Ticker Mapping** — Implemented keyword-based mapping logic to minimize LLM dependency and reduce response latency
- **Intent-Based Chart Type Routing** — Automatically switches between line charts (time-series) and scatter plots (correlation analysis) based on query intent
- **ChromaDB Embedding Pipeline** — Chunking, vectorization, and retry logic for API rate limit (429) handling; source-level deduplication to prevent redundant chunk accumulation; MMR retrieval (k=8, fetch_k=20) for diverse, high-quality context over naive similarity search
- **Hallucination Prevention** — Prompt engineered to refuse out-of-scope questions and explicitly disallow fabrication when retrieved context is insufficient; SEP projection context injected dynamically per request rather than cached at server startup
- **Scheduled Auto-Update** — Designed APScheduler job to crawl and index the latest Fed speeches and meeting minutes daily
- **Frontend** — Responsive UI, Plotly.js chart integration, full i18n across UI text, chart axis labels, indicator names, and SEP overlay labels (English / Korean / Spanish)

> This is a team project. The above reflects my individual contributions.

---

## Project Structure

```
fed-data-chatbot/
├── app.py                    # Flask server + RAG pipeline
├── sep_crawler.py            # SEP PDF crawler
├── sep_structurer.py         # SEP data structuring → CSV
├── sep_values.csv            # Structured SEP projection data
├── index.html                # Frontend
├── technical_report_EN.md    # English technical report (source)
├── technical_report_EN.pdf   # English technical report (PDF)
├── kcu_fed_report.pdf        # Original project report (Korean)
├── requirements.txt
├── assets/                   # Screenshots and diagrams
└── .env                      # API keys (excluded from Git)
```
