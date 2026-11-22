"""Ключевые слова: призы (PS5 и GTA 6 отдельно) и слово «розыгрыш» на разных языках."""
import re

# --- Призы: каждый со своей регуляркой, чтобы помечать и фильтровать отдельно ---
PRIZE_PATTERNS = {
    "ps5": re.compile(
        r"\bps\s*-?\s*5\b|playstation\s*-?\s*5|play\s+station\s*5|плейстейшн\s*5|плэйстейшн\s*5|\bпс\s*-?\s*5\b"
        r"|بلايستيشن\s*5|بلاي\s*ستيشن\s*5|プレステ\s*5|プレイステーション\s*5|플스\s*5|플레이스테이션\s*5"
        r"|ps5\s*(pro|slim|digital)",
        re.IGNORECASE),
    "gta6": re.compile(
        r"gta\s*-?\s*(6|vi)\b|grand\s+theft\s+auto\s*(6|vi)\b|гта\s*-?\s*(6|vi)\b|جي\s*تي\s*اي\s*6",
        re.IGNORECASE),
}
PRIZE_NAMES = {"ps5": "PS5", "gta6": "GTA 6"}
PRIZE_RE = re.compile("|".join(p.pattern for p in PRIZE_PATTERNS.values()), re.IGNORECASE)

# Как называть призы в поисковых запросах (порядок = приоритет)
PRIZE_TERMS = {
    "ps5": ["PS5", "PlayStation 5", "PS5 Pro", "PS5 Slim"],
    "gta6": ["GTA 6", "GTA VI"],
}
PRIZE_TERMS_RU = {
    "ps5": ["PS5", "ПС5", "плейстейшн 5", "PS5 Pro"],
    "gta6": ["GTA 6", "ГТА 6"],
}

# «Розыгрыш» на разных языках (первые слова — главные, идут в поисковые запросы)
GIVEAWAY_WORDS = {
    "ru": ["розыгрыш", "разыгрываем", "конкурс", "раздача", "разыгрываю", "дарим", "подарим", "приз", "выиграй"],
    "en": ["giveaway", "sweepstakes", "win a", "raffle", "contest", "give away", "giving away", "free ps5"],
    "uk": ["розіграш", "розігруємо", "конкурс"],
    "ro": ["concurs", "câștigă", "castiga", "giveaway"],
    "es": ["sorteo", "sorteamos", "concurso", "gana una"],
    "pt": ["sorteio", "sorteando", "ganhe um"],
    "de": ["gewinnspiel", "verlosung", "verlosen", "gewinne"],
    "fr": ["concours", "à gagner", "a gagner", "tirage au sort"],
    "it": ["concorso", "in palio", "estrazione", "vinci"],
    "pl": ["konkurs", "do wygrania", "rozdanie", "wygraj"],
    "tr": ["çekiliş", "cekilis", "hediye"],
    "kz": ["ұтыс"],
    "ar": ["مسابقة", "سحب", "جيف اواي"],
    "id": ["giveaway", "bagi bagi"],
    "ja": ["プレゼント企画", "抽選", "キャンペーン"],
    "ko": ["이벤트", "나눔", "추첨"],
    "zh": ["抽奖", "送"],
    "hi": ["giveaway", "जीतें"],
}

ALL_GIVEAWAY_WORDS = sorted({w for ws in GIVEAWAY_WORDS.values() for w in ws})
GIVEAWAY_RE = re.compile("|".join(re.escape(w) for w in ALL_GIVEAWAY_WORDS) + r"|#giveaway|#розыгрыш",
                         re.IGNORECASE)


def prizes_of(text: str):
    """Какие призы упомянуты: ['ps5'], ['gta6'] или оба."""
    return [k for k, p in PRIZE_PATTERNS.items() if p.search(text or "")]


def matches(text: str) -> bool:
    """Пост похож на розыгрыш нужного приза."""
    if not text:
        return False
    return bool(PRIZE_RE.search(text)) and bool(GIVEAWAY_RE.search(text))


def build_queries_tagged(langs=None, prizes=("ps5", "gta6"), words_per_lang=3, limit=None):
    """Список (язык, запрос). Порядок «вперемешку»: сначала самые важные комбинации на всех языках,
    потом менее важные — чтобы при ограниченной квоте покрыть все языки и оба приза."""
    langs = langs or list(GIVEAWAY_WORDS)
    tiers = []   # (приоритет, язык, запрос)
    for lang in langs:
        terms = PRIZE_TERMS_RU if lang == "ru" else PRIZE_TERMS
        for wi, word in enumerate(GIVEAWAY_WORDS.get(lang, [])[:words_per_lang]):
            for prize in prizes:
                for ti, term in enumerate(terms[prize]):
                    tiers.append((wi + ti, lang, f"{word} {term}"))
    tiers.sort(key=lambda t: t[0])
    seen, out = set(), []
    for _, lang, q in tiers:
        if q.lower() not in seen:
            seen.add(q.lower())
            out.append((lang, q))
    return out[:limit] if limit else out


def build_queries(langs=None, prizes=("ps5", "gta6"), limit=None):
    return [q for _, q in build_queries_tagged(langs, prizes, limit=limit)]
