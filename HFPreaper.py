#!/usr/bin/env python3
import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl import types
from pprint import pformat

from regexps import msg_parse

load_dotenv()

# Директория для данных (сессия, логи)
DATA_DIR = os.getenv('DATA_DIR', 'data')
os.makedirs(DATA_DIR, exist_ok=True)


def message_to_markdown(message):
    """Конвертирует сообщение Telegram в Markdown с форматированием."""
    text = message.message or ''
    entities = message.entities or []

    if not entities:
        return text

    # Маппинг типов entities на Markdown обёртки
    entity_formats = {
        types.MessageEntityBold: ('**', '**'),
        types.MessageEntityItalic: ('_', '_'),
        types.MessageEntityCode: ('`', '`'),
        types.MessageEntityPre: ('```\n', '\n```'),
        types.MessageEntityStrike: ('~~', '~~'),
        types.MessageEntityUnderline: ('__', '__'),
        types.MessageEntitySpoiler: ('||', '||'),
    }

    # Собираем все вставки (позиция, текст, приоритет)
    # приоритет: 0 - открывающий, 1 - закрывающий (закрывающие идут первыми при сортировке)
    insertions = []

    for entity in entities:
        start = entity.offset
        end = entity.offset + entity.length
        entity_type = type(entity)

        if entity_type in entity_formats:
            prefix, suffix = entity_formats[entity_type]
            insertions.append((start, 0, prefix))
            insertions.append((end, 1, suffix))
        elif entity_type == types.MessageEntityTextUrl:
            # [text](url)
            insertions.append((start, 0, '['))
            insertions.append((end, 1, f']({entity.url})'))
        elif entity_type == types.MessageEntityMentionName:
            # Упоминание пользователя по ID
            insertions.append((start, 0, '['))
            insertions.append((end, 1, f'](tg://user?id={entity.user_id})'))

    # Сортируем: по позиции (убывание), затем закрывающие перед открывающими
    insertions.sort(key=lambda x: (-x[0], -x[1]))

    # Применяем вставки справа налево
    result = text
    for pos, _, insert_text in insertions:
        result = result[:pos] + insert_text + result[pos:]

    return result

