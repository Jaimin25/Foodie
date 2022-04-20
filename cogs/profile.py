import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import PersistentView
import random

class Profile(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def profile_view(self, interaction):
        profile_embed = discord.Embed(title=interaction.user.name)
        profile_embed.set_thumbnail(url=interaction.user.avatar)
        profile_embed.add_field(name="Level", value="1 (5/500)", inline=False)
        profile_embed.add_field(name="Money", value=":coin: $23,445,667,454,768", inline=False)
        profile_embed.add_field(name="Total Multi", value="x5.66", inline=False)

        v = PersistentView.ProfilePersistentView()

        await interaction.response.edit_message(embed=profile_embed, view=v)

async def setup(client):
    await client.add_cog(Profile(client))