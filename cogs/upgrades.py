import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import PersistentView, profile, helper
import random

class Upgrades(commands.Cog):
    def __init__(self, client):
        self.client = client

    async def upgrades_btn_callback(self, interaction):
        profile_embed = discord.Embed(title="Upgrades", color=0xfee3a8)
        profile_embed.set_author(name=interaction.user.name)
        profile_embed.add_field(name=":one: Kitchen", value="Upgrade kitchen stuff", inline=False)
        profile_embed.add_field(name=":two: Staff", value="Hire new staffs", inline=False)
        profile_embed.add_field(name=":three: Farm", value="Upgrade/Buy farm equipments", inline=False)

        v = PersistentView.UpgradesPersistentView()

        await interaction.response.edit_message(embed=profile_embed, view=v)

    async def kitchen_upgrade_btn_callback(self, interaction):

        v = PersistentView.UpgradesPersistentView()
        v.clear_items()
        v.add_item(v.back_btn)

        kitchen_upg_embed = discord.Embed(title="Kitchen", color=0xfee3a8)
        kitchen_upg_embed.set_author(name=interaction.user.name)


        upg = await helper.kitchen_upgrade()
        max_buff = 0.000
        current_buff = 0.000

        for x in upg:
            kitchen_upg_embed.add_field(name=f"{x.capitalize()} - 0/{upg[x]['max_upgrades']}", value=f"Cost: ${int(upg[x]['cost']):,}\nBuff: {upg[x]['buff']}%", inline=False)
            max_buff = max_buff+float(upg[x]["max_upgrades"])*float(upg[x]['buff'])
            current_buff = current_buff + float(upg[x]['buff'])

        kitchen_upg_embed.set_footer(text=f"Current Buff: {round(current_buff, 3)}%\nMax Buff: {max_buff}%")

        await interaction.response.edit_message(embed=kitchen_upg_embed, view=v)


    async def staff_upgrade_btn_callback(self, interaction):

        v = PersistentView.UpgradesPersistentView()
        v.clear_items()
        v.add_item(v.back_btn)

        staff_upg_embed = discord.Embed(title="Staff", color=0xfee3a8)
        staff_upg_embed.set_author(name=interaction.user.name)

        upg = await helper.staff_upgrade()
        max_buff = 0.000
        current_buff = 0.000

        for x in upg:
            staff_upg_embed.add_field(name=f"{x.capitalize()} - 0/{upg[x]['max_upgrades']}",
                                        value=f"Cost: ${upg[x]['cost']}\nBuff: {upg[x]['buff']}%", inline=False)
            max_buff = max_buff + float(upg[x]["max_upgrades"]) * float(upg[x]['buff'])
            current_buff = current_buff + float(upg[x]['buff'])

        staff_upg_embed.set_footer(text=f"Current Buff: {round(current_buff, 3)}%\nMax Buff: {max_buff}%")

        await interaction.response.edit_message(embed=staff_upg_embed, view=v)

async def setup(client):
    await client.add_cog(Upgrades(client))