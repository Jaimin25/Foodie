import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import play, profile, upgrades

class PlayPersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.member)

    @discord.ui.button(label='Serve', style=discord.ButtonStyle.green, custom_id='persistent_view:serve_btn')
    async def serve_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await play.Play.serve_btn_callback(self, interaction)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.red, custom_id='persistent_view:back_btn')
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await profile.Profile.profile_view(self, interaction)

class ProfilePersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.member)

    @discord.ui.button(label='Serve', style=discord.ButtonStyle.green, custom_id='persistent_view:serve_btn')
    async def serve_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await play.Play.serve_btn_callback(self, interaction)

    @discord.ui.button(label='Upgrades', style=discord.ButtonStyle.green, custom_id='persistent_view:upgrades_btn')
    async def upgrades_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await upgrades.Upgrades.upgrades_btn_callback(self, interaction)

class UpgradesPersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.member)

    @discord.ui.button(emoji='1️⃣', style=discord.ButtonStyle.grey, custom_id='persistent_view:kitchen_upgrade_btn', row=1)
    async def kitchen_upgrade_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(emoji='2️⃣', style=discord.ButtonStyle.grey, custom_id='persistent_view:staff_upgrade_btn', row=1)
    async def staff_upgrade_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(emoji='3️⃣', style=discord.ButtonStyle.grey, custom_id='persistent_view:farm_upgrade_btn', row=1)
    async def farm_upgrade_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(emoji='4️⃣', style=discord.ButtonStyle.grey, custom_id='persistent_view:four_upgrade_btn',
                       row=1)
    async def sour_upgrade_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(emoji='5️⃣', style=discord.ButtonStyle.grey, custom_id='persistent_view:five_upgrade_btn', row=1)
    async def five_upgrade_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(label='Back', style=discord.ButtonStyle.red, custom_id='persistent_view:back_btn', row=2)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await profile.Profile.profile_view(self, interaction)
