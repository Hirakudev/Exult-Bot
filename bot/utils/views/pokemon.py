import discord


class PokemonGuessModal(discord.ui.Modal):
    def __init__(self, data):
        self.data = data
        self.name = data["name"]
        self.answer = data["answer"]
        self.question = data["question"]
        self.types = data["types"]
        self.guess = None
        super().__init__(title="Who's That Pokemon?")
        self.add_item(
            discord.ui.TextInput(
                label="Which pokemon do you think it is?", placeholder="e.g. Pikachu"
            )
        )

    async def on_submit(self, interaction: discord.Interaction):
        lives = self.data["lives"]
        guess = self.children[0].value
        self.guess = guess
        embed = interaction.message.embeds[0]
        if guess.lower() != self.name.lower() and lives > 0:
            lives -= 1
            self.data["lives"] = lives
            if self.data["lives"] > 0:
                embed.set_field_at(0, name="Guesses Remaining:", value=f"{lives}")
                self.stop()
                view = PokemonGuess(self.data)
                await interaction.response.send_message(
                    f"{guess} is incorrect! Lives left: {lives}", ephemeral=True
                )
                await interaction.message.edit(embed=embed, view=view)
            else:
                await interaction.response.send_message(
                    f"{guess} is incorrect! You lost.", ephemeral=True
                )
                self.stop()
                embed.set_field_at(
                    0, name="Correct Answer:", value=self.name, inline=True
                )
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
            await interaction.response.send_message(
                f"You got it! It was {self.name}", ephemeral=True
            )


class StartGuessPokemon(discord.ui.Button):
    def __init__(self, label, style, data):
        self.data = data
        self.answer = data["name"]
        super().__init__(style=style, label=label, custom_id=self.answer)

    async def callback(self, interaction: discord.Interaction):
        modal = PokemonGuessModal(self.data)
        await interaction.response.send_modal(modal)
        await modal.wait()
        self.view.guess = modal.guess


class PokemonGuess(discord.ui.View):
    def __init__(self, data):
        super().__init__()
        self.add_item(StartGuessPokemon("Guess", discord.ButtonStyle.blurple, data))
