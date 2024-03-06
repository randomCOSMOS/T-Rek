import os
from dotenv import load_dotenv
from discord import Intents, Client, Message
from responses import get_response 


load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")


intents = Intents.default()
intents.message_content = True
client = Client(intents=intents)


async def send_message(message, user_message):
    if not user_message:
        print("fucked up")
        return
    
    if is_private := user_message[0] == "?":
        user_message = user_message[1:]

    try:
        responses = get_response(user_message)
        await message.author.send(responses) if is_private else await message.channel.send(responses)
    except Exception as e:
        print(e)


@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(msg):
    if msg.author == client.user:
        return
    
    username = msg.author
    user_message = msg.content
    channel = str(msg.channel)

    print(f"[{channel}] {username}: '{user_message}'")
    await send_message(msg, user_message)


client.run(TOKEN)
