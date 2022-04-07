from discord import Interaction
from discord.app_commands import check, MissingPermissions, BotMissingPermissions
from discord import Permissions
# Discord Imports

from . import ExultBot


async def is_owner(itr: Interaction):
    bot: ExultBot = itr.client  # type: ignore
    return await bot.is_owner(itr.user)


def permissions(**perms: bool):
    user_invalid = perms.keys() - Permissions.VALID_FLAGS.keys()
    bot_invalid = set(perms) - set(Permissions.VALID_FLAGS)
    if user_invalid:
        raise TypeError(f"Invalid user permission(s): {', '.join(user_invalid)}")
    if bot_invalid:
        raise TypeError(f"Invalid bot permission(s): {', '.join(bot_invalid)}")

    async def predicate(itr: Interaction):
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

        if await is_owner(itr):
            return True

        # See if user is able to run command.
        _perms = itr.permissions
        missing = [perm for perm, value in perms.items() if getattr(_perms, perm) != value]
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
        bot: ExultBot = itr.client  # type: ignore
        if not itr.guild:
            return False
        guild_id = itr.guild.id
        if itr.user in bot.mod_users or itr.user in bot.admin_users:
            return True
        if any(r.id in bot.admin_roles[guild_id]
               or r.id in bot.mod_roles[guild_id]
               for r in itr.user.roles):
            return True
        return False

    return check(predicate)
