# Crawl4AI Tutorial

A hands-on tutorial project exploring the core features of [Crawl4AI](https://github.com/unclecode/crawl4ai).

## What's covered

| # | Feature | Description |
|---|---------|-------------|
| 1 | Raw Markdown Crawl | Fetch a page and get its raw markdown output |
| 2 | Fit Markdown Crawl | Filtered markdown using `PruningContentFilter` to remove noise |
| 3 | CSS Extraction | Scrape structured data (remote jobs) using CSS selectors |
| 4 | Deep Crawl | BestFirst crawl strategy with keyword scoring, URL filtering, and resumable state |
| 5 | LLM Extraction | Extract structured job listings using an LLM (DeepSeek) with a Pydantic schema |

## Setup

```bash
pip install crawl4ai python-dotenv
crawl4ai-setup
```

## API Key

LLM extraction (step 5) requires an API key from your LLM provider of choice. This project is LLM provider-agnostic — swap in any LLM provider supported by Crawl4AI (OpenAI, Gemini, DeepSeek, etc.).

Create a `.env` file and add your LLM provider API key. 

```
YOUR_LLM_PROVIDER_API_KEY=your_key_here
```

## Usage

Uncomment the function you want to run in `main()` inside `crawler.py` and run:

```bash
python crawler.py
```

## Requirements

- Python 3.9+
- Playwright (installed automatically with crawl4ai)
