import discord
from discord import app_commands
from discord.ext import commands

from typing import Union

from bot import ExultBot
from utils import *


class WelcomeConfig(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = WelcomeDB(bot)
        self.welcome_items = ["channel_id", "custom_message"]

    welcome_group = app_commands.Group(
        name="welcome", description="Configure the Welcome feature!"
    )

    # Config commands for welcome yet to be completed.
