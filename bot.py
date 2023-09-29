import os

import discord
from dotenv import load_dotenv

import PropertyCog

load_dotenv()
bot = discord.Bot(intents=discord.Intents.default())

TOKEN = str(os.getenv("DISCORD_TOKEN"))
USER_ID = int(os.getenv("USER_ID"))


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    PropertyCog.setup(bot)


bot.run(TOKEN)
