# HFPager Reaper

Telegram userbot для мониторинга и агрегации сообщений HFPager из радиолюбительских чатов.

## Описание

HFPager Reaper отслеживает сообщения от HFPager-ботов в указанном Telegram-чате, парсит метаданные радиосообщений и пересылает уникальные сообщения в отдельный чат с дедупликацией.

### Возможности

- Мониторинг сообщений от HFPager-ботов (Windows и Linux клиенты)
- Парсинг метаданных: ID отправителя/получателя, позывные, номер сообщения, текст
- Дедупликация по ключу (S_ID, M_ID, R_ID)
- Отслеживание кто принял каждое сообщение (via)
- Логирование с ротацией файлов
- Сохранение сырых сообщений с Markdown-форматированием

## Конфигурация

Скопируйте `.env.sample` в `.env` и заполните:

```env
SESSION=hfpreaper
APP_API_ID=12345678
APP_API_HASH=abcdef1234567890abcdef1234567890
NVIS_CHAT=-1001234567890
REAPER_CHAT=-1009876543210
```

| Переменная | Описание |
|------------|----------|
| `SESSION` | Имя сессии Telethon |
| `APP_API_ID` | API ID из [my.telegram.org](https://my.telegram.org) |
| `APP_API_HASH` | API Hash из [my.telegram.org](https://my.telegram.org) |
| `NVIS_CHAT` | ID чата-источника для мониторинга |
| `REAPER_CHAT` | ID чата для пересылки уникальных сообщений |

### Как получить ID чата

1. Добавьте бота [@userinfobot](https://t.me/userinfobot) в чат
2. Или перешлите сообщение из чата боту [@userinfobot](https://t.me/userinfobot)

## Запуск

### Docker (рекомендуется)

```bash
# Скопировать и настроить конфигурацию
cp .env.sample .env
nano .env

# Первый запуск — авторизация в Telegram
docker compose run --rm hfpreaper
```

При первом запуске появится запрос:
```
Please enter your phone (or bot token): +79001234567
Please enter the code you received: 12345
```

После успешной авторизации:
```bash
# Запустить в фоне
docker compose up -d

# Просмотр логов
docker compose logs -f

# Остановка
docker compose down

# Перезапуск
docker compose restart
```

### Локальный запуск

```bash
# Создать виртуальное окружение
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Установить зависимости
pip install -r requirements.txt

# Скопировать и настроить конфигурацию
cp .env.sample .env

# Запуск
python HFPreaper.py
```

При первом запуске потребуется авторизация в Telegram (ввод номера телефона и кода).

## Формат сообщений

### Входные форматы (HFPager)

**Windows клиент:**
```
2095[UA3AAA] (237) > 7502[UB3AYU]
CRC OK, Error Rate=0.5%
Message: Привет!
```

**Linux клиент:**
```
√ 2095[UA3AAA](237) > 7502[UB3AYU],ER=0.5% :
Привет!
```

### Выходной формат (REAPER_CHAT)

```
2095[UA3AAA] > 7502[UB3AYU] (237):
Привет!

via: @user1, @user2
```

## Логирование

Все логи хранятся в директории `data/`:

| Файл | Содержимое | Ротация |
|------|-----------|---------|
| `data/hfpreaper.log` | События приложения | 10 MB × 5 файлов |
| `data/messages_raw.log` | Сырые сообщения (Markdown) | 50 MB × 10 файлов |

### Уровни логирования

- Консоль: INFO и выше
- Файл: DEBUG и выше

## Структура проекта

```
HFPager-reaper/
├── HFPreaper.py        # Основной скрипт
├── regexps.py          # Regex-паттерны для парсинга
├── requirements.txt    # Зависимости
├── .env.sample         # Пример конфигурации
├── Dockerfile
├── docker-compose.yml
├── .dockerignore
└── data/               # Данные (создаётся автоматически)
    ├── hfpreaper.session
    ├── hfpreaper.log
    └── messages_raw.log
```

## Требования

- Python 3.8+
- Telethon
- python-dotenv

Или Docker.

## Лицензия

MIT
