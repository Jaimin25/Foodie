import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import PersistentView, profile
import random

class Upgrades(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def upgrades_btn_callback(self, interaction):
        profile_embed = discord.Embed(title="Upgrades")
        profile_embed.set_author(name=interaction.user.name)
        profile_embed.add_field(name=":one: Kitchen", value="Buy new kitchen appliances", inline=False)
        profile_embed.add_field(name=":two: Staff", value="Hire new staffs", inline=False)
        profile_embed.add_field(name=":three: Farm", value="Upgrade/Buy farm equipments", inline=False)
        profile_embed.add_field(name=":four: Farm", value="Upgrade/Buy farm equipments", inline=False)
        profile_embed.add_field(name=":five: Farm", value="Upgrade/Buy farm equipments", inline=False)

        v = PersistentView.UpgradesPersistentView()

        await interaction.response.edit_message(embed=profile_embed, view=v)

async def setup(client):
    await client.add_cog(Upgrades(client))