# Настройка логирования
def setup_logging():
    """Настройка логирования в консоль и файл с ротацией."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Корневой логгер
    logger = logging.getLogger('hfpreaper')
    logger.setLevel(logging.DEBUG)

    # Консольный handler (INFO и выше)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(console_handler)

    # Файловый handler с ротацией (DEBUG и выше)
    file_handler = RotatingFileHandler(
        os.path.join(DATA_DIR, 'hfpreaper.log'),
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter(log_format, date_format))
    logger.addHandler(file_handler)

    # Отдельный файл для сырых сообщений
    raw_handler = RotatingFileHandler(
        os.path.join(DATA_DIR, 'messages_raw.log'),
        maxBytes=50*1024*1024,  # 50 MB
        backupCount=10,
        encoding='utf-8'
    )
    raw_handler.setLevel(logging.DEBUG)
    raw_handler.setFormatter(logging.Formatter('%(asctime)s\n%(message)s\n', date_format))

    raw_logger = logging.getLogger('hfpreaper.raw')
    raw_logger.addHandler(raw_handler)
    raw_logger.setLevel(logging.DEBUG)

    return logger

logger = setup_logging()
raw_logger = logging.getLogger('hfpreaper.raw')

# Словарь уникальных сообщений: ключ (S_ID, M_ID, R_ID) -> {'parsed': dict, 'users': set, 'reaper_msg_id': int}
unique_messages = {}


def format_reaper_message(parsed, users_set):
    """Форматирует сообщение для отправки в REAPER_CHAT."""
    s_id = parsed.get('S_ID', '?')
    s_cs = parsed.get('S_CS')
    m_id = parsed.get('M_ID', '?')
    r_id = parsed.get('R_ID', '?')
    r_cs = parsed.get('R_CS')
    msg = parsed.get('MSG', '').strip()

    # Формируем S_ID[S_CS] если позывной известен
    sender = f"{s_id}[{s_cs}]" if s_cs else s_id
    # Формируем R_ID[R_CS] если позывной известен
    receiver = f"{r_id}[{r_cs}]" if r_cs else r_id

    # Список принявших (только имена)
    via_list = ', '.join(sorted(users_set))

    return f"{sender} > {receiver} ({m_id}):\n{msg}\n\nvia: {via_list}"

async def process_parsed_message(parsed, user_id, username):
    """Обработка распарсенного сообщения - добавление в словарь уникальных и пересылка в REAPER_CHAT."""
    if parsed is None:
        return

    # Формируем ключ уникальности
    msg_key = (parsed.get('S_ID'), parsed.get('M_ID'), parsed.get('R_ID'))

    user_info = username
    is_new = msg_key not in unique_messages

    if is_new:
        # Новое сообщение
        unique_messages[msg_key] = {
            'parsed': parsed,
            'users': {user_info},
            'reaper_msg_id': None
        }
    else:
        # Сообщение уже есть - добавляем пользователя
        unique_messages[msg_key]['users'].add(user_info)

    if is_new:
        logger.info(f"Новое сообщение: S_ID={parsed.get('S_ID')}, M_ID={parsed.get('M_ID')}, R_ID={parsed.get('R_ID')}")
    else:
        logger.info(f"Дубль сообщения: S_ID={parsed.get('S_ID')}, M_ID={parsed.get('M_ID')}, R_ID={parsed.get('R_ID')}, users={len(unique_messages[msg_key]['users'])}")
    logger.debug(f"Parsed message: {pformat(parsed)}")

    # Формируем текст для отправки в REAPER_CHAT
    reaper_text = format_reaper_message(parsed, unique_messages[msg_key]['users'])

    if is_new:
        # Отправляем новое сообщение
        sent_msg = await client.send_message(REAPER_CHAT, reaper_text)
        unique_messages[msg_key]['reaper_msg_id'] = sent_msg.id
    else:
        # Редактируем существующее сообщение
        reaper_msg_id = unique_messages[msg_key]['reaper_msg_id']
        if reaper_msg_id:
            await client.edit_message(REAPER_CHAT, reaper_msg_id, reaper_text)



SESSION = os.path.join(DATA_DIR, os.getenv('SESSION', 'hfpreaper'))
APP_API_ID = os.getenv('APP_API_ID')
APP_API_HASH = os.getenv('APP_API_HASH')
NVIS_CHAT = int(os.getenv('NVIS_CHAT'))
REAPER_CHAT = int(os.getenv('REAPER_CHAT'))

client = TelegramClient(SESSION, APP_API_ID, APP_API_HASH)

@client.on(events.NewMessage(chats=(NVIS_CHAT,)))
async def new_message_handler(event):
    try:
        msg_dict = event.message.to_dict()
        user_mess = msg_dict.get('message', '')

        from_id = msg_dict.get('from_id')
        if from_id is None:
            logger.warning("Сообщение без from_id, пропускаем")
            return

        user_id = int(from_id.get('user_id', 0))
        username = users.get(user_id, 'Unknown')

        # Логируем сырое сообщение с Markdown форматированием
        markdown_text = message_to_markdown(event.message)
        raw_logger.debug(f"USER: {user_id} ({username})\n{markdown_text}")

        logger.debug(f"Новое сообщение от {user_id} ({username})")

        parsed = msg_parse(user_mess)
        if parsed:
            await process_parsed_message(parsed, user_id, username)
        else:
            logger.debug(f"Сообщение не соответствует паттернам HFPager")

    except Exception as e:
        logger.exception(f"Ошибка обработки нового сообщения: {e}")


@client.on(events.MessageEdited(chats=(NVIS_CHAT,)))
async def edited_message_handler(event):
    try:
        msg_dict = event.message.to_dict()
        user_mess = msg_dict.get('message', '')

        from_id = msg_dict.get('from_id')
        if from_id is None:
            logger.warning("Отредактированное сообщение без from_id, пропускаем")
            return

        user_id = int(from_id.get('user_id', 0))
        username = users.get(user_id, 'Unknown')

        # Логируем сырое сообщение с Markdown форматированием
        markdown_text = message_to_markdown(event.message)
        raw_logger.debug(f"EDITED USER: {user_id} ({username})\n{markdown_text}")

        logger.debug(f"Отредактированное сообщение от {user_id} ({username})")

        parsed = msg_parse(user_mess)
        if parsed:
            await process_parsed_message(parsed, user_id, username)
        else:
            logger.debug(f"Отредактированное сообщение не соответствует паттернам HFPager")

    except Exception as e:
        logger.exception(f"Ошибка обработки отредактированного сообщения: {e}")

logger.info("Запуск HFPager Reaper...")

client.start()
logger.info("Подключение к Telegram успешно")

# Загружаем список участников чата (id -> @username)
users = {}
try:
    for partic in client.iter_participants(NVIS_CHAT):
        if partic.username:
            users[partic.id] = f"@{partic.username}"
        else:
            # Если нет username, используем имя
            name = partic.first_name or ''
            if partic.last_name:
                name = f"{name} {partic.last_name}"
            users[partic.id] = name.strip() or f"id{partic.id}"
    logger.info(f"Загружено {len(users)} участников из чата NVIS_CHAT")
except Exception as e:
    logger.warning(f"Не удалось загрузить участников чата: {e}")

logger.info(f"Мониторинг чата NVIS_CHAT={NVIS_CHAT}, пересылка в REAPER_CHAT={REAPER_CHAT}")
logger.info("Ожидание сообщений...")

try:
    client.run_until_disconnected()
except KeyboardInterrupt:
    logger.info("Остановка по Ctrl+C")
finally:
    logger.info("HFPager Reaper остановлен")
