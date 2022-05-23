import dotenv
import os
import aiohttp
import asyncpg
import asyncio
import kimochi

# Regular Imports

from bot import ExultBot
from utils import *

# Local Imports

dotenv.load_dotenv()


async def main():
    async with aiohttp.ClientSession() as session, asyncpg.create_pool(
        os.environ["TEST_PSQL_URI"]
    ) as pool, pool.acquire() as listener_connection, ExultBot(
        session=session,
        pool=pool,
        listener_connection=listener_connection,
        kimochi_client=kimochi.Client(session),
    ) as bot:
        await bot.start(os.environ["TEST_TOKEN"])


if __name__ == "__main__":
    asyncio.run(main())
