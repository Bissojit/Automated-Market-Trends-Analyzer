# Automated Market Trends Analyzer (No API, Python Only)

This project demonstrates an end‑to‑end workflow without any paid APIs:
1) **Scrape** public websites you configure.
2) **Summarize** article text locally (extractive summarization).
3) **Explore** results in a **Streamlit dashboard** with filters and export.

> ⚠️ Educational demo. Always check and respect each website’s robots.txt and terms of service. 
> Use only where allowed. Do not overload sites; crawl responsibly.

## Quickstart
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Features
- Configure **sources** and **keywords** in the sidebar.
- Crawl each source homepage and follow a limited set of internal links.
- Local **SQLite** (file: `data.db`) via the `db.py` helper.
- **Summarizer**: lightweight frequency-based extractive algorithm (no model download).
- **Dashboard**: search, filter by source and date, view details, open links.
- **Export**: download filtered table as CSV.

## Notes
- For JavaScript-heavy sites, consider adding Selenium/Playwright (not included in this minimal demo).
- Improve extraction per site by editing `extract_main_text` in `scraper.py`.
- Default demo sources are TechCrunch and The Verge — feel free to replace them.
