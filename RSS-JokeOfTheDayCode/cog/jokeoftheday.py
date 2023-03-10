import datetime
import aiosqlite
import nextcord
from nextcord.ext import commands, tasks

import aiohttp
import feedparser


async def fetch_rss_feed(session):
    async with session.get("https://www.hahaha.de/witze/witzdestages.xml") as response:
        return await response.text()

midnight = datetime.time(
    hour=0, minute=0, second=0, microsecond=0, tzinfo=datetime.timezone(datetime.timedelta(hours=1))
)


class JokeOfTheDay(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @ commands.Cog.listener()
    async def on_ready(self):
        self.JokeOfTheDay_task.start()

    @ tasks.loop(seconds=1)
    async def JokeOfTheDay_task(self):
        guild = self.bot.get_guild()  # <-- Your guild ID
        channel = guild.get_channel()  # <-- Your channel ID
        async with aiosqlite.connect("rssfeed.db") as db:
            async with db.cursor() as cursor:
                async with aiohttp.ClientSession() as session:
                    rss_feed = await fetch_rss_feed(session)
                    feed = feedparser.parse(rss_feed)
                    event = feed.entries[0]
                    desc = event.summary

                    query = """SELECT lastMessage FROM jokeoftheday WHERE lastMessage = ?"""
                    await cursor.execute(query, (desc,))
                    result = await cursor.fetchone()
                    await db.commit()
                    embed = nextcord.Embed(
                        title="Witz des Tages", description=f"{desc}")

                    if not result:
                        query2 = """INSERT INTO jokeoftheday(lastMessage) VALUES(?)"""
                        await cursor.execute(query2, (desc,))
                        await db.commit()
                        await channel.send(embed=embed)
                    await db.commit()

        self.JokeOfTheDay_task.change_interval(time=midnight)


def setup(bot):
    bot.add_cog(JokeOfTheDay(bot))
