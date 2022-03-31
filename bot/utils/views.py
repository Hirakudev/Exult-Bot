from re import L
import traceback
from discord import ButtonStyle, Interaction, SelectOption
from discord.ui import View, Button, Modal, TextInput, Select, button

from utils.tools import embed_builder

class Paginator(View):
    def __init__(self, pages, page=0, start_end=False, step_10=False):
        super().__init__(timeout=120)
        self.page = page
        self.pages = pages
        self.count = len(pages)
        self.start_end = start_end
        self.step_10 = step_10
        self.add_buttons()

    def add_buttons(self):
        non_page_buttons = [item for item in self.children if not isinstance(item, PaginatorButton)]
        if self.children:
            self.clear_items()
        if not self.count or self.count == 1:
            return
        previous_page = self.page - 1
        if previous_page < 0:
            previous_page = self.count - 1
        self.add_item(PaginatorButton(label="◀", page=previous_page, style=ButtonStyle.red))
        self.add_item(PaginatorButton(label=f"{self.page + 1} / {len(self.pages)}", style=ButtonStyle.grey, disabled=True))
        next_page = self.page + 1
        if next_page > self.count - 1:
            next_page = 0
        self.add_item(PaginatorButton(label="▶", page=next_page, style=ButtonStyle.green))
        for item in non_page_buttons:
            self.add_item(item)
            
class PaginatorButton(Button["Paginator"]):
    def __init__(self, label, style, row=0, page=None, disabled=False):
        super().__init__(style=style, label=label, row=row, disabled=disabled)
        self.page = page

    async def callback(self, interaction: Interaction):
        self.pages = self.view.pages
        self.view.page = self.page
        self.view.add_buttons()
        await interaction.message.edit(embed=self.pages[self.page], view=self.view)
        
class AvatarButton(Button):
    def __init__(self, label, style, custom_id):
        super().__init__(style=style, label=label, custom_id=custom_id)
        
    async def callback(self, interaction: Interaction):
        custom_id = interaction.data["custom_id"]
        member = await interaction.client.fetch_user(int(custom_id[6:]))
        await interaction.message.edit(embed=embed_builder(author=[member.display_avatar.url, f"{member.name}'s Avatar"],
                                                            image=member.display_avatar.url))

class BannerButton(Button):
    def __init__(self, label, style, custom_id):
        super().__init__(style=style, label=label, custom_id=custom_id)
        
    async def callback(self, interaction: Interaction):
        custom_id = interaction.data["custom_id"]
        member = await interaction.client.fetch_user(int(custom_id[6:]))
        await interaction.message.edit(embed=embed_builder(author=[member.display_avatar.url, f"{member.name}'s Banner"],
                                                            image=member.banner.url))
        
class Avatar(View):
    def __init__(self, member):
        super().__init__()
        self.add_item(AvatarButton("View Avatar", ButtonStyle.secondary, f"avatar{member.id}"))
        self.add_item(BannerButton("View Banner", ButtonStyle.secondary, f"banner{member.id}"))
        
class PokemonGuessModal(Modal):
    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.answer = data["answer"]
        self.question = data["question"]
        self.types = data["types"]
        self.guess = None
        super().__init__(title="Who's That Pokemon?")
        self.add_item(TextInput(label="Which pokemon do you think it is?", placeholder="e.g. Pikachu"))
        
    async def on_submit(self, interaction: Interaction):
        lives = self.data["lives"]
        guess = self.children[0].value
        self.guess = guess
        embed = interaction.message.embeds[0]
        if guess.lower() != self.name.lower() and lives > 0 :
            lives -= 1
            self.data["lives"] = lives
            if self.data["lives"] > 0:
                embed.set_field_at(0, name="Guesses Remaining:", value=f"{lives}")
                self.stop()
                view = PokemonGuess(self.data)
                await interaction.response.send_message(f"{guess} is incorrect! Lives left: {lives}", ephemeral=True)
                await interaction.message.edit(embed=embed, view=view)
            else:
                await interaction.response.send_message(f"{guess} is incorrect! You lost.", ephemeral=True)
                self.stop()
                embed.set_field_at(0, name="Correct Answer:", value=self.name, inline=True)
                embed.description = None
                embed.title = f"You lost!"
                embed.set_image(url=self.answer)
                await interaction.message.edit(embed=embed, view=None)
        elif guess.lower() == self.name.lower():
            embed.set_image(url=self.answer)
            embed.title = f"{interaction.user.name} Won!"
            embed.description = None
            embed.colour = interaction.client.green
            embed.set_field_at(0, name="Correct Answer:", value=self.name, inline=True)
            await interaction.message.edit(embed=embed, view=None)
            await self.stop()
            await interaction.response.send_message(f"You got it! It was {self.name}", ephemeral=True)
        
    async def on_error(self, error: Exception, interaction: Interaction):
        traceback.print_tb(error.__traceback__)

class StartGuessPokemon(Button):
    def __init__(self, label, style, data):
        self.data = data
        self.answer = data["name"]
        super().__init__(style=style, label=label, custom_id=self.answer)
        
    async def callback(self, interaction: Interaction):
        modal = PokemonGuessModal(self.data)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.view.guess = modal.guess

class PokemonGuess(View):
    def __init__(self, data):
        super().__init__()
        self.add_item(StartGuessPokemon("Guess", ButtonStyle.blurple, data))
        
class CategoriesDropdown(Select):
    def __init__(self, interaction: Interaction):
        self.interaction = interaction
        options = [SelectOption(label=c.name, value=str(c.id)) for c in self.interaction.guild.categories]
        super().__init__(placeholder="Select a Category...", options=options)
        
    async def callback(self, interaction: Interaction):
        self.view.values = self.values
        self.view.stop()
        
class CategoriesDropdownView(View):
    def __init__(self, interaction: Interaction):
        super().__init__()
        self.add_item(CategoriesDropdown(interaction))
        
class ChannelsDropdown(Select):
    def __init__(self, category):
        options = [SelectOption(label=c.name, value=c.id) for c in category.text_channels]
        super().__init__(placeholder="Select a Channel...", options=options)
        
    async def callback(self, interaction: Interaction):
        self.view.values = self.values
        self.view.stop()
        
class ChannelsDropdownView(View):
    def __init__(self, category):
        super().__init__()
        self.add_item(ChannelsDropdown(category))
        
class ConfirmDenyView(View):
    def __init__(self):
        super().__init__()
        self.value = None
        
    @button(emoji="✅", style=ButtonStyle.green)
    async def confirm(self, button: Button, interaction: Interaction):
        self.value = True
        self.stop()
        
    @button(emoji="❌", style=ButtonStyle.secondary)
    async def deny(self, button: Button, interaction: Interaction):
        self.value = False
        self.stop()