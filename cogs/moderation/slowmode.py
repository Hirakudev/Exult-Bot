import discord
from discord import app_commands

# Discord Imports

import datetime

# Regular Imports

from utils import *
from utils.helpers import FutureTime

# Local Imports


class Slowmode(ExultCog):

    slowmode = app_commands.Group(
        name="slowmode",
        description="Enable or Disable Slowmode.",
        default_permissions=discord.Permissions(manage_channels=True),
    )

    @slowmode.command(name="on", description="Enable slowmode for a given channel.")
    @app_commands.describe(
        duration="How long you want the slowmode to last (Max 6 hours).",
        channel="The channel you want to activate slowmode in.",
    )
    @guild_staff(manage_channels=True)
    async def slowmode_on_slash(
        self,
        itr: discord.Interaction,
        duration: str,
        channel: discord.TextChannel = None,
    ):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup
        channel = itr.channel if not channel else channel

        x = FutureTime(duration).dt
        y = x - datetime.datetime.utcnow()
        seconds = y.total_seconds()

        try:
            await channel.edit(slowmode_delay=seconds)
        except discord.HTTPException:
            embed = embed_builder(
                title="Duration given exceeds maximum limit. (6 hours)"
            )
            return await followup.send(embed=embed)

        embed = embed_builder(
            title=f"{channel} now has a slowmode of {duration}",
            url=f"https://discord.com/channels/{itr.guild.id}/{channel.id}",
        )
        await followup.send(embed=embed)

    @slowmode.command(name="off", description="Disable slowmode for a given channel.")
    @app_commands.describe(channel="The channel you want to activate slowmode in.")
    @guild_staff(manage_channels=True)
    async def slowmode_off_slash(
        self, itr: discord.Interaction, channel: discord.TextChannel = None
    ):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup
        channel = itr.channel if not channel else channel

        if not channel.slowmode_delay:
            return

        await channel.edit(slowmode_delay=None)

        embed = embed_builder(
            title=f"{channel} is no longer in slowmode.",
            url=f"https://discord.com/channels/{itr.guild.id}/{channel.id}",
        )
        await followup.send(embed=embed)
