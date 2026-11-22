"""Веб-поиск (DuckDuckGo/Bing и др. через библиотеку ddgs, ключ не нужен).
Через поисковик достаём то, что нельзя парсить напрямую: Instagram, TikTok, X, Facebook,
Gleam.io, Twitch, сайты-агрегаторы конкурсов."""
import random
import time

from ..keywords import matches
from ..models import Item

SITES = [
    # платформы, на которых держатся конкурсы
    "gleam.io", "rafflecopter.com", "woobox.com", "kingsumo.com", "viralsweep.com",
    # соцсети
    "instagram.com", "tiktok.com", "x.com", "twitter.com", "facebook.com", "threads.net",
    "youtube.com", "kick.com", "twitch.tv", "vk.com", "t.me", "dzen.ru",
    # агрегаторы конкурсов и официальные промо
    "online-sweepstakes.com", "contestgirl.com", "sweepstakesadvantage.com", "giveawayfrenzy.com",
    "playstation.com",
]
# фразы для site:-запросов (по ним ищем на каждом сайте)
SITE_PHRASES = ['giveaway PS5', '"win a PS5"', 'sweepstakes PS5', 'giveaway "PS5 Pro"',
                'giveaway "GTA 6"', 'розыгрыш PS5']
# общие фразы без привязки к сайту
PHRASES = ['giveaway PS5', '"win a PS5"', '"PS5 giveaway"', '"PS5 Pro giveaway"', 'sweepstakes PS5',
           '"PlayStation 5" giveaway', 'giveaway "GTA 6"', 'giveaway "GTA VI"', '"PS5" "GTA 6" giveaway',
           'розыгрыш PS5', 'розыгрыш ПС5', 'розыгрыш "плейстейшн 5"', 'розыгрыш "GTA 6"', 'розіграш PS5',
           'sorteo PS5', 'sorteo "GTA 6"', 'sorteio PS5', 'sorteio "GTA 6"', 'gewinnspiel PS5',
           'verlosung PS5', 'concours PS5', 'concorso PS5', 'çekiliş PS5', 'konkurs PS5', 'concurs PS5',
           'PS5 抽奖', 'PS5 プレゼント企画', 'PS5 이벤트', 'مسابقة بلايستيشن 5']


def fetch(cfg, log):
    from ddgs import DDGS
    out = []
    queries = PHRASES + [f"site:{s} {p}" for p in SITE_PHRASES for s in SITES]
    if cfg.get("max_queries"):
        queries = queries[:cfg["max_queries"]]
    ddg = DDGS()
    for i, q in enumerate(queries, 1):
        try:
            results = ddg.text(q, max_results=cfg.get("results_per_query", 30), timelimit=cfg.get("timelimit", "w"))
        except Exception as e:
            if "no results" in str(e).lower():   # просто ничего не нашлось — это не ошибка
                continue
            log(f"  web: '{q}': {type(e).__name__} — жду и продолжаю")
            time.sleep(20)
            continue
        for r in results or []:
            text = f"{r.get('title', '')}\n{r.get('body', '')}"
            # для Gleam/агрегаторов приз в тексте может не совпасть по слову «розыгрыш» — достаточно приза
            if matches(text) or ("gleam.io" in r.get("href", "") and matches(text + " giveaway")):
                out.append(Item(source="web", url=r["href"], title=r.get("title", ""), text=r.get("body", ""),
                                author=r["href"].split("/")[2] if "//" in r["href"] else "",
                                extra={"query": q}))
        if i % 10 == 0:
            log(f"  web: {i}/{len(queries)} запросов, найдено {len(out)}")
        time.sleep(random.uniform(2, 5))   # чтобы поисковик не забанил
    return out
