import discord

# Discord Imports

from .levelling import LevellingCommands
from .config import LevellingConfig

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Levelling(
    LevellingCommands, LevellingConfig
):  # Not inheriting LevellingConfig due to it being a GroupCog
    """Levelling Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(
        Levelling(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )