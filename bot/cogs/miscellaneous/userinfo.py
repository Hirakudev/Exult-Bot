from discord import Interaction, Member, Webhook, UserFlags as uf, Spotify, ActivityType
from discord.app_commands import command, describe
from discord.utils import format_dt
# Discord Imports

from humanize.number import ordinal
#Regular Imports

from utils import *
# Local Imports

class UserInfo(ExultCog):

    @command(name="userinfo", description="Display info on a given member.")
    @describe(user="The user you want to display info for.")
    async def userinfo_slash(self, itr: Interaction, user: Member=None):
        await itr.response.defer()
        bot: ExultBot = itr.client
        followup: Webhook = itr.followup

        user = user or itr.user
        guild = itr.guild
        fg = user.public_flags
        ac = user.activity

        _status = {"online": "🟢 Online", "idle": "🟠 Idle", "dnd": "🔴 DND", "offline": "⚫ Offline", "streaming": "🟣 Streaming"}
        _badges = {uf.hypesquad_balance: emojis["bal"], uf.hypesquad_bravery: emojis["brav"],
                  uf.hypesquad_brilliance: emojis["bril"], uf.hypesquad: emojis["hype"],
                  uf.early_supporter: emojis["early"], uf.bug_hunter: emojis["bugh"],
                  uf.bug_hunter_level_2: emojis["bugh2"], uf.partner: emojis["dpart"],
                  uf.staff: emojis["dstaff"], uf.verified_bot_developer: emojis["earlydev"],
                  uf.discord_certified_moderator: emojis["dmod"], uf.verified_bot: emojis["bot"]}
        
        status = _status[str(user.status)]
        badges = [_badges[f[0]] for f in fg if fg[1]]
        roles = "Member has no roles." if not len(user.roles[1:]) else str([role.mention for role in user.roles]).replace("[", "").replace("]", "").replace("'", "")
        position = "Couldn't retrieve member position" if not user.joined_at else ordinal(sorted([m.joined_at for m in guild.members]).index(user.joined_at) + 1)

        if ac:
            if isinstance(ac, Spotify):
                activity = f"Listening to [{ac.title} - {ac.artist}]({ac.track_url})\n"
            elif isinstance(ac, ActivityType.custom):
                activity = f"{str(ac)}\n"
            elif isinstance(ac, ActivityType.unknown):
                activity = ""
            else:
                activity_type_list = str(ac.type).split(".")
                activity = f"{activity_type_list[1].capitalize()} {ac.name}\n"
        else:
            activity = ""

        _user = await bot.fetch_user(user.id)
        banner = _user.banner.url

        embed = embed_builder(
            author=[bot.try_asset(user.avatar.url, user.default_avatar.url), f"User Info: {user}"],
            description=f"{activity}{badges}",
            thumbnail=bot.try_asset(user.avatar.url, user.default_avatar.url),
            image=bot.try_asset(banner),
            footer=f"{position} member to join {guild.name}",
            fields=[
                ["Account Created:", format_dt(user.created_at, style='R'), True], [f"Joined {guild.name}:", format_dt(user.joined_at, style='R'), True],
                ["Boosting Since:", "Not boosting" if not user.premium_since else format_dt(user.premium_since, style='R'), True],
                ["Nickname:", user.display_name, True], ["Discriminator", user.discriminator, True], ["User Type", "Bot" if user.bot else "Human"],
                ["Status:", status, True], ["Colour:", user.colour, True], ["Highest Role", "No roles" if not len(user.roles[1:]) else user.top_role.mention, True],
                ["Number of Roles:", str(len(user.roles[1:])), True], ["Roles:", reversed(roles), False]
            ]
        )
        await followup.send(embed=embed)



