import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import app_commands
from cogs import helper, accounts, profile
import time, datetime
from datetime import timedelta

class Menu(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description="Buy some slots for menu from here")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def menuslots(self, interaction: discord.Interaction):
        client = interaction.client
        user = interaction.user

        profile_date = await profile.Profile.get_user_details(self, interaction)

        income = profile_date[3]
        balance = profile_date[2]

        slot_2_val = "Cap: $2,500,000\nCost: $1,500,000" if income >= 1000 else ":lock: Unlocked at `$1,000/sec` income"
        slot_3_val = "Cap: $5,000,000\nCost: $2,500,000" if income >= 1000 else ":lock: Unlocked at `$2,000/sec` income"
        slot_4_val = "Cap: $7,500,000\nCost: $5,000,000" if income >= 1000 else ":lock: Unlocked at `$5,000/sec` income"
        slot_5_val = "Cap: $10,000,000\nCost: $9,000,000" if income >= 1000 else ":lock: Unlocked at `$10,000/sec` income"

        menu_embed = discord.Embed(title="Menu Slots", color=client.embed_color)
        menu_embed.add_field(name="Slot 1", value="Cap: $1,000,000\nCost: $500,000", inline=False)
        menu_embed.add_field(name="Slot 2", value=slot_2_val, inline=False)
        menu_embed.add_field(name="Slot 3", value=slot_3_val, inline=False)
        menu_embed.add_field(name="Slot 4", value=slot_4_val, inline=False)
        menu_embed.add_field(name="Slot 5", value=slot_5_val, inline=False)

        menu_embed.set_footer(text=f"\n💵 Income: ${income:,}/min\n💰 Balance: ${balance:,}")

        await interaction.response.send_message(embed=menu_embed)

async def setup(client):
    await client.add_cog(Menu(client))