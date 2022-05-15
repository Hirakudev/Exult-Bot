import discord
from discord import app_commands
from discord.ext import commands

from bot import ExultBot
from utils import *


class CustomCommands(commands.Cog):

    custom_commands = app_commands.Group(
        name="cc", description="Custom Command handler."
    )

    @custom_commands.command(name="create", description="Create a custom command!")
    async def custom_command_create_slash(
        self, itr: discord.Interaction, name: str, response: str
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup = itr.followup

        cmd = bot.tree.get_command(name)
        if not cmd:
            gcmd = bot.tree.get_command(name, guild=itr.guild)
            if gcmd:
                return
        else:
            return

        code = f"""
        @bot.tree.command(name=f'{name}')
        @guilds({itr.guild.id})
        async def cc_create(itr):
            await itr.response.send_message('{response}')
        await bot.tree.sync(guild={itr.guild})
        """
        exec(code)
        await CustomCommandsDB(bot).add_command(
            guild_id=itr.guild.id, name=name, response=response, added_by=itr.user.id
        )
        embed = embed_builder(
            name="Success!", description=f"Successfully created command `{name}`!"
        )
        await followup.send(embed=embed)

    @custom_commands.command(name="edit", description="Edit a custom command!")
    async def custom_command_edit_slash(
        self, itr: discord.Interaction, name: str, new_response: str
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup = itr.followup

        gcmd = bot.tree.get_command(name, guild=itr.guild)
        if not gcmd:
            return

        code = f"""
        @bot.tree.command(name=f'{name}', description=f'Custom command created by {itr.user}!')
        @guilds({itr.guild.id})
        async def cc_create(itr):
            await itr.response.send_message('{new_response}')
        await bot.tree.sync(guild={itr.guild})
        """
        exec(code)
        await CustomCommandsDB(bot).edit_response(
            guild_id=itr.guild.id, name=name, new_response=new_response
        )
        embed = embed_builder(
            name="Success!", description=f"Successfully edited command `{name}`!"
        )
        await followup.send(embed=embed)

    @custom_commands.command(name="delete", description="Delete a custom command!")
    async def custom_command_edit_slash(self, itr: discord.Interaction, name: str):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup = itr.followup

        gcmd = bot.tree.get_command(name, guild=itr.guild)
        if not gcmd:
            return

        code = f"""
        bot.tree.remove_command(f'{name}', guild={itr.guild})
        await bot.tree.sync(guild={itr.guild})
        """
        exec(code)
        await CustomCommandsDB(bot).delete_command(guild_id=itr.guild.id, name=name)
        embed = embed_builder(
            name="Success!", description=f"Successfully deleted command `{name}`!"
        )
        await followup.send(embed=embed)
