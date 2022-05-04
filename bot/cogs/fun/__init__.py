import discord

# Discord Imports

from .wtp import WTP
from .basic import Basic
from .weather import Weather

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Fun(WTP, Basic, Weather):
    """Fun Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(
        Fun(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )