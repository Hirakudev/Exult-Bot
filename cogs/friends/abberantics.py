import discord
from discord.ext import commands


class Abberantics:
    colour = 0xFF4500
    apexrole = 658508587496112193
    csgorole = 658508867172564992
    mwrole = 658508851372359690
    fortrole = 658509013666889759
    owrole = 658509166498807848
    r6role = 658509196764905492
    rlrole = 664996153288556595
    valrole = 701097388265308220
    eventsrole = 719761318684524556
    naerole = 657046413716357171
    nawrole = 657046579550879772
    eurole = 657046628800397315
    ocerole = 664998820610048000
    pcrole = 677171133199548483
    psrole = 701593482208477214
    xboxrole = 701593449014624344
    switchrole = 701593535618613397
    staff = 653741741249396796
    comprole = 934898482920181870

    class VerifyButton(discord.ui.View):
        def __init__(self, bot):
            self.bot = bot
            super().__init__(timeout=None)

        @discord.ui.button(
            label="Verify",
            style=discord.ButtonStyle.green,
            emoji="✅",
            custom_id="AEVerification",
        )
        async def verifybutton(self, button, interaction):
            await aeverify(self.bot, interaction)

    class GoToChannel(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.add_item(
                discord.ui.Button(
                    label="Verify now!", url="https://discord.gg/GEWxYrWzfn"
                )
            )


class Check:
    def guild(guild_id=None):
        async def guild_check(ctx):
            return ctx.guild.id == guild_id or ctx.author.id == 839248459704959058

        return commands.check(guild_check)


class AbberanticsCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @Check.guild(652725365856272394)
    async def aeverificationembedpanelpost(self, ctx: commands.Context):
        guild = self.bot.get_guild(652725365856272394)
        view = Abberantics.VerifyButton(self.bot)
        embed = discord.Embed(
            title="Welcome to Abberantics Esports!",
            description=f"To get started, please press the button that says `✅ Verify`!",
            colour=Abberantics.colour,
        ).set_image(url=guild.banner.url)
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        if member.guild.id == 652725365856272394:
            await member.add_roles(member.guild.get_role(941173849834266715))
            view = Abberantics.GoToChannel()
            await self.bot.get_channel(654613761537081345).send(
                f"Welcome to Abberantics Esports {member.mention}! Please read the rules the <#652738269800431626> and then click the button below to begin verification to get access to the rest of the chats! If you run into any issues getting into the community please @ the Staff role ;)",
                view=view,
            )


class GameSelect(discord.ui.Select):
    def __init__(self, verifyinteraction, games):
        self.games = games
        options = []
        options.append(discord.SelectOption(label="Reset", value="remove all"))
        for game in games:
            game = games[game]
            options.append(
                discord.SelectOption(label=game.name, value=game.id, emoji=game.icon)
            )
        super().__init__(
            placeholder="Please select your game roles!",
            options=options,
            custom_id=f"game-{verifyinteraction.user.id}",
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(interaction.user.id))
        if interaction.data["values"][0] == "remove all":
            for game in self.games:
                game = self.games[game]
                await member.remove_roles(game)
            return await interaction.response.send_message(
                "Successfully reset game roles", ephemeral=True
            )
        role = interaction.guild.get_role(int(interaction.data["values"][0]))
        if role not in member.roles:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Successfully added {role.mention}!", ephemeral=True
            )
        elif role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Successfully removed {role.mention}!", ephemeral=True
            )


class GameSelectView(discord.ui.View):
    def __init__(self, verifyinteraction, games):
        super().__init__(timeout=None)
        self.value = None
        self.add_item(GameSelect(verifyinteraction, games))

    @discord.ui.button(
        label="Continue",
        style=discord.ButtonStyle.green,
        custom_id="gamecontinue",
        row=1,
    )
    async def gamecontinue(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = True
        self.stop()


class PingSelect(discord.ui.Select):
    def __init__(self, verifyinteraction, pings):
        self.pings = pings
        options = []
        options.append(discord.SelectOption(label="Reset", value="remove all"))
        for ping in pings:
            ping = pings[ping]
            options.append(
                discord.SelectOption(label=ping.name, value=ping.id, emoji=ping.icon)
            )
        super().__init__(
            placeholder="Please select what you'd like to be pinged for!",
            options=options,
            custom_id=f"ping-{verifyinteraction.user.id}",
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(interaction.user.id))
        if interaction.data["values"][0] == "remove all":
            for ping in self.pings:
                ping = self.pings[ping]
                await member.remove_roles(ping)
            return await interaction.response.send_message(
                "Successfully reset ping roles", ephemeral=True
            )
        role = interaction.guild.get_role(int(interaction.data["values"][0]))
        if role not in member.roles:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Successfully added {role.mention}!", ephemeral=True
            )
        elif role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Successfully removed {role.mention}!", ephemeral=True
            )


