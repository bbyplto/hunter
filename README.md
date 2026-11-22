# Охотник за розыгрышами PS5 / GTA 6

Ищет розыгрыши PS5 (включая Pro, Slim, «ПС5», «плейстейшн 5») и GTA 6 по всему миру и присылает их тебе в Telegram. Работает бесплатно на серверах GitHub, компьютер держать включённым не нужно.

| Источник | Что покрывает | Ключ |
|---|---|---|
| `web` | Instagram, TikTok, X, Facebook, YouTube, Twitch, Gleam.io, Kingsumo, ViralSweep, агрегаторы конкурсов, playstation.com, VK, Дзен (через поисковик) | не нужен |
| `bluesky` | Bluesky | не нужен |
| `telegram` | каналы с розыгрышами + хэштеги по всему Telegram | api_id/api_hash + session_string |
| `youtube` | видео-розыгрыши на 19 языках | ключ Google |
| `reddit` | весь Reddit + r/giveaways, r/PS5 и др. | client_id/secret |
| `vk` | открытые посты ВК | токен |

Каждая находка помечается 🎮 PS5 / 🚗 GTA 6, получает **оценку 0–100** (проверка на скам) и **регион** (весь мир / ограничен / ?).

## Запуск на GitHub (бесплатно, 24/7)

1. Заведи аккаунт на https://github.com.
2. Нажми **New repository**, тип **Public**: у публичных репозиториев бесплатно и без лимита. Нажми Create.
3. Выбери **uploading an existing file** и перетащи **всё содержимое** этой папки, включая скрытые `.github`, `.gitignore`, `.nojekyll` (на Mac их видно после Cmd + Shift + . в Finder). Если есть база `giveaways.db` с прошлых запусков, добавь и её. **Не загружай `config.yaml` и файлы `.session`.** Нажми Commit changes.
4. Открой **Settings → Secrets and variables → Actions → New repository secret**. Name: `CONFIG_YAML`, Secret: весь текст твоего заполненного конфига.
5. Открой **Actions** и разреши workflows, если GitHub спросит. Дальше: «Охотник за розыгрышами» → **Run workflow**.

Как часто запускать, задаётся в файле `.github/workflows/hunt.yml`, в строке `cron`.

Отчёт можно смотреть по ссылке. Включи **Settings → Pages → Deploy from a branch → main / (root)**, и отчёт будет доступен по адресу `https://ИМЯ.github.io/РЕПОЗИТОРИЙ/giveaways.html`.

## Telegram на сервере

На своём компьютере один раз запусти `python3 make_tg_session.py`. Он выдаст `session_string`, вставь его в конфиг. **Эта строка — полный доступ к твоему аккаунту**, поэтому храни её только в секрете GitHub.

## Локальный запуск (по желанию)

```bash
pip3 install -r requirements.txt
cp config.example.yaml config.yaml
python3 main.py              # все включённые источники
python3 main.py --test-bot   # проверить бота
python3 main.py -s web       # только один источник
```

## Оценка

- **70+**: есть рандомайзер или Gleam, правила, дата итогов.
- **45–69**: проверь сам.
- **<45**: красные флаги: просят деньги или логин, APK, сокращённые ссылки, «подпишись на 30 каналов».

**Настоящий розыгрыш никогда не просит заплатить, ввести пароль или скачать файл.**
