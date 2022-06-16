import discord

# Discord Imports

from .config import LogsConfig
from .loggers import Loggers

# Cog Imports

from bot import ExultBot
from utils import *

# Local Imports


class Logs(Loggers, LogsConfig):
    """Server Logs Cog"""


async def setup(bot: ExultBot):
    await bot.add_cog(Logs(bot))
