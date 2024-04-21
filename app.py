import os
import json
from dotenv import load_dotenv
from discord import Intents, Client, Message, AllowedMentions, Interaction
from discord.ext import commands
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime, timedelta
from random import choice

# loading env variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
FIREBASE_TOKEN = os.getenv("FIREBASE_TOKEN")

# some predefined data
compliments = ["Great job!", "Excellent job!", "Impressive work!", "Great effort!", "Fantastic job!", "Well Done!", "Nice Work!", ]
with open("members.json", "r") as file:
    members = json.load(file)

# connecting to the firestore DB
cred = credentials.Certificate(FIREBASE_TOKEN)
app = firebase_admin.initialize_app(cred)
db = firestore.client()

# managing intents
intents = Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix=".",intents=intents)

# function when a msg is sent
@client.event
async def on_message(msg, date=datetime.now()):
    # ignore msg if sender is the bot itself, to prevent looping lol
    if msg.author == client.user:
        return
    
    # only reply msg if prefix is "="
    if msg.content.startswith("**") or msg.content.startswith("Prog") or msg.content.startswith("prog"):
        # msg.content = msg.content[1:]

        username = str(msg.author)
        user_message = msg.content.lower()
        channel = msg.channel

        # ask confirmation from user
        confirmation = await msg.reply("Finalized your post? (Yes/No)", mention_author=True)
        def check(m): # check if the channel and user are the same
            return (m.author == msg.author or m.author == "randomcosmos") and m.channel == channel
        try: # get the response or time out if afk
            response = await client.wait_for('message', check=check, timeout=30.0)
        except TimeoutError:
            await confirmation.delete()
            return

        # what happens if response is yes
        if response.content.lower() in ("yes", "y", "ye"):
            # delete redundant messages
            await confirmation.delete()
            await response.delete()

            # formatting data
            try:
                link = user_message.split("**link:**")
                project = link[0].split("**project status:**")
                progress = project[0].split("**progress:**")

                data = {
                    "progress": progress[1].strip(),
                    "project status": project[1].strip(),
                    "link": link[1].strip() if len(link) > 1 else ""
                }
            except:
                try:
                    link = user_message.split("link:")
                    project = link[0].split("project status:")
                    progress = project[0].split("progress:")

                    data = {
                        "progress": progress[1].strip(),
                        "project status": project[1].strip(),
                        "link": link[1].strip() if len(link) > 1 else ""
                    }
                except:
                    await channel.send("The format was wrong! 😔")
                    return

            # data is received and logged both side (client and server)
            await msg.reply(choice(compliments), mention_author=False)
            print(f"{date.strftime("%d/%m/%Y %H:%M:%S")} - Data Received - [{str(channel)}] {username}: '{user_message}'")

            # data sent to firebase and logged on server side
            doc_ref = db.collection(members[username]["name"]).document(members[username]["domain"])
            if doc_ref.get().exists:
                doc_ref.update({date.strftime('%d-%m-%Y'): data})
            else:
                doc_ref.set({date.strftime('%d-%m-%Y'): data})    

            print(f"{date.strftime("%d/%m/%Y %H:%M:%S")} - Data Stored Successfully!")
        else:
            await response.delete()
            await confirmation.delete()
            await channel.send("Ok discarding that!")

# slash command
@client.tree.command(name="scan",description="scans data after a date and sends it.")
async def scan(interaction:Interaction, date: str):
    await interaction.response.send_message("Hello World!")
    async for msg in interaction.channel.history(limit=50, after=datetime.strptime(date, "%d/%m/%y"), before=datetime.strptime(date, "%d/%m/%y") + timedelta(days=1)):
        await on_message(msg, datetime.strptime(date, "%d/%m/%y"))

# logging when bot is online
@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")
    await client.tree.sync()

# running the bot.....
client.run(DISCORD_TOKEN)
