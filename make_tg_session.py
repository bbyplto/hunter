"""Запусти ОДИН РАЗ на своём компьютере:  python3 make_tg_session.py
Он войдёт в твой Telegram и выдаст строку-сессию для сервера (session_string).
⚠ Эта строка = полный доступ к твоему аккаунту. Храни её ТОЛЬКО в секрете GitHub, никому не показывай."""
from telethon.sessions import StringSession
from telethon.sync import TelegramClient

api_id = int(input("api_id (цифры с my.telegram.org): ").strip())
api_hash = input("api_hash: ").strip()
print("\nСейчас спросит телефон (в формате +373...) и код из Telegram.\n")
with TelegramClient(StringSession(), api_id, api_hash) as client:
    s = client.session.save()
print("\n" + "=" * 60)
print("Твой session_string (скопируй ВСЮ строку целиком):\n")
print(s)
print("=" * 60)
