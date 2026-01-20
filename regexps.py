import re
import logging

logger = logging.getLogger('hfpreaper.parser')

REGEXPS = {
    'winbot': (r'(?s)(?P<S_ID>\d{1,5})\[{0,1}(?P<S_CS>[A-Z0-9-]+){0,1}\]{0,1} \((?P<M_ID>\d{1,3})\) > (?P<R_ID>\d{1,5})\[{0,1}(?P<R_CS>[A-Z0-9-]+){0,1}\]{0,1}.*CRC (?P<CRC>OK|ERROR).*Error Rate=(?P<ERR>[0-9.]+)%.*?:\s*(?P<MSG>.*)$'),
    'linux': (r'(?P<ACK>[√X]*) *(?P<S_ID>\d{1,5})\[{0,1}(?P<S_CS>[A-Z0-9-]+){0,1}\]{0,1}\((?P<M_ID>\d{1,3})\) > (?P<R_ID>\d{1,5})\[{0,1}(?P<R_CS>[A-Z0-9-]+){0,1}\]{0,1}.*,ER=(?P<ERR>[0-9.]+)% :\n(?P<MSG>.*)')
}


def msg_parse(msg):
    """Парсит сообщение HFPager и возвращает словарь с метаданными или None."""
    for pattern_name, pattern in REGEXPS.items():
        match_object = re.search(pattern, msg)
        if match_object:
            msg_meta = match_object.groupdict()
            msg_meta['TYPE'] = pattern_name
            logger.debug(f"Matched pattern '{pattern_name}': S_ID={msg_meta.get('S_ID')}, M_ID={msg_meta.get('M_ID')}")
            return msg_meta

    logger.debug(f"No pattern matched for message: {msg[:100]}...")
    return None
