import asyncio
import json
import os

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import List, Optional

from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode, DefaultMarkdownGenerator, LLMConfig
from crawl4ai.content_filter_strategy import PruningContentFilter
from crawl4ai.extraction_strategy import JsonCssExtractionStrategy, LLMExtractionStrategy
from crawl4ai.deep_crawling import BestFirstCrawlingStrategy
from crawl4ai.deep_crawling.scorers import KeywordRelevanceScorer
from crawl4ai.deep_crawling.filters import FilterChain, URLPatternFilter

load_dotenv()

# 1. RAW MARKDOWN CRAWL
async def run_raw_markdown_crawl(crawler):
    crawler_config = CrawlerRunConfig()
    result = await crawler.arun(
        url="https://techcrunch.com",
        config=crawler_config
    )
    # Print the raw markdown output (truncated at 1000 chars so it doesn't flood terminal)
    print(f"Raw Output:\n{result.markdown.raw_markdown}")


# 2. FIT MARKDOWN CRAWL (FILTERED)
async def run_fit_markdown_crawl(crawler):
    config = CrawlerRunConfig(
        markdown_generator=DefaultMarkdownGenerator(
            content_filter=PruningContentFilter(threshold=0.5) # 0–1 scale. higher = more aggressive filtering
        )
    )
    result = await crawler.arun(
        url="https://techcrunch.com",
        config=config 
    )
    # Print the fit markdown output
    print(f"Fit Output:\n{result.markdown.fit_markdown}") # shows only the first 500 chars for preview


# 3. CSS EXTRACTION (REMOTEOK JOBS)
async def run_css_extraction(crawler):
    schema = {
        "name": "Remote Jobs",
        "baseSelector": "tr.job",
        "fields": [
            {"name": "title",    "selector": "td.company_and_position h2",            "type": "text"},
            {"name": "company",  "selector": "td.company_and_position h3",            "type": "text"},
            {"name": "location", "selector": "td.company_and_position div.location",  "type": "text"},
            {"name": "tags",     "selector": "td.tags div.tag h3",                    "type": "list", "fields": [{"name": "tag", "type": "text"}]},
            {"name": "url",      "selector": "td.company_and_position a.preventLink", "type": "attribute", "attribute": "href"},
        ]
    }
    config = CrawlerRunConfig(
        extraction_strategy=JsonCssExtractionStrategy(schema),
        wait_for="css:tr.job",  # page is JS-rendered; wait for job rows to appear
        page_timeout=30000, # extend timeout to 30 seconds (for slow loading pages)
        delay_before_return_html=3.0,  # extra wait for JS to finish rendering
    )
    result = await crawler.arun(url="https://remoteok.com", config=config)
    jobs = json.loads(result.extracted_content)
    print(json.dumps(jobs[:3], indent=2))


# 4. DEEP CRAWL (BESTFIRST — REMOTEOK)
STATE_FILE = "crawl_state.json"

# creates json file for the output
async def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

async def run_deep_crawl(crawler):
    # Load saved state on disk if a previous run was interrupted
    resume = None
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            resume = json.load(f)

    scorer = KeywordRelevanceScorer(
        keywords=["python", "backend", "engineer", "remote"],
        weight=0.7  # Scores against URL text and link anchor text — not page content
    )

    strategy = BestFirstCrawlingStrategy(
        max_depth=2,
        max_pages=50,
        include_external=False,
        url_scorer=scorer,
        filter_chain=FilterChain([
            URLPatternFilter(patterns=["remoteok.com/remote-*-jobs", "remoteok.com/l/*"])
        ]),
        score_threshold=0.3,
        on_state_change=save_state,  # serialize progress to disk after every URL
        resume_state=resume          # pass saved state here to resume an interrupted run
    )

    async for result in await crawler.arun(
        url="https://remoteok.com",
        config=CrawlerRunConfig(
            deep_crawl_strategy=strategy,
            cache_mode=CacheMode.BYPASS,
            stream=True
        )
    ):
        if result.success:
            print(f"[depth {result.metadata.get('depth')}] {result.url}")


# 5. LLM EXTRACTION (REMOTEOK JOBS)

class JobListing(BaseModel):
    title: str = Field(..., description="Job title")
    company: str = Field(..., description="Company name")
    location: str = Field(..., description="Job location or 'Anywhere' if remote")
    salary: Optional[str] = Field(None, description="Salary range if listed")
    tags: List[str] = Field(default_factory=list, description="Tech stack and skills")

async def run_llm_extraction(crawler):
    extraction_strategy = LLMExtractionStrategy(
        llm_config=LLMConfig(
            provider="deepseek/deepseek-chat",
            api_token=os.getenv("DEEPSEEK_API_KEY")
        ),
        schema=JobListing.model_json_schema(),
        extraction_type="schema",
        instruction="Extract all job listings from the page. For each listing extract the job title, company name, location, salary range if present, and tech stack tags."
    )

    config = CrawlerRunConfig(
        extraction_strategy=extraction_strategy,
        wait_for="css:tr.job",                                                                               
        delay_before_return_html=3.0,    
    )

    result = await crawler.arun(
        url="https://remoteok.com",
        config=config
    )
    jobs = json.loads(result.extracted_content)
    print(json.dumps(jobs[:2], indent=2))



# RUN FUNCTION: UNCOMMENT ANY OF THE CORRESPONDING FUNCTION LINES BELOW
async def main():
    browser_config = BrowserConfig(headless=True)
    async with AsyncWebCrawler(config=browser_config) as crawler:
        
        # await run_raw_markdown_crawl(crawler)
        # await run_fit_markdown_crawl(crawler)
        # await run_css_extraction(crawler)
        # await run_llm_extraction(crawler)
        await run_deep_crawl(crawler)

if __name__ == "__main__":
    asyncio.run(main())
