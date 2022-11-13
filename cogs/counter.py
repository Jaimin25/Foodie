import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import app_commands
from cogs import helper, accounts, profile
import time, datetime
from datetime import timedelta
import random

class Counter(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description="Collect your income")
    @app_commands.checks.cooldown(1, 65)
    async def collect(self, interaction: discord.Interaction):
        client = interaction.client
        user = interaction.user

        is_acc_created = await accounts.Accounts.check_for_account(self, interaction)

        if not is_acc_created:
            return

        get_income_cd = await client.db.fetchrow("SELECT userid, income_collected FROM cooldowns WHERE userid = $1", user.id)
        profile_details = await profile.Profile.get_user_details(self, interaction)

        net_income = profile_details[3]
        balance = profile_details[2]

        income_collected_at = 1 if not len(get_income_cd) > 0 else int(get_income_cd[1])
        time_now = int(time.time())
        time_spent = time_now-income_collected_at

        counter_embed = discord.Embed(title="Income", color=discord.Color.brand_green())

        total_income = 100 if income_collected_at == 1 else net_income*int(time_spent/60)


        await client.db.execute("UPDATE cooldowns SET income_collected = $1 WHERE userid = $2", time.time(), user.id)
        await client.db.execute("UPDATE profiles SET balance = $1 WHERE userid = $2", balance+total_income, user.id)

        counter_embed.description = f":dollar: Collected ***${total_income:,}*** of income!"

        await interaction.response.send_message(embed=counter_embed)

    @collect.error
    async def on_test_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            cl_n = random.choice(
                ['1', '130', '2', '230', '3', '330', '4', '430', '5', '530', '6', '630', '7', '730', '8', '830', '9',
                 '930', '10', '1030', '11', '1130', '12', '1230'])
            cd_embed = discord.Embed(title="Cooldown",
                                     description=f":clock{cl_n}: Counter is empty, come back again in {self.hms(int(error.retry_after))}",
                                     color=discord.Color.brand_red())
            await interaction.response.send_message(embed=cd_embed)

    def hms(self, seconds):
        m = seconds % 3600 // 60
        s = seconds % 3600 % 60
        return '{:02d}m{:02d}s'.format(m, s)



async def setup(client):
    await client.add_cog(Counter(client))