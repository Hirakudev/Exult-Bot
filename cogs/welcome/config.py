import discord
from discord import app_commands
from discord.ext import commands

from typing import Union

from bot import ExultBot
from utils import *


class WelcomeConfig(commands.Cog):
    """Levelling Config Commands"""

    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db: WelcomeDB = WelcomeDB(bot)

    welcome_group = app_commands.Group(
        name="welcome", description="Configure the Welcome feature!"
    )
    welcome_set = app_commands.Group(
        name="set",
        description="Assign certain welcome settings a value!",
        parent=welcome_group,
    )

    @welcome_set.command(
        name="channel",
        description="Set which channel welcome messages should be sent to!",
    )
    @app_commands.guild_only()
    @app_commands.describe(
        channel="The channel you want welcome messages to be sent to!"
    )
    async def welcome_set_channel(
        self, itr: KnownInteraction[ExultBot], channel: discord.TextChannel
    ):
        await itr.response.defer()

        config = await self.db.get_config(itr.guild.id)
        if not config:
            return await itr.edit_original_message(
                content="Welcome has not been configured for this server!"
            )
        elif config.get("channel_id") == channel.id:
            return await itr.edit_original_message(
                content=f"{channel.mention} is already configured as the Welcome channel!"
            )
        await self.db.set_channel(itr.guild.id, channel.id)
        return await itr.edit_original_message(
            content=f"The Welcome channel has been set to {channel.mention}!"
        )

    @welcome_set.command(
        name="message",
        description="Configure the message sent for the welcome messages!",
    )  # type: ignore
    @app_commands.guild_only()
    @app_commands.describe(
        message=f'The message to set for the welcome message. "default" will use the default message.'
    )
    async def welcome_set_message(
        self, itr: KnownInteraction[ExultBot], message: str
    ) -> discord.InteractionMessage:
        await itr.response.defer()

        sender = itr.edit_original_message
        mentioned_user: bool = False

        config = await self.db.get_config(itr.guild.id)
        if config.get("custom_message") == message:
            return await sender(
                content="The message specified is already configured as the welcome message!"
            )

        if not any(("{user}" not in message, "{server}" not in message)):
            mentioned_user = True

        if message.lower() == "default":
            await self.db.set_message(itr.guild.id, None)
            return await sender(
                content="Set the custom welcome message to the default!"
            )
        else:
            await self.db.set_message(itr.guild.id, message)

        fmt = f"Welcome message message has been set to: ```\n{message}```"
        if not mentioned_user:
            fmt += (
                "\n*Pro Tip: You can mention the user who joined in the message by "
                'using "{user}" and the server name with "{server}".*\n`Welcome {user} to {server}!`'
            )
        return await sender(content=fmt)
