import discord

# Discord Imports

from typing import overload
import asyncpg

# Regular Imports

from bot import ExultBot

# Local Imports


class CoreDB:
    @overload
    def __init__(self, bot: discord.Client = None):
        ...

    def __init__(self, bot: ExultBot = None):
        self.bot: ExultBot = bot
        self.pool: asyncpg.Pool = bot.pool
