import discord
from discord import app_commands
from discord.ext import commands

from typing import Union

from bot import ExultBot
from utils import *


class CountingConfig(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = CountingDB(bot)

    counting = app_commands.Group(
        name="counting", description="Configure the counting feature!"
    )
    c_blacklist = app_commands.Group(
        name="blacklist",
        description="Configure the counting blacklist!",
        parent=counting,
    )
    c_channel = app_commands.Group(
        name="channel",
        description="Configure the channel for counting!",
        parent=counting,
    )

    @c_blacklist.command(
        name="add", description="Add a Role/Member to the counting blacklist!"
    )
    async def counting_blacklist_add_slash(
        self, itr: discord.Interaction, item: Union[discord.Role, discord.Member]
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup = itr.followup
        embed = None
        is_added = None

        if isinstance(item, discord.Role):
            if item in itr.guild.me.roles:
                embed = embed_builder(
                    description="You can't blacklist a role that I have!"
                )
            if not embed:
                is_added = await self.cdb.add_blacklisted_role(
                    guild_id=itr.guild.id, role_id=item.id
                )
        elif isinstance(item, discord.Member):
            if item.id == bot.user.id:
                embed = embed_builder(description=f"Do you hate me that much?")
            if not embed:
                is_added = await self.cdb.add_blacklisted_user(
                    guild_id=itr.guild.id, user_id=item.id
                )
        # Don't need to add an else since discord will only accept a valid role/member for the field
        if is_added:
            embed = embed_builder(
                description=f"{item.mention} is now blacklisted from counting!"
            )
        if is_added is False:
            embed = embed_builder(description=f"{item.mention} is already blacklisted!")
        await followup.send(embed=embed)

    @c_blacklist.command(
        name="remvove", description="Remove a Role/Member from the counting blacklist!"
    )
    async def counting_blacklist_remove_slash(
        self, itr: discord.Interaction, item: Union[discord.Role, discord.Member]
    ):
        await itr.response.defer()
        followup = itr.followup
        embed = None
        is_removed = None

        if isinstance(item, discord.Role):
            is_removed = await self.cdb.remove_blacklisted_role(
                guild_id=itr.guild.id, role_id=item.id
            )
        elif isinstance(item, discord.Member):
            is_removed = await self.cdb.remove_blacklisted_user(
                guild_id=itr.guild.id, user_id=item.id
            )
        # Don't need to add an else since discord will only accept a valid role/member for the field
        if is_removed:
            embed = embed_builder(
                description=f"{item.mention} is no longer blacklisted from counting!"
            )
        if is_removed is False:
            embed = embed_builder(
                description=f"{item.mention} is not already blacklisted!"
            )
        await followup.send(embed=embed)

    @c_channel.command(name="set", description="Configure the channel for counting!")
    async def counting_channel_set_slash(self, itr: discord.Interaction, item: str):
        await itr.response.defer()
        followup = itr.followup
        channel_id = None
        embed = None

        if item.isdigit():
            channel = itr.guild.get_channel(int(item))
            if channel:
                channel_id = channel.id
        elif item == "disable":
            config = await self.cdb.get_config(guild_id=itr.guild.id)
            if not config or not config.get("channel_id"):
                embed = embed_builder(
                    description=f"Counting has not been configued yet!"
                )
                return await followup.send(embed=embed)
            else:
                await self.cdb.remove_config(guild_id=itr.guild.id)
                embed = embed_builder(description="Counting has been disabled!")
        else:
            channels = [c for c in itr.guild.text_channels if c.name == item]
            if len(channels) == 1:
                channel_id = channels[0].id
            elif len(channels) > 1:
                embed = embed_builder(
                    description=f"Multiple channels with the name `{item}` exist. "
                    "Please use the dropdown provided in the channel menu or provide the channel's ID."
                )
                return followup.send(embed=embed)
        if not channel_id and not embed:
            embed = embed_builder(
                description="Invalid input given. Please try again using the values provided in the autocomplete menu."
            )
        elif channel_id:
            await self.cdb.set_channel(guild_id=itr.guild.id, channel=channel_id)
            if not embed:
                channel = itr.guild.get_channel(channel_id)
                embed = embed_builder(
                    description=f"{channel.mention} is now the counting channel!"
                )
        await followup.send(embed=embed)

    @counting_channel_set_slash.autocomplete("item")
    async def counting_channel_set_autocomplete(
        self, itr: discord.Interaction, current: str
    ):
        channels = [c for c in itr.guild.text_channels]
        choices = [app_commands.Choice(name="disable counting", value="disable")] + [
            app_commands.Choice(name=f"#{c.name}", value=str(c.id)) for c in channels
        ]
        return choices
