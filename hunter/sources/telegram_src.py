"""Telegram: самый богатый источник для СНГ.

Три способа поиска:
 1. Поиск каналов по названию («розыгрыш ps5», «giveaway gta 6») → читаем их свежие посты.
 2. Поиск публичных постов по хэштегам (#розыгрыш, #giveaway) по всему Telegram.
 3. Поиск по всем чатам/каналам, на которые ты подписан.
Нужен твой обычный аккаунт + api_id/api_hash с https://my.telegram.org
"""
import asyncio
import os
from datetime import datetime, timedelta, timezone

from ..keywords import matches
from ..models import Item

CHANNEL_QUERIES = [
    # PS5
    "розыгрыш ps5", "розыгрыш пс5", "розыгрыш playstation", "розыгрыш плейстейшн", "конкурс ps5",
    "ps5 розыгрыш", "выиграй ps5", "ps5", "playstation", "плейстейшн", "ps5 pro", "giveaway ps5",
    "ps5 giveaway", "playstation giveaway", "sorteo ps5", "sorteio ps5", "ps5 gewinnspiel", "розіграш ps5",
    # GTA 6
    "розыгрыш gta", "розыгрыш гта", "gta 6", "гта 6", "giveaway gta",
    # общее
    "розыгрыш", "розыгрыши", "раздача игр", "конкурсы призы", "giveaway", "розіграш",
    "gewinnspiel", "çekiliş", "konkurs", "free games giveaway",
]
HASHTAGS = ["розыгрыш", "конкурс", "giveaway", "раздача", "розіграш", "sorteo", "sorteio", "gewinnspiel",
            "çekiliş", "ps5", "playstation5", "розыгрышps5", "gta6"]
GLOBAL_QUERIES = ["розыгрыш PS5", "розыгрыш ПС5", "разыгрываем PS5", "розыгрыш плейстейшн", "конкурс PS5",
                  "розыгрыш PS5 Pro", "розыгрыш GTA 6", "розыгрыш ГТА 6", "giveaway PS5", "giveaway GTA 6"]


def _url(chat, msg_id):
    uname = getattr(chat, "username", None)
    if uname:
        return f"https://t.me/{uname}/{msg_id}"
    return f"https://t.me/c/{chat.id}/{msg_id}"


def fetch(cfg, log):
    return asyncio.run(_fetch(cfg, log))


async def _fetch(cfg, log):
    from telethon import TelegramClient, functions, types
    from telethon.errors import FloodWaitError, RPCError

    days = cfg.get("days", 14)
    since = datetime.now(timezone.utc) - timedelta(days=days)
    per_channel = cfg.get("messages_per_channel", 150)
    out = []

    from telethon.sessions import StringSession
    on_server = bool(os.environ.get("GITHUB_ACTIONS"))
    if cfg.get("session_string"):
        session = StringSession(cfg["session_string"].strip())
    elif on_server:
        log("  telegram: на сервере нужен session_string (сделай его скриптом make_tg_session.py)")
        return []
    else:
        session = cfg.get("session", "hunter_session")

    client = TelegramClient(session, int(cfg["api_id"]), cfg["api_hash"])
    if on_server:
        await client.connect()
        if not await client.is_user_authorized():
            log("  telegram: session_string недействителен — сделай новый через make_tg_session.py")
            await client.disconnect()
            return []
    else:
        await client.start()   # в первый раз спросит номер телефона и код

    async def safe(coro):
        try:
            return await coro
        except FloodWaitError as e:
            log(f"  telegram: флуд-лимит, жду {e.seconds} с")
            await asyncio.sleep(e.seconds + 1)
        except RPCError as e:
            log(f"  telegram: {type(e).__name__}: {e}")
        return None

    def add(chat, msg):
        text = msg.message or ""
        if msg.date and msg.date < since:
            return
        if matches(text):
            out.append(Item(
                source="telegram", url=_url(chat, msg.id),
                title=(getattr(chat, "title", "") or "")[:120], text=text,
                author=getattr(chat, "username", "") or getattr(chat, "title", ""),
                published=msg.date.isoformat() if msg.date else "",
                audience=getattr(chat, "participants_count", 0) or 0,
                extra={"views": getattr(msg, "views", 0) or 0}))

    # --- 1. находим каналы ---
    channels = {}
    for q in CHANNEL_QUERIES + cfg.get("extra_channel_queries", []):
        res = await safe(client(functions.contacts.SearchRequest(q=q, limit=100)))
        if res:
            for ch in res.chats:
                if isinstance(ch, types.Channel):
                    channels[ch.id] = ch
        await asyncio.sleep(1.5)
    for uname in cfg.get("extra_channels", []):
        ent = await safe(client.get_entity(uname))
        if ent:
            channels[ent.id] = ent
    log(f"  telegram: найдено каналов/групп: {len(channels)}")

    for i, ch in enumerate(channels.values(), 1):
        try:
            async for msg in client.iter_messages(ch, limit=per_channel):
                if msg.date and msg.date < since:
                    break
                add(ch, msg)
        except FloodWaitError as e:
            log(f"  telegram: флуд-лимит, жду {e.seconds} с")
            await asyncio.sleep(e.seconds + 1)
        except Exception as e:   # приватный/забаненный канал и т.п.
            log(f"  telegram: пропуск {getattr(ch, 'username', ch.id)}: {type(e).__name__}")
        if i % 20 == 0:
            log(f"  telegram: прочитано {i}/{len(channels)} каналов, найдено {len(out)}")
        await asyncio.sleep(cfg.get("delay", 1.0))

    # --- 2. публичный поиск по хэштегам ---
    for tag in HASHTAGS:
        res = await safe(client(functions.channels.SearchPostsRequest(
            hashtag=tag, offset_rate=0, offset_peer=types.InputPeerEmpty(), offset_id=0, limit=100)))
        if res:
            chats = {c.id: c for c in res.chats}
            for msg in res.messages:
                peer = getattr(msg.peer_id, "channel_id", None)
                if peer in chats:
                    add(chats[peer], msg)
        await asyncio.sleep(2)

    # --- 3. поиск по твоим подпискам ---
    for q in GLOBAL_QUERIES:
        try:
            async for msg in client.iter_messages(None, search=q, limit=200):
                chat = await msg.get_chat()
                if chat:
                    add(chat, msg)
        except Exception as e:
            log(f"  telegram global: {type(e).__name__}: {e}")
        await asyncio.sleep(2)

    await client.disconnect()
    return out
