import discord

# Discord Imports

from .config import GuildConfig

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Config(GuildConfig):
    """Guild Config Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(
        Config(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds]
    )
