from typing import *
from discord import *

from utils.embeds import ErrorEmbed



class ErrorButtons(ui.View):
    def __init__(self, timeout = 180, descs:Dict[str, str] = ..., embed:ErrorEmbed = ..., message:Message = ..., **kwargs):
        super().__init__(timeout = timeout)
        self.descs = descs
        self.embed = embed
        self.message = message


    @ui.button(
        label = "preview",
        custom_id = "errorbuttons.preview",
        style = ButtonStyle.blurple,
    )
    async def preview(self, interaction:Interaction, button:ui.Button):
        self.embed.description = self.descs["preview"]
        await interaction.response.defer()
        await self.message.edit(embed = self.embed)
        button.disabled = True
        for child in self.children:
            if child.custom_id != "errorbuttons.full":
                child.disabled = False
        ...

    @ui.button(
        label = "full",
        custom_id = "errorbuttons.full",
        style = ButtonStyle.blurple,
    )
    async def full(self, interaction:Interaction, button:ui.Button):
        self.embed.description = self.descs["full"]
        await interaction.response.defer()
        await self.message.edit(embed = self.embed)
        button.disabled = True
        for child in self.children:
            if child.custom_id != "errorbuttons.preview":
                child.disabled = False
        ...
    


        