import discord
from discord import app_commands
from discord.ext import commands

from typing import TYPE_CHECKING

from utils import *

if TYPE_CHECKING:
    from bot import SupportBot


class Info(commands.Cog):
    def __init__(self, bot: "SupportBot"):
        self.bot = bot
        self.panels = ["info", "rules", "support", "tickets", "verify"]

    infopanel = app_commands.Group(
        name="infopanel",
        description="Info panel command handler.",
        default_permissions=discord.Permissions(administrator=True),
    )

    @infopanel.command(name="send", description="Send an info panel!")
    async def send(
        self, itr: discord.Interaction, panel: str, channel: discord.TextChannel = None
    ):
        if panel not in self.panels:
            return await itr.response.send_message(
                f"`{panel}` is not a valid info panel!", ephemeral=True
            )
        channel = itr.channel if not channel else channel
        embed = discord.Embed(colour=0xFB5F5F, timestamp=discord.utils.utcnow())
        embed.set_thumbnail(url=itr.guild.icon.url)
        embed.set_footer(text="Last Updated")
        if panel == "rules":
            fields = [
                ["1・Discord ToS", "", False],
                ["2・NSFW Content", "", False],
                ["3・Respect & Harassment", "", False],
                ["4・Profanity & Hate Speech", "", False],
                ["5・Sensitive Topics", "", False],
                ["6・Staff Have The Final Say", "", True],
                ["7・Stay Safe & Have Fun", "", True],
            ]
            embed.title = "Exult Community Guidelines"
            embed.description = "It is important that you read these and follow them throughout your time in this server. If you breach these Rules, relevant action will be taken  by the Moderation Team."
        with open(f"utils/text/{panel}.txt") as f:
            lines = f.read()
            if panel != "tickets":
                lines = lines.split("\n\n")
                for count, field in enumerate(lines):
                    fields[count][1] = field
                    embed.add_field(
                        name=fields[count][0],
                        value=fields[count][1],
                        inline=fields[count][2],
                    )
            else:
                embed.description = lines
        file = discord.File(f"utils/images/{panel}.png")
        await channel.send(file=file, embed=embed)
        await itr.response.send_message("Sent!", ephemeral=True)


async def setup(bot: "SupportBot"):
    await bot.add_cog(Info(bot), guilds=[discord.Object(g) for g in bot.app_guilds])
