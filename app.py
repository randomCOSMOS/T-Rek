import os
import json
from dotenv import load_dotenv
from discord import Intents, Client, Message, AllowedMentions
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
from random import choice

# loading env variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FIREBASE_TOKEN = os.getenv("FIREBASE_TOKEN")

# some predefined data
compliments = ["Great job!", "Excellent job!", "Impressive work!", "Great effort!", "Fantastic job!", "Well Done!"]
with open("members.json", "r") as file:
    members = json.load(file)

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
    if msg.content.startswith("**"):
        # msg.content = msg.content[1:]

        username = str(msg.author)
        user_message = msg.content
        channel = msg.channel

        # ask confirmation from user
        confirmation = await msg.reply("Finalized your post? (Yes/No)", mention_author=True)
        def check(m): # check if the channel and user are the same
            return m.author == msg.author and m.channel == channel
        try: # get the response or time out if afk
            response = await client.wait_for('message', check=check, timeout=30.0)
        except asyncio.TimeoutError:
            return

        # what happens if response is yes
        if response.content.lower() in ("yes", "y", "ye"):
            # delete redundant messages
            await confirmation.delete()
            await response.delete()

            # formatting data
            try:
                link = user_message.split("**Link:**")
                project = link[0].split("**Project Status:**")
                progress = project[0].split("**Progress:**")

                data = {
                    "progress": progress[1].strip(),
                    "project status": project[1].strip(),
                    "link": link[1].strip()
                }
            except:
                await channel.send("The format was wrong! 😔")
                return

            # data is received and logged both side (client and server)
            await channel.send(choice(compliments))
            print(f"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} - Data Received - [{str(channel)}] {username}: '{user_message}'")

            # data sent to firebase and logged on server side
            doc_ref = db.collection(members[username]["name"]).document(members[username]["domain"])
            doc_ref.update({datetime.today().strftime('%d-%m-%Y'): data})
            print(f"{datetime.now().strftime("%d/%m/%Y %H:%M:%S")} - Data Stored Successfully!")
        else:
            await response.delete()
            await channel.send("Ok discarding that!")

# running the bot.....
client.run(DISCORD_TOKEN)

