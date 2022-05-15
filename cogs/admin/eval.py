from click import Choice
import discord
from discord import app_commands
from discord.ext import commands

from bot import ExultBot
from utils import *


class ReturnEphTransformer(app_commands.Transformer):
    @classmethod
    async def transform(cls, itr: discord.Interaction, value: str):
        if value == "true":
            return True
        return False


async def return_eph_autocomplete(itr: discord.Interaction, current: str):
    return [
        app_commands.Choice(name="true", value="true"),
        app_commands.Choice(name="false", value="false"),
    ]


class Eval(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot = bot

    @app_commands.command(name="sql", description="Run some SQL!")
    @app_commands.autocomplete(return_eph=return_eph_autocomplete)
    async def sql_slash(
        self,
        itr: discord.Interaction,
        return_eph: app_commands.Transform[bool, ReturnEphTransformer] = None,
    ):
        if await self.bot.is_owner(itr.user) or itr.user.id in [
            957437570546012240,
            343019667511574528,
            689564113415962717,
            349373972103561218,
            857103603130302514,
        ]:
            eph = False if return_eph is None else return_eph
            last_sql = await self.bot.pool.fetchval("SELECT last_sql FROM temp_data")
            await itr.response.send_modal(SQLModal(self.bot, eph, last_sql))
        else:
            await itr.response.send_message(
                f"You have to own the bot to run this command!"
            )

    @app_commands.command(name="eval", description="Eval some code!")
    @app_commands.autocomplete(return_eph=return_eph_autocomplete)
    async def eval_slash(
        self,
        itr: discord.Interaction,
        return_eph: app_commands.Transform[bool, ReturnEphTransformer] = None,
    ):
        if await self.bot.is_owner(itr.user):
            eph = False if return_eph is None else return_eph
            last_eval = await self.bot.pool.fetchval("SELECT last_eval FROM temp_data")
            modal = EvalModal(self.bot, eph, last_eval)
            await itr.response.send_modal(modal)
        else:
            await itr.response.send_message(
                f"You have to own the bot to run this command!"
            )
