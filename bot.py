import os

import discord
from dotenv import load_dotenv

from Property import Property
from PropertyAnalyzer import PropertyAnalyzer, get_profitable_properties

load_dotenv()
bot = discord.Bot(intents=discord.Intents.default())

TOKEN = str(os.getenv('DISCORD_TOKEN'))
USER_ID = int(os.getenv('USER_ID'))


@bot.event
async def on_ready():
    print(f"{bot.user} is ready and online!")
    analyzer = PropertyAnalyzer()
    properties = get_profitable_properties(analyzer.get_all_unique_properties())
    for prop in properties:
        await send_dm(prop)


async def send_dm(prop: Property):
    user = await bot.fetch_user(USER_ID)
    await user.send(
        f"{prop.street_address}, {prop.city}, {prop.province}, {prop.postal_code}\nPrice={prop.price}\nEstimated Profitability=${prop.calculate_profitability(5, 6, 550).__round__(2)}")


bot.run(TOKEN)
