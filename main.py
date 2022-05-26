import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
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
import jishaku

class MyBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True
        intents.members = True

        self.embed_color = 0xfee3a8

        super().__init__(command_prefix='f', self_bot=True, intents=intents, strip_after_prefix=True)
        self.initial_extensions = [
            'cogs.admin',
            'cogs.accounts',
            'cogs.profile',
            'cogs.menu',
            'cogs.upgrades',
            'cogs.play',
            'cogs.counter',
            'jishaku'
        ]

    async def setup_hook(self):
        self.background_task.start()
        self.session = aiohttp.ClientSession()
        for ext in self.initial_extensions:
            await self.load_extension(ext)

    async def on_message(self, message):
        if message.content == "sync":
            await self.tree.sync(guild=discord.Object(955385300513878026))
            print("synced")

        if message.guild is None:
            return

        if message.content.startswith('<@') and message.content.endswith('>'):
            for mention in message.mentions:
                if mention == client.user:
                    prefix = await client.get_prefix(message)
                    await message.channel.send(
                        f"I am {client.user.name} Bot. type `/help` to get help, have fun :wink:. ")
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

        print('Ready!')

client = MyBot()

@client.event
async def on_guild_join(guild):
    timestamp = datetime.datetime.now()
    member_count = (guild.member_count)  # includes bots

    humans_member_count = len([m for m in guild.members if not m.bot])

    bots_member_count = member_count - humans_member_count

    channels = len(guild.channels)

    join_logs = discord.Embed(title=f"Server Joined - {guild.name}", color=0xfee3a8)
    join_logs.set_thumbnail(url=guild.icon)
    join_logs.add_field(name="Owner:", value=f"{guild.owner} (ID: {guild.owner_id})", inline=False)
    join_logs.add_field(name="Info:", value=f"Channels: {channels}\nHumans: {humans_member_count}\nBots: {bots_member_count}\nTotal: {member_count}", inline=False)
    join_logs.add_field(name=f"Joined At:", value=f"{timestamp.strftime(r'%d %B, %Y  %I:%M %p')}", inline=False)
    await client.get_channel(965112419305291786).send(embed=join_logs)

@client.event
async def on_guild_remove(guild):
    timestamp = datetime.datetime.now()
    leave_logs = discord.Embed(title=f"Server Left - {guild.name}", color=0xfee3a8)
    leave_logs.set_thumbnail(url=guild.icon)
    leave_logs.add_field(name="Owner:", value=f"{guild.owner} (ID: {guild.owner_id})", inline=False)
    leave_logs.add_field(name=f"Left At:", value=f"{timestamp.strftime(r'%d %B, %Y  %I:%M %p')}", inline=False)
    await client.get_channel(965112419305291786).send(embed=leave_logs)

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
