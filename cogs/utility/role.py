import discord
from discord import app_commands

# Discord Imports

import asyncio
import datetime
import time
from humanfriendly import format_timespan

# Regular Imports

from bot import ExultBot
from utils import *

# Local Imports


class Role(ExultCog):

    role = app_commands.Group(
        name="role",
        description="Get information on a specific role.",
        default_permissions=discord.Permissions(manage_roles=True),
    )
    all_group = app_commands.Group(
        name="all",
        description="Mass Handle Roles with every member in the server!",
        parent=role,
    )

    @role.command(name="info", description="Display info on a given role.")
    @app_commands.rename(_role="role")
    @app_commands.describe(_role="The role you want to view info about.")
    async def role_info_slash(self, itr: discord.Interaction, _role: discord.Role):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        _permissions = (
            str(get_perms(_role.permissions))
            .replace("[", "")
            .replace("]", "")
            .replace("'", "")
        )
        _permissions = (
            "No special permissions." if not len(_permissions) else _permissions
        )

        embed = embed_builder(
            colour=_role.colour,
            thumbnail=bot.try_asset(_role.icon),
            fields=[
                ["ID:", str(_role.id), True],
                ["Name:", _role.name, True],
                ["Colour:", _role.colour, True],
                ["Mention:", _role.mention, True],
                ["Hoisted:", "Yes" if _role.hoist else "No", True],
                ["Position:", _role.position, True],
                ["Mentionable:", "Yes" if _role.mentionable else "No", True],
                ["Created:", discord.utils.format_dt(_role.created_at, "R"), True],
                ["Members with Role:", len(_role.members), True],
                ["Important Permissions:", _permissions, False],
            ],
        )
        await followup.send(embed=embed)

    @role.command(name="members", description="Display members with a given role.")
    @app_commands.rename(_role="role")
    @app_commands.describe(_role="The role you want to view the members of.")
    async def role_members_slash(self, itr: discord.Interaction, _role: discord.Role):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup

        formatted_members = discord.utils.as_chunks(
            sorted([f"{str(member)} `{member.id}`" for member in _role.members]), 20
        )
        embeds = []

        for members in formatted_members:
            embed = embed_builder(
                title=f"Members with {_role.name}",
                footer=f"Total Members with {_role.name}: {len(_role.members)}",
                thumbnail=bot.try_asset(_role.icon),
            )
            embed.description = str("\n".join(members))
            embeds.append(embed)

        if len(embeds) > 1:
            view = Paginator(pages=embeds)
            return await followup.send(embed=embeds[0], view=view)
        await followup.send(embed=embeds[0])

    @role.command(name="add", description="Give a role to a member!")
    @app_commands.rename(_role="role")
    @app_commands.describe(
        member="The member you want to give the role to.",
        _role="The role you want to give to the member.",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def role_add_slash(
        self, itr: discord.Interaction, member: discord.Member, _role: discord.Role
    ):
        if all((_role < itr.user.top_role, _role < itr.guild.me.top_role)):
            if _role not in member.roles:
                await member.add_roles(_role)
                msg = {
                    "title": "Role Added!",
                    "description": f"Given {_role.mention} to {member.mention}",
                }
            else:
                msg = {
                    "title": "Role Not Added",
                    "description": f"{member.mention} already has the {_role.mention} role!",
                }
        else:
            msg = {
                "title": "Oops!",
                "description": f"One of us is unable to give {_role.mention} to members!",
            }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await itr.response.send_message(embed=embed)

    @role.command(name="remove", description="Remove a role from a member!")
    @app_commands.rename(_role="role")
    @app_commands.describe(
        member="The member you want to remove the role from.",
        _role="The role you want to remove from the member.",
    )
    @app_commands.default_permissions(manage_roles=True)
    async def role_remove_slash(
        self, itr: discord.Interaction, member: discord.Member, _role: discord.Role
    ):
        if all((_role < itr.user.top_role, _role < itr.guild.me.top_role)):
            if _role in member.roles:
                await member.remove_roles(_role)
                msg = {
                    "title": "Role Removed!",
                    "description": f"Removed {_role.mention} from {member.mention}",
                }
            else:
                msg = {
                    "title": "Role Not Removed",
                    "description": f"{member.mention} does not have the {_role.mention} role!",
                }
        else:
            msg = {
                "title": "Oops!",
                "description": f"One of us is unable to remove {_role.mention} from members!",
            }
        embed = embed_builder(
            title=msg.get("title"), description=msg.get("description")
        )
        await itr.response.send_message(embed=embed)

    @all_group.command(
        name="add", description="Give every member in the server a role!"
    )
    @app_commands.rename(_role="role")
    @app_commands.describe(
        _role="The role you want to give every member in the server. (Ignores Bots)"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def role_all_add_slash(self, itr: discord.Interaction, _role: discord.Role):
        await itr.response.defer(thinking=True)
        bot: ExultBot = itr.client

        if all((_role < itr.user.top_role, _role < itr.guild.me.top_role)):
            members_to_give = [
                m for m in itr.guild.members if _role not in m.roles and not m.bot
            ]
            time_complete = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=len(members_to_give) * 2.5
            )
            embed = embed_builder(
                description=f"Giving {_role.mention} to {len(members_to_give)} members! (Excluding Bots)\nThis should be complete {discord.utils.format_dt(bot.time(time_complete), style='R')}!"
            )
            await itr.edit_original_message(embed=embed)

            added_to = 0
            x = time.perf_counter()
            for member in members_to_give:
                await member.add_roles(_role)
                added_to += 1
                await asyncio.sleep(2)
            y = time.perf_counter()
            z = int(y - x)

            embed = embed_builder(
                title=f"Mass Role Add Complete!",
                description=f"{added_to} members have been given {_role.mention} in {format_timespan(int(z))}!",
            )
            await itr.edit_original_message(embed=embed)

    @all_group.command(
        name="remove", description="Remove a role from every member in the server!"
    )
    @app_commands.rename(_role="role")
    @app_commands.describe(
        _role="The role you want to remove from every member in the server. (Ignores Bots)"
    )
    @app_commands.default_permissions(manage_roles=True)
    async def role_all_remove_slash(
        self, itr: discord.Interaction, _role: discord.Role
    ):
        await itr.response.defer(thinking=True)
        bot: ExultBot = itr.client

        if all((_role < itr.user.top_role, _role < itr.guild.me.top_role)):
            members_to_remove = [
                m for m in itr.guild.members if _role in m.roles and not m.bot
            ]
            time_complete = datetime.datetime.utcnow() + datetime.timedelta(
                seconds=len(members_to_remove) * 2.5
            )
            embed = embed_builder(
                description=f"Removing {_role.mention} from {len(members_to_remove)} members! (Excluding Bots)\nThis should be complete {discord.utils.format_dt(bot.time(time_complete), style='R')}!"
            )
            await itr.edit_original_message(embed=embed)

            removed_from = 0
            x = time.perf_counter()
            for member in members_to_remove:
                await member.remove_roles(_role)
                removed_from += 1
                await asyncio.sleep(2)
            y = time.perf_counter()
            z = int(y - x)

            embed = embed_builder(
                title=f"Mass Role Remove Complete!",
                description=f"{removed_from} members have had {_role.mention} removed in {format_timespan(int(z))}!",
            )
            await itr.edit_original_message(embed=embed)
