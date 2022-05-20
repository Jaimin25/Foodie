import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import app_commands
from cogs import helper, accounts, profile
import time, datetime
from datetime import timedelta
from discord.app_commands import Choice
import random


class Play(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description="Serve food to your customars")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 180.0, key=lambda i: (i.guild_id, i.user.id))
    async def serve(self, interaction: discord.Interaction):
        client = interaction.client
        user = interaction.user

        is_acc_created = await accounts.Accounts.check_for_account(self, interaction)

        if not is_acc_created:
            return

        upg_data = await client.db.fetch("SELECT * FROM upgrades WHERE userid = $1", user.id)
        user_data = await profile.Profile.get_user_details(self, interaction)

        income = user_data[3]

        amt_sum = 0
        for i in upg_data:
            amt_sum = amt_sum+int(i['amount'])

        f1 = random.randint(1, amt_sum)
        f2 = random.randint(1, amt_sum)
        f3 = random.randint(1, amt_sum)
        f4 = random.randint(1, amt_sum)
        f5 = random.randint(1, amt_sum)

        serve_embed = discord.Embed(title=f":fork_knife_plate:  Food Served", color=0xf6c112)
        serve_embed.add_field(name="Items", value=f":hamburger: {f1}x **|** :ramen: {f2}x **|** :pizza: {f3}x", inline=False)
        serve_embed.add_field(name="Income",value=f":moneybag: You have served **{f1+f2+f3}** of food items and earned ***${int(int(income)+float(1+(amt_sum/100)*int(f1*2)+int(f2*3)+int(f3*4))):,}***",inline=False)

        await interaction.response.send_message(embed=serve_embed)


    @serve.error
    async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            await interaction.response.send_message(str(error), ephemeral=True)

async def setup(client):
    await client.add_cog(Play(client))