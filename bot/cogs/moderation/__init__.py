from discord import Object
#Discord Imports

from .core import Core
from .purge import Purge
from .slowmode import Slowmode
from .stats import Stats
from .cases import Cases
from .case import Case
#Cog Imports

from utils import *
#Local Imports

class Moderation(Core, Purge, Slowmode, Stats, Cases, Case):
    """Moderation Cog"""

async def setup(bot: ExultBot):
    await bot.add_cog(Moderation(bot), guilds=[Object(guild) for guild in bot.app_guilds])