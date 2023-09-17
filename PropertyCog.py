import os

from discord.ext import commands, tasks

from Property import Property
from PropertyAnalyzer import PropertyAnalyzer, get_profitable_properties


class PropertyCog(commands.Cog):
    def __init__(self, bot, user_id):
        self.bot = bot
        self.user_id = user_id
        self.ANALYZER = PropertyAnalyzer()
        self.update_properties_task.start()

    @tasks.loop(hours=2)
    async def update_properties_task(self):
        await self.update_properties()

    @commands.Cog.listener()
    async def on_ready(self):
        print("Cog is ready")

    async def update_properties(self):
        properties = get_profitable_properties(
            self.ANALYZER.get_all_unique_properties()
        )
        for prop in properties:
            await self.send_dm(prop)

    async def send_dm(self, prop: Property):
        user = await self.bot.fetch_user(self.user_id)
        await user.send(
            f"{prop.street_address}, {prop.city}, {prop.province}, {prop.postal_code}\n"
            f"Price = ${prop.price}\n"
            f"Estimated Profitability = ${prop.calculate_profitability(5, 6, 550).__round__(2)}"
        )


def setup(bot):
    user_id = int(os.getenv("USER_ID"))
    bot.add_cog(PropertyCog(bot, user_id))
