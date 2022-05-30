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
    @app_commands.checks.cooldown(1, 240.0, key=lambda i: (i.guild_id, i.user.id))
    async def serve(self, interaction: discord.Interaction):
        client = interaction.client
        user = interaction.user

        is_acc_created = await accounts.Accounts.check_for_account(self, interaction)

        if not is_acc_created:
            return

        upg_data = await client.db.fetch("SELECT * FROM upgrades WHERE userid = $1", user.id)
        user_data = await profile.Profile.get_user_details(self, interaction)

        income = user_data[3]
        balance = user_data[2]
        stars = user_data[8]

        amt_sum = 0
        if upg_data is not None:
            for i in upg_data:
                amt_sum = amt_sum+int(i['amount'])
        else:
            amt_sum = 5

        f1 = random.randint(1, amt_sum)
        f2 = random.randint(1, amt_sum)
        f3 = random.randint(1, amt_sum)

        f1_emote = random.choice([':hamburger:', ':fries:', ':pizza:', ':sandwich:', ':taco:'])
        f2_emote = random.choice([':pretzel:', ':pancakes:', ':waffle:', ':salad:', ':tamale:'])
        f3_emote = random.choice([':shaved_ice:', ':ice_cream:', ':icecream:', ':cupcake:', ':cake:'])

        net_serve_income = int(int(income)+float(1+(amt_sum/100)*int(f1*2)+int(f2*3)+int(f3*4)))

        serve_embed = discord.Embed(title=f":fork_knife_plate:  Food Served", color=0xf6c112)
        serve_embed.add_field(name="Items", value=f"{f1_emote} {f1}x **|** {f2_emote} {f2}x **|** {f3_emote} {f3}x", inline=False)
        serve_embed.add_field(name="Income",value=f":moneybag: You have served **{f1+f2+f3}** of food items and earned ***${net_serve_income:,}***",inline=False)

        star_amt = random.randint(1, 3)

        stars = star_amt + stars
        serve_embed.add_field(name="Review ", value=f":star2: Your food was so tasty! You got **{star_amt}** star(s) as food review.")

        await client.db.execute("UPDATE profiles SET balance = $1, stars = $2 WHERE userid = $3", balance+net_serve_income, stars, user.id)

        await interaction.response.send_message(embed=serve_embed)

    @app_commands.command(description="Collect tips from your customers")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 120.0, key=lambda i: (i.guild_id, i.user.id))
    async def tips(self, interaction: discord.Interaction):
        client = interaction.client
        user = interaction.user

        is_acc_created = await accounts.Accounts.check_for_account(self, interaction)

        if not is_acc_created:
            return

        upg_data = await client.db.fetch("SELECT * FROM upgrades WHERE userid = $1", user.id)
        user_data = await profile.Profile.get_user_details(self, interaction)

        income = user_data[3]
        balance = user_data[2]

        tips = int(income/random.randint(3,5))

        tip_embed = discord.Embed(color=0xf6c112)
        tip_embed.description = f":dollar: You have collected **${tips:,}** of tips!"

        await client.db.execute("UPDATE profiles SET balance = $1 WHERE userid = $2",
                                balance + tips, user.id)

        await interaction.response.send_message(embed=tip_embed)

    @serve.error
    @tips.error
    async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            cl_n = random.choice(['1', '130', '2', '230', '3', '330', '4', '430', '5', '530', '6', '630', '7', '730', '8', '830', '9', '930', '10', '1030', '11', '1130', '12', '1230'])
            cd_embed = discord.Embed(title="Cooldown", description=f":clock{cl_n}: Try again in {self.hms(int(error.retry_after))}", color=discord.Color.brand_red())
            await interaction.response.send_message(embed=cd_embed)

    def hms(self, seconds):
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60
        return '{:02d}m{:02d}s'.format(m, s)

async def setup(client):
    await client.add_cog(Play(client))