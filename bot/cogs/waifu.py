from discord import app_commands, Interaction, Object
from discord.ext.commands import Bot, Cog

from typing import List

from utils import *
from database import *

class Waifu:
    
    @staticmethod
    async def waifuim_request(interaction:Interaction, is_nsfw: bool, selected_tags: List[str], excluded_tags: List[str]=None):
        image = await interaction.client.wf.random(selected_tags=selected_tags, excluded_tags=excluded_tags, is_nsfw=is_nsfw)
        embed = embed_builder(author=[interaction.user.display_avatar.url, f"{interaction.user.name}'s Waifu"],
                              image=image)
        return embed
    
    @staticmethod
    async def not_nsfw_channel(interaction: Interaction):
        embed = embed_builder(author=[interaction.user.display_avatar.url, "Horny Jail for you!"], description=f"You can't use nsfw commands in sfw channels!")
        return embed

class waifu(Cog, app_commands.Group, name="waifu"):
    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__()
    
    sfw = app_commands.Group(name="sfw", description="SFW Waifu Pics")
    nsfw = app_commands.Group(name="nsfw", description="NSFW Waifu Pics")
    
    @sfw.command(name="waifu", description="Send a Waifu pic")
    async def waifu_waifu(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, False, ["waifu"])
        await interaction.response.send_message(embed=embed)
            
    @sfw.command(name="uniform", description="Send a Uniform Waifu pic")
    async def waifu_uniform(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, False, ["uniform"])
        await interaction.response.send_message(embed=embed)
        
    @sfw.command(name="maid", description="Send a Maid Waifu pic")
    async def waifu_maid(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, False, ["maid"])
        await interaction.response.send_message(embed=embed)
        
    @sfw.command(name="marin", description="Send a Marin-Kitagawa Waifu pic")
    async def waifu_marin(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, False, ["marin-kitagawa"])
        await interaction.response.send_message(embed=embed)
        
    @sfw.command(name="mori", description="Send a Mori-calliope Waifu pic")
    async def waifu_mori(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, False, ["mori-calliope"])
        await interaction.response.send_message(embed=embed)
        
    @sfw.command(name="raiden", description="Send a Raiden-Shogun Waifu pic")
    async def waifu_raiden(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, False, ["raiden-shogun"])
        await interaction.response.send_message(embed=embed)
        
    @sfw.command(name="oppai", description="Send a Oppai Waifu pic")
    async def waifu_maid(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, False, ["oppai"])
        await interaction.response.send_message(embed=embed)
        
    @nsfw.command(name="ass", description="Send a Ass Waifu pic")
    async def waifu_ass(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, True, ["ass"]) if interaction.channel.nsfw \
                else await Waifu.not_nsfw_channel(interaction)
        await interaction.response.send_message(embed=embed)
        
    @nsfw.command(name="selfie", description="Send a Selfie Waifu pic")
    async def waifu_selfie(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, True, ["selfies"]) if interaction.channel.nsfw \
                else await Waifu.not_nsfw_channel(interaction)
        await interaction.response.send_message(embed=embed)
        
    @nsfw.command(name="hentai", description="Send a Hentai Waifu pic")
    async def waifu_hentai(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, True, ["hentai"]) if interaction.channel.nsfw \
                else await Waifu.not_nsfw_channel(interaction)
        await interaction.response.send_message(embed=embed)
        
    @nsfw.command(name="milf", description="Send a Milf Waifu pic")
    async def waifu_milf(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, True, ["milf"]) if interaction.channel.nsfw \
                else await Waifu.not_nsfw_channel(interaction)
        await interaction.response.send_message(embed=embed)
        
    @nsfw.command(name="oral", description="Send a Oral Waifu pic")
    async def waifu_oral(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, True, ["oral"]) if interaction.channel.nsfw \
                else await Waifu.not_nsfw_channel(interaction)
        await interaction.response.send_message(embed=embed)
        
    @nsfw.command(name="paizuri", description="Send a Paizuri Waifu pic")
    async def waifu_paizuri(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, True, ["paizuri"]) if interaction.channel.nsfw \
                else await Waifu.not_nsfw_channel(interaction)
        await interaction.response.send_message(embed=embed)
        
    @nsfw.command(name="ecchi", description="Send a Ecchi Waifu pic")
    async def waifu_ecchi(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, True, ["ecchi"]) if interaction.channel.nsfw \
                else await Waifu.not_nsfw_channel(interaction)
        await interaction.response.send_message(embed=embed)
        
    @nsfw.command(name="ero", description="Send a Ero Waifu pic")
    async def waifu_ero(self, interaction: Interaction):
        embed = await Waifu.waifuim_request(interaction, True, ["ero"]) if interaction.channel.nsfw \
                else await Waifu.not_nsfw_channel(interaction)
        await interaction.response.send_message(embed=embed)

async def setup(bot: Bot):
    await bot.add_cog(waifu(bot), guilds=[Object(guild) for guild in bot.app_guilds])