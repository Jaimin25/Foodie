import discord
from discord.ui import Button, View
from discord.ext import commands
import json

f = open("data/upgrades.json", "r")
upgrades = json.loads(f.read())

['stove']

async def kitchen_upgrade():
    return upgrades['kitchen']

async def staff_upgrade():
    return upgrades['staff']