class PingSelectView(discord.ui.View):
    def __init__(self, verifyinteraction, pings):
        super().__init__(timeout=None)
        self.value = None
        self.add_item(GameSelect(verifyinteraction, pings))

    @discord.ui.button(
        label="Continue",
        style=discord.ButtonStyle.green,
        custom_id="pingcontinue",
        row=1,
    )
    async def pingcontinue(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = True
        self.stop()


class RegionSelect(discord.ui.Select):
    def __init__(self, verifyinteraction, regions):
        self.regions = regions
        options = []
        for region in regions:
            region = regions[region]
            options.append(
                discord.SelectOption(
                    label=region.name, value=region.id, emoji=region.icon
                )
            )
        super().__init__(
            placeholder="Please select what region you are in!",
            options=options,
            custom_id=f"region-{verifyinteraction.user.id}",
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(interaction.user.id))
        role = interaction.guild.get_role(int(interaction.data["values"][0]))
        if role not in member.roles:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Successfully added {role.mention}!", ephemeral=True
            )
        elif role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Successfully removed {role.mention}!", ephemeral=True
            )


class RegionSelectView(discord.ui.View):
    def __init__(self, verifyinteraction, regions):
        super().__init__(timeout=None)
        self.value = None
        self.add_item(GameSelect(verifyinteraction, regions))

    @discord.ui.button(
        label="Continue",
        style=discord.ButtonStyle.green,
        custom_id="regioncontinue",
        row=1,
    )
    async def regioncontinue(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = True
        self.stop()


class PlatformSelect(discord.ui.Select):
    def __init__(self, verifyinteraction, platforms):
        self.platforms = platforms
        options = []
        options.append(discord.SelectOption(label="Reset", value="remove all"))
        for platform in platforms:
            platform = platforms[platform]
            options.append(
                discord.SelectOption(
                    label=platform.name, value=platform.id, emoji=platform.icon
                )
            )
        super().__init__(
            placeholder="Please select what platform(s) you play on!",
            options=options,
            custom_id=f"platform-{verifyinteraction.user.id}",
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.guild.get_member(int(interaction.user.id))
        if interaction.data["values"][0] == "remove all":
            for platform in self.platforms:
                platform = self.platforms[platform]
                await member.remove_roles(platform)
            return await interaction.response.send_message(
                "Successfully reset platform roles", ephemeral=True
            )
        role = interaction.guild.get_role(int(interaction.data["values"][0]))
        if role not in member.roles:
            await member.add_roles(role)
            await interaction.response.send_message(
                f"Successfully added {role.mention}!", ephemeral=True
            )
        elif role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message(
                f"Successfully removed {role.mention}!", ephemeral=True
            )


class PlatformSelectView(discord.ui.View):
    def __init__(self, verifyinteraction, platforms):
        super().__init__(timeout=None)
        self.value = None
        self.add_item(GameSelect(verifyinteraction, platforms))

    @discord.ui.button(
        label="Finish",
        style=discord.ButtonStyle.green,
        custom_id="platformfinish",
        row=1,
    )
    async def platformfinish(
        self, button: discord.ui.Button, interaction: discord.Interaction
    ):
        self.value = True
        self.stop()


async def aeverify(bot, interaction: discord.Interaction):
    user = interaction.guild.get_member(interaction.user.id)
    guild = interaction.guild
    for channel in interaction.channel.category.channels:
        if channel.name[7:] == user.name.lower():
            return await interaction.response.send_message(
                f"You already have a verification ticket open at {channel.mention}!",
                ephemeral=True,
            )
    overwrites = {
        interaction.guild.default_role: discord.PermissionOverwrite(
            read_messages=False
        ),
        interaction.user: discord.PermissionOverwrite(
            read_messages=True,
            send_messages=False,
            add_reactions=False,
            read_message_history=True,
        ),
        interaction.guild.get_role(Abberantics.staff): discord.PermissionOverwrite(
            view_channel=True,
            manage_channels=True,
            manage_permissions=True,
            send_messages=True,
            manage_messages=True,
        ),
    }
    channel = await interaction.channel.category.create_text_channel(
        name=f"verify-{user.name}", overwrites=overwrites
    )
    await interaction.response.send_message(
        embed=discord.Embed(
            description=f"Verification Ticket Successfully created in {channel.mention}!",
            colour=bot.green,
        ),
        ephemeral=True,
    )
    games = {
        "apex": interaction.guild.get_role(Abberantics.apexrole),
        "csgo": interaction.guild.get_role(Abberantics.csgorole),
        "mw": interaction.guild.get_role(Abberantics.mwrole),
        "fortnite": interaction.guild.get_role(Abberantics.fortrole),
        "ow": interaction.guild.get_role(Abberantics.owrole),
        "r6": interaction.guild.get_role(Abberantics.r6role),
        "rl": interaction.guild.get_role(Abberantics.rlrole),
        "val": interaction.guild.get_role(Abberantics.valrole),
    }
    pings = {
        "events": interaction.guild.get_role(Abberantics.eventsrole),
        "comp": interaction.guild.get_role(Abberantics.comprole),
    }
    regions = {
        "nae": interaction.guild.get_role(Abberantics.naerole),
        "naw": interaction.guild.get_role(Abberantics.nawrole),
        "eu": interaction.guild.get_role(Abberantics.eurole),
        "oce": interaction.guild.get_role(Abberantics.ocerole),
    }
    platforms = {
        "pc": interaction.guild.get_role(Abberantics.pcrole),
        "ps": interaction.guild.get_role(Abberantics.psrole),
        "xbox": interaction.guild.get_role(Abberantics.xboxrole),
        "switch": interaction.guild.get_role(Abberantics.switchrole),
    }
    view = GameSelectView(interaction, games)
    gamesembed = discord.Embed(
        description='Please select the games you play from the menu below!\n**PRESS THE "`✅ CONTINUE`" BUTTON TO PROCEED.**',
        color=Abberantics.colour,
    ).set_author(icon_url=interaction.guild.icon.url, name="Abberantics Verification")
    await channel.send(content=user.mention, embed=gamesembed, view=view)
    await view.wait()
    isfinished = view.value
    while isfinished != True:
        await view.wait()
        isfinished = view.value
    pingsembed = discord.Embed(
        description="We don't want to ping you for things you aren't interested in, so select what you'd like to be pinged for below!\n\n**PRESS THE \"`✅ CONTINUE`\" BUTTON TO PROCEED.**",
        color=Abberantics.colour,
    ).set_author(icon_url=interaction.guild.icon.url, name="Abberantics Verification")
    view = PingSelectView(interaction, pings)
    await channel.send(embed=pingsembed, view=view)
    await view.wait()
    isfinished = view.value
    while isfinished != True:
        await view.wait()
        isfinished = view.value
    regionembed = discord.Embed(
        description='Please select what region you are in from the menu below!\n**PRESS THE "`✅ CONTINUE`" BUTTON TO PROCEED.**',
        color=Abberantics.colour,
    ).set_author(icon_url=interaction.guild.icon.url, name="Abberantics Verification")
    view = RegionSelectView(interaction, regions)
    await channel.send(embed=regionembed, view=view)
    await view.wait()
    isfinished = view.value
    while isfinished != True:
        await view.wait()
        isfinished = view.value
    platformembed = discord.Embed(
        description='Please select what platforms you play on from the menu below!\n**PRESS THE "`✅ CONTINUE`" BUTTON TO PROCEED.**',
        color=Abberantics.colour,
    ).set_author(icon_url=interaction.guild.icon.url, name="Abberantics Verification")
    view = PlatformSelectView(interaction, platforms)
    await channel.send(embed=platformembed, view=view)
    await view.wait()
    isfinished = view.value
    while isfinished != True:
        await view.wait()
        isfinished = view.value
    if user.id != 839248459704959058:
        nickname = user.display_name
        await user.edit(nick=f"[NH] {nickname}")
    await user.add_roles(guild.get_role(653072985682346017))
    await user.remove_roles(guild.get_role(941173849834266715))
    await channel.delete()
    await bot.get_channel(652725365856272397).send(
        f"Welcome {user.mention} to {guild.name}!"
    )
