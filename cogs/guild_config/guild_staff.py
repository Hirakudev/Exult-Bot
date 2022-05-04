import discord
from discord import app_commands

# Discord Imports

# Regular Imports

from bot import ExultBot
from utils import *

# Local Imports


class GuildStaff(ExultCog):

    config = app_commands.Group(
        name="config", description="Configure the bot to suit your server's needs!"
    )
    modrole = app_commands.Group(
        name="modrole",
        description="Configure the server's custom moderator roles!",
        parent=config,
    )
    moduser = app_commands.Group(
        name="moduser",
        description="Configure the server's custom moderator users!",
        parent=config,
    )
    adminrole = app_commands.Group(
        name="adminrole",
        description="Configure the server's custom admin roles!",
        parent=config,
    )
    adminuser = app_commands.Group(
        name="adminuser",
        description="Configure the server's custom admin users!",
        parent=config,
    )

    @modrole.command(
        name="add",
        description="Make an addition to the server's custom moderator roles!",
    )
    @app_commands.describe(
        role="The role that you want to add as a custom moderator role."
    )
    async def modrole_add_slash(self, itr: discord.Interaction, role: discord.Role):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        role_id = role.id

        added = await GuildsDB(bot).add_moderator_role(itr.guild.id, role_id)

        if not added:
            return await followup.send("This role is already a moderator role.")

        embed = embed_builder(
            description=f"Successfully added {role.mention} as a `MODERATOR ROLE`!"
            "\n\nUsers with this role now have access to all moderation commands "
            "even without having the relevant permissions. For example they can now "
            "run the `ban` command successfully without having `BAN MEMBERS` permissions in the server."
        )
        await followup.send(embed=embed)

    @modrole.command(
        name="remove",
        description="Remove a role as one of the server's custom moderator roles!",
    )
    @app_commands.describe(
        role="The role that you want to remove as a custom moderator role."
    )
    async def modrole_remove_slash(self, itr: discord.Interaction, role: discord.Role):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        role_id = role.id

        added = await GuildsDB(bot).remove_moderator_role(itr.guild.id, role_id)

        if not added:
            return await followup.send("That role isn't a moderator role.")

        embed = embed_builder(
            description=f"Successfully removed {role.mention} as a moderator role!"
        )
        await followup.send(embed=embed)

    @moduser.command(
        name="add",
        description="Make an addition to the server's custom moderator users!",
    )
    @app_commands.describe(user="The user that you want to add as a custom moderator.")
    async def moduser_add_slash(self, itr: discord.Interaction, user: discord.Member):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        member_id = user.id

        added = await GuildsDB(bot).add_moderator_user(itr.guild.id, member_id)

        if not added:
            return await followup.send("This user is already a moderator user.")

        embed = embed_builder(
            description=f"Successfully added {user.mention} as a `MODERATOR USER`!"
            f"\n\n{user} now has access to all moderation commands "
            "even without having the relevant permissions. For example they can now "
            "run the `ban` command successfully without having `BAN MEMBERS` permissions in the server."
        )
        await followup.send(embed=embed)

    @moduser.command(
        name="remove",
        description="Remove a role as one of the server's custom moderator users!",
    )
    @app_commands.describe(
        user="The user that you want to remove as a custom moderator user."
    )
    async def moduser_remove_slash(
        self, itr: discord.Interaction, user: discord.Member
    ):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: discord.Webhook = itr.followup
        member_id = user.id

        added = await GuildsDB(bot).remove_moderator_user(itr.guild.id, member_id)

        if not added:
            return await followup.send("That user isn't a moderator user.")

        embed = embed_builder(
            description=f"Successfully removed {user.mention} as a moderator user!"
        )
        await followup.send(embed=embed)
