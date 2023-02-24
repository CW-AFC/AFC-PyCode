import nextcord
import aiohttp
from nextcord.ext import commands


async def get_joke(session):
    async with session.get("https://witzapi.de/api/joke/") as response:
        data = await response.json()
        data = data[0]["text"]
        return data


class refreshJoke(nextcord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @nextcord.ui.button(style=nextcord.ButtonStyle.green, emoji="🔄", custom_id="refreshJoke:btn")
    async def _new_joke(self, button: nextcord.ui.Button, interaction: nextcord.Interaction):
        oldJoke = interaction.message

        async with aiohttp.ClientSession() as session:
            data = await get_joke(session)

            while data == oldJoke:
                data = await get_joke(session)

            text = f"""**New Joke 😆**\n\n{data}"""

            await interaction.response.edit_message(content=text)


class Joke(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.persistent_views_added = False

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.persistent_views_added:
            self.bot.add_view(refreshJoke())
            self.bot.persistent_views_added = True

    @nextcord.slash_command()
    async def joke(self, ctx: nextcord.Interaction):
        async with aiohttp.ClientSession() as session:
            data = await get_joke(session)

            text = f"""**New Joke 😆**\n\n{data}"""
            await ctx.response.send_message(content=text, view=refreshJoke())


def setup(bot):
    bot.add_cog(Joke(bot))
