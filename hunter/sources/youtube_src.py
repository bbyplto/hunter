"""YouTube Data API v3. Бесплатно ~100 поисков в день (квота 10 000, поиск = 100)."""
import time
from datetime import datetime, timedelta, timezone

import requests

from ..keywords import build_queries_tagged, matches
from ..models import Item

API = "https://www.googleapis.com/youtube/v3/search"
LANGS = {"ru": "ru", "uk": "uk", "en": "en", "es": "es", "pt": "pt", "de": "de", "fr": "fr",
         "it": "it", "pl": "pl", "tr": "tr", "ar": "ar", "id": "id", "ja": "ja", "ko": "ko", "hi": "hi", "ro": "ro",
         "zh": "zh-Hans", "kz": "kk"}


def fetch(cfg, log):
    key = cfg["api_key"]
    after = (datetime.now(timezone.utc) - timedelta(days=cfg.get("days", 14))).strftime("%Y-%m-%dT%H:%M:%SZ")
    queries = build_queries_tagged(list(LANGS), prizes=cfg.get("prizes", ["ps5", "gta6"]),
                                   limit=cfg.get("max_queries", 90))
    out = []
    for lang, q in queries:
        params = {"part": "snippet", "q": q, "type": "video", "order": "date", "maxResults": 50,
                  "publishedAfter": after, "relevanceLanguage": LANGS[lang], "key": key}
        r = requests.get(API, params=params, timeout=30)
        if r.status_code == 403:
            log(f"  youtube: квота кончилась или ключ неверный ({r.json().get('error', {}).get('message', '')})")
            return out
        r.raise_for_status()
        for v in r.json().get("items", []):
            sn = v["snippet"]
            text = f"{sn.get('title', '')}\n{sn.get('description', '')}"
            if matches(text):
                out.append(Item(source="youtube", url=f"https://www.youtube.com/watch?v={v['id']['videoId']}",
                                title=sn.get("title", ""), text=sn.get("description", ""),
                                author=sn.get("channelTitle", ""), published=sn.get("publishedAt", ""),
                                extra={"lang": lang}))
        time.sleep(0.3)
    return out
