import discord

# Discord Imports

import os

# Regular Imports

from .abberantics import AbberanticsCog

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Friends(AbberanticsCog):
    """Friends Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(
        Friends(bot), guilds=[discord.Object(guild) for guild in bot.friend_guilds]
    )
