import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import app_commands
from cogs import helper
import time

class Accounts(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description="Create a profile")
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def start(self, interaction: discord.Interaction, name: str) -> None:
        is_acc_created = await self.check_for_account(interaction)

        client = interaction.client
        user = interaction.user

        if is_acc_created:
            return await interaction.response.send_message(content=f"**{user.name}**, You already have an profile!")
        else:
            if not len(name) >= 3 and len(name) > 15:
                return await interaction.response.send_message(content=f"Name must be between 3 to 15 characters.")

            fetch_account_query = "SELECT * FROM profiles WHERE userid = $1"

            user_id = user.id

            client.user_account = await client.db.fetchrow(
                fetch_account_query, (user_id))

            if client.user_account is None:
                create_account_query = "INSERT INTO profiles(userid, name, location, balance, income, clean, tax, prestige, buff, created_at, stars, cookies) VALUES($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12)"
                await client.db.execute(create_account_query,
                                        (user.id),
                                       str(name), 1, 10000, 100, 1, 1,
                                        0, 1, (time.time()), 0, 0)
                await client.db.execute("INSERT INTO cooldowns(userid, income_collected) VALUES($1, $2)", user.id, 1)
                await interaction.response.send_message(content=f"Félicitations **{user.name}**, Your profile has been created!\nView your profile using `/profile`\n`/guide` will help you on how to play! ")

    async def check_for_account(self, interaction):
        user = interaction.user
        fetch_account_query = "SELECT * FROM profiles WHERE userid = $1"

        user_id = user.id

        interaction.client.user_account = await interaction.client.db.fetchrow(
            fetch_account_query, (user_id))

        if interaction.client.user_account is None:
            if interaction.command.name.lower() != "start":
                await interaction.response.send_message(content=f"**{user.name}**, You do not have any profile!\nType `/start [restaurant_name]` to create one.")
                return False
        else:
            return True

async def setup(client):
    await client.add_cog(Accounts(client))