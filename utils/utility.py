import discord
from discord.ext import commands

# Discord Imports

from typing import Union, Any, Dict, Optional
import parsedatetime as pdt
import datetime

import pytz

# Regular Imports


from .database import ServerStatsDB, CustomCommandsDB

# Local Imports







class ServerUtils:
    def __init__(
        self,
        category: discord.CategoryChannel,
        timezone: str = None,
        milestone: int = None,
    ):
        self.bot = None
        self.db = None
        self.category = category
        self.func_dict = {
            "Timezone": [self.timezone_channel, timezone],
            "MemberCount": self.member_channel,
            "Channels": self.channel_channel,
            "Status Counter": self.member_count_channel,
            "Milestone": [self.milestone_channel, milestone],
        }
        self.funcs = ["Timezone", "Member", "Channels", "Status Counter", "Milestone"]

        self.to_be_uploaded = {
            "Timezone": None,
            "MemberCount": None,
            "Channels": None,
            "Status Counter": None,
            "Milestone": None,
        }

    def overwrites(self, ctx: discord.Interaction):
        overwrites = {
            ctx.guild.default_role: discord.PermissionOverwrite(
                connect=False, view_channel=True
            )
        }
        return overwrites

    @staticmethod
    def guild_milestone(guild: discord.Guild, milestone: Optional[int] = None) -> int:
        def gtx(num: int, *, bound: int) -> int:
            if num % bound == 0:
                return num + bound
            return (num - (num % bound)) + bound

        def bound(_num: int) -> int:
            _num = milestone if milestone else _num
            return int("1" + "0" * (len(str(_num)) - 1))

        __temp = gtx(guild.member_count, bound=bound(guild.member_count))

        if __temp < 100:
            return 100
        return gtx(guild.member_count, bound=bound(guild.member_count))

    @staticmethod
    def guild_member_count(guild: discord.Guild) -> int:
        online = 0
        idle = 0
        dnd = 0
        offline = 0
        for m in guild.members:
            if m.status == discord.Status.online:
                online += 1
            elif m.status == discord.Status.idle:
                idle += 1
            elif m.status == discord.Status.dnd:
                dnd += 1
            else:
                offline += 1
        return f"\U0001f7e2{online}\U0001f7e1{idle}\U0001f534{dnd}\U000026ab{offline}"

    @staticmethod
    def channel_count(guild: discord.Guild):
        return f"\U0001f4dc {len(guild.text_channels)} \U0001f509 {len(guild.voice_channels)}"

    @staticmethod
    def get_time(country: str):
        try:
            timezone = pytz.timezone(country)
            now = datetime.datetime.now(timezone)
            return now.strftime("%H:%M")
        except:
            raise commands.BadArgument("Invalid timezone")

    async def timezone_channel(
        self,
        ctx: discord.Interaction,
        timezone: str = None,
    ):
        if timezone is None:
            return None
        channel = await self.category.create_voice_channel(
            name=f"\U000023f0 {self.get_time(timezone)}",
            position=0,
            overwrites=self.overwrites(ctx),
        )
        self.to_be_uploaded["Timezone"] = [channel.id, timezone]

    async def member_channel(self, ctx: discord.Interaction):
        channel = await self.category.create_voice_channel(
            name=f"\U0001fac2 Members {ctx.guild.member_count}",
            position=1,
            overwrites=self.overwrites(ctx),
        )
        self.to_be_uploaded["MemberCount"] = channel.id

    async def channel_channel(self, ctx: discord.Interaction):
        channel = await self.category.create_voice_channel(
            name=self.channel_count(ctx.guild),
            position=2,
            overwrites=self.overwrites(ctx),
        )
        self.to_be_uploaded["Channels"] = channel.id

    async def member_count_channel(self, ctx: discord.Interaction):
        channel = await self.category.create_voice_channel(
            name=self.guild_member_count(ctx.guild),
            position=3,
            overwrites=self.overwrites(ctx),
        )
        self.to_be_uploaded["Status Counter"] = channel.id

    async def milestone_channel(self, ctx: discord.Interaction, milestone: int) -> None:
        channel = await self.category.create_voice_channel(
            name=f"\U0001f4c8 {ctx.guild.member_count}/{self.guild_milestone(ctx.guild, milestone)}",
            position=4,
            overwrites=self.overwrites(ctx),
        )
        self.to_be_uploaded["Milestone"] = [channel.id, milestone]

    async def create_channels(self, ctx: discord.Interaction, types: list):
        for _type in types:
            await self.func_dict[_type][0](ctx, self.func_dict[_type][1]) if isinstance(
                self.func_dict[_type], list
            ) else await self.func_dict[_type](ctx)
        await self.upload_to_db(ctx)

    async def upload_to_db(self, ctx: discord.Interaction):
        if not self.bot:
            self.bot = ctx.client
        if not self.db:
            self.db = ServerStatsDB(self.bot)
        time_stats = self.to_be_uploaded.get("Timezone")
        member_stats = self.to_be_uploaded.get("MemberCount")
        channel_stats = self.to_be_uploaded.get("Channels")
        status_stats = self.to_be_uploaded.get("Status Counter")
        milestone_stats = self.to_be_uploaded.get("Milestone")
        if time_stats:
            await self.db.upload_timezone(
                ctx.guild.id, channel_id=time_stats[0], timezone=time_stats[1]
            )
        if member_stats:
            await self.db.upload_membercount(ctx.guild.id, member_stats)
        if channel_stats:
            await self.db.upload_channels(ctx.guild.id, channel_stats)
        if status_stats:
            await self.db.upload_statuses(ctx.guild.id, status_stats)
        if milestone_stats:
            await self.db.upload_milestone(
                ctx.guild.id,
                channel_id=milestone_stats[0],
                milestone=milestone_stats[1],
            )


