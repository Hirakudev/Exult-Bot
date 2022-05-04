import discord
from discord import app_commands
# Discord Imports

#Regular Imports

from bot import ExultBot
from utils import *
# Local Imports

class Role(ExultCog):

    role = app_commands.Group(name="role", description="Get information on a specific role.")

    @role.command(name="info", description="Display info on a given role.")
    @app_commands.rename(_role="role")
    @app_commands.describe(_role="The role you want to view info about.")
    async def role_info_slash(self, itr: discord.Interaction, _role: discord.Role):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        _permissions = str(get_perms(_role.permissions)).replace("[", "").replace("]", "").replace("'", "")
        _permissions = "No special permissions." if not len(_permissions) else _permissions

        embed = embed_builder(
            colour=_role.colour,
            thumbnail=bot.try_asset(_role.icon),
            fields = [
                ["ID:", str(_role.id), True], ["Name:", _role.name, True], ["Colour:", _role.colour, True],
                ["Mention:", _role.mention, True], ["Hoisted:", "Yes" if _role.hoist else "No", True], 
                ["Position:", _role.position, True], ["Mentionable:", "Yes" if _role.mentionable else "No", True], 
                ["Created:", discord.utils.format_dt(_role.created_at, "R"), True],
                ["Members with Role:", len(_role.members), True], ["Important Permissions:", _permissions, False]
            ]
        )
        await followup.send(embed=embed)

    @role.command(name="members", description="Display members with a given role.")
    @app_commands.rename(_role="role")
    @app_commands.describe(_role="The role you want to view the members of.")
    async def role_members_slash(self, itr: discord.Interaction, _role: discord.Role):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        formatted_members = discord.utils.as_chunks(sorted([f"{str(member)} `{member.id}`" for member in _role.members]), 20)
        embeds = []

        for members in formatted_members:
            embed = embed_builder(
                title=f"Members with {_role.name}",
                footer=f"Total Members with {_role.name}: {len(_role.members)}",
                thumbnail=bot.try_asset(_role.icon)
            )
            embed.description = str("\n".join(members))
            embeds.append(embed)

        if len(embeds) > 1:
            view = Paginator(pages=embeds)
            return await followup.send(embed=embeds[0], view=view)
        await followup.send(embed=embeds[0])