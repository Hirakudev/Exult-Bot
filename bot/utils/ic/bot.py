from datetime import datetime
from discord import (Activity, ActivityType, Asset, Forbidden, Intents, Member, Permissions,
                     Message, DMChannel, Object, Interaction, Guild,
                     User, HTTPException, Embed)
from discord.ext.commands import AutoShardedBot
from discord.utils import oauth_url, utcnow
from discord.app_commands import ContextMenu, Command, AppCommandError
from discord import InteractionType
#Discord Imports

from aiohttp import ClientSession
from asyncpg import Pool
from logging import getLogger
from waifuim import WaifuAioClient
from sys import exc_info
from typing import Optional, Union
import pytz
#Regular Imports

class ExultBot(AutoShardedBot):
    def __init__(self, *, session: ClientSession, pool: Pool, **kwargs):
        self.start_time = utcnow()
        self.logger = getLogger(__name__)
        self.owner_id = 957437570546012240
        self.app_guilds = [957469645089157120, 912148314223415316]
        self.pool: Pool = pool
        self.session: ClientSession = session
        self.wf: WaifuAioClient = WaifuAioClient(session=self.session, appname="Exult")
        super().__init__(
            command_prefix="t!",
            description="An all-in-one bot to fit all your needs. Moderation, Fun, Utility and More!",
            activity=Activity(type=ActivityType.watching, name="Exult Rewrite"),
            intents=Intents.all()
        )
    red = 0xfb5f5f
    green = 0x2ecc71
    gold = 0xf1c40f
    invite = oauth_url(889185777555210281, permissions=Permissions(3757567166))

    async def setup_hook(self):
        exts = ["jishaku", "cogs.moderation"]
        for ext in exts:
            await self.load_extension(ext)

    async def on_ready(self):
        self.startup_time = utcnow() - self.start_time
        msg = f"Successfully logged into {self.user}. ({round(self.latency*1000)}ms)\n" \
              f"Startup Time: {self.startup_time.total_seconds():.2f} seconds."
        print(msg)

    async def on_message(self, message: Message):
        if isinstance(message.channel, DMChannel) and await self.is_owner(message.author):
            if message.content.lower() == "sync":
                commands, guilds = 0, 0
                for guild in self.app_guilds:
                    g = Object(guild)
                    x = await self.tree.sync(guild=g)
                    commands += len(x)
                    guilds += 1
                await message.reply(f"Synced {commands} commands across {guilds} guilds.")
        await self.process_commands(message)

    async def on_error(self, event: str, *args, **kwargs):
        error_type, error, traceback_object = exc_info()
        if not error:
            raise

        embed = Embed(title=f"An Error Occurred", 
                      description=f"**__Event:__** {event.title().replace('_', ' ')}\n**__Error:__** {error_type.__name__}\n```py\n{error}\n```", 
                      colour=self.red,
                      timestamp=utcnow()
                      )
        await self.get_channel(961090013624401970).send(embed=embed)
        return await super().on_error(event, *args, **kwargs)

    async def on_tree_error(self, interaction: Interaction, command: Optional[Union[ContextMenu, Command]], error: AppCommandError):
        if command and getattr(command, "on_error", None):
            return

        if self.extra_events.get("on_app_command_error"):
            return interaction.client.dispatch("app_command_error", interaction, command, error)

        raise error from None

    async def on_command_completion(self, ctx):
        await self.pool.execute("INSERT INTO commands (user_id, command_name) VALUES ($1, $2)", ctx.author.id, ctx.command.name)

    async def on_interaction(self, interaction: Interaction):
        if interaction.type == InteractionType.application_command: #Application Command.
            await self.pool.execute("INSERT INTO commands (user_id, command_name) VALUES ($1, $2)", interaction.user.id, interaction.command.name)

    async def close(self):
        await super().close()
        await self.wf.close()
        self.logger.info("Closed Waifu Client.")
        await self.pool.close()
        self.logger.info("Closed PSQL Pool Connection.")
        await self.session.close()
        self.logger.info("Closed Session.")
        await self.http.close()
        self.logger.info("HTTP Session Closed.")

    @staticmethod
    async def get_or_fetch_member(self, guild: Guild, user: Union[User, int]):
        user = user.id if isinstance(User) else user
        try:
            return guild.get_member(user) or await guild.fetch_member(user)
        except HTTPException:
            return None

    @staticmethod
    async def get_or_fetch_user(self, user: int):
        try:
            return self.get_member(user) or await self.fetch_member(user)
        except HTTPException:
            return None
                
    @staticmethod
    async def try_send(user: Union[User, Member], *args, **kwargs):
        try:
            await user.send(*args, **kwargs)
        except Forbidden:
            pass

    @staticmethod
    def try_asset(asset: Asset, backup: Asset=None):
        """ Insert a backup `Asset` if `asset` is None """
        if not asset and not backup:
            return None
        return backup.url if not asset else asset.url

    @staticmethod
    def time(time: datetime):
        return pytz.utc.localize(time)
