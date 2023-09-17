import os

import discord
from dotenv import load_dotenv

import PropertyCog
from PropertyAnalyzer import PropertyAnalyzer

load_dotenv()
bot = discord.Bot(intents=discord.Intents.default())

TOKEN = str(os.getenv("DISCORD_TOKEN"))
USER_ID = int(os.getenv("USER_ID"))
ANALYZER = PropertyAnalyzer()


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    PropertyCog.setup(bot)


bot.run(TOKEN)
