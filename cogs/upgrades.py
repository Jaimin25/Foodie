import discord
from discord.ext import commands
from discord.ui import Button, View, Select
from discord import app_commands
from cogs import helper, accounts, profile
import time, datetime
from datetime import timedelta
from discord.app_commands import Choice


class Upgrades(commands.Cog):
    def __init__(self, client):
        self.client = client

    @app_commands.command(description="Check your upgrades")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def upgrades(self, interaction: discord.Interaction):
        client = interaction.client
        user = interaction.client

        profile_data = await profile.Profile.get_user_details(self, interaction)

        btn_one = Button(emoji="1️⃣")
        btn_two = Button(emoji="2️⃣")

        upg_view = View()
        upg_view.add_item(btn_one)
        upg_view.add_item(btn_two)

        upgrades_embed = discord.Embed(title="Upgrades", color=client.embed_color)
        upgrades_embed.set_author(name=interaction.user.name)
        upgrades_embed.add_field(name=":one: Kitchen", value="Upgrade kitchen stuff", inline=False)
        upgrades_embed.add_field(name=":two: Staff", value="Hire new staffs", inline=False)

        async def kitchen_upgrade_btn_callback(interaction: discord.Interaction):
            await self.refresh_embed_view(interaction, "kitchen", upg_view, "edit")

        btn_one.callback = kitchen_upgrade_btn_callback

        async def staff_upgrade_btn_callback(interaction: discord.Interaction):
            await self.refresh_embed_view(interaction, "staff", upg_view, "edit")

        btn_two.callback = staff_upgrade_btn_callback

        await interaction.response.send_message(embed=upgrades_embed, view=upg_view)

    async def refresh_embed_view(self, interaction, type, v: View, t=None):

        upg_embed = discord.Embed(title=type.capitalize(), color=0xfee3a8)
        upg_embed.set_author(name=interaction.user.name)
        user = interaction.user

        profile_date = await profile.Profile.get_user_details(self, interaction)

        income = profile_date[3]
        balance = profile_date[2]

        if type == "kitchen":
            upg = await helper.kitchen_upgrade()
            v.children[0].disabled = True
            v.children[1].disabled = False
        elif type == "staff":
            upg = await helper.staff_upgrade()
            v.children[0].disabled = False
            v.children[1].disabled = True

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
            n = n+sum
            amount = 0
            c = cost
            bufff = buff

            if len(upg_data) > 0 and str(upg_data[0]['name']).lower() == x.lower():
                amount = upg_data[0]['amount']
                c = int(c) + (int(amount) * int(c))
                bufff = round(float(bufff) + (float(bufff) * float(amount)), 3)
            else:
                bufff = 0

            max_buff = max_buff + float(max_upg) * float(buff)
            current_buff = current_buff + float(bufff)

            upg_embed.add_field(name=f"__{name}__ - `{amount}/{max_upg}`",
                                    value=f"Cost: ${int(c):,}\nIncome: +${buff}/min\nID: `{x.lower()}`", inline=False)

            upg_embed.set_footer(text=f"💵 Income: ${income:,}/min\n💰 Balance: ${balance:,}")

        if t is not None:
            if t == "edit":
                await interaction.response.edit_message(embed=upg_embed, view=v)

    def summa(self, max_upg, cost):
        c=0
        sum = 0

        sum = max_upg*cost

        return sum

    @app_commands.command(description="Check your upgrades")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        amount='Amount of items you want to buy',
        item='Item to buy'
    )
    @app_commands.choices(item=[
        Choice(name='Stove', value=1),
        Choice(name='Utensils', value=2),
        Choice(name='Oven', value=3),
        Choice(name='Microwave', value=4),
        Choice(name='Dishwasher', value=5)
    ])
    async def buy(self, interaction: discord.Interaction, item: Choice[int], amount: int):
        success_embed = await self.refresh_upg_embed(interaction, item, "kitchen", amount)
        await interaction.response.send_message(embed=success_embed)

    @app_commands.command(description="Check your upgrades")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    @app_commands.describe(
        amount='Amount of staff you want to hire',
        item='Staff to hire'
    )
    @app_commands.choices(item=[
        Choice(name='Waiter', value=1),
        Choice(name='Busperson', value=2),
        Choice(name='Cheff', value=3),
        Choice(name='Cook', value=4),
        Choice(name='Receptionist', value=5),
        Choice(name='Manager', value=6)
    ])
    async def hire(self, interaction: discord.Interaction, item: Choice[int], amount: int):
        success_embed = await self.refresh_upg_embed(interaction, item, "staff", amount)
        await interaction.response.send_message(embed=success_embed)

    async def refresh_upg_embed(self, interaction, item, type, amt):

            if item is not None:
                if type == "kitchen":
                    upg = await helper.kitchen_upgrade()
                elif type == "staff":
                    upg = await helper.staff_upgrade()

                user = interaction.user
                upg_data = await self.client.db.fetchrow("SELECT * FROM upgrades WHERE userid = $1 AND name = $2", user.id,
                                                         item.name)
                user_data = await profile.Profile.get_user_details(self, interaction)

                bal = int(user_data[2])
                income = int(user_data[3])

                amount = 0 if upg_data is None else upg_data[3]

                success_embed = discord.Embed(title="Kitchen" if type == "kitchen" else "Staff", color=interaction.client.embed_color)

                for x in upg:
                    if x == item.name.lower():
                        cost = int(upg[x]["cost"]) * int(amount+amt)
                        max_upgrades = int(upg[x]["max_upgrades"])
                        buff = int(upg[x]["buff"])*int(amount+amt)

                if amount < max_upgrades:
                    amount = amount + amt

                    if amt == 0:
                        success_embed.add_field(name=f"{item.name}",
                                                value=f":exclamation: **{interaction.user.name}**, Amount must be greater than 0.")
                        return success_embed

                    if amount > max_upgrades:
                        success_embed.add_field(name=f"{item.name}",
                                                value=f":exclamation: **{interaction.user.name}**, You are exceeding the maximum upgrade amount for this item.")
                        return success_embed

                    if bal >= cost:
                        if upg_data is None:
                            query = "INSERT INTO upgrades(userid, type, name, amount) VALUES ($1, $2, $3, $4)"
                            await self.client.db.execute(query, user.id, type, item.name, amount)
                        else:
                            query = "UPDATE upgrades SET amount = $1 WHERE userid = $2 AND name = $3"
                            await self.client.db.execute(query, amount, user.id, item.name)


                        query = "UPDATE profiles SET balance = $1, income = $2 WHERE userid = $3"
                        await self.client.db.execute(query, bal-cost, income+int(buff),user.id)

                        if type == "staff":
                            success_embed.add_field(name=f":small_orange_diamond: {item.name} - {amount}/{max_upgrades}",
                                                    value=f"Succefully hired **{item.name}** for **${int(cost):,}** and got **+${(int(buff)):,}** in total income.",
                                                    inline=False)
                        else:
                            success_embed.add_field(name=f":small_orange_diamond: {item.name} - {amount}/{max_upgrades}",
                                                value=f"Succefully bought **{item.name}** for **${int(cost):,}** and got **+${(int(buff)):,}** in total income.",
                                                inline=False)
                        success_embed.set_footer(text=f"💰 Balance: {(bal-cost):,}")


                    else:
                        if type == "staff":
                            success_embed.add_field(name=f"{item.name}", value=f":exclamation: **{interaction.user.name}**, You do not have enough money to hire this person.")
                        else:
                            success_embed.add_field(name=f"{item.name}", value=f":exclamation: **{interaction.user.name}**, You do not have enough money to buy this item.")

                        success_embed.set_footer(text=f"💵 Cost: ${int(cost):,}\n💰 Balance: ${int(bal):,}")
                else:
                    success_embed.add_field(name=f":white_check_mark: {item.name}",
                                            value=f"**{interaction.user.name}**, This item is already maxed!")

            return success_embed

async def setup(client):
    await client.add_cog(Upgrades(client))