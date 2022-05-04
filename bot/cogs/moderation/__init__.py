import discord
#Discord Imports

from .core import Core
from .purge import Purge
from .slowmode import Slowmode
from .stats import Stats
from .cases import Cases
from .case import Case
#Cog Imports

from bot import ExultBot
from utils import *
#Local Imports

class Moderation(Core, Purge, Slowmode, Stats, Cases, Case):
    """Moderation Cog"""

async def setup(bot: ExultBot):
    await bot.add_cog(Moderation(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds])