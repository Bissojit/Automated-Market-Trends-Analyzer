import re
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0 Safari/537.36"
}

def fetch(url, timeout=20):
    try:
        r = requests.get(url, headers=HEADERS, timeout=timeout)
        if r.status_code == 200 and r.content:
            return r.text
    except requests.RequestException:
        return None
    return None

def find_links(html, base_url):
    soup = BeautifulSoup(html, "lxml")
    links = set()
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if href.startswith("#") or href.startswith("mailto:") or href.startswith("javascript:"):
            continue
        abs_url = urljoin(base_url, href)
        # Limit to same host
        if urlparse(abs_url).netloc == urlparse(base_url).netloc:
            links.add(abs_url)
    return list(links)

def extract_main_text(html):
    soup = BeautifulSoup(html, "lxml")
    article = soup.find("article")
    if article:
        nodes = article.find_all(["p", "li"])
    else:
        main = soup.find("main") or soup.find(id=re.compile("content|main", re.I)) or soup
        nodes = main.find_all(["p", "li"])
    text = " ".join(n.get_text(" ", strip=True) for n in nodes)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def guess_title(html):
    soup = BeautifulSoup(html, "lxml")
    if soup.title and soup.title.string:
        return soup.title.string.strip()
    h1 = soup.find("h1")
    return h1.get_text(strip=True) if h1 else ""

def looks_like_article(url, title, text, keywords):
    if len(text.split()) >= 200:
        return True
    low = (title + " " + text).lower()
    if keywords and any(k.lower() in low for k in keywords):
        return True
    if re.search(r"/(about|contact|privacy|terms)/?$", url):
        return False
    return False
