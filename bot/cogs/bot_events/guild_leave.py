import discord
from discord.ext import commands

from utils import *

class GuildLeave(ExultCog):

    @commands.Cog.listener(name="on_guild_remove")
    async def remove_guild(self, guild: discord.Guild):
        await GuildsDB(self.bot).remove_guild(guild.id)

        users = len([user for user in guild.members if not user.bot])
        bots = len([user for user in guild.members if user.bot])
        total = len(guild.members)

        guilds = len(self.bot.guilds)
        _users = len(self.bot.users)

        embed = embed_builder(
            title=f"Removed from guild",
            description=f"""
                         **Name:** {guild.name}
                         **Owner:** {guild.owner} | `{guild.owner.id}`
                         **Total Users:**
                         👨 {users} | 🤖 {bots} | 💫 {total}""",
            author=[self.bot.try_asset(self.bot.user.avatar), f"Guilds: {guilds} | Users: {_users}"],
            thumbnail=self.bot.try_asset(guild.icon),
            footer=f"ID: {guild.id}"
        )
        await self.bot.bot_logs.send(embed=embed)