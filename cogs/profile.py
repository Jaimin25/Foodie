import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import PersistentView, helper
import random
import traceback
import time

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description="View your profile")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def profile(self, interaction: discord.Interaction) -> None:
        account = await Profile.check_for_account(self, interaction)

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.send_message(embed=em, view=v)
        elif account[0] is True:

            profile_view = await Profile.set_profile_view(self, interaction)
            await interaction.response.send_message(embed=profile_view)

    async def send_profile_view(self, interaction):
        profile_view = await Profile.set_profile_view(self, interaction)
        await interaction.response.edit_message(embed=profile_view, v=self)

    async def set_profile_view(self, interaction):
        client = interaction.client
        user = interaction.user

        profile_query = "SELECT * FROM profiles WHERE userid = $1"
        profile_data = await client.db.fetchrow(profile_query, user.id)

        name = profile_data[1]
        location = ":flag_us: New York, US" if profile_data[2] == 1 else ""
        balance = profile_data[3]
        clean = ":white_check_mark: Clean" if profile_data[4] == 1 else ":bangbang: Not Clean"
        tax = ":white_check_mark: Payed" if profile_data[5] == 1 else ":bangbang: Pending"
        level = profile_data[6]
        exp = profile_data[7]
        total_exp = profile_data[8]
        prestige = profile_data[9]
        buff = round(profile_data[10], 3)

        profile_embed = discord.Embed(title=interaction.user.name, color=0xfee3a8)
        profile_embed.set_thumbnail(url=interaction.user.avatar)
        profile_embed.add_field(name="Location", value=f"{location}", inline=False)
        profile_embed.add_field(name="Prestige", value=f":crown:  {prestige}", inline=False)
        profile_embed.add_field(name="Level", value=f":arrow_up: {level} ({exp}/{total_exp})", inline=False)
        profile_embed.add_field(name="Money", value=f":coin: ${balance:,}", inline=False)
        profile_embed.add_field(name="Clean", value=f"{clean}", inline=False)
        profile_embed.add_field(name="Tax", value=f"{tax}", inline=False)
        profile_embed.add_field(name="Total Multi", value=f":bar_chart: x{buff}", inline=False)

        return profile_embed

    async def get_user_details(self, interaction):
        client = interaction.client
        user = interaction.user

        profile_query = "SELECT * FROM profiles WHERE userid = $1"
        profile_data = await client.db.fetchrow(profile_query, user.id)

        name = profile_data[1]
        location = profile_data[2]
        balance = profile_data[3]
        clean = profile_data[4]
        tax = profile_data[5]
        level = profile_data[6]
        exp = profile_data[7]
        total_exp = profile_data[8]
        prestige = profile_data[9]
        buff = round(profile_data[10], 3)

        return name, location, balance, clean, tax, level, exp, total_exp, prestige, buff

    async def check_for_account(self, interaction):
        user = interaction.user
        fetch_account_query = "SELECT * FROM profiles WHERE userid = $1"

        user_id = user.id

        interaction.client.user_account = await interaction.client.db.fetchrow(
            fetch_account_query, (user_id))

        v = PersistentView.StartPersistentView()

        acc_embed = discord.Embed(title="Foodie", color=0xfee3a8)
        acc_embed.set_author(name=user.name)
        acc_embed.set_thumbnail(url=interaction.client.user.avatar)
        acc_embed.description = f"Hello **{user.name}**, You do not have a profile, click on *Start* to create one!"

        if interaction.client.user_account is None:
            return False, acc_embed, v
        else:
            return True, acc_embed, v

    async def start_btn_callback(self, interaction: discord.Interaction):
        account = await Profile.check_for_account(self, interaction)

        if account[0] is False:
            await interaction.response.send_modal(Feedback())
        elif account[0] is True:
            await Profile.send_profile_view(self, interaction)


class Feedback(discord.ui.Modal, title='Restaurant Name'):

    name = discord.ui.TextInput(
        label='Name',
        placeholder='Enter a name for you restaurant here...',
        min_length= 3,
        max_length= 10
    )

    async def on_submit(self, interaction: discord.Interaction):
        await self.create_account(self.name.value, interaction.user, interaction)

    async def create_account(self, name, user, interaction):
        client = interaction.client
        fetch_account_query = "SELECT * FROM profiles WHERE userid = $1"

        user_id = user.id

        client.user_account = await client.db.fetchrow(
            fetch_account_query, (user_id))

        kitchen_upg = await helper.kitchen_upgrade()
        staff_upg = await helper.staff_upgrade()
        current_buff = 0.000

        for x in kitchen_upg:
            current_buff = current_buff + float(kitchen_upg[x]['buff'])

        for x in staff_upg:
            current_buff = current_buff + float(staff_upg[x]['buff'])

        if client.user_account is None:

            create_account_query = "INSERT INTO profiles(userid, name, location, balance, clean, tax, level, exp, total_exp, prestige, buff, created_at) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)"
            await client.db.execute(create_account_query,
                                    (user.id),
                                    str(name), 1, 10000, 1, 1, 1, 0, 250,
                                    0, round(1+current_buff, 3), (time.time()))

        await Profile.send_profile_view(self, interaction)

async def setup(client):
    await client.add_cog(Profile(client))