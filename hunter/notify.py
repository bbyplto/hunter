"""Уведомления о новых розыгрышах тебе в Telegram через своего бота (@BotFather)."""
import time

import requests


def _chat_ids(cfg):
    """chat_id может быть одним числом или списком: [111, 222, -100333]."""
    ids = cfg.get("chat_id")
    if not isinstance(ids, list):
        ids = [ids]
    return [str(i).strip() for i in ids if str(i or "").strip()]


def _post(cfg, text, log):
    ok_any = False
    for cid in _chat_ids(cfg):
        r = requests.post(f"https://api.telegram.org/bot{cfg['bot_token']}/sendMessage",
                          data={"chat_id": cid, "text": text, "disable_web_page_preview": True},
                          timeout=20)
        if r.ok:
            ok_any = True
        else:
            log(f"  notify → {cid}: {r.text[:200]}  (этот человек нажал Start у бота?)")
    return ok_any


def test(cfg, log):
    if not cfg.get("bot_token") or not cfg.get("chat_id"):
        return log("Заполни notify.bot_token и notify.chat_id в config.yaml")
    if _post(cfg, "✅ Бот работает! Сюда будут приходить новые розыгрыши.", log):
        log("Сообщение отправлено — проверь Telegram")


def send(cfg, items, log):
    if not cfg.get("bot_token") or not cfg.get("chat_id"):
        return
    wanted = set(cfg.get("prizes", ["ps5", "gta6"]))
    items = [it for it in items if wanted & set(it["prizes"])]
    # PS5 первыми, внутри — по оценке
    items.sort(key=lambda it: ("ps5" not in it["prizes"], -it["score"]))
    if not items:
        if cfg.get("send_empty"):
            _post(cfg, "🔎 Проверил всё — новых розыгрышей пока нет.", log)
        return
    n_ps5 = sum("ps5" in it["prizes"] for it in items)
    n_gta = sum("gta6" in it["prizes"] for it in items)
    head = f"🎁 Новых розыгрышей: {len(items)}  (🎮 PS5: {n_ps5}, 🚗 GTA 6: {n_gta})"
    if cfg.get("report_url"):
        head += f"\n📋 Все находки: {cfg['report_url']}"
    if not _post(cfg, head, log):
        return
    for it in items[:cfg.get("max_per_run", 30)]:
        icon = ("🎮" if "ps5" in it["prizes"] else "") + ("🚗" if "gta6" in it["prizes"] else "")
        msg = (f"{icon} {it['prize']} · {it['source']} · оценка {it['score']} · регион: {it['region']}\n"
               f"{it['title'][:150]}\n{it['url']}")
        if not _post(cfg, msg, log):
            return
        time.sleep(1.1 * len(_chat_ids(cfg)))
