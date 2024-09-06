import re

REGEXPS={
    'winbot':(r'^(?P<S_ID>\d{1,5})\[{0,1}(?P<S_CS>[A-Z0-9-]+){0,1}\]{0,1} \((?P<M_ID>\d{1,3})\) > (?P<R_ID>\d{1,5})\[{0,1}(?P<R_CS>[A-Z0-9-]+){0,1}\]{0,1}.*CRC (?P<CRC>OK|ERROR).*Error Rate=(?P<ERR>[0-9.]+)%.*\s:\s(?P<MSG>.*)$'),
    'linux':(r'(?P<ACK>[√X]*) *(?P<S_ID>\d{1,5})\[{0,1}(?P<S_CS>[A-Z0-9-]+){0,1}\]{0,1}\((?P<M_ID>\d{1,3})\) > (?P<R_ID>\d{1,5})\[{0,1}(?P<R_CS>[A-Z0-9-]+){0,1}\]{0,1}.*,ER=(?P<ERR>[0-9.]+)% :\n(?P<MSG>.*)')
}

def msg_parse(msg):
    for key, value in REGEXPS.items():
        match_object = re.search(value, msg)
        if match_object:
            msg_meta = match_object.groupdict()
            msg_meta['TYPE']=key
            return msg_meta
    return None
