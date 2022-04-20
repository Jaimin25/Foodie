import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import PersistentView, profile
import random

class Play(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def serve_btn_callback(self, interaction):
        bucket = self.cd_mapping.get_bucket(interaction.message)
        retry_after = bucket.update_rate_limit()

        v = PersistentView.PlayPersistentView()

        play_embed = discord.Embed(title=f"{interaction.user.name}")
        f1 = round((random.randint(5, 20)))
        f2 = round((random.randint(5, 20)))
        f3 = round((random.randint(5, 15)))
        xp = round((random.randint(5, 50)))
        play_embed.add_field(name="__Food Served:__",
                             value=f"Hamburger 🍔 x**{f1}** \nFries 🍟  x**{f2}** \n Drinks <:drink:964935572869222430> x**{f3}** \n Exp: **{xp}** xp")

        await interaction.response.edit_message(embed=play_embed, view=v)

    async def upgrades_btn_callback(self, interaction):
        profile_embed = discord.Embed(title=interaction.user.name)
        profile_embed.set_thumbnail(url=interaction.user.avatar)

        v = PersistentView.PlayPersistentView()
        v.clear_items()
        v.add_item(v.back_btn)

        await interaction.response.edit_message(embed=profile_embed, view=v)

    @app_commands.command(description="Start Playing")
    @app_commands.guilds(discord.Object(955385300513878026))
    async def serve(self, interaction: discord.Interaction) -> None:
        play_embed = discord.Embed(title=f"{interaction.user.name}")
        f1 = (0+1)*(random.randint(1,20))
        f2 = (0+1)*(random.randint(1,15))
        xp = (0+1)*(random.randint(1,50))
        play_embed.add_field(name="Food Served:", value=f"🍔 {f1} Hamburger \n <:drink:964935572869222430> {f2} Drinks \n You got {xp} xp.")
        await interaction.response.send_message(embed=play_embed, view=PersistentView.PlayPersistentView())

async def setup(client):
    await client.add_cog(Play(client))