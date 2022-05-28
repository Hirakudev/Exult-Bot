"""
The MIT License (MIT)

Copyright (c) 2015 Rapptz

Permission is hereby granted, free of charge, to any person obtaining a
copy of this software and associated documentation files (the "Software"),
to deal in the Software without restriction, including without limitation
the rights to use, copy, modify, merge, publish, distribute, sublicense,
and/or sell copies of the Software, and to permit persons to whom the
Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.

Snippets used from RoboDanny in 
lines 100 - 141 and 162 - 201 https://github.com/Rapptz/RoboDanny/blob/rewrite/cogs/admin.py
"""

import discord

import io
import textwrap
import time
import traceback
from contextlib import redirect_stdout
from typing import TYPE_CHECKING, Awaitable, Callable, Union, Optional, Any

if TYPE_CHECKING:
    from asyncpg import Record

from bot import ExultBot
from utils.database import CasesDB
from utils.helpers import embed_builder, TabularData, plural, cleanup_code, CommandUtils


class CaseEditModal(discord.ui.Modal):
    def __init__(self, bot: ExultBot, case, data):
        self.case_id = case["case_id"]
        self.case_offender = case["user_id"]
        self.case_reason = case["reason"]
        self.new_reason = None
        super().__init__(
            title=f"Editing Case #{self.case_id} for {bot.get_user(self.case_offender)}",
            timeout=120.0,
        )
        self.add_item(
            discord.ui.TextInput(
                label="New Case Reason",
                placeholder='e.g. "Spam"',
                default=self.case_reason,
            )
        )

    async def on_submit(self, itr: discord.Interaction):
        await itr.response.defer()
        self.new_reason = self.children[0].value

        new_case = await CasesDB(itr.client).update_case(
            itr.guild.id, self.case_id, self.new_reason
        )

        if new_case:
            embed = embed_builder(
                title=f"Case {self.case_id} reason has been updated",
                fields=[
                    ["Old Reason:", self.case_reason, False],
                    ["New Reason:", self.new_reason, False],
                ],
            )
            await itr.followup.send(embed=embed)
        else:
            return


class SQLModal(discord.ui.Modal):
    def __init__(self, bot: ExultBot, return_eph: bool, last_val: str = None):
        self.bot = bot
        self.eph = return_eph
        super().__init__(title="SQL Query", timeout=120.0)
        self.add_item(
            discord.ui.TextInput(
                label="Query",
                placeholder="SELECT last_sql FROM temp_data",
                default=last_val,
                style=discord.TextStyle.paragraph,
            )
        )

    async def on_submit(self, itr: discord.Interaction):
        await itr.response.defer(ephemeral=self.eph)
        _query = self.children[0].value
        query = cleanup_code(_query)

        is_multistatement = query.count(";") > 1
        strategy: Callable[[str], Union[Awaitable[list[Record]], Awaitable[str]]]
        if is_multistatement:
            # fetch does not support multiple statements
            strategy = self.bot.pool.execute
        else:
            strategy = self.bot.pool.fetch

        try:
            start = time.perf_counter()
            results = await strategy(query)
            dt = (time.perf_counter() - start) * 1000.0
        except Exception:
            return await itr.followup.send(
                f"```py\n{traceback.format_exc()}\n```", ephemeral=self.eph
            )

        rows = len(results)
        if isinstance(results, str) or rows == 0:
            return await itr.followup.send(
                f"`{dt:.2f}ms: {results}`", ephemeral=self.eph
            )

        headers = list(results[0].keys())
        table = TabularData()
        table.set_columns(headers)
        table.add_rows(list(r.values()) for r in results)
        render = table.render()

        fmt = f"```\n{render}\n```\n*Returned {plural(rows):row} in {dt:.2f}ms*"
        if len(fmt) > 2000:
            fp = io.BytesIO(fmt.encode("utf-8"))
            await itr.followup.send(
                "Too many results...",
                file=discord.File(fp, "results.txt"),
                ephemeral=self.eph,
            )
        else:
            await itr.followup.send(fmt, ephemeral=self.eph)
        await self.bot.pool.execute("UPDATE temp_data SET last_sql=$1", _query)


class EvalModal(discord.ui.Modal):
    def __init__(self, bot: ExultBot, return_eph: bool, last_val: str = None):
        self.bot = bot
        self.eph = return_eph
        self._last_result: Optional[Any] = None
        super().__init__(title="Eval Query", timeout=120.0)
        self.add_item(
            discord.ui.TextInput(
                label="Eval",
                placeholder='print("Hello World!")',
                default=last_val,
                style=discord.TextStyle.paragraph,
            )
        )

    async def on_submit(self, itr: discord.Interaction):
        await itr.response.defer(ephemeral=self.eph)
        env = {
            "bot": self.bot,
            "itr": itr,
            "interaction": itr,
            "ctx": itr,
            "_": self._last_result,
        }
        env.update(globals())

        code = self.children[0].value
        body = cleanup_code(code)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await itr.followup.send(
                f"```py\n{e.__class__.__name__}: {e}\n```", ephemeral=self.eph
            )

        func = env["func"]
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await itr.followup.send(
                f"```py\n{value}{traceback.format_exc()}\n```", ephemeral=self.eph
            )
        else:
            value = stdout.getvalue()

            if ret is None:
                if value:
                    await itr.followup.send(f"```py\n{value}\n```", ephemeral=self.eph)
            else:
                self._last_result = ret
                await itr.followup.send(f"```py\n{value}{ret}\n```", ephemeral=self.eph)
        await self.bot.pool.execute("UPDATE temp_data SET last_eval=$1", code)


class CreateCommandModal(discord.ui.Modal):
    def __init__(self, utils: CommandUtils):
        self.utils = utils
        super().__init__(title="Create Custom Command", timeout=60.0)
        self.add_item(
            discord.ui.TextInput(
                label="Command Name",
                placeholder="ping",
                style=discord.TextStyle.short,
            )
        )
        self.add_item(
            discord.ui.TextInput(
                label="Command Response",
                placeholder="pong!",
                style=discord.TextStyle.paragraph,
            )
        )

    async def on_submit(self, itr: discord.Interaction):
        await itr.response.defer()
        await self.utils.create_command(
            itr, self.children[0].value, self.children[1].value
        )
        await itr.followup.send(
            content=f"Command Created! Try it with `{await self.utils.get_prefix(itr)}{self.children[0].value}`!"
        )
