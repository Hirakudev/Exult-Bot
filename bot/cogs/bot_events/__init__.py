from discord import Object
#Discord Imports

from .guild_join import GuildJoin
from .guild_leave import GuildLeave
#Cog Imports

from utils import *
#Local Imports


class BotEvents(GuildJoin, GuildLeave):
    """ Bot Events Cog """

async def setup(bot: ExultBot):
    await bot.add_cog(BotEvents(bot), guilds=[Object(guild) for guild in bot.app_guilds])