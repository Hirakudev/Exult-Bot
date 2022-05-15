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

    sfw_tags = [
        "maid",
        "marin-kitagawa",
        "mori-calliope",
        "oppai",
        "raiden-shogun",
        "selfies",
        "uniform",
        "waifu",
    ]
    nsfw_tags = ["ass", "hentai", "milf", "oral", "paizuri" "ecchi", "ero"] + sfw_tags

    def waifu_embed(self, user: discord.Member, tag: str, image: str):
        embed = embed_builder(
            author=[
                self.bot.try_asset(user.avatar, user.default_avatar),
                f"{user.name.capitalize()}'s {tag.replace('waifu', 'random').capitalize()} Waifu",
            ],
            image=image,
        )
        return embed

    waifu = app_commands.Group(name="waifu", description=f"Get images of waifus!")

    @waifu.command(name="sfw", description="Get an SFW Waifu Image")
    async def waifu_sfw_slash(self, itr: discord.Interaction, tag: str):
        if tag not in self.sfw_tags:
            return await itr.response.send_message(
                f"`{tag}` is not a valid tag! Try again with one of the tags in the autocomplete menu."
            )
        await itr.response.defer()
        image = await self.bot.wf.random(selected_tags=[tag], is_nsfw=False)
        embed = self.waifu_embed(itr.user, tag, image)
        await itr.followup.send(embed=embed)

    @waifu.command(name="nsfw", description="Get an NSFW Waifu Image")
    async def waifu_nsfw_slash(self, itr: discord.Interaction, tag: str):
        if not itr.channel.nsfw:
            return await itr.response.send_message(
                f"This is not an nsfw channel!", ephemeral=True
            )
        elif tag not in self.sfw_tags or tag not in self.nsfw_tags:
            await itr.response.send_message(
                f"`{tag}` is not a valid tag! Try again with one of the tags in the autocomplete menu."
            )
        await itr.response.defer()
        image = await self.bot.wf.random(selected_tags=[tag], is_nsfw=True)
        embed = self.waifu_embed(itr.user, tag, image)
        await itr.followup.send(embed=embed)

    @waifu_sfw_slash.autocomplete("tag")
    async def waifu_sfw_autocomplete(self, itr: discord.Interaction, current: str):
        sfw_tags = [
            w.replace("-", " ").replace("waifu", "random").title()
            for w in self.sfw_tags
        ]
        num = 0
        choices = []
        for w in sfw_tags:
            choices.append((sfw_tags[num], self.sfw_tags[num]))
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
