import discord
from discord import app_commands
from discord.ext import commands

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bot import SupportBot


class BoolTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, itr: discord.Interaction, value: str):
        if value == "true":
            return True
        return False


async def app_guilds_autocomplete(itr: discord.Interaction, current: str):
    return [
        app_commands.Choice(name="true", value="true"),
        app_commands.Choice(name="false", value="false"),
    ]


class Sync(commands.Cog):
    def __init__(self, bot: "SupportBot"):
        self.bot = bot

    @app_commands.command(name="sync", description="Sync app commands!")
    @app_commands.autocomplete(dev_guilds=app_guilds_autocomplete)
    async def sync_slash(
        self,
        itr: discord.Interaction,
        dev_guilds: app_commands.Transform[bool, BoolTransformer] = None,
    ):
        await itr.response.defer()
        if dev_guilds:
            commands, guilds = 0, 0
            for guild in self.bot.app_guilds:
                g = discord.Object(guild)
                x = await self.bot.tree.sync(guild=g)
                commands += len(x)
                guilds += 1
            msg = f"Synced {int(commands/guilds)} commands across {guilds} guilds."
        else:
            x = await self.bot.tree.sync()
            msg = f"Synced {len(x)} commands globally."
        await itr.followup.send(msg)


async def setup(bot: "SupportBot"):
    await bot.add_cog(Sync(bot), guilds=[discord.Object(g) for g in bot.app_guilds])
