from discord import app_commands, TextStyle, Interaction, Object, Member
from discord.ui import TextInput, Modal
from discord.ext.commands import Cog, Bot
        
class TestModal(Modal, title="Modal which is a test one"):
    default = TextInput(label="Name")
    short = TextInput(label="Name", style=TextStyle.short)
    paragraph = TextInput(label="Answer", style=TextStyle.paragraph)
    
    async def on_submit(self, interaction: Interaction):
        await interaction.response.send_message(f"Thanks for your response of {self.default}!", ephemeral=True)
        
class Test(Cog):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()
        
    @app_commands.command(description="Test slash command")
    async def slash_test(self, interaction: Interaction, name: str):
        await interaction.response.send_message(f"Hey, {name}!", ephemeral=True)
    
    @app_commands.command()
    async def modal_slash_test(self, interaction: Interaction):
        await interaction.response.send_modal(TestModal())
        
    @app_commands.context_menu()
    async def bonk(self, interaction: Interaction, member: Member):
        await interaction.response.send_message('Bonk', ephemeral=True)

    @app_commands.command(name="rangeoption", description="Slash command with range defined for param")
    async def range_option(self, interaction: Interaction, value: app_commands.Range[int, 1, 100]):
        await interaction.response.send_message(f"You selected number {value}", ephemeral=True)

    @app_commands.command()
    async def fruits(self, interaction: Interaction, fruit: str):
        await interaction.response.send_message(f'Your favourite fruit seems to be {fruit}')

    @fruits.autocomplete('fruit')
    async def fruits_autocomplete(self, interaction: Interaction, current: str, namespace: app_commands.Namespace):
        fruits = ['Banana', 'Pineapple', 'Apple', 'Watermelon', 'Melon', 'Cherry']
        return [app_commands.Choice(name=fruit, value=fruit) for fruit in fruits if current.lower() in fruit.lower()]
        
async def setup(bot: Bot):
    await bot.add_cog(Test(bot), guilds=[Object(guild) for guild in bot.app_guilds])