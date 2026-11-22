"""Охотник за розыгрышами GTA 6 / PS5.

    python main.py                 # запустить все источники, включённые в config.yaml
    python main.py -s web reddit   # только выбранные
    python main.py --report        # только пересобрать отчёт из базы
    python main.py --loop 60       # крутиться и проверять каждые 60 минут
"""
import argparse
import sys
import time
import traceback
from datetime import datetime

import yaml

from hunter import notify, report
from hunter.sources import SOURCES
from hunter.storage import Storage


def log(msg):
    print(f"[{datetime.now():%H:%M:%S}] {msg}", flush=True)


def run_once(cfg, only):
    db = Storage(cfg.get("database", "giveaways.db"))
    new = []
    for name, mod in SOURCES.items():
        scfg = cfg.get(name) or {}
        if only and name not in only:
            continue
        if not only and not scfg.get("enabled"):
            continue
        scfg.setdefault("days", cfg.get("days", 14))
        log(f"▶ {name}")
        try:
            items = mod.fetch(scfg, log)
        except KeyError as e:
            log(f"  {name}: не заполнено поле {e} в config.yaml — пропускаю")
            continue
        except Exception:
            log(f"  {name}: ошибка, пропускаю\n{traceback.format_exc(limit=2)}")
            continue
        added = [it.url for it in items if db.add(it)]
        new += added
        log(f"  {name}: подходящих {len(items)}, новых {len(added)}")

    rows = db.all()
    report.to_html(rows, cfg.get("html", "giveaways.html"))
    report.to_csv(rows, cfg.get("csv", "giveaways.csv"))
    log(f"Готово. Новых: {len(new)}, всего в базе: {len(rows)} → {cfg.get('html', 'giveaways.html')}")

    fresh = [r for r in rows if r["url"] in set(new) and r["score"] >= cfg.get("notify", {}).get("min_score", 45)]
    notify.send(cfg.get("notify", {}), fresh, log)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-c", "--config", default="config.yaml")
    ap.add_argument("-s", "--sources", nargs="*", choices=list(SOURCES))
    ap.add_argument("--report", action="store_true")
    ap.add_argument("--loop", type=int, metavar="MIN")
    ap.add_argument("--test-bot", action="store_true", help="отправить тестовое сообщение ботом")
    a = ap.parse_args()
    try:
        with open(a.config, encoding="utf-8") as f:
            cfg = yaml.safe_load(f) or {}
    except FileNotFoundError:
        sys.exit("Нет config.yaml — скопируй config.example.yaml в config.yaml и заполни.")

    if a.test_bot:
        return notify.test(cfg.get("notify", {}), log)

    if a.report:
        rows = Storage(cfg.get("database", "giveaways.db")).all()
        report.to_html(rows, cfg.get("html", "giveaways.html"))
        report.to_csv(rows, cfg.get("csv", "giveaways.csv"))
        return log(f"Отчёт пересобран: {len(rows)} записей")

    while True:
        run_once(cfg, a.sources)
        if not a.loop:
            break
        log(f"Следующий запуск через {a.loop} мин")
        time.sleep(a.loop * 60)


if __name__ == "__main__":
    main()
