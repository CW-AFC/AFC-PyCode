import dotenv
import nextcord
from nextcord.ext import commands
from pathlib import Path
import os
from colorama import Fore
from dotenv import load_dotenv
import aiosqlite

dotenv_file = dotenv.find_dotenv()
load_dotenv(dotenv_file)

BOT_TOKEN = os.getenv('BOT_TOKEN')

cog_directory = 'cog'


bot = commands.Bot(intents=nextcord.Intents.all(),
                   case_insensitive=True, help_command=None)


@bot.event
async def on_ready():
    await bot.sync_all_application_commands(delete_unknown=True, register_new=True, update_known=True)
    async with aiosqlite.connect("rssfeed.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("""CREATE TABLE IF NOT EXISTS jokeoftheday(
                id INTEGER PRIMARY KEY,
                lastMessage TEXT)""")
            await db.commit()
    activity = nextcord.Activity(
        type=nextcord.ActivityType.watching, name="movies")
    await bot.change_presence(activity=activity)
    print("Ready")


if __name__ == "__main__":
    _cogs = [p.stem for p in Path(cog_directory).glob('*.py')]

    [(bot.load_extension(f'.{ext}', package=cog_directory), print(
        f'{Fore.LIGHTGREEN_EX}[✅] IMPORTED | {Fore.LIGHTYELLOW_EX}{ext} {Fore.LIGHTBLUE_EX}was loaded successfully{Fore.RESET}')) for ext in _cogs]

    bot.run(BOT_TOKEN)
