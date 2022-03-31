from discord import app_commands, Interaction, File, Object
from discord.ext.commands import Cog, Bot

import time
import traceback
import io

from utils import *

class SQL:
    def __init__(self, bot):
        self.bot = bot
        
    @classmethod
    def cleanup_code(self, content: str):
        if content.startswith("```") and content.endswith("```"):
            return "\n".join(content.split("\n")[1:-1])
        return content.strip('` \n')
        
class TabularData:
    def __init__(self):
        self._widths = []
        self._columns = []
        self._rows = []

    def set_columns(self, columns):
        self._columns = columns
        self._widths = [len(c) + 2 for c in columns]

    def add_row(self, row):
        rows = [str(r) for r in row]
        self._rows.append(rows)
        for index, element in enumerate(rows):
            width = len(element) + 2
            if width > self._widths[index]:
                self._widths[index] = width

    def add_rows(self, rows):
        for row in rows:
            self.add_row(row)

    def render(self):
        sep = '+'.join('-' * w for w in self._widths)
        sep = f'+{sep}+'

        to_draw = [sep]

        def get_entry(d):
            elem = '|'.join(f'{e:^{self._widths[i]}}' for i, e in enumerate(d))
            return f'|{elem}|'

        to_draw.append(get_entry(self._columns))
        to_draw.append(sep)

        for row in self._rows:
            to_draw.append(get_entry(row))

        to_draw.append(sep)
        return '\n'.join(to_draw)


class Plural:
    def __init__(self, value):
        self.value = value

    def __format__(self, format_spec):
        v = self.value
        singular, sep, plural = format_spec.partition('|')
        plural = plural or f'{singular}s'
        if abs(v) != 1:
            return f'{v} {plural}'
        return f'{v} {singular}'
    
async def noperms(interaction: Interaction):
    embed = embed_builder(description="You do not have sufficient permissions to run that command!")
    return await interaction.response.send_message(embed=embed, ephemeral=True)

class sql(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        super().__init__()
        
    @app_commands.command(name="sql", description="Carry out sql statements to interact with the database")
    async def sql_slash(self, interaction: Interaction, query: str):
        bot = interaction.client
        if await bot.is_owner(interaction.user):
            pass
        else:
            await noperms(interaction)
        if query != "all tables":
            query = SQL.cleanup_code(query)
            
            is_multistatement = query.count(";") > 1
            strategy = bot.pool.execute if is_multistatement else bot.pool.fetch
            
            try:
                start = time.perf_counter()
                results = await strategy(query)
                dt = (time.perf_counter() - start) * 1000.0
            except Exception:
                return await interaction.response.send_message(f"```py\n{traceback.format_exc()}\n```")
            
            rows = len(results)
            if is_multistatement or rows == 0:
                return await interaction.response.send_message(f'`{dt:.2f}ms: {results}`')
            
            headers = list(results[0].keys())
            table = TabularData()
            table.set_columns(headers)
            table.add_rows(list(r.values()) for r in results)
            render = table.render()
            
            fmt = f'```\n{render}\n```\n*Returned {Plural(rows):row} in {dt:.2f}ms*'
            if len(fmt) > 2000:
                fp = io.BytesIO(fmt.encode("utf-8"))
                return await interaction.response.send_message("Too many results...", file=File(fp, "results.txt"))
            else:
                return await interaction.response.send_message(fmt)
        elif query == "all tables":
            strategy = bot.pool.fetch
            try:
                start = time.perf_counter()
                results = await strategy("SELECT * FROM pg_catalog.pg_tables WHERE schemaname != 'pg_catalog' AND schemaname != 'information_schema'")
                dt = (time.perf_counter() - start) * 1000.0
            except Exception:
                return await interaction.response.send_message(f'```py\n{traceback.format_exc()}\n```')
            rows = len(results)
            if rows == 0:
                return await interaction.response.send_message(f'`{dt:.2f}ms: {results}`')
            headers = list(results[0].keys())
            table = TabularData()
            table.set_columns(headers)
            table.add_rows(list(r.values()) for r in results)
            render = table.render()
            fmt = f'```\n{render}\n```\n*Returned {Plural(rows):row} in {dt:.2f}ms*'
            if len(fmt) > 2000:
                fp = io.BytesIO(fmt.encode('utf-8'))
                return await interaction.response.send_message('Too many results...', file=File(fp, 'results.txt'))
            else:
                return await interaction.response.send_message(fmt)
                
    @sql_slash.autocomplete("query")
    async def sql_slash_query_autocomplete(self, interaction: Interaction, current: str):
        options = ["all tables"]
        return [app_commands.Choice(name=option, value=option) for option in options if current.lower() in option.lower()]

async def setup(bot: Bot):
    await bot.add_cog(sql(bot), guilds=[Object(guild) for guild in bot.app_guilds])