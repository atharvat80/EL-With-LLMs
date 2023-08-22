import re
import json
from urllib.parse import unquote
from duckduckgo_search import DDGS
from urlextract import URLExtract

extractor = URLExtract()

def get_mention_idx(sentences):
    for idx, s in enumerate(sentences):
        if "<a>" in s:
            return idx

def get_neighboring_sentences(text, n = 1):
    sentences = re.split(r'(?<=[.!?])\s+', text)  # Split the text into sentences
    idx = get_mention_idx(sentences)
    start, end = max(idx - n, 0), idx + n + 1
    return " ".join(sentences[start:end])

def get_tagged_context(text, span):
    s, e = span
    text = text[:s] + "<a>" + text[s:e] + "</a>" + text[e:]
    return text

def get_query(string):
    start_tag = ">"
    end_tag = "</"
    start_index = string.find(start_tag)
    end_index = string.find(end_tag)

    if start_index == -1 or end_index == -1:
        return None

    text_start = start_index + len(start_tag)
    text_end = end_index

    if text_start >= text_end:
        return None

    return string[text_start:text_end].strip()


def get_wikipedia_link(string):
    urls = extractor.find_urls(string)
    if urls:
        return urls[0]


def get_candidates(mention, limit=30):
    results = ""
    urls = []
    with DDGS() as ddgs:
        for idx, r in enumerate(ddgs.answers(mention)):
            title = unquote(r['url'].split('/')[-1])
            url = "https://en.wikipedia.org/wiki/" + title
            if url in urls:
                continue
            # results += f"\n{idx+1}. {title.replace('_', ' ')}\n\t- URL: {url}\n\t- abstract: {r['text']}"
            results += f"\n {idx+1}. {url} - {r['text']}"
            urls.append(url)
            if len(urls) >= limit-1:
                break
        
    return results, urls


def search_ddg(term, limit=3):
    results = "results:\n"
    urls = []

    with DDGS() as ddgs:
        for idx, r in enumerate(ddgs.text(f'{term} site:en.wikipedia.org', safesearch="Off")):
            results += f"\n{idx+1}. {r['href']} - {r['body']}"
            urls.append(r["href"])
            if idx >= limit-1:
                break
        
        return results, urls


def parse_json(string: str):
    start, end = string.find("{"), string.rfind("}")
    if start == -1 or end == -1:
        return None
    string = string[start:end+1]
    try:
        return json.loads(string)
    except json.JSONDecodeError:
        return None
