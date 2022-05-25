import discord
from discord import Guild, app_commands
from discord.ext import commands

import functools
from typing import Union

from bot import ExultBot
from utils import *


class CountingConfig(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = CountingDB(bot)

    counting = app_commands.Group(
        name="counting",
        description="Configure the counting feature!",
        default_permissions=discord.Permissions(manage_guild=True),
    )
    counting_blacklist = app_commands.Group(
        name="blacklist",
        description="Configure the counting blacklist!",
        parent=counting,
    )
    counting_channel = app_commands.Group(
        name="channel",
        description="Configure the channel for counting!",
        parent=counting,
    )

    @counting_blacklist.command(
        name="add", description="Add a Role/Member to the counting blacklist!"
    )
    @app_commands.guild_only()
    @app_commands.describe(item="The Role/Member you want to blacklist from counting.")
    async def counting_blacklist_add(
        self, itr: KnownInteraction[ExultBot], item: Union[discord.Member, discord.Role]
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        is_added = await self.db.blacklist_add(itr.guild.id, item)

        fmt = (
            f"{item.mention} is now blacklisted from counting!"
            if is_added
            else f"{item.mention} is already blacklisted!"
        )
        return await itr.edit_original_message(content=fmt)

    @counting_blacklist.command(
        name="remove", description="Remove a Role/Member from the counting blacklist!"
    )
    @app_commands.guild_only()
    @app_commands.describe(
        item="The Role/Member you want to remove the blacklist from."
    )
    async def counting_blacklist_remove(
        self, itr: KnownInteraction[ExultBot], item: Union[discord.Member, discord.Role]
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        is_removed = await self.db.blacklist_remove(itr.guild.id, item)
        fmt = (
            f"{item.mention} is not blacklisted from counting!"
            if not is_removed
            else f"{item.mention} is no longer blacklisted from counting!"
        )
        return await itr.edit_original_message(content=fmt)

    @counting_channel.command(
        name="set", description="Set which channel should be the counting channel!"
    )
    @app_commands.guild_only()
    @app_commands.describe(
        channel="The channel that you want to be a counting channel."
    )
    async def counting_channel_set(
        self, itr: KnownInteraction[ExultBot], channel: discord.TextChannel
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        config = await self.db.get_config(itr.guild.id)
        new_conf = False
        if not config:
            await self.db.new_config(itr.guild.id, channel.id)
            new_conf = True
        elif config.get("channel_id") == channel.id:
            return await itr.edit_original_message(
                content=f"The counting channel is already set to {channel.mention}!"
            )
        if not new_conf:
            await self.db.set_channel(itr.guild.id, channel.id)
        return await itr.edit_original_message(
            content=f"The counting channel has been set to {channel.mention}!"
        )
