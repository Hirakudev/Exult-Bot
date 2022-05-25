import discord

import asyncio

from ..helpers import embed_builder
from ..database import EmotionDB


class MarriageView(discord.ui.View):
    def __init__(
        self,
        emotion_client,
        user_one: discord.Member,
        user_two: discord.Member,
    ):
        self.emotion_client = emotion_client
        self.user_one = user_one
        self.user_two = user_two
        self.img_data = None
        super().__init__(timeout=60)

    async def on_timeout(self):
        await self.message.edit(
            content=self.message.content
            + f"\n{self.user_two.mention} took too long to respond 😔",
            view=None,
        )

    async def interaction_check(self, itr: discord.Interaction):
        if itr.user.id != self.user_two.id:
            await itr.response.send_message(
                "This proposal isn't for you!", ephemeral=True
            )
            return False
        return True

    @discord.ui.button(style=discord.ButtonStyle.green, emoji="💍", disabled=False)
    async def accept_proposal(
        self, itr: discord.Interaction, button: discord.ui.Button
    ):
        await itr.response.send_message(
            content=f"{self.user_two.mention} accepted the proposal from {self.user_one.mention}!",
            embed=self.img_data["embed"],
            file=self.img_data["file"],
        )
        await self.message.edit(view=None)
        await EmotionDB(itr.client).marry(self.user_one, self.user_two)
        self.stop()

    @discord.ui.button(style=discord.ButtonStyle.gray, emoji="❌", disabled=False)
    async def deny_proposal(self, itr: discord.Interaction, button: discord.ui.Button):
        await self.message.edit(view=None)
        await itr.response.send_message(
            f"{self.user_two.mention} has denied the proposal 😔💔"
        )
        self.stop()
