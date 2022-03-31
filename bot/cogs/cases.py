from discord import app_commands, Interaction, User, Member, Guild, errors, Embed, TextChannel, Object
from discord.ext.commands import Bot, Cog

from utils import *
from database import *
from .moderation import ModLogging, noperms

class Cases(Cog, app_commands.Group, name="cases"):
    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__(name="cases", description="Handle Moderation Cases stored for this server")
    
    @app_commands.command(name="display", description="Display all cases for a given member")
    async def cases_display_slash(self, interaction: Interaction, member: Member=None):
        if interaction.user.guild_permissions.manage_messages:
            pass
        else:
            return await noperms(interaction)
        member = interaction.user if not member else member
        await ModLogging(interaction=interaction).get_cases_for_member(interaction.guild, member)
        
    clear = app_commands.Group(name="clear", description="Clear all cases for the server or a member")
    
    @clear.command(name="server", description="Clear all cases for the entire server")
    async def clear_cases_guild_slash(self, interaction: Interaction):
        if interaction.user.guild_permissions.manage_messages:
            pass
        else:
            return await noperms(interaction)
        embed = await ModLogging(interaction=interaction).clear_cases_for_guild()
        await interaction.response.send_message(embed=embed)
    
    @clear.command(name="member", description="Clear all cases for a specific member")
    async def clear_cases_member_slash(self, interaction: Interaction, member: Member):
        if interaction.user.guild_permissions.manage_messages:
            pass
        else:
            return await noperms(interaction)
        embed = await ModLogging(interaction=interaction).clear_cases_for_member(member)
        await interaction.response.send_message(embed=embed)
        
async def setup(bot: Bot):
    await bot.add_cog(Cases(bot), guilds=[Object(guild) for guild in bot.app_guilds])