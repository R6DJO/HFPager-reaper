import os
from dotenv import load_dotenv

from telethon import TelegramClient, sync, events


load_dotenv()


SESSION = os.getenv('SESSION')
APP_API_ID = os.getenv('APP_API_ID')
APP_API_HASH = os.getenv('APP_API_HASH')
NVIS_CHAT = int(os.getenv('NVIS_CHAT'))

client = TelegramClient(SESSION, APP_API_ID, APP_API_HASH)

@client.on(events.NewMessage(chats=(NVIS_CHAT,)))
async def normal_handler(event):
#    print(event.message)
    user_mess=event.message.to_dict()['message']

    s_user_id=event.message.to_dict()['from_id']
    user_id=int(s_user_id['user_id'])
    user=users.get(user_id)

    mess_date=event.message.to_dict()['date']

    f.write(mess_date.strftime("%d-%m-%Y %H:%M")+"\n")
    f.write(user+"\n")
    f.write(user_mess+"\n\n")

    f.flush()
    print(mess_date.strftime("%d-%m-%Y %H:%M"))
    print(user)
    print(user_mess)
    print()

@client.on(events.MessageEdited(chats=(NVIS_CHAT,)))
async def normal_handler(event):
#    print(event.message)
    user_mess=event.message.to_dict()['message']

    s_user_id=event.message.to_dict()['from_id']
    user_id=int(s_user_id['user_id'])
    user=users.get(user_id)

    mess_date=event.message.to_dict()['date']

    f.write(mess_date.strftime("%d-%m-%Y %H:%M")+"\n")
    f.write(user+"\n")
    f.write(user_mess+"\n\n")

    f.flush()
    print(mess_date.strftime("%d-%m-%Y %H:%M"))
    print(user)
    print(user_mess)
    print()

client.start()

group=NVIS_CHAT

participants = client.get_participants(group)
users={}

for partic in client.iter_participants(group):
    lastname=""
    if partic.last_name:
       lastname=partic.last_name
    users[partic.id]=partic.first_name+" "+lastname

f=open('messages_from_chat', 'a') 

client.run_until_disconnected()
f.close()
