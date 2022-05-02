from typing import List, Union, Optional

import discord
from discord.ui import Button, View, Select
from discord.ext import commands, tasks
from discord import app_commands
from cogs import PersistentView, profile, helper
import random
from discord.app_commands import Choice

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
        v.clear_items()
        v.add_item(v.kitchen_upgrade_btn)
        v.add_item(v.staff_upgrade_btn)
        v.add_item(v.farm_upgrade_btn)
        v.add_item(v.back_btn)

        await interaction.response.edit_message(embed=profile_embed, view=v)

    async def kitchen_upgrade_btn_callback(self, interaction):
        await Upgrades.refresh_embed_view(self, interaction, "kitchen")


    async def staff_upgrade_btn_callback(self, interaction):
        await Upgrades.refresh_embed_view(self, interaction, "staff")

    async def farm_upgrade_btn_callback(self, interaction):

        await Upgrades.refresh_embed_view(self, interaction, "farm")

    async def refresh_embed_view(self, interaction, type):
        v = PersistentView.UpgradesPersistentView()
        v.back_btn.row = 1
        v.clear_items()
        upg_embed = discord.Embed(title=type.capitalize(), color=0xfee3a8)
        upg_embed.set_author(name=interaction.user.name)

        if type == "kitchen":
            upg = await helper.kitchen_upgrade()
        elif type == "staff":
            upg = await helper.staff_upgrade()
        else:
            upg = await helper.farm_upgrade()

            max_storage = 0

        v.add_item(v.back_btn)

        max_buff = 0.000
        current_buff = 0.000

        for x in upg:


            name = x.capitalize()

            max_upg = upg[x]['max_upgrades']
            cost = upg[x]['cost']
            buff = upg[x]['buff']

            if type == "farm":

                    if x != "storage":
                        max_buff = max_buff + float(max_upg) * float(buff)
                        current_buff = current_buff + float(buff)
                        upg_embed.add_field(name=f"{name} - 0/{max_upg}",
                                              value=f"Cost: ${cost}\nBuff: +{buff}", inline=False)
                    else:
                        max_storage = max_storage + float(max_upg) * float(buff)
                        upg_embed.add_field(name=f"{name} - 0/{max_upg}",
                                            value=f"Cost: ${cost}\nSpace: +{buff}", inline=False)
                    upg_embed.set_footer(
                    text=f"Current Production Buff: +{round(current_buff, 3)}\nMax Production Buff: +{max_buff}\nMax Storage Space: {int(max_storage):,}")

            else:
                max_buff = max_buff + float(max_upg) * float(buff)
                current_buff = current_buff + float(buff)
                upg_embed.add_field(name=f"{name} - 0/{max_upg}",
                                    value=f"Cost: ${cost}\nBuff: +{buff}", inline=False)

                upg_embed.set_footer(text=f"Current Buff: {round(current_buff, 3)}%\nMax Buff: {max_buff}%")

        await interaction.response.edit_message(embed=upg_embed, view=v)

    @app_commands.command(description="Upgrades")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def upgrade(self, interaction) -> None:
        print("opt")

async def setup(client):
    await client.add_cog(Upgrades(client))