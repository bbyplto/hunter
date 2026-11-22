"""SQLite-база: хранит всё найденное и убирает дубли."""
import json
import sqlite3
from datetime import datetime, timezone

from .keywords import PRIZE_NAMES, prizes_of
from .models import Item
from .scoring import score


class Storage:
    def __init__(self, path="giveaways.db"):
        self.db = sqlite3.connect(path)
        self.db.execute("""CREATE TABLE IF NOT EXISTS items (
            url TEXT PRIMARY KEY, source TEXT, title TEXT, text TEXT, author TEXT,
            published TEXT, audience INTEGER, found_at TEXT, score INTEGER,
            flags TEXT, region TEXT, extra TEXT)""")
        self.db.commit()

    def add(self, it: Item) -> bool:
        """True, если запись новая."""
        sc, flags, region = score(f"{it.title}\n{it.text}", it.url)
        cur = self.db.execute(
            "INSERT OR IGNORE INTO items VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
            (it.url, it.source, it.title[:300], it.text[:3000], it.author, it.published,
             it.audience, datetime.now(timezone.utc).isoformat(timespec="seconds"),
             sc, json.dumps(flags, ensure_ascii=False), region,
             json.dumps(it.extra, ensure_ascii=False)))
        self.db.commit()
        return cur.rowcount == 1

    def all(self):
        cur = self.db.execute("SELECT * FROM items ORDER BY COALESCE(NULLIF(published,''), found_at) DESC")
        cols = [c[0] for c in cur.description]
        rows = [dict(zip(cols, r)) for r in cur.fetchall()]
        for r in rows:
            r["flags"] = json.loads(r["flags"] or "[]")
            r["prizes"] = prizes_of(f"{r['title']}\n{r['text']}")
            r["prize"] = " + ".join(PRIZE_NAMES[p] for p in r["prizes"]) or "?"
        return rows
