import discord

# Discord Imports

from math import *

# Regular Imports

from bot import ExultBot
from utils import *

# Local Imports


class LevellingClient:
    def __init__(self, bot: ExultBot):
        self.bot: ExultBot = bot
        self.db = LevellingDB(self.bot)

    XP_PER_MESSAGE = 15
    MULTIPLIER = 1

    def formula(self, lvl, xp):
        return 5 * (lvl ^ 2) + (50 * lvl) + 100 - xp

    def get_msg(self, user, level):
        return f"{user.mention} just levelled up to level {level}!"

    async def level_up(self, user: discord.Member, message: discord.Message):
        config = await self.db.get_config(user.guild.id)
        rewards = await self.db.get_rewards(user.guild.id)
        profile = await self.db.add_level(user.guild.id, user.id)
        msg = "there's no msg lol"
        if rewards:
            _roles_added = []
            for reward in rewards:
                if profile.get("level") == reward.get("level"):
                    role = user.guild.get_role(reward.get("role"))
                    _roles_added.append(role)

            msg = config.get("levelup_message")
            if msg:
                msg = msg.replace("{user}", user.mention).replace(
                    "{level}", str(profile.get("level"))
                )
            if _roles_added:
                roles_added = []
                for role in _roles_added:
                    try:
                        await user.add_roles(role)
                        roles_added.append(role)
                    except discord.Forbidden:
                        pass
        else:
            msg = self.get_msg(user, profile.get("level"))

        channel_id = config.get("announce_channel")
        channel = user.guild.get_channel(channel_id)
        if not channel:
            channel = message.channel
        try:

            await channel.send(msg)
        
        except discord.Forbidden:
            pass

    async def add_xp(self, user: discord.Member, message: discord.Message):
        xp = self.XP_PER_MESSAGE * self.MULTIPLIER
        profile = await self.db.add_xp(user.guild.id, user.id, xp)

        level = profile.get("level")
        xp = profile.get("xp")

        if all((level != 0, self.formula(level, xp) <= 0)):
            await self.level_up(user, message)
