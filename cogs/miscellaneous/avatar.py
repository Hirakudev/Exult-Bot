import discord
from discord import app_commands

# Discord Imports

from bot import ExultBot
from utils import *

# Local Imports


class Avatar(ExultCog):
    @app_commands.command(
        name="avatar", description="UI for viewing a user's avatar and banner."
    )
    @app_commands.describe(user="The user that you want to view the avatar of.")
    async def avatar_slash(self, itr: discord.Interaction, user: discord.Member = None):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        member = itr.user if not user else user
        user = await bot.fetch_user(member.id)
        avatar = bot.try_asset(user.avatar, user.default_avatar)

        embed = embed_builder(author=[avatar, f"{user.name}'s Avatar"], image=avatar)

        if user.banner:
            view = AvatarView(user)
            return await followup.send(embed=embed, view=view)
        await followup.send(embed=embed)
