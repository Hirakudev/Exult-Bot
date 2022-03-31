from discord import Activity, ActivityType, Intents, Permissions, Object
from discord.ext.commands import Bot
from discord.utils import oauth_url
#Discord Related Imports

from dotenv import load_dotenv
import os
import logging
from time import time
import asyncpg
import aiohttp
from waifuim import WaifuAioClient
import asyncio
#Regular Imports

from database import *
#Local Imports

load_dotenv("utils/")
TOKEN = os.environ["TEST_TOKEN"]

class ExultTest(Bot):
    def __init__(self):
        self.startTime = time()
        self.synced = False
        self.persistent_views_added = False
        self.db = Database()
        self.logger = logging.getLogger(__name__)
        self.owner_id = 839248459704959058
        self.app_guilds = [912148314223415316, 949429956843290724]
        super().__init__(
            activity=Activity(type=ActivityType.watching, name="Exult Rewrite"),
            command_prefix="t!",
            description="An all-in-one bot to fit all your needs. Moderation, Fun, Utility and More!",
            intents=Intents.all()
        )
        
    async def setup_hook(self):
        exts = [f"cogs.{file[:-3]}" for file in os.listdir("cogs") if file.endswith(".py") and not file.startswith("_") and not file.startswith("test") and not file.startswith("config")]
        exts.insert(0, "jishaku")
        for ext in exts: await self.load_extension(ext)
        
    async def close(self):
        await super().close()
        await self.wf.close()
        self.logger.info("Closed Waifu Client")
        await self.pool.close()
        self.logger.info("Closed psql connection.")
        await self.session.close()
        self.logger.info("Bot AIOHTTP client session closed")
        await self.http.close()
        self.logger.info("HTTP Session closed")
        
    async def get_latency(self):
        _ = []
        for x in range(3):
            x = time()
            await self.pool.execute("SELECT * FROM latency_test")
            y = time()
            _.append(y-x)
        return (_[0] + _[1] + _[2]) / 3
    
    red = 0xfb5f5f
    green = 0x2ecc71
    gold = 0xf1c40f
    invite = oauth_url(889185777555210281, permissions=Permissions(3757567166))
    
    async def on_ready(self):
        if not self.synced:
            for guild in [912148314223415316, 949429956843290724]:
                await self.tree.sync(guild=Object(id=guild))
            total_synced = await self.tree.fetch_commands(guild=Object(912148314223415316))
            self.synced = True
        if not self.persistent_views_added:
            self.persistent_views_added = True
        msg = f"Application Commands Synced: {len(total_synced) if self.synced else 'No'}\n" \
              f"Persistent Views Added: {'Yes' if self.persistent_views_added else 'No'}\n" \
              f"Successfully logged in to {self.user}. ({round(self.latency*1000)}ms)\n" \
              f"Startup time: {round(time() - self.startTime)}s"
        print(msg)

bot = ExultTest()

async def main():
    async with aiohttp.ClientSession() as session:
        async with bot:
            bot.session = session
            bot.pool = await asyncpg.create_pool(os.environ["PSQL_URI"])
            bot.wf = WaifuAioClient(session=session, appname="Exult")
            await bot.start(os.environ["TEST_TOKEN"])
        
if __name__ == "__main__":
    asyncio.run(main())