from discord import Interaction, Member, Webhook
from discord.app_commands import command, describe
from discord.utils import format_dt, utcnow
#Discord Imports

from utils import *
#Local Imports

class Core(ExultCog):

    @command(name="ban", description="Ban a member from the server.")
    @describe(member="A member you want to ban.", reason="The reason for the ban")
    @permissions(ban_members=True)
    async def ban_slash(self, itr: Interaction, member: Member, reason: str="Unspecified"):
        bot: ExultBot = itr.client
        await itr.response.defer()
        followup: Webhook = itr.followup

        embed = embed_builder(
            title=f"You have been banned from {itr.guild.name}",
            description=f"**Reason:** {reason}\n**Banned at:** {format_dt(utcnow(), style='R')}",
            thumbnail=None if not itr.guild.icon else itr.guild.icon.url
        )

        await bot.try_send(member, embed=embed)
        