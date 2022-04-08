from discord.ui import Modal, TextInput
from discord import Interaction

class CaseEditModal(Modal):
    def __init__(self, bot, case, data):
        self.case_id = case["case_id"]
        self.case_offender = case["user_id"]
        self.case_reason = case["reason"]
        self.new_reason = None
        self.db = data["db"]
        self.embed_builder = data["embed"]
        super().__init__(title=f"Editing Case #{self.case_id} for {bot.get_user(self.case_offender)}", timeout=120.0)
        self.add_item(TextInput(label="New Case Reason", placeholder="e.g. \"Spam\"", default=self.case_reason))

    async def on_submit(self, itr: Interaction):
        await itr.response.defer()
        self.new_reason = self.children[0].value

        new_case = await self.db(itr.client).update_case(itr.guild.id, self.case_id, self.new_reason)

        if new_case:
            embed = self.embed_builder(title=f"Case {self.case_id} reason has been updated",
                                fields=[["Old Reason:", self.case_reason, False],
                                        ["New Reason:", self.new_reason, False]])
            await itr.followup.send(embed=embed)
        else:
            return