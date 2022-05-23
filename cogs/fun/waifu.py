import discord
from discord import app_commands
from discord.ext import commands

import random

from bot import ExultBot
from utils import *


class Waifu(commands.Cog):
    """Waifu Cog"""

    def __init__(self, bot: ExultBot):
        self.bot = bot

    async def cog_load(self):
        endpoints = await self.bot.wf.endpoints()
        self.versatile_tags = ["andeh"] + endpoints.get("versatile")
        self.nsfw_tags = endpoints.get("nsfw") + endpoints.get("versatile")

    andeh = ["https://i.imgur.com/cZvj1Ws.png", "https://i.imgur.com/Mlz5Iri.png"]

    def waifu_embed(self, user: discord.Member, tag: str, image: str):
        name = (
            f" {tag.replace('waifu', 'random').capitalize()} "
            if tag != "andeh"
            else " "
        )
        embed = embed_builder(
            author=[
                self.bot.try_asset(user.avatar, user.default_avatar),
                f"{user.name.capitalize()}'s{name}Waifu",
            ],
            image=image,
        )
        return embed

    waifu = app_commands.Group(name="waifu", description=f"Get images of waifus!")

    @waifu.command(name="sfw", description="Get an SFW Waifu Image")
    async def waifu_sfw_slash(self, itr: discord.Interaction, tag: str):
        if tag not in self.versatile_tags:
            return await itr.response.send_message(
                f"`{tag}` is not a valid tag! Try again with one of the tags in the autocomplete menu."
            )
        await itr.response.defer()
        image = (
            random.choice(self.andeh)
            if tag == "andeh"
            else await self.bot.wf.random(selected_tags=[tag], is_nsfw=False)
        )
        embed = self.waifu_embed(itr.user, tag, image)
        await itr.followup.send(embed=embed)

    @waifu.command(name="nsfw", description="Get an NSFW Waifu Image")
    async def waifu_nsfw_slash(self, itr: discord.Interaction, tag: str):
        if not itr.channel.nsfw:
            return await itr.response.send_message(
                f"This is not an nsfw channel!", ephemeral=True
            )
        elif tag not in self.versatile_tags or tag not in self.nsfw_tags:
            await itr.response.send_message(
                f"`{tag}` is not a valid tag! Try again with one of the tags in the autocomplete menu."
            )
        await itr.response.defer()
        image = await self.bot.wf.random(selected_tags=[tag], is_nsfw=True)
        embed = self.waifu_embed(itr.user, tag, image)
        await itr.followup.send(embed=embed)

    @waifu_sfw_slash.autocomplete("tag")
    async def waifu_sfw_autocomplete(self, itr: discord.Interaction, current: str):
        versatile_tags = [
            w.replace("-", " ").replace("waifu", "random").title()
            for w in self.versatile_tags
        ]
        num = 0
        choices = []
        for w in versatile_tags:
            choices.append((versatile_tags[num], self.versatile_tags[num]))
            num += 1
        return [
            app_commands.Choice(name=c[0], value=c[1])
            for c in choices
            if current in c[0] or current in c[1]
        ]

    @waifu_nsfw_slash.autocomplete("tag")
    async def waifu_nsfw_autocomplete(self, itr: discord.Interaction, current: str):
        nsfw_tags = [
            w.replace("-", " ").replace("waifu", "random").title()
            for w in self.nsfw_tags
            if w != "andeh"
        ]
        choices = []
        num = 0
        for w in nsfw_tags:
            choices.append((nsfw_tags[num], self.nsfw_tags[num]))
            num += 1
        return [
            app_commands.Choice(name=c[0], value=c[1])
            for c in choices
            if current in c[0] or current in c[1]
        ]
