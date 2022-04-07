from asyncpg import Pool
#Regular Imports

from ..ic import ExultBot
#Local Imports

class CoreDB:
    def __init__(self, bot: ExultBot):
        self.bot: ExultBot = bot
        self.pool: Pool = bot.pool