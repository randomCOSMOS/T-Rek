import os
from dotenv import load_dotenv
from discord import Intents, Client, Message, AllowedMentions
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime

# loading env variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FIREBASE_TOKEN = os.getenv("FIREBASE_TOKEN")

# connecting to the firestore DB
cred = credentials.Certificate(FIREBASE_TOKEN)
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# managing intents
intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)

# logging when bot is online
@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

# function when a msg is sent
@client.event
async def on_message(msg):
    # ignore msg if sender is the bot itself, to prevent looping lol
    if msg.author == client.user:
        return
    
    # only reply msg if prefix is "="
    if msg.content.startswith("="):
        msg.content = msg.content[1:]

        username = msg.author
        user_message = msg.content
        channel = str(msg.channel)

        # ask confirmation from user
        confirmation = await msg.channel.send("You wanna send that?")
        def check(m): # check if the channel and user are the same
            return m.author == username and m.channel == msg.channel
        try: # get the response or time out if afk
            response = await client.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            return

        # what happens if response is yes
        if response.content.lower() in ("yes", "y", "ye"):
            # delete redundant messages
            await confirmation.delete()
            await response.delete()

            # data is received and logged both side (client and server)
            await msg.channel.send("Received msg and logged!")
            print(f"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} - Data Received - [{channel}] {username}: '{user_message}'")

            # data sent to firebase and logged on server side
            doc_ref = db.collection('logs').document(str(username))
            doc_ref.set({datetime.today().strftime('%d-%m-%Y'): user_message})
            print(f"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} - Data Stored Successfully!")
        else:
            await response.delete()
            await msg.channel.send("Ok discarding that!")

# running the bot.....
client.run(DISCORD_TOKEN)

