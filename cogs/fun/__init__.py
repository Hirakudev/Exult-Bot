import discord

# Discord Imports

import os

# Regular Imports

from .wtp import WTP
from .basic import Basic
from .weather import Weather
from .waifu import Waifu
from .emotion import EmotionCommands

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Fun(WTP, Basic, Weather, Waifu, EmotionCommands):
    """Fun Cog"""

    dagpi_token = os.environ["DAGPI_TOKEN"]
    emotion_client = None
    kimochi_client = None


async def setup(bot: ExultBot):
    Fun.kimochi_client = bot.kimochi_client
    Fun.emotion_client = Emotions(bot.kimochi_client)
    await bot.add_cog(
        Fun(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )
