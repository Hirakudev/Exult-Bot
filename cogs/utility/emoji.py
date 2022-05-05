import discord
from discord import app_commands
from discord.ext import commands

from bot import ExultBot
from utils import *


class Emojis(ExultCog):

    emojis_group = app_commands.Group(
        name="emoji", description="Configure emojis in the server!"
    )

    @emojis_group.command(name="add", description="Add an emoji to the server!")
    @app_commands.describe(
        name="The name that you want to give the emoji.",
        link="The direct link to the image that you want the emoji to be.",
    )
    async def emoji_add_slash(self, itr: discord.Interaction, name: str, link: str):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        async with bot.request("GET", link) as req:
            data = await req.read()
        emoji = await itr.guild.create_custom_emoji(name=name, image=data)
        embed = embed_builder(description=f"Successfully created {emoji}!")
        await followup.send(embed=embed)

    @emojis_group.command(name="delete", description="Delete an emoji from the server!")
    @app_commands.describe(name="The name of the emoji you want to delete.")
    async def emoji_delete_slash(self, itr: discord.Interaction, name: str):
        await itr.response.defer()
        followup: discord.Webhook = itr.followup

        emoji = [e for e in itr.guild.emojis if e.name.lower() == name.lower()][0]
        await emoji.delete(reason=f"Deleted by user: {itr.user}")
        embed = embed_builder(description=f"Successfully deleted `{name}`!")
        await followup.send(embed=embed)

    @emoji_delete_slash.autocomplete("name")
    async def emoji_delete_slash_autocomplete(
        self, itr: discord.Interaction, current: str
    ):
        emojis = [e.name for e in itr.guild.emojis]
        return [
            app_commands.Choice(name=emoji, value=emoji)
            for emoji in emojis
            if current.lower() in emoji.lower()
        ]