class CommandUtils:
    def __init__(self, bot: commands.Bot) -> None:
        self.bot: commands.Bot = bot
        self.db = CustomCommandsDB(bot)
        self.cache: Dict[Union[str, int], Any] = {}

    def checks(self, ctx: Union[discord.Interaction, commands.Context]) -> bool:
        if not ctx.guild and not (
            ctx.author.bot if isinstance(ctx, commands.Context) else ctx.user.bot
        ):
            return False
        return True

    async def get_prefix(
        self, ctx: Union[commands.Context, discord.Message]
    ) -> Optional[str]:
        pre = await self.bot.get_prefix(
            ctx.message if isinstance(ctx, commands.Context) else ctx
        )
        return pre[0] if isinstance(pre, list) else pre

    async def create_command(
        self,
        ctx: Union[discord.Interaction, commands.Context],
        name: str,
        response: str,
    ) -> None:
        if self.checks(ctx):
            if ctx.guild is not None:
                resp = {
                    name: {
                        "guild_id": ctx.guild.id,
                        "command_name": name,
                        "command_text": response,
                        "command_creator": ctx.author.id
                        if isinstance(ctx, commands.Context)
                        else ctx.user.id,
                        "created_id": ctx.message.created_at.timestamp()
                        if isinstance(ctx, commands.Context)
                        else ctx.created_at.timestamp(),
                    }
                }
                try:
                    self.cache[ctx.guild.id].update(resp)
                except KeyError:
                    self.cache[ctx.guild.id] = {}
                    self.cache[ctx.guild.id].update(resp)

    def cache_command(self, command: dict):
        guild_id = command.get("guild_id")
        name = command.get("command_name")
        response = command.get("command_text")
        creator = command.get("command_creator")
        created_at = command.get("created_at")
        resp = {
            name: {
                "guild_id": guild_id,
                "command_name": name,
                "command_text": response,
                "command_creator": creator,
                "created_id": created_at,
            }
        }
        try:
            self.cache[guild_id].update(resp)
        except KeyError:
            self.cache[guild_id] = {}
            self.cache[guild_id].update(resp)

    async def get_command(
        self, ctx: Union[discord.Interaction, commands.Context], name: str
    ) -> Optional[Dict[str, Any]]:
        if self.checks(ctx):
            if ctx.guild is not None:
                return self.cache[ctx.guild.id].get(name, "Not found..")

    async def upload_db(self) -> None:
        for guild in list(self.cache):
            await self.db.upload_commands(self.cache[guild])