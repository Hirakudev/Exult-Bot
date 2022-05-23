import discord
from discord import app_commands
from discord.ext import commands

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
