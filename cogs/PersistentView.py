import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import play, profile, upgrades

class ButtonOnCooldown(commands.CommandError):
  def __init__(self, retry_after: float):
    self.retry_after = retry_after

def key(interaction: discord.Interaction):
  return interaction.user

class PlayPersistentView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)
        self.cd = commands.CooldownMapping.from_cooldown(1, 10, key)

    def key(interaction: discord.Interaction):
        return interaction.user

    @discord.ui.button(label='Serve', style=discord.ButtonStyle.blurple, custom_id='persistent_view:serve_btn')
    async def serve_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        retry_after = self.cd.update_rate_limit(interaction)

        if retry_after:
            cd_embed = discord.Embed(title=interaction.user.name, colour=0xfee3a8)
            cd_embed.add_field(name=f"Cooldown",
                               value=f":exclamation: **{interaction.user.name}**, You're on cooldown for {round(error.retry_after, 2)}s!")

            return await interaction.response.edit_message(embed=cd_embed)

        await play.Play.serve_btn_callback(self, interaction, "edit")

    @discord.ui.button(label='Back', style=discord.ButtonStyle.red, custom_id='persistent_view:back_btn')
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await profile.Profile.send_profile_view(self, interaction)

class ProfilePersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd = commands.CooldownMapping.from_cooldown(1, 10, key)

    async def interaction_check(self, interaction: discord.Interaction):
        retry_after = self.cd.update_rate_limit(interaction)

        if retry_after:
            raise ButtonOnCooldown(retry_after)

            # not rate limited
        return True

    async def on_error(self, interaction: discord.Interaction, error: Exception, item: discord.ui.Item):
        if isinstance(error, ButtonOnCooldown):

            cd_embed = discord.Embed(title=interaction.user.name, colour=0xfee3a8)
            cd_embed.add_field(name=f"Cooldown",
                                    value=f":exclamation: **{interaction.user.name}**, You're on cooldown for {round(error.retry_after,2)}s!")

            await interaction.response.edit_message(embed=cd_embed)
        else:
            # call the original on_error, which prints the traceback to stderr
            await super().on_error(interaction, error, item)

    @discord.ui.button(label='Serve', style=discord.ButtonStyle.blurple, custom_id='persistent_view:serve_btn')
    async def serve_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await play.Play.serve_btn_callback(self, interaction, "edit")
        self.remove_item(self.upgrades_btn)

    @discord.ui.button(label='Upgrades', style=discord.ButtonStyle.green, custom_id='persistent_view:upgrades_btn')
    async def upgrades_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        account = await profile.Profile.check_for_account(self, interaction)

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.edit_message(embed=em, view=v)
        elif account[0] is True:
            await upgrades.Upgrades.upgrades_btn_callback(self, interaction)

class UpgradesPersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.member)

    @discord.ui.button(emoji='1️⃣', style=discord.ButtonStyle.grey, custom_id='persistent_view:kitchen_upgrade_btn', row=1)
    async def kitchen_upgrade_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        account = await profile.Profile.check_for_account(self, interaction)

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.edit_message(embed=em, view=v)
        elif account[0] is True:
            await upgrades.Upgrades.kitchen_upgrade_btn_callback(self, interaction)

    @discord.ui.button(emoji='2️⃣', style=discord.ButtonStyle.grey, custom_id='persistent_view:staff_upgrade_btn', row=1)
    async def staff_upgrade_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        account = await profile.Profile.check_for_account(self, interaction)

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.edit_message(embed=em, view=v)
        elif account[0] is True:
            await upgrades.Upgrades.staff_upgrade_btn_callback(self, interaction)

    @discord.ui.button(emoji='3️⃣', style=discord.ButtonStyle.grey, custom_id='persistent_view:farm_upgrade_btn', row=1)
    async def farm_upgrade_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        account = await profile.Profile.check_for_account(self, interaction)

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.edit_message(embed=em, view=v)
        elif account[0] is True:
            await upgrades.Upgrades.farm_upgrade_btn_callback(self, interaction)

    @discord.ui.button(label='Back', style=discord.ButtonStyle.red, custom_id='persistent_view:back_btn', row=2)
    async def back_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await profile.Profile.send_profile_view(self, interaction)

class StartPersistentView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.cd_mapping = commands.CooldownMapping.from_cooldown(1, 30, commands.BucketType.member)

    @discord.ui.button(label='Start', style=discord.ButtonStyle.blurple, custom_id='persistent_view:start_btn')
    async def start_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        await profile.Profile.start_btn_callback(self, interaction)