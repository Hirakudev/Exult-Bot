from discord import Interaction, Member, Webhook
from discord.app_commands import command, describe
# Discord Imports

from utils import *
# Local Imports

class Avatar(ExultCog):

    @command(name="avatar", description="UI for viewing a user's avatar and banner.")
    @describe(user="The user that you want to view the avatar of.")
    async def avatar_slash(self, itr: Interaction, user: Member=None):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup
        user = await bot.fetch_user(user.id or itr.user.id)
        avatar = bot.try_asset(user.avatar, user.default_avatar)

        embed = embed_builder(
            author=[avatar, f"{user.name}'s Avatar"],
            image=avatar
        )

        if user.banner:
            view = AvatarView(user)
            return followup.send(embed=embed, view=view)
        await followup.send(embed=embed)

