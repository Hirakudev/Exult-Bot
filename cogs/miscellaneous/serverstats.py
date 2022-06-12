import discord
from discord import app_commands
from discord.ext import commands, tasks

from typing import TYPE_CHECKING

from utils import *

if TYPE_CHECKING:
    from bot import ExultBot


class ServerStats(commands.Cog):
    def __init__(self, bot: "ExultBot"):
        self.bot = bot
        self.db = ServerStatsDB(bot)
        self.update_stats.start()

    @tasks.loop(minutes=5.1)
    async def update_stats(self):
        guild = self.bot.get_guild(self.bot.guild.id)
        config = await self.db.try_config(guild.id)
        time_channel = self.bot.get_channel(config.get("time_channel"))
        timezone = config.get("timezone")
        membercount_channel = self.bot.get_channel(config.get("membercount_channel"))
        channels_channel = self.bot.get_channel(config.get("channels_channel"))
        status_channel = self.bot.get_channel(config.get("status_channel"))
        milestone_channel = self.bot.get_channel(config.get("milestone_channel"))
        milestone = config.get("milestone")
        if time_channel and timezone:
            tz = ServerUtils.get_time(timezone)
            name = f"\U000023f0 {tz}"
            if time_channel.name != name:
                await time_channel.edit(name=f"\U000023f0 {name}")
        if membercount_channel:
            count = f"\U0001fac2 Members {guild.member_count}"
            if membercount_channel.name != count:
                await membercount_channel.edit(name=count)
        if channels_channel:
            count = ServerUtils.channel_count(guild)
            if channels_channel.name != count:
                await channels_channel.edit(name=count)
        if status_channel:
            count = ServerUtils.guild_member_count(guild)
            if status_channel.name != count:
                await status_channel.edit(name=count)
        if milestone_channel:
            target = ServerUtils.guild_milestone(guild, milestone)
            count = f"\U0001f4c8 {guild.member_count}/{target}"
            if milestone_channel.name != count:
                await milestone_channel.edit(name=count)

    server_stats = app_commands.Group(
        name="serverstats",
        description="Configure Server stats!",
        default_permissions=discord.Permissions(administrator=True),
    )

    @server_stats.command(
        name="create", description="Create your server stats channels!"
    )
    @app_commands.guild_only()
    async def server_stats_create(self, itr: discord.Interaction):
        embed = embed_builder(
            title="Server Stats",
            description="Enhance your server with Server Stats. Choose the channels you wish to add in the dropdown below.\n",
            thumbnail="https://serverstatsbot.com/serverstats_icon.png",
            footer=f"Server Stats for {itr.guild.name}",
            fields=[
                [
                    "\U0001f4dc Channel Creation",
                    "This will create a Category, hoisted to the top of the server.",
                    False,
                ]
            ],
        )
        await itr.response.send_message(embed=embed, view=ServerStatsView())
