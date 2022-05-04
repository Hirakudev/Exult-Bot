import discord
from discord import app_commands
# Discord Imports

from bot import ExultBot
from utils import *
from ._fun_helper import FunHelper
# Local Imports

class WTP(ExultCog):

    @app_commands.command(name="wtp", description="Who's that pokemon?")
    async def wtp_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        async with bot.session.get("https://api.dagpi.xyz/data/wtp", headers={"Authorization": FunHelper.dagpi_token}) as data:
            data = await data.json()

            data = {
                "name": data["Data"]["name"],
                "question": data["question"],
                "answer": data["answer"],
                "types": ", ".join(data["Data"]["Type"]),
                "lives": 3
            }
        
        embed = embed_builder(title="Who's that pokemon?", description=f"Type(s): {data['types']}", image=data["question"], 
                            fields=[["Guesses Remaining:", str(data["lives"]), True]])
        view = PokemonGuess(data)
        await followup.send(embed=embed, view=view)