import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
import aiohttp
import config
import asyncpg
import asyncio
import time
import string
import random
import datetime
import pytz
import traceback
from discord import app_commands
from cogs import admin

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()  # All but the THREE privileged ones
        intents.message_content = True
        super().__init__(command_prefix='f', self_bot=True, intents=intents, strip_after_prefix=True)
        self.initial_extensions = [
            'cogs.admin'
        ]

    async def setup_hook(self):
        self.background_task.start()
        self.session = aiohttp.ClientSession()
        for ext in self.initial_extensions:
            await self.load_extension(ext)
        self.add_view(admin.PersistentView())

    async def on_message(self, message):

        if message.guild is None:
            return

        if message.content.startswith('<@') and message.content.endswith('>'):
            for mention in message.mentions:
                if mention == client.user:
                    prefix = await client.get_prefix(message)
                    await message.channel.send(
                        f"I am {client.user.name} Bot. My prefix is `d`, type `dhelp` to get help, have fun :wink:. ")
                    return

        if message.author.bot:
            return
        else:
            await self.process_commands(message)


    async def close(self):
        await super().close()
        await self.session.close()

    @tasks.loop(minutes=10)
    async def background_task(self):
        print('Running background task...')

    async def on_ready(self):
        await self.tree.sync(guild=discord.Object(955385300513878026))
        print('Ready!')


client = MyBot()

@client.tree.command(description="Help")
async def help(interaction: discord.Interaction) -> None:
    await interaction.response.send_message("Hello from my command!")

client.tree.add_command(help, guild=discord.Object(955385300513878026))

@client.command(hidden=True)
@commands.is_owner()
async def shutdown(ctx):
    await ctx.send("Turning myself off...")
    await client.close()

local_tz = pytz.timezone('Asia/Kolkata')


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def aslocaltimestr(utc_dt):
    return utc_to_local(utc_dt).strftime('%d-%m-%Y %H:%M:%S %p')

async def run():
    async with client:
        db = await asyncpg.create_pool(**config.DATABASE_CREDENTIALS)
        client.db = db

        await client.start(config.TOKEN)

asyncio.run(run())
