import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, AllowedMentions
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

cred = credentials.Certificate('./t-rek-cfafd-firebase-adminsdk-651wx-a3fc8cbe5f.json')
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# doc_ref = db.collection('logs').document()
# doc_ref.set()

# 
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    
    if msg.content[0] == "=":
        msg.content = msg.content[1:]

        username = msg.author
        user_message = msg.content
        channel = str(msg.channel)

        print(f"[{channel}] {username}: '{user_message}'")
        await msg.channel.send(f"Got an message from {username.mention} that says \n `{user_message}`")


client.run(TOKEN)

