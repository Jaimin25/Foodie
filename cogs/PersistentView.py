import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import play, admin

class PlayPersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.member)

    @discord.ui.button(label='Play', style=discord.ButtonStyle.green, custom_id='persistent_view:play_btn')
    async def play_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await play.Play.play_btn_callback(self, interaction)
