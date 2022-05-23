import discord
from discord import app_commands
from discord.ext import commands

import functools
from typing import Union

from bot import ExultBot
from utils import *


class LevellingConfig(commands.Cog):
    """Levelling Config Commands"""

    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db: LevellingDB = LevellingDB(bot)

    levelling = app_commands.Group(
        name="levelling",
        description="Configure the levelling feature!",
        default_permissions=discord.Permissions(manage_guild=True),
    )
    levelling_set = app_commands.Group(
        name="set",
        description="Give levelling config properties a value!",
        parent=levelling,
    )
    levelling_blacklist = app_commands.Group(
        name="blacklist",
        description="Configure the levelling blacklist!",
        parent=levelling,
    )
    levelling_reward = app_commands.Group(
        name="reward-role",
        description="Configure the role rewards for levelling!",
        parent=levelling,
    )

    @levelling_set.command(
        name="announce-channel",
        description="Set where level-up announcements are sent!",
    )  # type: ignore
    async def levelling_set_announce_channel(
        self, itr: KnownInteraction[ExultBot], channel: discord.TextChannel
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        config = await self.db.get_custom_channel(itr.guild.id)
        if config == channel.id:
            return await itr.edit_original_message(
                content=f"Level-up Announcements are already set to {channel.mention}!"
            )

        await self.db.set_custom_channel(itr.guild.id, channel.id)
        return await itr.edit_original_message(
            content=f"Level-up Announcements will now be sent to {channel.mention}!"
        )

    @levelling_set.command(
        name="message",
        description="Configure the message sent for the level-up announcement!",
    )  # type: ignore
    @app_commands.guild_only()
    @app_commands.describe(
        message=f'The message to set for the level-up announcement. "default" will use the default message.'
    )
    async def levelling_set_message(
        self, itr: KnownInteraction[ExultBot], message: str
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        sender = itr.edit_original_message
        mentioned_user: bool = False

        if not any(("{user}" not in message, "{level}" not in message)):
            mentioned_user = True

        if message.lower() == "default":
            await self.db.remove_custom_message(itr.guild.id)
            return await sender(
                content="Set the custom level-up message to the default!"
            )
        else:
            await self.db.set_message(itr.guild.id, message)

        fmt = f"Level-up announcement message has been set to: ```\n{message}```"
        if not mentioned_user:
            fmt += '\n*Pro Tip: You can mention the user who levelled up in the message by " \
            "using "{user}" and the level they reached with "{level}".*'
        return await sender(content=fmt)

    @levelling_blacklist.command(
        name="add", description="Add a Role/Channel to the levelling blacklist!"
    )  # type: ignore
    @app_commands.guild_only()
    @app_commands.describe(item="The item to add to the levelling blacklist.")
    async def levelling_blacklist_add_slash(
        self,
        itr: KnownInteraction[ExultBot],
        item: app_commands.Transform[
            Union[discord.Role, discord.TextChannel], RoleChannelTransformer
        ],
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        if isinstance(item, (discord.Role, discord.TextChannel)):
            is_added = await self.db.blacklist_add(itr.guild.id, item.id)
        else:
            return await itr.edit_original_message(
                content=f"That is not a valid Role or Text Channel!"
            )

        fmt = (
            f"{item.mention} is now blacklisted from levelling!"
            if is_added
            else f"{item.mention} is already blacklisted!"
        )
        return await itr.edit_original_message(content=fmt)

    @levelling_blacklist.command(
        name="remvove",
        description="Remove a Role/Channel from the levelling blacklist!",
    )  # type: ignore
    @app_commands.guild_only()
    @app_commands.describe(item="The item to remove from the levelling blacklist.")
    async def levelling_blacklist_remove_slash(
        self,
        itr: KnownInteraction[ExultBot],
        item: app_commands.Transform[
            Union[discord.Role, discord.TextChannel], RoleChannelTransformer
        ],
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        if isinstance(item, (discord.Role, discord.TextChannel)):
            is_added = await self.db.blacklsit_remove(itr.guild.id, item.id)
        else:
            return await itr.edit_original_message(
                content=f"That is not a valid Role or Text Channel!"
            )

        fmt = (
            f"{item.mention} is no longer blacklisted from levelling!"
            if is_added
            else f"{item.mention} is not blacklisted!"
        )
        return await itr.edit_original_message(content=fmt)

    @levelling_reward.command(name="add", description="Add a levelling role reward!")  # type: ignore
    @app_commands.guild_only()
    @app_commands.describe(
        level="The level to reward for.", role="The role to reward with."
    )
    async def levelling_role_reward_add_slash(
        self,
        itr: KnownInteraction[ExultBot],
        level: int,
        role: app_commands.Transform[discord.Role, NotBotRoleTransformer],
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        if role.managed:
            return await itr.edit_original_message(
                content="You cannot assign a bot role as a role reward!"
            )

        is_added = await self.db.add_reward(itr.guild.id, level, role.id)
        fmt = (
            f"{role.mention} will now be given to members when they reach `LEVEL {level}`!"
            if is_added
            else f"{role.mention} is already a role reward!"
        )
        return await itr.edit_original_message(content=fmt)

    @levelling_reward.command(name="remove", description="Remove a levelling role reward!")  # type: ignore
    @app_commands.guild_only()
    @app_commands.describe(role="The role to remove from rewards.")
    async def levelling_role_reward_remove_slash(
        self,
        itr: KnownInteraction[ExultBot],
        role: app_commands.Transform[discord.Role, NotBotRoleTransformer],
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        is_removed = await self.db.remove_reward(itr.guild.id, role.id)
        fmt = (
            f"{role.mention} has been removed as a role reward!"
            if is_removed
            else f"{role.mention} is not a role reward!"
        )
        return await itr.edit_original_message(content=fmt)
