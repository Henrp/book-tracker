import re
from selectolax.parser import HTMLParser

CHAPTER_RE = re.compile(r'"chapterNum"\s*:\s*(\d+)')

def parse_book(html: str) -> dict | None:
    tree = HTMLParser(html)

    og = {}
    for node in tree.css('meta[property^="og:"]'):
        prop = node.attributes.get("property")
        content = node.attributes.get("content")
        if prop and content:
            og[prop[3:]] = content

    if "title" not in og:
        return None

    return {
        "title":          og["title"],
        "author":         og.get("author"),
        "cover_url":      og.get("image"),
        "updated_time":   og.get("updated_time"),
        "tags":           og.get("tag", "").split(", ") if og.get("tag") else [],
        "latest_chapter": _chapter_num(html),
    }

def _chapter_num(html: str) -> int | None:
    hits = CHAPTER_RE.findall(html)
    if len(hits) != 1:
        return None          # 0 = field gone, >1 = ambiguous. Both mean "don't guess."
    return int(hits[0])