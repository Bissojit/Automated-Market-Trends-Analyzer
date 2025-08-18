import time
from datetime import datetime
import pandas as pd
import streamlit as st

from db import init_db, upsert_article, query_articles
from scraper import fetch, find_links, extract_main_text, guess_title, looks_like_article
from summarizer import summarize

st.set_page_config(page_title="Automated Market Trends Analyzer", layout="wide")

# Sidebar configuration
st.sidebar.header("Configuration")
default_sources = "https://techcrunch.com, https://www.theverge.com"
sources_input = st.sidebar.text_area("Sources (comma-separated URLs)", value=default_sources, height=90)
keywords_input = st.sidebar.text_input("Keywords (comma-separated, optional)", value="AI, cloud, privacy, cybersecurity")
max_pages = st.sidebar.slider("Max pages per source (crawl depth 1)", 3, 30, 8, 1)
max_sentences = st.sidebar.slider("Summary length (sentences)", 2, 7, 3, 1)

st.sidebar.markdown("---")
run_scrape = st.sidebar.button("Run Scrape Now")
st.sidebar.info("Tip: Start with fewer sources and a small page limit.")

st.title("Automated Market Trends Analyzer")

# Top filters
col1, col2, col3, col4 = st.columns([2,2,2,2])
with col1:
    search_text = st.text_input("Search text (title/content/summary)")
with col2:
    keyword_filter = st.text_input("Keyword filter (contains)")
with col3:
    start_date = st.date_input("Start date", value=None)
with col4:
    end_date = st.date_input("End date", value=None)

# Initialize DB
init_db()

def do_scrape(sources, keywords):
    scraped = 0
    for src in sources:
        src = src.strip()
        if not src:
            continue
        st.write(f"**Crawling:** {src}")
        html = fetch(src)
        if not html:
            st.warning(f"Failed to fetch source: {src}")
            continue
        links = find_links(html, src)[:max_pages]
        for url in links:
            page = fetch(url)
            if not page:
                continue
            title = guess_title(page)[:300]
            text = extract_main_text(page)
            if not text:
                continue
            if not looks_like_article(url, title, text, keywords):
                continue
            summ = summarize(text, max_sentences=max_sentences)[:5000]
            now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
            kws = ", ".join(keywords) if keywords else ""
            upsert_article(url=url, source=src, title=title, content=text[:200000], summary=summ,
                           keywords=kws, published_at="", scraped_at=now)
            scraped += 1
            st.caption(f"Saved: {title}")
            time.sleep(0.4)  # be polite
    return scraped

if run_scrape:
    sources = [s.strip() for s in sources_input.split(",") if s.strip()]
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    with st.spinner("Scraping..."):
        count = do_scrape(sources, keywords)
    st.success(f"Scraped {count} pages. Scroll down to see results.")

# Build filters
filters = {}
if search_text:
    filters["search_text"] = search_text
if keyword_filter:
    filters["keyword"] = keyword_filter
if start_date:
    filters["start_date"] = start_date.isoformat()
if end_date:
    filters["end_date"] = end_date.isoformat()

rows = query_articles(filters)
df = pd.DataFrame(rows)

st.subheader("Latest Articles")
if df.empty:
    st.info("No articles yet. Add sources and click **Run Scrape Now** in the sidebar.")
else:
    # Display table with selected columns
    view_cols = ["source", "title", "summary", "url", "scraped_at"]
    st.dataframe(df[view_cols], use_container_width=True, hide_index=True)

    # Export
    csv = df[view_cols].to_csv(index=False).encode("utf-8")
    st.download_button("Download CSV (filtered view)", data=csv, file_name="articles_filtered.csv", mime="text/csv")

    # Details panel
    st.markdown("---")
    st.subheader("Details")
    selected_url = st.selectbox("Select an article URL to view full content", options=[""] + df["url"].tolist())
    if selected_url:
        row = df[df["url"] == selected_url].iloc[0]
        st.markdown(f"**Title:** {row['title']}")
        st.markdown(f"**Source:** {row['source']}")
        st.markdown(f"**Scraped at:** {row['scraped_at']}")
        if row.get("published_at"):
            st.markdown(f"**Published:** {row['published_at']}")
        st.markdown(f"**URL:** [{row['url']}]({row['url']})")
        with st.expander("Summary"):
            st.write(row["summary"] or "(no summary)")
        with st.expander("Full Content"):
            st.write(row["content"] or "(no content)")