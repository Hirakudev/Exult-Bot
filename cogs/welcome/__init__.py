import discord

# Discord Imports

from .welcomer import Welcomer
from .config import WelcomeConfig

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Welcome(WelcomeConfig, Welcomer):
    """Welcome Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(
        Welcome(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )
