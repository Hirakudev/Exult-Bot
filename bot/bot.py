import discord
from discord import app_commands
from discord.ext import commands
# Discord Imports

import aiohttp
import asyncpg
import collections
import datetime
import logging
import pytz
import sys
import typing
import waifuim
# Regular Imports

class ExultBot(commands.AutoShardedBot):
    def __init__(self, *, session: aiohttp.ClientSession, pool: asyncpg.Pool, listener_connection: asyncpg.Connection, **kwargs):
        self._connected = False
        self.startup_time: typing.Optional[datetime.timedelta] = None
        self.start_time = discord.utils.utcnow()
        self.logger = logging.getLogger(__name__)
        self.app_guilds = [912148314223415316]
        self.pool: asyncpg.Pool = pool
        self.session: aiohttp.ClientSession = session
        self.wf: waifuim.WaifuAioClient = waifuim.WaifuAioClient(session=self.session, appname="Exult")
        super().__init__(
            command_prefix="t!",
            description="An all-in-one bot to fit all your needs. Moderation, Fun, Utility and More!",
            activity=discord.Activity(type=discord.ActivityType.watching, name="Exult Rewrite"),
            intents=discord.Intents.all()
        )
        self.mod_roles: collections.DefaultDict[int, typing.Set[int]] = collections.defaultdict(set)
        self.admin_roles: collections.DefaultDict[int, typing.Set[int]] = collections.defaultdict(set)
        self.mod_users: collections.DefaultDict[int, typing.Set[int]] = collections.defaultdict(set)
        self.admin_users: collections.DefaultDict[int, typing.Set[int]] = collections.defaultdict(set)
        self._db_listener_connection: asyncpg.Connection = listener_connection

        self.exult_guild = None
        self.bot_logs = None
        self.dev_role = None

    red = 0xfb5f5f
    green = 0x2ecc71
    gold = 0xf1c40f
    invite = discord.utils.oauth_url(889185777555210281, permissions=discord.Permissions(3757567166))

    async def setup_hook(self):
        exts = ["jishaku", "cogs.moderation", "cogs.fun",
                "cogs.guild_config", "cogs.bot_events", "cogs.miscellaneous"]
        for ext in exts:
            await self.load_extension(ext)
        await self.populate_cache()
        await self.create_db_listeners()

    async def populate_cache(self, guild_id: typing.Optional[int] = None) -> None:
        query = '''
            SELECT guild_id, 
                   moderator_users, 
                   moderator_roles, 
                   admin_users, 
                   admin_roles 
            FROM guilds 
            WHERE CASE WHEN ($1::bigint = 0) THEN TRUE ELSE guild_id = $1 END
        '''
        data = await self.pool.fetch(query, guild_id or 0)
        for guild_id, moderator_users, moderator_roles, admin_users, admin_roles in data:
            self.mod_users[guild_id] = set(moderator_users)
            self.mod_roles[guild_id] = set(moderator_roles)
            self.admin_users[guild_id] = set(admin_users)
            self.admin_roles[guild_id] = set(admin_roles)

    async def create_db_listeners(self) -> None:
        """|coro|

        Registers listeners for database events.
        """
        async def _delete_everything_callback(conn, pid, channel, payload):
            guild_id = int(payload)
            exceptions = (KeyError, AttributeError, ValueError)
            try:
                del self.mod_users[guild_id]
            except exceptions:
                pass
            try:
                del self.mod_roles[guild_id]
            except exceptions:
                pass
            try:
                del self.admin_users[guild_id]
            except exceptions:
                pass
            try:
                del self.admin_roles[guild_id]
            except exceptions:
                pass

        async def _update_moderator_roles_callback(conn, pid, channel, payload):
            payload = discord.utils._from_json(payload)  # noqa
            self.mod_roles[payload['guild_id']] = set(payload['ids'])

        async def _update_moderator_users_callback(conn, pid, channel, payload):
            payload = discord.utils._from_json(payload)  # noqa
            self.mod_users[payload['guild_id']] = set(payload['ids'])

        async def _update_admin_roles_callback(conn, pid, channel, payload):
            payload = discord.utils._from_json(payload)  # noqa
            self.admin_roles[payload['guild_id']] = set(payload['ids'])

        async def _update_admin_users_callback(conn, pid, channel, payload):
            payload = discord.utils._from_json(payload)  # noqa
            self.admin_users[payload['guild_id']] = set(payload['ids'])

        async def _insert_everything_callback(conn, pid, channel, payload):
            await self.populate_cache(int(payload))

        await self._db_listener_connection.add_listener('delete_everything', _delete_everything_callback)
        await self._db_listener_connection.add_listener('update_moderator_roles', _update_moderator_roles_callback)
        await self._db_listener_connection.add_listener('update_moderator_users', _update_moderator_users_callback)
        await self._db_listener_connection.add_listener('update_admin_roles', _update_admin_roles_callback)
        await self._db_listener_connection.add_listener('update_admin_users', _update_admin_users_callback)
        await self._db_listener_connection.add_listener('insert_everything', _insert_everything_callback)

    async def on_ready(self):
        if self._connected:
            msg = f"Bot reconnected at {datetime.now().strftime('%b %d %Y %H:%M:%S')}"
            print(msg)
        else:
            self.exult_guild = self.get_guild(912148314223415316)
            self.bot_logs = self.get_channel(961278438965116949)
            self.error_logs = self.get_channel(961090013624401970)
            self.dev_role = self.exult_guild.get_role(914159464406470656)
            self._connected = True
            self.startup_time = discord.utils.utcnow() - self.start_time
            msg = f"Successfully logged into {self.user}. ({round(self.latency * 1000)}ms)\n" \
                f"Startup Time: {self.startup_time.total_seconds():.2f} seconds."
            print(msg)

    async def on_message(self, message: discord.Message):
        if isinstance(message.channel, discord.DMChannel) and await self.is_owner(message.author):
            if message.content.lower() == "sync":
                commands, guilds = 0, 0
                for guild in self.app_guilds:
                    g = discord.Object(guild)
                    x = await self.tree.sync(guild=g)
                    commands += len(x)
                    guilds += 1
                await message.reply(f"Synced {commands} commands across {guilds} guilds.")
        await self.process_commands(message)

    async def on_error(self, event: str, *args, **kwargs):
        error_type, error, traceback_object = sys.exc_info()
        if not error:
            raise

        embed = discord.Embed(title=f"An Error Occurred",
                      description=f"**__Event:__** {event.title().replace('_', ' ')}\n**__Error:__** {error_type.__name__}\n```py\n{error}\n```",
                      colour=self.red,
                      timestamp=discord.utils.utcnow()
                      )
        await self.get_channel(961776237490094150).send(embed=embed)
        return await super().on_error(event, *args, **kwargs)

    async def on_tree_error(self, interaction: discord.Interaction, command: typing.Optional[typing.Union[app_commands.ContextMenu, app_commands.Command]],
                            error: app_commands.AppCommandError):
        if command and getattr(command, "on_error", None):
            return

        if self.extra_events.get("on_app_command_error"):
            return interaction.client.dispatch("app_command_error", interaction, command, error)

        raise error from None

    async def on_command_completion(self, ctx):
        await self.pool.execute("INSERT INTO commands (user_id, command_name) VALUES ($1, $2)", ctx.author.id,
                                ctx.command.name)

    async def on_interaction(self, interaction: discord.Interaction):
        if interaction.type == discord.InteractionType.application_command:  # Application Command.
            await self.pool.execute("INSERT INTO commands (user_id, command_name) VALUES ($1, $2)", interaction.user.id,
                                    interaction.command.name)

    async def close(self):
        try:
            await self.wf.close()
            self.logger.info("Closed Waifu Client.")
            await self._db_listener_connection.close(timeout=5)
            self.logger.info("Closed DB Listener Connection.")
            await self.pool.close()
            self.logger.info("Closed PSQL Pool Connection.")
            await self.session.close()
            self.logger.info("Closed Session.")
            await self.http.close()
            self.logger.info("HTTP Session Closed.")
        finally:
            await super().close()

    @staticmethod
    async def get_or_fetch_member(self, guild: discord.Guild, user: typing.Union[discord.User, int]):
        user = user.id if isinstance(user, discord.User) else user
        try:
            return guild.get_member(user) or await guild.fetch_member(user)
        except discord.HTTPException:
            return None

    @staticmethod
    async def get_or_fetch_user(self, user: int):
        try:
            return self.get_member(user) or await self.fetch_member(user)
        except discord.HTTPException:
            return None

    @staticmethod
    async def try_send(user: typing.Union[discord.User, discord.Member], *args, **kwargs):
        try:
            await user.send(*args, **kwargs)
        except discord.Forbidden:
            pass

    @staticmethod
    def try_asset(asset: discord.Asset, backup: discord.Asset = None):
        """ Insert a backup `Asset` if `asset` is None """
        if not asset and not backup:
            return None
        return backup.url if not asset else asset.url

    @staticmethod
    def time(time: datetime):
        return pytz.utc.localize(time)
