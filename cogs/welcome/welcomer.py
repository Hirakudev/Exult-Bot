import discord
from discord.ext import commands

from utils import *


class Welcomer(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = WelcomeDB(self.bot)

    @commands.Cog.listener("on_member_join")
    async def welcome_message(self, member: discord.Member):
        config = await self.db.get_config(member.guild.id)
        channel_id = config.get("channel_id")
        message: str = config.get("custom_message")

        if not channel_id:
            return
        if not message:
            msg = f"Welcome {member.mention} to {member.guild.name}!"
        else:
            if any(("{user}" in message, "{server}" in message)):
                msg = message.replace("{user}", member.mention)
                msg = msg.replace("{server}", member.guild.name)
            else:
                msg = message
        channel = self.bot.get_channel(channel_id)

        card = await WelcomeCard(self.bot).make_image(member)
        file = discord.File(fp=card, filename="welcome.png")

        await channel.send(content=msg, file=file)
