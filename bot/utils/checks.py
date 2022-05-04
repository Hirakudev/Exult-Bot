from discord import Interaction, Member
from discord.app_commands import check, MissingPermissions, BotMissingPermissions
from discord import Permissions
# Discord Imports

from bot import ExultBot


async def is_owner(itr: Interaction):
    bot: ExultBot = itr.client  # type: ignore
    return await bot.is_owner(itr.user)


def permissions(perms, itr: Interaction):
    final_result = [False, False]

    # See if bot is able to carry out command.
    me = itr.guild.me if itr.guild is not None else itr.client.user
    if itr.channel is None:
        _perms = Permissions.none()
    else:
        _perms = itr.channel.permissions_for(me)

    missing = [perm for perm, value in perms.items() if getattr(_perms, perm) != value]

    if not missing:
        final_result[1] = True
    else:
        raise BotMissingPermissions(missing)

    # See if user is able to run command.
    _perms = itr.permissions
    missing = [perm for perm, value in perms.items() if getattr(_perms, perm) != value]
    if not missing:
        final_result[0] = True
    else:
        raise MissingPermissions(missing)

    if final_result[0] and final_result[1]:
        return True


def guild_staff(*, admin: bool=False, **perms: bool):
    user_invalid = perms.keys() - Permissions.VALID_FLAGS.keys()
    bot_invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if user_invalid:
        raise TypeError(f"Invalid user permission(s): {', '.join(user_invalid)}")
    if bot_invalid:
        raise TypeError(f"Invalid bot permission(s): {', '.join(bot_invalid)}")

    async def predicate(itr: Interaction):
        if await is_owner(itr): #If the user is the bot owner, return True
            return True

        bot: ExultBot = itr.client
        if not itr.guild: #If the command isn't being run in a guild, return False
            return False
        
        guild_id = itr.guild.id
        user_id = itr.user.id

        if not admin:

            if user_id in bot.mod_users[guild_id] \
                or user_id in bot.admin_users[guild_id]:
                return True
            
            elif any(r.id in bot.admin_roles[guild_id]
                or r.id in bot.mod_roles[guild_id]
                for r in itr.user.roles):
                return True

            elif permissions(perms, itr):
                return True

        elif admin:
            if user_id in bot.admin_users[guild_id]:
                return True
            
            elif any(r.id in bot.admin_roles[guild_id] for r in itr.user.roles):
                return True

            elif itr.user.guild_permissions.manage_guild:
                return True

        return False

    return check(predicate)

def moderation(**kwargs):
    async def predicate(itr: Interaction):
        if kwargs.get("self_action"):
            for value in vars(itr.namespace).values():
                if isinstance(value, Member):
                    if value.id == itr.user.id:
                        return False
        return True

    return check(predicate)