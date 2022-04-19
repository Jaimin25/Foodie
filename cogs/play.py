import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands

class Play(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description="Start Playing")
    @app_commands.guilds(discord.Object(955385300513878026))
    async def play(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message("Play!")

async def setup(client):
    await client.add_cog(Play(client))