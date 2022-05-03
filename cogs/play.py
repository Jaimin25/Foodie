import datetime

import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import PersistentView, profile
import random
import time

class Play(commands.Cog):
    def __init__(self, client):
        self.client = client
        client.tree.on_error = self.on_app_command_error

    async def serve_btn_callback(self, interaction):

        v = PersistentView.PlayPersistentView()

        play_embed = discord.Embed(title=f"{interaction.user.name}", color=0xfee3a8)
        play_embed.set_thumbnail(url=interaction.client.user.avatar)

        play_embed.set_footer(text="test",icon_url=interaction.user.avatar)

        details = await profile.Profile.get_user_details(self, interaction)
        buff = details[9]

        f1 = round((random.randint(5, 20))*buff)
        f2 = round((random.randint(5, 20))*buff)
        f3 = round((random.randint(5, 15))*buff)
        xp = round((random.randint(5, 50))*buff)

        play_embed.add_field(name="__Food Served:__",
                             value=f"Hamburger 🍔 x**{f1}** \nFries 🍟  x**{f2}** \n Drinks <:drink:964935572869222430> x**{f3}** \n Exp: **{xp}** xp")

        await interaction.response.edit_message(embed=play_embed, view=v)

    async def upgrades_btn_callback(self, interaction):
        profile_embed = discord.Embed(title=interaction.user.name, color=0xfee3a8)
        profile_embed.set_thumbnail(url=interaction.user.avatar)

        v = PersistentView.PlayPersistentView()
        v.clear_items()
        v.add_item(v.back_btn)

        await interaction.response.edit_message(embed=profile_embed, view=v)

    async def on_app_command_error(
            self,
            interaction: discord.Interaction,
            error: discord.app_commands.AppCommandError
    ):
        raise error

    @app_commands.command(description="Collect food materials from here")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 5.0, key=lambda i: (i.guild_id, i.user.id))
    async def farm(self, interaction) -> None:
        farm_embed = discord.Embed(title="Farm", color=0xfee3a8)
        user = interaction.user
        farm_embed.set_footer(text="test", icon_url=interaction.user.avatar)

        farm_data = await interaction.client.db.fetchrow("SELECT * FROM farm WHERE userid = $1", user.id)
        upg_data = await interaction.client.db.fetch("SELECT * FROM upgrades WHERE userid = $1 AND type = $2", user.id, "farm")
        cooldowns = await interaction.client.db.fetchrow("SELECT userid, farm_produce FROM cooldowns WHERE userid = $1", user.id)

        production = 2 if farm_data is None else farm_data[1]
        storage_space = 10000 if farm_data is None else farm_data[2]
        amount = 10000 if farm_data is None else farm_data[3]

        current_time = time.time()
        production_collected_at = 0 if cooldowns is None else cooldowns[1]
        check_time = int(current_time)-int(production_collected_at)
        check_time = 3600 if check_time > 3600 else check_time

        produce_amount = 2*int(check_time)

        v = View()
        collect_btn = Button()
        collect_btn.label = "Collect"
        collect_btn.style = discord.ButtonStyle.blurple

        if int(amount)+int(produce_amount) < storage_space and check_time >= 60:
            collect_btn.disabled = False
        else:
            collect_btn.disabled = True

        async def collect_btn_callback(interaction: discord.Interaction):
            if farm_data is None:
                farm_query = "INSERT INTO farm(userid, production, storage, amount) VALUES($1, $2, $3, $4)"
                await interaction.client.db.execute(farm_query, user.id, 2, 10000, 10000)
            else:
                farm_query = "UPDATE farm SET amount = $1 WHERE userid = $2"
                await interaction.client.db.execute(farm_query, amount+produce_amount, user.id)

            if cooldowns is None:
                cd_query = "INSERT INTO cooldowns(userid, farm_produce) VALUES($1, $2)"
                await interaction.client.db.execute(cd_query, user.id, time.time())
            else:
                cd_query = "UPDATE cooldowns SET farm_produce = $1 WHERE userid = $2"
                await interaction.client.db.execute(cd_query, time.time(), user.id)

            collect_btn.disabled = True
            farm_embed.clear_fields()
            farm_embed.add_field(name="Rate",
                                 value=f"Current production rate of your farm is +{production}/s materials.",
                                 inline=False)
            farm_embed.add_field(name="Production", value=f"0 materials", inline=False)
            farm_embed.add_field(name="Storage",
                                 value=f"{(int(amount)+int(produce_amount)):,}/{storage_space:,} ({round(((int(amount)+int(produce_amount))/int(storage_space)) * 100, 1)})%",
                                 inline=False)

            await interaction.response.edit_message(embed=farm_embed, view=v)

        collect_btn.callback = collect_btn_callback
        v.add_item(collect_btn)

        farm_embed.add_field(name="Rate", value=f"Current production rate of your farm is +{production}/s materials for 1h.", inline=False)
        farm_embed.add_field(name="Production", value=f"{produce_amount:,} materials", inline=False)
        farm_embed.add_field(name="Storage", value=f"{amount:,}/{storage_space:,} ({round((int(amount)/int(storage_space))*100,1)})%", inline=False)

        await interaction.response.send_message(embed=farm_embed, view=v)

    @app_commands.command(description="Serve food to customers")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    async def serve(self, interaction) -> None:

        play_embed = discord.Embed(title=f"{interaction.user.name}", color=0xfee3a8)
        play_embed.set_footer(text="test",icon_url=interaction.user.avatar)
        account = await profile.Profile.check_for_account(self, interaction)
        user = interaction.user

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.send_message(embed=em, view=v)
        elif account[0] is True:

            details = await profile.Profile.get_user_details(self, interaction)
            farm_data = await interaction.client.db.fetchrow("SELECT * FROM farm WHERE userid = $1", user.id)

            mat_amount = 10000 if farm_data is None else farm_data[3]

            buff = float(details[9])
            min_food = 10 + (2*details[5])
            max_food = 30 + (2*details[5])

            min_xp = 20 + (2*details[5])
            max_xp = 50 + (2*details[5])

            f1 = round((random.randint(min_food, max_food)) * buff)
            f2 = round((random.randint(min_food, max_food)) * buff)
            f3 = round((random.randint(min_food, max_food)) * buff)
            xp = round((random.randint(min_xp, max_xp)) * buff)

            money = round(float(f1) * (4.00 * buff) + float(f2) * (3.00 * buff) + float(f3) * (2.00 * buff))
            lvl_up_check = None
            if farm_data is None:
                query = "INSERT INTO farm(userid, production, storage, amount) VALUES($1, $2, $3, $4)"
                await interaction.client.db.execute(query, user.id, 2, 10000, 10000)

            if mat_amount >= f1+f2+f3:
                    query = "UPDATE farm SET amount = $1 WHERE userid = $2"
                    await interaction.client.db.execute(query, mat_amount-(f1+f2+f3), user.id)

                    play_embed.add_field(name=f"__Food Served:__",
                                     value=f"Hamburger 🍔 x**{f1}** \nFries 🍟  x**{f2}** \nDrinks <:drink:964935572869222430> x**{f3}** \nExp: **{xp}** xp\nMoney: **${money}**",
                                     inline=False)

                    lvl_up_check = await self.update_data(interaction, details, xp, money)
            else:
                    play_embed.add_field(name=f"Unable To Serve Food", value=f":exclamation: **{interaction.user.name}**, There are not enough materials to cook, please visit your farm `/farm` and collect materials to continue.")

            if lvl_up_check == "level_up":
                    play_embed.add_field(name="Level Up",
                                         value=f"**{interaction.user.name}**, Congrats!! You are now level **{details[5] + 1}**, +{round((details[5] + 1) / 100, 3)}% increase in total buff",
                                         inline=False)
                    await interaction.response.send_message(embed=play_embed, view=PersistentView.PlayPersistentView())
            elif lvl_up_check is None or lvl_up_check != "level_up":
                    await interaction.response.send_message(embed=play_embed, view=PersistentView.PlayPersistentView())


    async def update_data(self, interaction, details, xp, money):
        balance = details[2]
        level = details[5]
        exp = details[6]
        total_exp = details[7]
        buff = details[9]

        client = interaction.client
        user = interaction.user
        query = "UPDATE profiles SET balance = $1, level = $2, exp = $3, total_exp = $4, buff = $5 WHERE userid = $6"

        if xp+exp >= total_exp:
            await client.db.execute(query, balance+money, level+1, (xp+exp)-total_exp, total_exp+250, round(float(buff)+((level+1)/100), 3), user.id)
            return "level_up"
        else:
            await client.db.execute(query, balance+money, level, (xp + exp), total_exp, buff, user.id)



async def setup(client):
    await client.add_cog(Play(client))