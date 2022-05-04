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

    XP_PER_MESSAGE = 15
    MULTIPLIER = 1

    def formula(self, lvl):
        return (
            round(
                (pi ** -(e ** (1 / factorial(3) * gamma(pi)) / 10))
                * (log(e ** (lvl * 2) ** 1.078) * cosh(pi))
                * 10
                / 100
            )
            * 100
        )

    async def add_xp(self, user: discord.Member, message: discord.Message):
        xp = self.XP_PER_MESSAGE * self.MULTIPLIER
        user_xp = await LevellingDB(self.bot).add_xp(
            guild_id=user.guild.id, user_id=user.id, xp=xp
        )
        if not user_xp:
            return

        level = user_xp.get("level")
        xp = user_xp.get("xp")

        def get_msg(user, level):
            return f"{user.mention} just levelled up to level {level}!"

        role = None

        if all((level != 0, xp >= self.formula(level))):
            user_xp = await LevellingDB(self.bot).level_up(
                guild_id=user.guild.id, user_id=user.id
            )
            rewards = await LevellingDB(self.bot).get_rewards(guild_id=message.guild.id)
            for key, value in rewards.items():
                if user_xp.get("level") == key:
                    role = message.guild.get_role(value)
                    break

            msg = await LevellingDB(self.bot).get_custom_message(guild_id=user.guild.id)
            if msg:
                msg = msg.replace("{user}", user.mention).replace(
                    "{level}", user_xp.get("level")
                )
            if role:
                await message.author.add_roles(role)
                msg = f"{user.mention} just levelled up to level {user_xp.get('level')} and has been rewarded with the `{role.name}` role!"
            if not msg:
                msg = get_msg(user, user_xp.get("level"))

            channel_id = await LevellingDB(self.bot).get_custom_channel(
                guild_id=user.guild.id
            )
            channel = user.guild.get_channel(channel_id)
            if not channel:
                channel = message.channel

            await channel.send(msg)
