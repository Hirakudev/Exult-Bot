from discord import app_commands, Interaction, Member, Role, Spotify, Object
from discord.ext.commands import Bot, Cog

import time
from psutil import Process, cpu_percent
from os import getpid
from random import randint

from utils import *
from database import *

class Miscellaneous(Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command(name="avatar", description="Get a user's avatar and banner")
    @app_commands.describe(member="A member whose avatar/banner you want to view.")
    async def avatar_slash(self, interaction: Interaction, member:Member=None):
        member = interaction.user if not member else member
        embed = embed_builder(author=[member.display_avatar.url, f"{member.name}'s Avatar"],
                            image=member.display_avatar.url)
        member = await interaction.client.fetch_user(member.id)
        if member.banner:
            view = Avatar(member)
            return await interaction.response.send_message(embed=embed, view=view)
        await interaction.response.send_message(embed=embed)
    
    role = app_commands.Group(name="role", description="Display Stats and Info on a given role")
    
    @role.command(name="info", description="Display info on a given role")
    @app_commands.describe(role="The role you want to display info on")
    async def role_info_slash(self, interaction: Interaction, role:Role):
            Permissions = []
            if role.permissions.administrator:
                Permissions.append("Administrator")
            if role.permissions.ban_members:
                Permissions.append("Ban Members")
            if role.permissions.deafen_members:
                Permissions.append("Server Deafen Members")
            if role.permissions.kick_members:
                Permissions.append("Kick Members")
            if role.permissions.manage_channels:
                Permissions.append("Manage Channels")
            if role.permissions.manage_emojis:
                Permissions.append("Manage Emojis")
            if role.permissions.manage_guild:
                Permissions.append("Manage Server")
            if role.permissions.manage_messages:
                Permissions.append("Manage Messages")
            if role.permissions.manage_nicknames:
                Permissions.append("Manage Nicknames")
            if role.permissions.manage_permissions:
                Permissions.append("Manage Permissions")
            if role.permissions.manage_roles:
                Permissions.append("Manage Roles")
            if role.permissions.manage_webhooks:
                Permissions.append("Manage Webhooks")
            if role.permissions.mention_everyone:
                Permissions.append("Mention Everyone")
            if role.permissions.move_members:
                Permissions.append("Move Members")
            if role.permissions.mute_members:
                Permissions.append("Server Mute Members")
            if role.permissions.view_audit_log:
                Permissions.append("View Audit Log")
            if len(Permissions) == 0:
                Permissions = "No special permissions"
            elif Permissions[0] == "Administrator":
                Permissions = Permissions[0]
            else:
                Permissions = str(Permissions)
                Permissions = Permissions.replace("'", "").replace("[", "").replace("]", "")
            embed = embed_builder(colour=role.colour, 
                                author=f"Role Info: {role.name}",
                                thumbnail=None if not role.icon else role.icon.url,
                                fields=[
                                    ["ID:", str(role.id), True],
                                    ["Name:", role.name, True],
                                    ["Colour:", role.colour, True],
                                    ["Mention:", role.mention, True],
                                    ["Hoisted:", "Yes" if role.hoist else "No", True],
                                    ["Position:", str(role.position), True],
                                    ["Mentionable:", "Yes" if role.mentionable else "No"],
                                    ["Created At:", Time.parsedate(role.created_at), True],
                                    ["Members with role:", len(role.members), True],
                                    ["Important Permissions:", Permissions, False]
                                ])
            await interaction.response.send_message(embed=embed)
            
    @role.command(name="members", description="Display all members with a given role.")
    @app_commands.describe(role="The role you want to view members for.")
    async def role_members_slash(self, interaction: Interaction, role: Role):
        formatted_members = get_chunks(20, sorted([str(member) for member in role.members]))
        embeds = []
        for members in formatted_members:
            embed = embed_builder(title=f"Members with {role.name}",
                                footer=f"Total Members with {role.name}: {len(role.members)}",
                                thumbnail=None if not role.icon else role.icon.url)
            for member in members:
                if not embed.description:
                    embed.description = f"{member}\n"
                else:
                    embed.description += f"{member}\n"
            embeds.append(embed)
        if len(embeds) > 1:
            view = Paginator(pages=embeds)
            return await interaction.response.send_message(embed=embeds[0], view=view)
        await interaction.response.send_message(embed=embeds[0])
        
    @app_commands.command(name="serverinfo", description="Display info on the current server.")
    async def serverinfo_slash(self, interaction: Interaction):
        guild = interaction.guild
        statuses = [len(list(filter(lambda m: str(m.status) == "online", guild.members))),
                    len(list(filter(lambda m: str(m.status) == "idle", guild.members))),
                    len(list(filter(lambda m: str(m.status) == "dnd", guild.members))),
                    len(list(filter(lambda m: str(m.status) == "offline", guild.members)))]
        embed = embed_builder(author=f"Server Info: {guild.name}",
                            footer=f"Server ID: {guild.id}",
                            thumbnail=None if not guild.icon else guild.icon.url,
                            fields=[
                                ["Owner:", guild.owner, True], ["Created At:", Time.parsedate(guild.created_at), True],
                                ["Members:", len([member for member in guild.members if not member.bot]), True],
                                ["Bots:", len([member for member in guild.members if member.bot]), True],
                                ["Banned Members:", len(await guild.bans()), True], ["Roles", len(guild.roles), True],
                                ["Categories:", len(guild.categories), True], ["Text Channels:", len(guild.text_channels), True],
                                ["Voice Channels:", len(guild.voice_channels), True], ["Nitro Boosts:", guild.premium_subscription_count, True],
                                ["Booster Level:", guild.premium_tier, True], ["Invites", len(await guild.invites()), True],
                                ["Statuses:", f"🟢 {statuses[0]} 🟠 {statuses[1]} 🔴 {statuses[2]} ⚪ {statuses[3]}", False]
                            ])
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Display info on a given member.")
    @app_commands.describe(member="The member you want to display info for.")
    async def userinfo_slash(self, interaction: Interaction, member: Member=None):
        member = interaction.guild.get_member(member.id)
        if str(member.status) == "dnd":
            status = "🔴 DND"
        elif str(member.status) == "online":
            status = "🟢 Online"
        elif str(member.status) == "offline":
            status = "⚫ Offline"
        elif str(member.status) == "idle":
            status = "🟠 Idle"
        elif str(member.status) == "streaming":
            status = "🟣 Streaming"
            
        badges = "" if not member.public_flags.hypesquad_balance else "<:Balance:951943457193214014>  "
        badges += "" if not member.public_flags.hypesquad_bravery else "<:Bravery:951943457738477608>  "
        badges += "" if not member.public_flags.hypesquad_brilliance else "<:Brilliance:951943457214169160>  "
        badges += "" if not member.public_flags.hypesquad else "<:Hypesquad:951943457700720660>  "
        badges += "" if not member.public_flags.early_supporter else "<:EarlySupporter:951943457621028864>  "
        badges += "" if not member.public_flags.bug_hunter else "<:BugHunter:951943457511964792>  "
        badges += "" if not member.public_flags.bug_hunter_level_2 else "<:BugHunter2:951943457629405264>  "
        badges += "" if not member.public_flags.partner else "<:DiscordPartner:951943457495207986>  "
        badges += "" if not member.public_flags.staff else "<:DiscordStaff:951943457721700402>  "
        badges += "" if not member.public_flags.early_verified_bot_developer else "<:EarlyVerifiedBotDev:951943458174689391>  "
        badges += "" if not member.public_flags.discord_certified_moderator else "<:DiscordCertifiedModerator:951945202963198062>  "
        badges += "" if not member.public_flags.verified_bot else "<:VerifiedBot:951943457788813363>  "
        
        if len(member.roles[1:]) > 0:
            roles = []
            for role in member.roles[1:]:
                roles.append(role.mention) 
            roles = ", ".join(reversed(roles))
        roles = "Member has no roles" if len(roles) == 0 else roles
        
        position = "Couldn't retrieve member position" if not member.joined_at else sum(m.joined_at < member.joined_at for m in interaction.guild.members if m.joined_at) + 1
        if position%10 == 1:
            indicator = "st"
        elif position%10 == 2:
            indicator = "nd"
        elif position%10 == 3:
            indicator = "rd"
        else:
            indicator = "th"
        
        if member.activity:
            if type(member.activity) == Spotify:
                activity = f"Listening to [{member.activity.title} - {member.activity.artist}]({member.activity.track_url})"
            elif str(member.activity.type) == "ActivityType.custom":
                activity = str(member.activity)
            elif str(member.activity.type) == "ActivityType.unknown":
                pass
            else:
                activity_type_list = str(member.activity.type).split(".")
                activity = f"{activity_type_list[1].capitalize()} {member.activity.name}"
        else:
            activity = ""
        banner = await interaction.client.fetch_user(member.id)
        banner = banner.banner
        embed = embed_builder(description=f"{activity}\n{badges}", 
                            thumbnail=member.display_avatar.url, 
                            author=[member.display_avatar.url, f"User Info: {member}"],
                            footer=f"{position}{indicator} member to join",
                            image=None if not banner else banner.url,
                            fields=[
                                ["Account Created:", Time.parsedate(member.created_at), True],
                                [f"Joined {interaction.guild.name}:", Time.parsedate(member.joined_at), True],
                                ["Boosting Since:", "Not Boosting" if not member.premium_since else Time.parsedate(member.premium_since), True],
                                ["Nickname:", member.display_name, True], ["Discriminator:", member.discriminator, True],
                                ["User Type:", "Bot" if member.bot else "User", True],
                                ["Status:", status, True], ["Colour:", member.colour, True],
                                ["Highest Role:", "No Roles" if len(member.roles) == 1 else member.top_role.mention, True],
                                ["Number of Roles:", str(len(member.roles)-1), True],
                                ["Roles:", roles, False]
                            ])
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="info", description="Display information about the bot")
    async def info_slash(self, interaction: Interaction):
        discord_url = "https://com/users/"
        
        msg = f"**Bot Runtime:** {Time.minimalise_seconds(round(time.time() - interaction.client.startTime))}\n" \
            f"**Bot Latency:** `{round(interaction.client.latency*1000)}ms`\n" \
            f"**Database Latency:** `{round(await interaction.client.get_latency()*1000, 2)}ms`\n" \
            f"**Guild Count:** `{len(interaction.client.guilds)}`\n" \
            f"**Memory Used:** `{round(Process(getpid()).memory_info().rss/1204/1204/1204, 3)}GB Used ({round(Process(getpid()).memory_percent())}%)`\n" \
            f"**CPU Usage:** `{cpu_percent()}%`\n" \
            f"**Lead Dev & Owner:** [{interaction.client.get_user(839248459704959058)}]({discord_url}839248459704959058)\n" \
            f"**Developers:** [{interaction.client.get_user(689564113415962717)}]({discord_url}689564113415962717), [{interaction.client.get_user(384023748531060737)}]({discord_url}384023748531060737)"
        await interaction.response.send_message(embed=embed_builder(author=[interaction.client.user.display_avatar.url, f"Exult Bot: Information"],
                                                                    description=msg,
                                                                    thumbnail=interaction.client.user.display_avatar.url))
    
    @app_commands.command(name="invite", description="Invite links for the Bot, and the Bot Support Server")
    async def invite_slash(self, interaction: Interaction):
        embed = embed_builder(title="Click here to invite me!", 
                            description="[Click here to join the support server!](https://exult.games/discord)",
                            url=interaction.client.invite)
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="feedback", description="Give feedback directly to the Exult Bot Developers!")
    async def feedback_slash(self, interaction: Interaction, feedback: str):
        channel = interaction.client.get_channel(914193452428836884)
        embed = embed_builder(author=[interaction.user.display_avatar.url, f"Feedback from {interaction.user}"],
                            footer=f"User ID: {interaction.user.id}",
                            fields=[
                                ["Mention:", interaction.user.mention, True],
                                ["Guild:", interaction.guild, True],
                                ["Suggested At:", Time.parsedate(), True],
                                ["Feedback:", feedback, False]
                            ])
        devs = interaction.client.get_guild(912148314223415316).get_role(914159464406470656)
        await channel.send(content=devs.mention, embed=embed)
        embed = embed_builder(author=[interaction.client.user.display_avatar.url, f"Thanks for your feedback!"],
                            description="Your feedback has been forwarded directly to our developers!",
                            fields=[["Feedback:", feedback, True]])
        await interaction.response.send_message(embed=embed)
    
    @app_commands.command(name="rng", description="Randomly generate a number between 1 and a number of your choice!")
    @app_commands.describe(max_num="Max number you'd like the random number to be generated between (Max: 1000)")
    async def rng_slash(self, interaction: Interaction, max_num: app_commands.Range[int, 2, 1000]):
        num = randint(1, max_num)
        embed = embed_builder(author=f"Your random number is {num}!")
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="testreason", description="Testing reason transformer")
    async def testreason_slash(self, interaction: Interaction, reason: str="Unspecified"):
        await interaction.response.send_message(reason, ephemeral=True)
    
async def setup(bot: Bot):
    await bot.add_cog(Miscellaneous(bot), guilds=[Object(guild) for guild in bot.app_guilds])
        