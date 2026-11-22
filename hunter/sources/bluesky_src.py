"""Bluesky: открытый поиск постов, ключ не нужен (если сервер вдруг потребует вход — источник просто пропустится)."""
import time

import requests

from ..keywords import build_queries, matches
from ..models import Item

HOSTS = ["https://public.api.bsky.app", "https://api.bsky.app"]


def fetch(cfg, log):
    out = []
    queries = build_queries(["en", "es", "pt", "de", "fr", "ru", "ja", "it", "pl", "tr"],
                            prizes=cfg.get("prizes", ["ps5", "gta6"]), limit=cfg.get("max_queries", 60))
    host = None
    for q in queries:
        r, status = None, "нет связи"
        for h in ([host] if host else HOSTS):
            try:
                r = requests.get(f"{h}/xrpc/app.bsky.feed.searchPosts",
                                 params={"q": q, "sort": "latest", "limit": 100}, timeout=30)
            except requests.RequestException:
                continue
            status = r.status_code
            if r.ok:
                host = h
                break
        else:
            log(f"  bluesky: поиск недоступен ({status}), пропускаю")
            return out
        for p in r.json().get("posts", []):
            text = p.get("record", {}).get("text", "")
            if matches(text):
                handle = p["author"]["handle"]
                out.append(Item(source="bluesky",
                                url=f"https://bsky.app/profile/{handle}/post/{p['uri'].split('/')[-1]}",
                                title=text[:100], text=text, author=handle,
                                published=p.get("record", {}).get("createdAt", ""),
                                extra={"likes": p.get("likeCount", 0)}))
        time.sleep(1)
    return out
