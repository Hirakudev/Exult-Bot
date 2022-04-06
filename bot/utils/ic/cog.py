from discord.ext.commands import Cog
#Discord Imports

from . import ExultBot
#Local Imports

class ExultCog(Cog):
    def __init__(self, bot: ExultBot):
        self.bot: ExultBot = bot