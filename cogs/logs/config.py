import discord
from discord import app_commands
from discord.ext import commands

from bot import ExultBot
from utils import *


class LogsConfig(commands.Cog):
    """Logs Config Commands"""

    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = LogsDB(bot)

    logs_group = app_commands.Group(
        name="logs", description="Configure the Logging feature!"
    )

    @logs_group.command(
        name="set", description="Assign which channel logs should be sent to!"
    )
    @app_commands.rename(_channel="channel")
    async def logs_set_slash(self, itr: discord.Interaction, log: str, _channel: str):
        await itr.response.defer()
        followup = itr.followup

        if log not in self.log_types:
            embed = embed_builder(
                description=f"`{log}` is not a valid log type! Please make sure you select a log displayed in the autocomplete menu."
            )
            return await followup.send(embed=embed)
        try:
            channel = itr.guild.get_channel(int(_channel))
        except ValueError:
            channel = _channel
        if channel:
            if isinstance(channel, discord.TextChannel):
                pass
            elif isinstance(channel, str):
                if channel == "disable":
                    pass
                else:
                    embed = embed_builder(
                        description=f"{channel.mention if not isinstance(channel, discord.CategoryChannel) else channel} is not a text channel!"
                    )
                    return await followup.send(embed=embed)
            else:
                embed = embed_builder(
                    description=f"{channel.mention if not isinstance(channel, discord.CategoryChannel) else channel} is not a text channel!"
                )
                return await followup.send(embed=embed)
        else:
            embed = embed_builder(description="Please provide a valid text channel!")
            return await followup.send(embed=embed)
        is_updated = await self.db.set_log(
            guild_id=itr.guild.id,
            log=log,
            channel_id=channel.id if isinstance(channel, discord.TextChannel) else None,
        )
        if not is_updated:
            if channel:
                embed = embed_builder(
                    description=f"`{log.replace('_', ' ').replace('guild', 'server').title()}` are already sent to {channel.mention}!"
                )
            else:
                embed = embed_builder(
                    description=f"`{log.replace('_', ' ').replace('guild', 'server').title()}` is already disabled!"
                )
        else:
            if channel:
                embed = embed_builder(
                    description=f"`{log.replace('_', ' ').replace('guild', 'server').title()}` will now be sent to {channel.mention}!"
                )
            else:
                embed = embed_builder(
                    description=f"`{log.replace('_', ' ').replace('guild', 'server').title()}` has been disabled!"
                )
        await followup.send(embed=embed)

    @logs_set_slash.autocomplete("log")
    async def logs_set_log_autocomplete(self, itr: discord.Interaction, current: str):
        return [
            app_commands.Choice(
                name=l.replace("_", " ").replace("guild", "server").title(), value=l
            )
            for l in self.log_types
        ]

    @logs_set_slash.autocomplete("_channel")
    async def logs_set_channel_autocomplete(
        self, itr: discord.Interaction, current: str
    ):
        log_type = (
            itr.namespace.log.replace("_", " ").replace("guild", "server").title()
        )
        channels = [c for c in itr.guild.text_channels]
        choices = [
            app_commands.Choice(name=f"Disable {log_type}", value="disable"),
            app_commands.Choice(name="Create a channel for me", value="create"),
        ] + [app_commands.Choice(name=f"#{c.name}", value=str(c.id)) for c in channels]
        return choices
