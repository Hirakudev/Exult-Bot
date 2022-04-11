from dotenv import load_dotenv
from os import environ
from aiohttp import ClientSession
from asyncpg import create_pool
from asyncio import run
# Regular Imports

from utils import *
# Local Imports

load_dotenv(r"bot/utils/.env")


async def main():
    async with ClientSession() as session, \
            create_pool(environ["PSQL_URI"]) as pool, \
            pool.acquire() as listener_connection, \
            ExultBot(session=session, pool=pool,
                     listener_connection=listener_connection) as bot:
        await bot.start(environ["TEST_TOKEN"])


if __name__ == "__main__":
    run(main())
