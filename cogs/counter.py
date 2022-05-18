import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import app_commands
from cogs import helper, accounts, profile
import time, datetime
from datetime import timedelta

class Counter(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description="Collect your income")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def collect(self, interaction: discord.Interaction):
        client = interaction.client
        user = interaction.user

        get_income_cd = await client.db.fetchrow("SELECT userid, income_collected FROM cooldowns WHERE userid = $1", user.id)
        profile_details = await profile.Profile.get_user_details(self, interaction)

        net_income = profile_details[3]
        balance = profile_details[2]

        income_collect_at = 1 if get_income_cd is None or not len(get_income_cd) > 0 else int(get_income_cd[1])
        time_now = int(time.time())
        time_spent = time_now-income_collect_at

        counter_embed = discord.Embed(title="Income", color=discord.Color.green())

        if time_spent >= 20:

            total_income = 100 if income_collect_at == 1 else net_income*int(time_spent)


            await client.db.execute("UPDATE cooldowns SET income_collected = $1 WHERE userid = $2", time.time(), user.id)
            await client.db.execute("UPDATE profiles SET balance = $1 WHERE userid = $2", balance+total_income, user.id)

            counter_embed.description = f"You have successfully collected ***${total_income:,}*** of income."
        else:
            counter_embed.color = discord.Color.red()
            counter_embed.description = f"**{user.name}**, Your counter seems empty! Come back later..."

        await interaction.response.send_message(embed=counter_embed)

async def setup(client):
    await client.add_cog(Counter(client))
