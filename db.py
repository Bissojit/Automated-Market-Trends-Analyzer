import sqlite3
from contextlib import closing

DB_PATH = "data.db"

def init_db():
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT UNIQUE,
                source TEXT,
                title TEXT,
                content TEXT,
                summary TEXT,
                keywords TEXT,
                published_at TEXT,
                scraped_at TEXT
            )
            """
        )
        conn.commit()

def upsert_article(url, source, title, content, summary, keywords, published_at, scraped_at):
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute(
            """
            INSERT INTO articles (url, source, title, content, summary, keywords, published_at, scraped_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(url) DO UPDATE SET
                source=excluded.source,
                title=excluded.title,
                content=excluded.content,
                summary=excluded.summary,
                keywords=excluded.keywords,
                published_at=excluded.published_at,
                scraped_at=excluded.scraped_at
            """,
            (url, source, title, content, summary, keywords, published_at, scraped_at)
        )
        conn.commit()

def query_articles(filters=None):
    filters = filters or {}
    query = "SELECT id, url, source, title, content, summary, keywords, published_at, scraped_at FROM articles WHERE 1=1"
    params = []
    if kw := filters.get("keyword"):
        query += " AND (lower(content) LIKE ? OR lower(title) LIKE ? OR lower(summary) LIKE ?)"
        s = f"%{kw.lower()}%"
        params += [s, s, s]
    if srcs := filters.get("sources"):
        placeholders = ",".join(["?"] * len(srcs))
        query += f" AND source IN ({placeholders})"
        params += list(srcs)
    if start := filters.get("start_date"):
        query += " AND date(scraped_at) >= date(?)"
        params.append(start)
    if end := filters.get("end_date"):
        query += " AND date(scraped_at) <= date(?)"
        params.append(end)
    if search := filters.get("search_text"):
        s = f"%{search.lower()}%"
        query += " AND (lower(content) LIKE ? OR lower(title) LIKE ? OR lower(summary) LIKE ?)"
        params += [s, s, s]
    query += " ORDER BY datetime(scraped_at) DESC"
    with closing(sqlite3.connect(DB_PATH)) as conn:
        c = conn.cursor()
        c.execute(query, params)
        rows = c.fetchall()
    cols = ["id", "url", "source", "title", "content", "summary", "keywords", "published_at", "scraped_at"]
    return [dict(zip(cols, r)) for r in rows]
