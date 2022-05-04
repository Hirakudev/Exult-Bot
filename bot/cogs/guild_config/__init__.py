import discord
#Discord Imports

from .guild_staff import GuildStaff
#Cog Imports

from bot import ExultBot
from utils import *
#Local Imports


class GuildConfig(GuildStaff):
    """ Guild Config Cog """

async def setup(bot: ExultBot):
    await bot.add_cog(GuildConfig(bot), guilds=[discord.Object(guild) for guild in bot.app_guilds])