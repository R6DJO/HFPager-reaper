#!/usr/bin/env python3
import os
from dotenv import load_dotenv
from telethon import TelegramClient, sync, events
from pprint import pformat,pprint

from regexps import msg_parse

load_dotenv()



SESSION = os.getenv('SESSION')
APP_API_ID = os.getenv('APP_API_ID')
APP_API_HASH = os.getenv('APP_API_HASH')
NVIS_CHAT = int(os.getenv('NVIS_CHAT'))

client = TelegramClient(SESSION, APP_API_ID, APP_API_HASH)

@client.on(events.NewMessage(chats=(NVIS_CHAT,)))
async def normal_handler(event):
    # print(event.message)
    user_mess=event.message.to_dict()['message']

    s_user_id=event.message.to_dict()['from_id']
    user_id=int(s_user_id['user_id'])
    user=users.get(user_id)

    mess_date=event.message.to_dict()['date']

    f.write(pformat(event.message.to_dict())+'\n')
    f.write(mess_date.strftime('%d-%m-%Y %H:%M')+'\n')
    f.write(str(user_id)+' ('+user+')\n')
    f.write(user_mess+'\n\n')
    f.flush()

    print(mess_date.strftime('%d-%m-%Y %H:%M'))
    print(str(user_id)+' ('+user+')')
    print(user_mess)
    pprint(msg_parse(user_mess))
    

@client.on(events.MessageEdited(chats=(NVIS_CHAT,)))
async def normal_handler(event):
    # print(event.message)
    user_mess=event.message.to_dict()['message']

    s_user_id=event.message.to_dict()['from_id']
    user_id=int(s_user_id['user_id'])
    user=users.get(user_id)

    mess_date=event.message.to_dict()['date']

    f.write(pformat(event.message.to_dict())+'\n')
    f.write(mess_date.strftime('%d-%m-%Y %H:%M')+'\n')
    f.write(str(user_id)+' ('+user+')\n')
    f.write(user_mess+'\n\n')
    f.flush()

    print(mess_date.strftime('%d-%m-%Y %H:%M'))
    print(str(user_id)+' ('+user+')')
    print(user_mess)
    pprint(msg_parse(user_mess))

client.start()

group=NVIS_CHAT

participants = client.get_participants(group)
users={}

for partic in client.iter_participants(group):
    users[partic.id]=partic.first_name
    if partic.last_name:
        users[partic.id]=partic.first_name+' '+partic.last_name

f=open('messages_from_chat', 'a') 

client.run_until_disconnected()
f.close()
