from discord import Object
#Discord Imports

from .guild_staff import GuildStaff
#Cog Imports

from utils import *
#Local Imports


class GuildConfig(GuildStaff):
    """ Guild Config Cog """

async def setup(bot: ExultBot):
    await bot.add_cog(GuildConfig(bot), guilds=[Object(guild) for guild in bot.app_guilds])