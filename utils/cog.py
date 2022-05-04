from discord.ext import commands

# Discord Imports

from bot import ExultBot

# Local Imports


class ExultCog(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot: ExultBot = bot
