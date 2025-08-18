import re
from collections import Counter

STOPWORDS = set('''a about above after again against all am an and any are as at
be because been before being below between both but by could did do does doing down
during each few for from further had has have having he her here hers herself him
himself his how i if in into is it its itself just me more most my myself no nor not
of off on once only or other our ours ourselves out over own same she should so some
such than that the their theirs them themselves then there these they this those through
to too under until up very was we were what when where which while who whom why will with
you your yours yourself yourselves'''.split())

def sent_tokenize(text):
    return [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]

def word_tokenize(text):
    return re.findall(r"[A-Za-z']+", text.lower())

def summarize(text, max_sentences=3):
    if not text or not text.strip():
        return ""
    sentences = sent_tokenize(text)
    if len(sentences) <= max_sentences:
        return " ".join(sentences)

    words = [w for w in word_tokenize(text) if w not in STOPWORDS and len(w) > 2]
    if not words:
        return " ".join(sentences[:max_sentences])

    freqs = Counter(words)
    scores = []
    for s in sentences:
        sw = [w for w in word_tokenize(s) if w not in STOPWORDS and len(w) > 2]
        score = sum(freqs.get(w, 0) for w in sw) / (len(sw) + 1e-6) if sw else 0
        scores.append((score, s))

    top = sorted(scores, key=lambda x: x[0], reverse=True)[:max_sentences]
    chosen = {s for _, s in top}
    ordered = [s for s in sentences if s in chosen]
    return " ".join(ordered)
