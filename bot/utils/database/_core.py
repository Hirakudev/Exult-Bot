from typing import overload

from asyncpg import Pool
from discord import Client
#Regular Imports

from ..ic import ExultBot
#Local Imports

class CoreDB:
    @overload
    def __init__(self, bot: Client = None):
        ...

    def __init__(self, bot: ExultBot = None):
        self.bot: ExultBot = bot
        self.pool: Pool = bot.pool