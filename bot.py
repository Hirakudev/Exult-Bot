import discord
from discord.ext import commands

import aiohttp
import asyncio
import asyncpg
import datetime
import os
import pytz
import sys
import traceback
from contextlib import asynccontextmanager
from typing import Optional, Union, Any


class SupportBot(commands.Bot):
    def __init__(
        self,
        *,
        session: aiohttp.ClientSession,
        pool: asyncpg.Pool,
        listener_connection: asyncpg.Connection,
    ):
        self._connected = False
        self.startup_time: Optional[datetime.timedelta] = None
        self.start_time = discord.utils.utcnow()
        self.app_guilds = [912148314223415316]
        self.owner_ids = [957437570546012240]
        self.pool: asyncpg.Pool = pool
        self.session: aiohttp.ClientSession = session
        self.lock = asyncio.Lock()
        self._db_listener_connection: asyncpg.Connection = listener_connection
        super().__init__(command_prefix="b!", intents=discord.Intents.all())

    red = 0xFB5F5F
    green = 0x2ECC71
    gold = 0xF1C40F

    async def setup_hook(self):
        dirs = [
            f"cogs.{ext}" for ext in ["info", "admin"]
        ]  # [f"cogs.{ext}" for ext in os.listdir("cogs")]
        exts = ["jishaku"] + dirs
        for ext in exts:
            await self.load_extension(ext)

    async def on_ready(self):
        if self._connected:
            print(
                f"Bot reconnected at {datetime.datetime.now().strftime('%b %d %Y %H:%M:%S')}"
            )
        else:
            self.exult_guild = self.get_guild(912148314223415316)
            self.bot_logs = None
            self.error_logs = None
            self.dev_role = None
            await self.tree.sync(guild=self.exult_guild)
            self._connected = True
            self.startup_time = discord.utils.utcnow() - self.start_time
            print(
                f"Successfully logged into {self.user}. ({round(self.latency*1000)}ms)\n"
                f"Startup Time: {self.startup_time.total_seconds():.2f} seconds"
            )

    async def on_error(self, event: str, *args, **kwargs):
        error = sys.exc_info()[1]
        error_type = type(error)
        trace = error.__traceback__
        error_message = "".join(traceback.format_exception(error_type, error, trace))
        channel = self.get_channel(978641023850909776)
        embed = discord.Embed(
            title="An Error Occurred",
            description=f"**__Event:__** {event.title().replace('_', ' ')}\n"
            f"**__Error:__** {error_type.__name__}\n```py\n{error_message}\n```",
            colour=self.red,
            timestamp=discord.utils.utcnow(),
        )
        await channel.send(embed=embed)
        return await super().on_error(event, *args, **kwargs)

    async def close(self):
        try:
            await self._db_listener_connection.close(timeout=5)
            await self.pool.close()
            await self.session.close()
            await self.http.close()
        finally:
            await super().close()

    @staticmethod
    async def try_send(
        target: Union[discord.abc.GuildChannel, discord.User, discord.Member],
        *args,
        **kwargs,
    ):
        try:
            await target.send(*args, **kwargs)
        except:
            pass

    @staticmethod
    def try_asset(asset: discord.Asset, backup: discord.Asset = None):
        if not asset and not backup:
            return None
        return backup.url if not asset else asset.url

    @staticmethod
    def time(time: datetime.datetime):
        return pytz.utc.localize(time)

    @asynccontextmanager
    async def request(self, method: str, url: str, **kwargs: Any):
        await self.lock.acquire()

        response = await self.session.request(method, url, **kwargs)
        try:
            yield response
        finally:
            response.close()
            self.lock.release()
