import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import app_commands
from cogs import helper, accounts
import time, datetime
from datetime import timedelta

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description="View profile")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def profile(self, interaction: discord.Interaction):
        is_acc_created = await accounts.Accounts.check_for_account(self, interaction)

        if not is_acc_created:
            return

        profile_data = await self.get_user_details(interaction)

        name = profile_data[0]
        location = ":flag_us: New York, US" if profile_data[1] == 1 else ""
        balance = profile_data[2]
        income = profile_data[3]
        clean = ":white_check_mark: Clean" if profile_data[4] == 1 else ":bangbang: Not Clean"
        prestige = profile_data[5]
        buff = round(profile_data[6], 2)
        created_at = (profile_data[7])

        tm = self.convert_timedelta(
            datetime.timedelta(seconds=time.time()-float(created_at)))

        profile_embed = discord.Embed(title=name, color=interaction.client.embed_color)
        profile_embed.set_thumbnail(url=interaction.user.avatar)
        profile_embed.set_footer(text=f"Created {tm} ago")
        profile_embed.add_field(name="Location", value=f"{location}", inline=False)
        profile_embed.add_field(name="Prestige", value=f":crown:  {prestige}", inline=False)
        profile_embed.add_field(name="Income", value=f":coin: ${income:,}/min", inline=False)
        profile_embed.add_field(name="Balance", value=f":moneybag: ${balance:,}", inline=False)
        profile_embed.add_field(name="Clean", value=f"{clean}", inline=False)
        profile_embed.add_field(name="Total Multi", value=f":bar_chart: x{buff}", inline=False)

        await interaction.response.send_message(embed=profile_embed)

    async def get_user_details(self, interaction):
        client = interaction.client
        user = interaction.user

        profile_query = "SELECT * FROM profiles WHERE userid = $1"
        profile_data = await client.db.fetchrow(profile_query, user.id)

        name = profile_data[1]
        location = profile_data[2]
        balance = profile_data[3]
        income = profile_data[4]
        clean = profile_data[5]
        prestige = profile_data[7]
        buff = round(profile_data[8], 2)
        created_at = (profile_data[9])

        return name, location, balance, income, clean, prestige, buff, created_at

    def convert_timedelta(self, duration):
        days, seconds = duration.days, duration.seconds
        hours = days * 24 + seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = (seconds % 60)

        if duration.days != 0:
            return f"{days} days"
        elif hours != 0:
            return f"{hours}h"
        elif minutes != 0:
            return f"{minutes}m"
        else:
            return f"{seconds}s"

async def setup(client):
    await client.add_cog(Profile(client))