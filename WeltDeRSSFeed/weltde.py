import feedparser
import aiohttp
from colorama import Fore, Style
import asyncio
import aiosqlite


async def main():
    async with aiosqlite.connect("./rssfeed.db") as db:
        async with db.cursor() as cursor:
            await cursor.execute("""CREATE TABLE IF NOT EXISTS weltRSS(
            id INTEGER PRIMARY KEY,
            lastMessage TEXT)""")
            await db.commit()

            async with aiohttp.ClientSession() as session:
                async with session.get("https://www.welt.de/feeds/latest.rss") as response:
                    data = await response.text()
                    feed = feedparser.parse(data)
                    last_entry = feed.entries[0]

                    try:
                        title = last_entry["title"]
                    except KeyError:
                        title = "No title"

                    try:
                        desc = last_entry["description"]
                    except KeyError:
                        desc = "No description"
                    try:
                        published = last_entry["published"]
                    except KeyError:
                        published = "No published date"

                    try:
                        category = last_entry["category"]
                    except KeyError:
                        category = "No category"

                    try:
                        author = last_entry["author"]
                    except KeyError:
                        author = "No author"

                    query = """SELECT lastMessage FROM weltRSS WHERE lastMessage = ?"""
                    await cursor.execute(query, (title,))
                    result = await cursor.fetchone()

                    if not result:
                        query2 = """INSERT INTO weltRSS(lastMessage) VALUES(?)"""
                        await cursor.execute(query2, (title,))
                        await db.commit()
                        text = f"""{Style.BRIGHT}{Fore.LIGHTCYAN_EX}{title}({Fore.CYAN}category: {category}{Fore.LIGHTCYAN_EX}){Fore.RESET}\n\n{Fore.WHITE}{desc}{Fore.RESET}\n\n{Fore.LIGHTMAGENTA_EX}> Published at: {published}\n> Author: {author}{Fore.RESET}"""

                        print(text)

                    else:
                        print(
                            f'{Style.NORMAL}{Fore.LIGHTRED_EX}The article with the Title {Style.BRIGHT}{Fore.LIGHTWHITE_EX}"{title}"{Style.NORMAL}{Fore.LIGHTRED_EX} is already in the database{Style.NORMAL}{Fore.RESET}!')


if __name__ == "__main__":
    asyncio.run(main())
