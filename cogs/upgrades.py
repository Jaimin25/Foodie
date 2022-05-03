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
        await Upgrades.refresh_embed_view(self, interaction, "kitchen", "edit")


    async def staff_upgrade_btn_callback(self, interaction):
        await Upgrades.refresh_embed_view(self, interaction, "staff", "edit")

    async def farm_upgrade_btn_callback(self, interaction):

        await Upgrades.refresh_embed_view(self, interaction, "farm", "edit")

    async def refresh_embed_view(self, interaction, type, t=None):
        v = PersistentView.UpgradesPersistentView()
        v.back_btn.row = 1
        v.clear_items()
        upg_embed = discord.Embed(title=type.capitalize(), color=0xfee3a8)
        upg_embed.set_author(name=interaction.user.name)
        user = interaction.user

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
        c = 0
        n = 0
        sum = 0

        for x in upg:

            name = x.capitalize()
            upg_data = await interaction.client.db.fetch("SELECT * FROM upgrades WHERE userid = $1 AND name = $2",
                                                         user.id, x.capitalize())

            max_upg = upg[x]['max_upgrades']
            cost = upg[x]['cost']
            buff = upg[x]['buff']

            sum = Upgrades.summa(self, int(max_upg), int(cost))
            n = n + sum

            amount = 0
            c = cost
            bufff = buff

            if len(upg_data) > 0 and str(upg_data[0]['name']).lower() == x.lower():
                amount = upg_data[0]['amount']
                c = int(c)+(int(amount)*250)
                bufff = round(float(bufff) + (float(bufff) * float(amount)), 3)

            if type == "farm":

                    if x != "storage":
                        max_buff = max_buff + float(max_upg) * float(buff)
                        current_buff = current_buff + float(bufff)

                        upg_embed.add_field(name=f"{name} - {amount}/{max_upg}",
                                              value=f"Cost: ${int(c):,}\nBuff: +{buff}", inline=False)
                    else:
                        max_storage = max_storage + float(max_upg) * float(buff)
                        upg_embed.add_field(name=f"{name} - {amount}/{max_upg}",
                                            value=f"Cost: ${int(c):,}\nSpace: +{buff}", inline=False)
                    upg_embed.set_footer(
                    text=f"Current Production Buff: +{round(current_buff, 3)}\nMax Production Buff: +{max_buff}\nMax Storage Space: {int(max_storage):,}\nMax Cost: ${n:,}")

            else:

                max_buff = max_buff + float(max_upg) * float(buff)
                current_buff = current_buff + float(bufff)

                upg_embed.add_field(name=f"{name} - {amount}/{max_upg}",
                                            value=f"Cost: ${int(c):,}\nBuff: +{bufff}", inline=False)

                upg_embed.set_footer(text=f"Current Buff: +{round(current_buff, 3)}\nMax Buff: +{round(max_buff, 3)}\nMax Cost: ${n:,}")

        if t is not None:
            if t == "edit":
                await interaction.response.edit_message(embed=upg_embed, view=v)
            elif t == "send":
                await interaction.response.send_message(embed=upg_embed, view=v)
        else:
            await interaction.response.edit_message(embed=upg_embed, view=v)

    def summa(self, max_upg, cost):
        c=0
        sum = 0
        while max_upg:
            if c >= int(max_upg):
                break
            c += 1
            n = int(cost)
            n = n + int(c) * 250
            sum = sum + n
        return sum

    @app_commands.command(description="Buy Kitchen Items")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.choices(item=[
        Choice(name='Stove', value=1),
        Choice(name='Oven', value=2),
        Choice(name='Microwave', value=3),
        Choice(name='Dishwasher', value=4),
        Choice(name='Utensils', value=5)
    ])
    async def kitchenbuy(self, interaction, item: Choice[int]) -> None:
        account = await profile.Profile.check_for_account(self, interaction)

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.send_message(embed=em, view=v)

        v = View()
        buy_btn = Button()
        buy_btn.label = "Buy"
        buy_btn.style = discord.ButtonStyle.blurple

        v.add_item(buy_btn)

        success_embed = await self.refresh_upg_embed(interaction, item, "kitchen")

        await interaction.response.send_message(embed=success_embed, view=v)

        async def buy_button_callback(interaction: discord.Interaction):
            success_embed = await self.refresh_upg_embed(interaction, item, "kitchen")
            await interaction.response.send_message(embed=success_embed, view=v)

        buy_btn.callback = buy_button_callback

    @app_commands.command(description="Hire Staff")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.choices(item=[
        Choice(name='Manager', value=1),
        Choice(name='Waiter', value=2),
        Choice(name='Cheff', value=3),
        Choice(name='Cook', value=4),
        Choice(name='Busperson', value=5),
        Choice(name='Receptionist', value=6)
    ])
    async def staffhire(self, interaction, item: Choice[int]) -> None:
        account = await profile.Profile.check_for_account(self, interaction)

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.send_message(embed=em, view=v)

        v = View()
        hire_btn = Button()
        hire_btn.label = "Hire"
        hire_btn.style = discord.ButtonStyle.blurple

        v.add_item(hire_btn)

        success_embed = await self.refresh_upg_embed(interaction, item, "staff")

        await interaction.response.send_message(embed=success_embed, view=v)

        async def hire_button_callback(interaction: discord.Interaction):
            success_embed = await self.refresh_upg_embed(interaction, item, "staff")
            await interaction.response.send_message(embed=success_embed, view=v)

        hire_btn.callback = hire_button_callback

    @app_commands.command(description="Buy Kitchen Items")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 3.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.choices(item=[
        Choice(name='Farmland', value=1),
        Choice(name='Machines', value=2),
        Choice(name='Storage', value=3),
        Choice(name='Fertilizers', value=4),
        Choice(name='Seed', value=5)
    ])
    async def farmbuy(self, interaction, item: Choice[int]) -> None:
        account = await profile.Profile.check_for_account(self, interaction)

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.send_message(embed=em, view=v)

        v = View()
        buy_btn = Button()
        buy_btn.label = "Buy"
        buy_btn.style = discord.ButtonStyle.blurple

        v.add_item(buy_btn)

        success_embed = await self.refresh_upg_embed(interaction, item, "farm")

        await interaction.response.send_message(embed=success_embed, view=v)

        async def buy_button_callback(interaction: discord.Interaction):
            success_embed = await self.refresh_upg_embed(interaction, item, "farm")
            await interaction.response.send_message(embed=success_embed, view=v)

        buy_btn.callback = buy_button_callback

    async def refresh_upg_embed(self, interaction, item, type):

            if item is not None:
                if type == "kitchen":
                    upg = await helper.kitchen_upgrade()
                elif type == "staff":
                    upg = await helper.staff_upgrade()
                else:
                    upg = await helper.farm_upgrade()

                user = interaction.user
                upg_data = await self.client.db.fetchrow("SELECT * FROM upgrades WHERE userid = $1 AND name = $2", user.id,
                                                         item.name)
                user_data = await profile.Profile.get_user_details(self, interaction)

                farm_data = await interaction.client.db.fetchrow("SELECT * FROM farm WHERE userid = $1", user.id)
                storage_space = 10000 if farm_data is None else farm_data[2]

                bal = int(user_data[2])
                current_buff = user_data[9]

                current_rate = 2 if farm_data is None else farm_data[1]

                amount = 0 if upg_data is None else upg_data[3]
                success_embed = discord.Embed(title="Kitchen" if type == "kitchen" else "Staff" if type == "staff" else "Farm", color=0xfee3a8)
                for x in upg:
                    if x == item.name.lower():

                        cost = int(upg[x]["cost"]) + int(amount * 250)
                        max_upgrades = int(upg[x]["max_upgrades"])
                        buff = upg[x]["buff"]

                if bal >= cost:
                    if amount < max_upgrades:
                        if upg_data is None:
                            query = "INSERT INTO upgrades(userid, type, name, amount) VALUES ($1, $2, $3, $4)"
                            await self.client.db.execute(query, user.id, "kitchen", item.name, amount+1)
                        else:
                            query = "UPDATE upgrades SET amount = $1 WHERE userid = $2 AND name = $3"
                            await self.client.db.execute(query, amount+1, user.id, item.name)

                        if type == "farm":
                            if farm_data is None:
                                farm_query = "INSERT INTO farm(userid, production, storage, amount) VALUES($1, $2, $3, $4)"
                                await interaction.client.db.execute(farm_query, user.id, 2, 10000, 10000)

                            if item.name == "Storage":
                                query = "UPDATE farm SET storage = $1 WHERE userid = $2"
                                await self.client.db.execute(query, storage_space+5000, user.id)
                            else:
                                query = "UPDATE farm SET production = $1 WHERE userid = $2"

                                await self.client.db.execute(query, float(current_rate)+float(buff), user.id)

                            query = "UPDATE profiles SET balance = $1 WHERE userid = $2"
                            await self.client.db.execute(query, bal - cost,
                                                         user.id)
                        else:

                            query = "UPDATE profiles SET balance = $1, buff = $2 WHERE userid = $3"
                            await self.client.db.execute(query, bal-cost, float(current_buff)+(float(buff)),user.id)

                        if type == "staff":
                            success_embed.add_field(name=f":small_orange_diamond: {item.name} - {amount+1}/{max_upgrades}",
                                                    value=f"Succefully hired **{item.name}** for **${int(cost):,}** and got **+{round(float(buff), 3)}** in total multi.",
                                                    inline=False)
                        elif item.name == "Storage":
                            success_embed.add_field(name=f":small_orange_diamond: {item.name} - {amount+1}/{max_upgrades}",
                                                    value=f"Succefully bought **{item.name}** for **${int(cost):,}** and got **+{round(float(buff), 3)}** in total storage space.",
                                                    inline=False)
                        else:
                            success_embed.add_field(name=f":small_orange_diamond: {item.name} - {amount+1}/{max_upgrades}",
                                                value=f"Succefully bought **{item.name}** for **${int(cost):,}** and got **+{round(float(buff), 3)}** in total multi.",
                                                inline=False)
                        success_embed.set_footer(text=f"Balance: {(bal-cost):,}")
                    else:
                        success_embed.add_field(name=f":white_check_mark: {item.name}",
                                                value=f"**{interaction.user.name}**, This item is already maxed!")

                else:
                    if type == "staff":
                        success_embed.add_field(name=f"{item.name}", value=f":exclamation: **{interaction.user.name}**, You do not have enough money to hire this person.")
                    elif type == "kitchen":
                        success_embed.add_field(name=f"{item.name}", value=f":exclamation: **{interaction.user.name}**, You do not have enough money to buy this item.")
                    elif type == "farm":
                        success_embed.add_field(name=f"{item.name}", value=f":exclamation: **{interaction.user.name}**, You do not have enough money to buy this item.")

                    success_embed.set_footer(text=f"Cost: ${int(cost):,}\nBalance: ${int(bal):,}")

            return success_embed

async def setup(client):
    await client.add_cog(Upgrades(client))