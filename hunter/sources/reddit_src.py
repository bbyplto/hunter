"""Reddit: поиск по всему сайту и по профильным сабреддитам.
Без ключа часто отвечает 403/429 — тогда впиши client_id/client_secret (бесплатно: reddit.com/prefs/apps)."""
import time
from datetime import datetime, timezone

import requests

from ..keywords import matches
from ..models import Item

QUERIES = ["PS5 giveaway", "PlayStation 5 giveaway", "PS5 Pro giveaway", "PS5 Slim giveaway",
           "\"win a PS5\"", "PS5 sweepstakes", "PS5 contest", "PS5 raffle",
           "GTA 6 giveaway", "GTA VI giveaway", "win GTA 6"]
SUBS = ["giveaways", "sweepstakes", "GiveawaysForGamers", "PS5", "PS5pro", "playstation", "PlayStationPlus",
        "GTA6", "GameDeals", "FreeGameFindings", "RandomActsOfGaming"]


def _session(cfg):
    s = requests.Session()
    s.headers["User-Agent"] = cfg.get("user_agent", "giveaway-hunter/1.0 (personal script)")
    base = "https://www.reddit.com"
    if cfg.get("client_id") and cfg.get("client_secret"):
        r = s.post("https://www.reddit.com/api/v1/access_token",
                   auth=(cfg["client_id"], cfg["client_secret"]),
                   data={"grant_type": "client_credentials"}, timeout=30)
        r.raise_for_status()
        s.headers["Authorization"] = f"bearer {r.json()['access_token']}"
        base = "https://oauth.reddit.com"
    return s, base


def fetch(cfg, log):
    s, base = _session(cfg)
    t = cfg.get("time", "week")
    targets = [(f"{base}/search.json", {"q": q}) for q in QUERIES]
    targets += [(f"{base}/r/{sub}/search.json", {"q": "PS5 OR \"GTA 6\" OR \"GTA VI\"", "restrict_sr": 1})
                for sub in SUBS]
    out = []
    for url, params in targets:
        params.update({"sort": "new", "t": t, "limit": 100})
        r = s.get(url, params=params, timeout=30)
        if r.status_code in (403, 429):
            log(f"  reddit: {r.status_code} — нужен client_id/client_secret в config.yaml")
            return out
        if not r.ok:
            continue
        for ch in r.json().get("data", {}).get("children", []):
            d = ch["data"]
            text = f"{d.get('title', '')}\n{d.get('selftext', '')}"
            if matches(text):
                out.append(Item(source="reddit", url="https://www.reddit.com" + d["permalink"],
                                title=d.get("title", ""), text=d.get("selftext", ""),
                                author=f"r/{d.get('subreddit')} u/{d.get('author')}",
                                published=datetime.fromtimestamp(d["created_utc"], timezone.utc).isoformat(),
                                extra={"comments": d.get("num_comments", 0)}))
        time.sleep(2)
    return out
