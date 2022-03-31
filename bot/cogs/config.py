from discord import app_commands, Interaction, Object
from discord.ext.commands import Cog, Bot

from database import *
from utils import *

class Config(Cog, app_commands.Group):
    def __init__(self, bot):
        self.bot = bot
        self.db = GuildConfigDB(bot)
        super().__init__(name="config", description="Configure the bot for this server")
        
    @app_commands.command(name="prefix", description="Change the prefix for the bot! Leave 'new_prefix' blank to view current prefix")
    @app_commands.describe(new_prefix="The new prefix you want to assign the bot for this server.")
    async def config_prefix_slash(self, interaction: Interaction, new_prefix: str=None):
        config = await self.db.get_config(interaction.guild, "config")
        prefix = config["prefix"]
        if not new_prefix:
            embed = embed_builder(description=f"The prefix for `{interaction.guild.name}` is {prefix}")
            return await interaction.response.send_message(embed=embed)
        await self.db.update_prefix(interaction.guild, new_prefix)
        embed = embed_builder(description=f"Prefix has been updated from `{prefix}` to {new_prefix}")
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="botnick", description="Change my nickname in this server")
    @app_commands.describe(nick="The new nickname you want to give me")
    async def config_botnick_slash(self, interaction: Interaction, nick: str):
        await interaction.guild.me.edit(nick=nick)
        embed = embed_builder(description=f"Changed my nickname to {interaction.guild.me.nick}")
        await interaction.response.send_message(embed=embed)
        
    @app_commands.command(name="suggestions", description="Configure Suggestions")
    async def config_suggestions_slash(self, interaction: Interaction):
        config = await self.db.get_config(interaction.guild, "modules")
        configured = config["suggestions"]["channel_id"]
        if not configured:
            """  SELECT CATEGORY OF THE SUGGESTIONS CHANNEL  """
            view = CategoriesDropdownView(interaction)
            embed = embed_builder(description="Please select the category in which your desired suggestions channel is in below.",
                                  author=[interaction.guild.icon.url, "Suggestions Setup"])
            await interaction.response.send_message(embed=embed, view=view)
            msg = await interaction.original_message()
            await view.wait()
            category = view.values[0]
            
            """  SELECT CHANNEL WITHIN CHOSEN CATEGORY  """
            view = ChannelsDropdownView(interaction.client.get_channel(int(category)))
            embed.description = "Please select the channel that you would like suggestions to be sent to below."
            await msg.edit(embed=embed, view=view)
            await view.wait()
            channel = view.values[0]
            
            """  ENABLE/DISABLE SAFEMODE  """
            view = ConfirmDenyView()
            embed.description = "**Would you like to enable safemode?**\n\n" \
                                "> Safemode means that a suggestion will have to be approved by a " \
                                "higher-up before being sent into your suggestions channel. " \
                                "Please select a button below to either enable/disable safemode."
            await msg.edit(embed=embed, view=view)
            await view.wait()
            safemode = view.value
            
            """  GET SAFEMODE IF ENABLED   """
            if safemode:
                """  SELECT CATEGORY OF THE SAFEMODE CHANNEL  """
                view = CategoriesDropdownView(interaction)
                embed.description = "Select the category of the channel that you want suggestions to be approved in."
                await msg.edit(embed=embed, view=view)
                await view.wait()
                safemode_category = view.values[0]
                
                """  SELECT CHANNEL WITHIN CHOSEN CATEGORY   """
                view = ChannelsDropdownView(interaction.client.get_channel(int(safemode_category)))
                embed.description = "Select the channel that you want suggestions to be approved in."
                await interaction.response.edit_message(embed=embed, view=view)
                await view.wait()
                safemode = view.values[0]
                
            await self.db.update_suggestions(interaction.guild, channel=channel, safemode=safemode)
            embed.description = f"Suggestions has been successfully setup for `{interaction.guild.name}`!\n\n" \
                                f"If you made a mistake or would like to make edits in future, simply run `/config suggestions` again!\n\n" \
                                f"**NEW CONFIGURATION:**\nChannel: {interaction.guild.get_channel(int(channel)).mention}\n" \
                                f"Safemode: {f'Enabled in {interaction.guild.get_channel(int(safemode)).mention}' if safemode else 'Disabled'}"
            await msg.edit(embed=embed, view=None)
                
        
async def setup(bot: Bot):
    await bot.add_cog(Config(bot), guilds=[Object(guild) for guild in bot.app_guilds])