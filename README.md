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
python -m venv venv
source venv/bin/activate
pip install crawl4ai python-dotenv pydantic
```

Create a `.env` file:

```
DEEPSEEK_API_KEY=your_key_here
```

## Usage

Uncomment the function you want to run in `main()` inside `crawler.py`, then:

```bash
python crawler.py
```

## Requirements

- Python 3.9+
- Playwright (installed automatically with crawl4ai)
