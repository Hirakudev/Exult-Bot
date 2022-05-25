import discord
from discord import app_commands
from discord.ext import commands
from jishaku.functools import executor_function

import asyncio
import functools

from bot import ExultBot
from utils import *


class EmotionCommands(commands.Cog):
    def __init__(self, bot: ExultBot):
        self.bot = bot

    @app_commands.command(name="kiss", description="Give someone a kiss!")
    async def kiss_slash(self, itr: KnownInteraction[ExultBot], member: discord.Member):
        await itr.response.defer()
        embed = await self.emotion_client.action(
            count=0, action="kiss", person=itr.user, target=member
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="hug", description="Give someone a hug!")
    async def hug_slash(self, itr: KnownInteraction[ExultBot], member: discord.Member):
        await itr.response.defer()
        embed = await self.emotion_client.action(
            count=0, action="hug", person=itr.user, target=member
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="pat", description="Pat someone!")
    async def pat_slash(self, itr: KnownInteraction[ExultBot], member: discord.Member):
        await itr.response.defer()
        embed = await self.emotion_client.action(
            count=0, action="pat", person=itr.user, target=member
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="slap", description="Slap someone!")
    async def slap_slash(self, itr: KnownInteraction[ExultBot], member: discord.Member):
        await itr.response.defer()
        embed = await self.emotion_client.action(
            count=0, action="slap", person=itr.user, target=member
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="poke", description="Poke someone!")
    async def poke_slash(self, itr: KnownInteraction[ExultBot], member: discord.Member):
        await itr.response.defer()
        embed = await self.emotion_client.action(
            count=0, action="poke", person=itr.user, target=member
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="cuddle", description="Cuddle someone!")
    async def cuddle_slash(
        self, itr: KnownInteraction[ExultBot], member: discord.Member
    ):
        await itr.response.defer()
        embed = await self.emotion_client.action(
            count=0, action="cuddle", person=itr.user, target=member
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="lick", description="Lick someone!")
    async def lick_slash(self, itr: KnownInteraction[ExultBot], member: discord.Member):
        await itr.response.defer()
        embed = await self.emotion_client.action(
            count=0, action="lick", person=itr.user, target=member
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="bite", description="Bite someone!")
    async def bite_slash(self, itr: KnownInteraction[ExultBot], member: discord.Member):
        await itr.response.defer()
        embed = await self.emotion_client.action(
            count=0, action="bite", person=itr.user, target=member
        )
        await itr.edit_original_message(content=None, embed=embed)

    @app_commands.command(name="marry", description="Get married!")
    async def marry_slash(
        self, itr: KnownInteraction[ExultBot], partner: discord.Member
    ):
        data = await self.emotion_client.marry(itr, person=itr.user, target=partner)
        is_married = await self.db.get_marriage(itr.user, partner)
        if is_married:
            return await itr.response.send_message(
                content="You two are already married!", ephemeral=True
            )
        await itr.response.defer()
        view = MarriageView(self.emotion_client, itr.user, partner)
        view.message = await itr.followup.send(
            content=f"{itr.user.mention} has proposed to {partner.mention}!", view=view
        )
        view.img_data = data

    @app_commands.command(name="divorce", description="Divorce your marriage!")
    async def divorce_slash(
        self, itr: KnownInteraction[ExultBot], partner: discord.Member
    ):
        is_married = await self.db.get_marriage(itr.user, partner)
        if not is_married:
            return await itr.response.send_message(
                "You aren't married to this person!", ephemeral=True
            )
        await itr.response.defer()
        await self.db.divorce(itr.user, partner)
        await itr.followup.send(
            f"You just divorced {partner.mention}. Hope you're happy with your decision. 😔💔"
        )
