"""Антискам-оценка и определение, для каких стран розыгрыш."""
import re

RED_FLAGS = {
    r"оплат\w* доставк|оплат\w* комисси|pay (for )?shipping|shipping fee|processing fee": "просят деньги",
    r"введ\w* (логин|пароль)|enter (your )?(login|password)|войд\w* через steam|sign in with steam": "просят логин/пароль",
    r"human verification|verify you are human|complete (a |the )?survey|пройд\w* опрос": "«проверка/опрос» (скам)",
    r"mod\s*apk|\.apk\b|crack|кряк|free download|скачать бесплатно|for android|на андроид": "фейковая игра/APK",
    r"bit\.ly|tinyurl|cutt\.ly|is\.gd|shorturl|t\.ly/": "сокращённая ссылка",
    r"подпиш\w* на (все )?\d{2,} канал|subscribe to \d{2,} channels|папк\w* канал": "куча каналов (накрутка)",
    r"напиш\w* в лс за призом|dm (me|us) to claim|claim your prize": "«напиши в ЛС за призом»",
    r"crypto|крипт|usdt|airdrop|nft": "крипта/airdrop",
    r"гарантир\w* выигрыш|guaranteed win|100% win": "«гарантированный выигрыш»",
}

GREEN_FLAGS = {
    r"gleam\.io|rafflecopter|kingsumo|woobox|randomizer|рандомайзер|random\.org|giveaway bot|@\w*randombot": "сервис/рандомайзер",
    r"итоги|результаты|winner will be announced|победител\w* объяв|ends on|до \d{1,2}[.\s]": "есть дата/итоги",
    r"правила|условия|official rules|terms and conditions|no purchase necessary": "есть правила",
}

WORLDWIDE_RE = re.compile(r"worldwide|international|весь мир|все страны|любой стран|ww\b|global giveaway|"
                          r"todo el mundo|mundial|weltweit", re.I)
RESTRICTED_RE = re.compile(r"us only|usa only|u\.s\. residents|uk only|eu only|только (рф|россия|россии|по рф)|"
                           r"residents of|legal residents|open to residents", re.I)


def score(text: str, url: str = ""):
    """Возвращает (оценка 0-100, флаги, регион)."""
    blob = f"{text}\n{url}"
    s, flags = 60, []
    for pat, name in RED_FLAGS.items():
        if re.search(pat, blob, re.I):
            s -= 25
            flags.append("⚠ " + name)
    for pat, name in GREEN_FLAGS.items():
        if re.search(pat, blob, re.I):
            s += 10
            flags.append("✓ " + name)
    if WORLDWIDE_RE.search(blob):
        region = "весь мир"
    elif RESTRICTED_RE.search(blob):
        region = "ограничен"
    else:
        region = "?"
    return max(0, min(100, s)), flags, region
