from discord import Interaction
from discord.app_commands import check, MissingPermissions, BotMissingPermissions
from discord import Permissions
#Discord Imports

from .database import GuildsDB

async def is_owner(itr: Interaction):
    return await itr.client.is_owner(itr.user)

def permissions(**perms: bool):
    user_invalid = perms.keys() - Permissions.VALID_FLAGS.keys()
    bot_invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if user_invalid:
        raise TypeError(f"Invalid user permission(s): {', '.join(user_invalid)}")
    if bot_invalid:
        raise TypeError(f"Invalid bot permission(s): {', '.join(bot_invalid)}")
    async def predicate(itr: Interaction):
        final_result = [False, False]
        #See if bot is able to carry out command.
        me = itr.guild.me if itr.guild is not None else itr.client.user
        if itr.channel is None:
            permissions = Permissions.none()
        else:
            permissions = itr.channel.permissions_for(me)

        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]

        if not missing:
            final_result[1] = True
        else:
            raise BotMissingPermissions(missing)

        if await is_owner(itr):
            return True

        #See if user is able to run command.
        permissions = itr.permissions
        missing = [perm for perm, value in perms.items() if getattr(permissions, perm) != value]
        if not missing:
            final_result[0] = True
        else:
            raise MissingPermissions(missing)

        if final_result[0] and final_result[1]:
            return True

    return check(predicate)

def guild_staff():
    async def predicate(itr: Interaction):
        if await is_owner(itr):
            return True
        staff_roles = await GuildsDB(itr.client).get_staff_roles(itr.guild.id)
        staff_users = await GuildsDB(itr.client).get_staff(itr.guild.id)
        if itr.user in staff_users["moderator_users"] or itr.user in staff_users["admin_users"]:
            return True
        for role in itr.user.roles:
            if role.id in staff_roles["moderator_roles"]:
                return True
            elif role.id in staff_roles["admin_roles"]:
                return True

    return check(predicate)
        