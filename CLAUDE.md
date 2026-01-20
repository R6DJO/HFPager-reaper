# CLAUDE.md

Инструкции для Claude Code при работе с этим репозиторием.

## Быстрый старт

```bash
pip install -r requirements.txt
cp .env.sample .env  # настроить переменные
python HFPreaper.py
```

## Архитектура

### HFPreaper.py

Основной модуль. Ключевые компоненты:

- `message_to_markdown(message)` — конвертация Telegram entities в Markdown
- `format_reaper_message(parsed, users_set)` — форматирование сообщения для REAPER_CHAT
- `process_parsed_message(parsed, user_id, username)` — обработка и дедупликация
- `new_message_handler(event)` / `edited_message_handler(event)` — обработчики событий Telethon

### regexps.py

Парсинг сообщений HFPager. Два паттерна:

- `winbot` — Windows клиент: `S_ID[S_CS] (M_ID) > R_ID[R_CS] ... CRC OK/ERROR ... Error Rate=X% ... : MSG`
- `linux` — Linux клиент: `ACK S_ID[S_CS](M_ID) > R_ID[R_CS] ... ,ER=X% :\nMSG`

Функция `msg_parse(msg)` возвращает dict с полями или None.

## Структуры данных

### unique_messages

In-memory словарь для дедупликации:

```python
unique_messages = {
    (S_ID, M_ID, R_ID): {
        'parsed': dict,      # результат msg_parse()
        'users': set,        # множество @username принявших
        'reaper_msg_id': int # ID сообщения в REAPER_CHAT (для edit)
    }
}
```

### Поля parsed dict

| Поле | Описание | Пример |
|------|----------|--------|
| `TYPE` | Тип паттерна | `winbot`, `linux` |
| `S_ID` | ID отправителя | `2095` |
| `S_CS` | Позывной отправителя (опц.) | `UA3AAA` |
| `M_ID` | Номер сообщения | `237` |
| `R_ID` | ID получателя | `7502` |
| `R_CS` | Позывной получателя (опц.) | `UB3AYU` |
| `ERR` | Error rate | `0.5` |
| `MSG` | Текст сообщения | `Привет!` |
| `CRC` | CRC статус (только winbot) | `OK`, `ERROR` |
| `ACK` | ACK статус (только linux) | `√`, `X`, `` |

## Логгеры

```python
logger = logging.getLogger('hfpreaper')           # основной
logging.getLogger('hfpreaper.parser')             # парсинг (regexps.py)
logging.getLogger('hfpreaper.raw')                # сырые сообщения
```

## Переменные окружения

| Переменная | Обязательная | Описание |
|------------|--------------|----------|
| `SESSION` | да | Имя файла сессии (без .session) |
| `APP_API_ID` | да | Telegram API ID |
| `APP_API_HASH` | да | Telegram API Hash |
| `NVIS_CHAT` | да | ID чата-источника |
| `REAPER_CHAT` | да | ID чата для пересылки |
| `DATA_DIR` | нет | Директория для данных (по умолчанию: `data`) |

## Важно

- Используется **userbot** (не Bot API) — только так можно видеть сообщения других ботов
- Дедупликация только в памяти — при перезапуске сбрасывается
- `users` dict загружается при старте из участников NVIS_CHAT
- Все данные (сессия, логи) хранятся в `DATA_DIR` (по умолчанию `data/`)
- Docker: первый запуск требует интерактивной авторизации (`docker compose run --rm hfpreaper`)
