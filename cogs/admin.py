import discord
from discord.ext import commands
import asyncpg
from prettytable import PrettyTable
import traceback
import sys
import asyncio
import io
from contextlib import redirect_stdout
import textwrap
import requests
import json
import html
import psutil

from discord.ui import Button, View, Select

class Admin(commands.Cog, command_attrs=dict(hidden=True)):
    def __init__(self, client):
        self.client = client
        self._last_result = None
        self.x = 65
        self.y = 71

    @commands.command()
    async def stats(self, ctx):
        bedem = discord.Embed(title='System Resource Usage', description='See CPU and memory usage of the system.')
        bedem.add_field(name='CPU Usage', value=f'{psutil.cpu_percent()}%', inline=False)
        bedem.add_field(name='Memory Usage', value=f'{psutil.virtual_memory().percent}%', inline=False)
        bedem.add_field(name='Available Memory',
                        value=f'{round(psutil.virtual_memory().available * 100 / psutil.virtual_memory().total, 2)}%',
                        inline=False)
        await ctx.send(embed=bedem)

    @commands.command()
    async def ping(self, ctx):
        await ctx.send(f"{round(self.client.latency * 1000)}ms")

    @commands.command()
    async def support(self, ctx):
        support_embed = discord.Embed(
            title="Support Server",
            description="**[Click Here To Get Support From Official Server](https://discord.gg/DPKxWe4HW8)**",
            color=0x8a42d0
        )
        await ctx.send(embed=support_embed)

    @commands.command()
    async def invite(self, ctx):
        invite_embed = discord.Embed(
            title="Invite Me!",
            description="**[Click Here To Invite Me](https://discord.com/oauth2/authorize?client_id=815102986937696276&permissions=388160&scope=bot)**",
            color=0x9b6be3)
        await ctx.send(embed=invite_embed)

    @commands.is_owner()
    @commands.command()
    async def pull(self, ctx):
        proc = await asyncio.create_subprocess_shell("git pull origin main", stdout=asyncio.subprocess.PIPE,
                                                     stderr=asyncio.subprocess.PIPE)
        stdout, stderr = await proc.communicate()
        stdout = f"{stdout.decode()}" if stdout != b"" else ""
        stderr = f"\n{stderr.decode()}" if stderr != b"" else ""
        final = f"```diff\n{stdout}\n{stderr}\n```"
        embed = discord.Embed(color=0x2196f3, title="Pulling from GitHub...",
                              description=final)
        return await ctx.send(embed=embed)

    @commands.is_owner()
    @commands.group(name="sql")
    async def sql(self, ctx, *, command):

        res = await self.client.db.fetch(command)
        if len(res) == 0:
            return await ctx.send(
                "Query finished successfully No results to display")
        headers = list(res[0].keys())
        table = PrettyTable()
        table.field_names = headers
        for record in res:
            lst = list(record)
            table.add_row(lst)

        msg = table.get_string()

        with open("cogs/dt.sql", "w") as n:

            n.write(msg)

        await ctx.send(file=discord.File("cogs/dt.sql"))

    @commands.is_owner()
    @commands.command(aliases=["tsks"])
    async def tasks(self, ctx):
        command = "SELECT * FROM kingdom_upg_running_tasks"
        res = await self.client.db.fetch(command)
        headers = list(res[0].keys())
        table = PrettyTable()
        table.field_names = headers
        for record in res:
            lst = list(record)
            table.add_row(lst)

        msg = table.get_string()
        await ctx.send(f"```sql\n{msg}\n```")

    @sql.error
    async def sql_error_handling(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
            if isinstance(error, asyncpg.exceptions.UndefinedTableError):
                return await ctx.send("The table does not exists")
            elif isinstance(error, asyncpg.exceptions.PostgresSyntaxError):
                return await ctx.send(f"syntax error ```\n {error} ```")
            else:
                print('Ignoring exception in command {}:'.format(ctx.command),
                      file=sys.stderr)
                traceback.print_exception(type(error),
                                          error,
                                          error.__traceback__,
                                          file=sys.stderr)
        else:
            print('Ignoring exception in command {}:'.format(ctx.command),
                  file=sys.stderr)
            traceback.print_exception(type(error),
                                      error,
                                      error.__traceback__,
                                      file=sys.stderr)

    @commands.is_owner()
    @commands.command(pass_context=True, hidden=True, name='eval')
    async def _eval(self, ctx, *, body: str):
        """Evaluates a code"""

        env = {
            'bot': self.client,
            'ctx': ctx,
            'channel': ctx.channel,
            'author': ctx.author,
            'guild': ctx.guild,
            'message': ctx.message,
            '_': self._last_result
        }

        env.update(globals())

        body = self.cleanup_code(body)
        stdout = io.StringIO()

        to_compile = f'async def func():\n{textwrap.indent(body, "  ")}'

        try:
            exec(to_compile, env)
        except Exception as e:
            return await ctx.send(f'```py\n{e.__class__.__name__}: {e}\n```')

        func = env['func']
        try:
            with redirect_stdout(stdout):
                ret = await func()
        except Exception as e:
            value = stdout.getvalue()
            await ctx.send(f'```py\n{value}{traceback.format_exc()}\n```')
        else:
            value = stdout.getvalue()
            try:
                await ctx.message.add_reaction('\u2705')
            except:
                pass

            if ret is None:
                if value:
                    await ctx.send(f'```py\n{value}\n```')
            else:
                self._last_result = ret
                await ctx.send(f'```py\n{value}{ret}\n```')

    def cleanup_code(self, content):
        """Automatically removes code blocks from the code."""
        # remove ```py\n```
        if content.startswith('```') and content.endswith('```'):
            return '\n'.join(content.split('\n')[1:-1])

        # remove `foo`
        return content.strip('` \n')

async def setup(client):
    await client.add_cog(Admin(client))
