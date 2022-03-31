from discord import app_commands, Interaction, Object, File
from discord.ext.commands import Cog, Bot

from typing import Union

from utils.tools import embed_builder

class Utility(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        
    emoji = app_commands.Group(name="emoji", description="Carry out various emoji-related tasks")
    
    @emoji.command(name="add", description="Add an emoji to your server")
    @app_commands.describe(name="The name you want to give your new emoji", link="Link to the image/gif for the emoji you want to add")
    async def emoji_add_slash(self, interaction: Interaction, name: str, link: str):
        async with self.bot.session.get(link) as req:
            data = await req.read()
        emoji = await interaction.guild.create_custom_emoji(name=name, image=data)
        embed = embed_builder(description=f"Successfully added {emoji}!")
        await interaction.response.send_message(embed=embed)
        
    @emoji.command(name="edit", description="Edit the name of an emoji in your server")
    @app_commands.describe(emoji_id="The ID of the emoji which you want to edit the name of", new_name="The new name you want to assign this emoji")
    async def emoji_edit_slash(self, interaction: Interaction, emoji_id: str, new_name: str):
        emoji = await interaction.guild.fetch_emoji(int(emoji_id))
        emoji = await emoji.edit(name=new_name.replace(" ", "_"))
        embed = embed_builder(description=f"Successfully edited the name for {emoji} to `{emoji.name}`")
        await interaction.response.send_message(embed=embed)
        
    @emoji.command(name="delete", description="Delete an emoji in your server")
    @app_commands.describe(emoji_id="The ID of the emoji which you want to delete")
    async def emoji_delete_slash(self, interaction: Interaction, emoji_id: str):
        emoji = await interaction.guild.fetch_emoji(int(emoji_id))
        embed = embed_builder(description=f"Successfully deleted `{emoji.name}`")
        await emoji.delete()
        await interaction.response.send_message(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(Utility(bot), guilds=[Object(guild) for guild in bot.app_guilds])