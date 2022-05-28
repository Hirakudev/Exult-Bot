import discord
from discord import app_commands

# Discord Imports

import random

# Regular Imports

from bot import ExultBot
from utils import *

# Local Imports


class Basic(ExultCog):
    @app_commands.command(name="roast", description="Get a roast!")
    async def roast_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        async with bot.session.get(
            "https://api.dagpi.xyz/data/roast",
            headers={"Authorization": self.dagpi_token},
        ) as data:
            data = await data.json()

        await followup.send(data["roast"])

    @app_commands.command(name="joke", description="Get a joke!")
    async def joke_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        async with bot.session.get(
            "https://api.dagpi.xyz/data/joke",
            headers={"Authorization": self.dagpi_token},
        ) as data:
            data = await data.json()

        await followup.send(data["joke"])

    @app_commands.command(name="fact", description="Get a fact!")
    async def fact_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        async with bot.session.get(
            "https://api.dagpi.xyz/data/fact",
            headers={"Authorization": self.dagpi_token},
        ) as data:
            data = await data.json()

        await followup.send(data["fact"])

    pickup = app_commands.Group(name="pickup", description="Get a pickup line!")

    @pickup.command(name="line", description="Get a pickup line!")
    async def pickup_line_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        async with bot.session.get(
            "https://api.dagpi.xyz/data/pickupline",
            headers={"Authorization": self.dagpi_token},
        ) as data:
            data = await data.json()

        await followup.send(data["joke"])

    @app_commands.command(name="8ball", description="Get a 8ball response!")
    async def eight_ball_slash(self, itr: discord.Interaction, query: str):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        async with bot.session.get(
            "https://api.dagpi.xyz/data/8ball",
            headers={"Authorization": self.dagpi_token},
        ) as data:
            data = await data.json()

        await followup.send(data["response"])

    @app_commands.command(name="yomama", description="Get a Yo-Mama joke!")
    async def yo_mama_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        async with bot.session.get(
            "https://api.dagpi.xyz/data/yomama",
            headers={"Authorization": self.dagpi_token},
        ) as data:
            data = await data.json()

        await followup.send(data["description"])

    @app_commands.command(name="meme", description="Get a random meme!")
    async def meme_slash(self, itr: discord.Interaction):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        subreddit = random.choice(("memes", "dankmemes"))
        async with bot.session.get(
            f"https://reddit.com/r/{subreddit}/random.json"
        ) as data:
            data = await data.json()
            post = data[0]["data"]["children"][0]["data"]

        embed = embed_builder(title=post["title"], image=post["url_overridden_by_dest"])
        await followup.send(embed=embed)
