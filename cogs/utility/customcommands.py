import discord
from discord import app_commands
from discord.ext import commands, tasks

from bot import ExultBot
from utils import *


class CustomCommands(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot = bot
        self.db = CustomCommandsDB(bot)
        self.utils = CommandUtils(bot)

    async def cog_load(self):
        commands = await self.db.get_commands()
        if commands:
            for cmd in commands:
                self.utils.cache_command(cmd)

    cc_group = app_commands.Group(
        name="custom-command",
        description="Custom Command Handler!",
        default_permissions=discord.Permissions(manage_guild=True),
    )

    @commands.Cog.listener("on_upload_commands")
    async def upload_commands_listener(self):
        await self.utils.upload_db()

    @commands.Cog.listener("on_message")
    async def custom_command_listener(self, msg: discord.Message):
        if self.utils.checks(msg):
            if msg.content.startswith("t!"):
                resp = msg.content.split("t!")[1]
                try:
                    if resp in self.utils.cache[msg.guild.id]:
                        await msg.channel.send(
                            self.utils.cache[msg.guild.id][resp]["command_text"]
                        )
                except KeyError:
                    return

    @commands.Cog.listener()
    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if ctx.command is None:
            return
        pass

    @cc_group.command(name="create", description="Create a custom command!")
    async def cc_create_slash(self, itr: KnownInteraction[ExultBot]):
        modal = CreateCommandModal(self.utils)
        await itr.response.send_modal(modal)

    @cc_group.command(name="get", description="View info on a custom command!")
    async def cc_get_slash(self, itr: KnownInteraction[ExultBot], command_name: str):
        await itr.response.defer()
        cmd = await self.utils.get_command(itr, command_name)
        if cmd:
            return await itr.edit_original_message(
                content=f"Command found! Try it with `t!{command_name}`!"
            )
        return await itr.edit_original_message(
            content=f"`{command_name}` does not exist!\nYou can create it with `/custom-command create`!"
        )
