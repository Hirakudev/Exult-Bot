import discord


class Paginator(discord.ui.View):
    def __init__(self, pages, page=0, start_end=False, step_10=False):
        super().__init__(timeout=120)
        self.page = page
        self.pages = pages
        self.count = len(pages)
        self.start_end = start_end
        self.step_10 = step_10
        self.add_buttons()

    def add_buttons(self):
        non_page_buttons = [
            item for item in self.children if not isinstance(item, PaginatorButton)
        ]
        if self.children:
            self.clear_items()
        if not self.count or self.count == 1:
            return
        previous_page = self.page - 1
        if previous_page < 0:
            previous_page = self.count - 1
        self.add_item(
            PaginatorButton(
                label="◀", page=previous_page, style=discord.ButtonStyle.red
            )
        )
        self.add_item(
            PaginatorButton(
                label=f"{self.page + 1} / {len(self.pages)}",
                style=discord.ButtonStyle.grey,
                disabled=True,
            )
        )
        next_page = self.page + 1
        if next_page > self.count - 1:
            next_page = 0
        self.add_item(
            PaginatorButton(label="▶", page=next_page, style=discord.ButtonStyle.green)
        )
        for item in non_page_buttons:
            self.add_item(item)


class PaginatorButton(discord.ui.Button["Paginator"]):
    def __init__(self, label, style, row=0, page=None, disabled=False):
        super().__init__(style=style, label=label, row=row, disabled=disabled)
        self.page = page

    async def callback(self, interaction: discord.Interaction):
        self.pages = self.view.pages
        self.view.page = self.page
        self.view.add_buttons()
        await interaction.message.edit(embed=self.pages[self.page], view=self.view)
