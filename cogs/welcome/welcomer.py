import discord
from discord.ext import commands

from bot import ExultBot
from utils import *


class Welcomer(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot = bot

    @commands.Cog.listener("on_member_join")
    async def welcome_message(self, member: discord.Member):
        config = await WelcomeDB(self.bot).get_config(guild_id=member.guild.id)
        channel_id = config.get("channel_id")
        message: str = config.get("custom_message")

        if not channel_id:
            return
        if not message:
            msg = f"Welcome {member.mention} to {member.guild.name}!"
        else:
            if "{user}" in message:
                msg = message.replace("{user}", member.mention)
            else:
                msg = message
        channel = self.bot.get_channel(channel_id)

        card = await WelcomeCard(self.bot).make_image(member)
        file = discord.File(fp=card, filename="welcome.png")

        await channel.send(content=msg, file=file)
