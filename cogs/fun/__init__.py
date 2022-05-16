import discord

# Discord Imports

import os

# Regular Imports

from .wtp import WTP
from .basic import Basic
from .weather import Weather
from .waifu import Waifu

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Fun(WTP, Basic, Weather, Waifu):
    """Fun Cog"""

    dagpi_token = os.environ["DAGPI_TOKEN"]


async def setup(bot: ExultBot):
    await bot.add_cog(
        Fun(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )
