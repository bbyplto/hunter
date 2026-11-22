"""ВКонтакте: поиск по всем открытым постам (newsfeed.search). Нужен пользовательский токен."""
import time
from datetime import datetime, timedelta, timezone

import requests

from ..keywords import matches
from ..models import Item

QUERIES = ["розыгрыш PS5", "розыгрыш ПС5", "разыгрываем PS5", "конкурс PS5", "розыгрыш плейстейшн 5",
           "розыгрыш playstation 5", "розыгрыш PS5 Pro", "розыгрыш PS5 Slim", "разыгрываем плейстейшн",
           "выиграй PS5", "дарим PS5", "розіграш PS5",
           "розыгрыш GTA 6", "разыгрываем GTA 6", "розыгрыш гта 6"]


def fetch(cfg, log):
    start = int((datetime.now(timezone.utc) - timedelta(days=cfg.get("days", 14))).timestamp())
    out = []
    for q in QUERIES + cfg.get("extra_queries", []):
        start_from = None
        for _page in range(cfg.get("pages", 5)):
            params = {"q": q, "count": 200, "start_time": start, "extended": 1,
                      "access_token": cfg["access_token"], "v": "5.199"}
            if start_from:
                params["start_from"] = start_from
            data = requests.get("https://api.vk.com/method/newsfeed.search", params=params, timeout=30).json()
            if "error" in data:
                log(f"  vk: {data['error'].get('error_msg')}")
                return out
            resp = data["response"]
            names = {g["id"]: g for g in resp.get("groups", [])}
            for p in resp.get("items", []):
                text = p.get("text", "")
                if not matches(text):
                    continue
                oid = p["owner_id"]
                g = names.get(-oid, {})
                out.append(Item(source="vk", url=f"https://vk.com/wall{oid}_{p['id']}",
                                title=g.get("name", "")[:120], text=text, author=g.get("screen_name", str(oid)),
                                published=datetime.fromtimestamp(p["date"], timezone.utc).isoformat(),
                                extra={"views": p.get("views", {}).get("count", 0)}))
            start_from = resp.get("next_from")
            time.sleep(0.4)
            if not start_from:
                break
    return out
