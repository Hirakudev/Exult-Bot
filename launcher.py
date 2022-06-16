import aiohttp
import asyncpg
import asyncio
import os
from dotenv import load_dotenv

from bot import SupportBot

load_dotenv()


async def main():
    async with aiohttp.ClientSession() as session, asyncpg.create_pool(
        os.environ["PSQL_URI"]
    ) as pool, pool.acquire() as listener_connection, SupportBot(
        session=session, pool=pool, listener_connection=listener_connection
    ) as bot:
        await bot.start(os.environ["TOKEN"])


if __name__ == "__main__":
    asyncio.run(main())
