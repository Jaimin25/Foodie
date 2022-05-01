import discord
from discord.ui import Button, View
from discord.ext import commands, tasks
from discord import app_commands
from cogs import PersistentView, profile
import random

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
        await interaction.response.send_message(error, ephemeral=True)

    @app_commands.command(description="Serve food to customers")
    @app_commands.guilds(discord.Object(955385300513878026))
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.guild_id, i.user.id))
    async def serve(self, interaction) -> None:

        play_embed = discord.Embed(title=f"{interaction.user.name}", color=0xfee3a8)
        play_embed.set_footer(text="test",icon_url=interaction.user.avatar)

        details = await profile.Profile.get_user_details(self, interaction)
        buff = float(details[9])

        f1 = round((random.randint(5, 20)) * buff)
        f2 = round((random.randint(5, 20)) * buff)
        f3 = round((random.randint(5, 15)) * buff)
        xp = round((random.randint(5, 50)) * buff)

        money = round(float(f1)*(4.00*buff)+float(f2)*(3.00*buff)+float(f3)*(2.00*buff))

        play_embed.add_field(name=f"__Food Served:__",
                             value=f"Hamburger 🍔 x**{f1}** \nFries 🍟  x**{f2}** \n Drinks <:drink:964935572869222430> x**{f3}** \n Exp: **{xp}** xp\n Money: **${money}**", inline=False)

        account = await profile.Profile.check_for_account(self, interaction)

        if account[0] is False:
            em = account[1]
            v = account[2]

            await interaction.response.send_message(embed=em, view=v)
        elif account[0] is True:
            lvl_up_check = await self.update_data(interaction, details, xp, money)
            if lvl_up_check == "level_up":
                play_embed.add_field(name="Level Up", value=f"**{interaction.user.name}**, Congrats!! You are now level **{details[5]+1}**, +{round((details[5]+1)/100, 3)}% increase in total buff", inline=False)
                await interaction.response.send_message(embed=play_embed, view=PersistentView.PlayPersistentView())
            else:
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
            await client.db.execute(query, balance+money, level+1, (xp+exp)-total_exp, total_exp+500, round(float(buff)+((level+1)/100), 3), user.id)
            return "level_up"
        else:
            await client.db.execute(query, balance+money, level, (xp + exp), total_exp, buff, user.id)



async def setup(client):
    await client.add_cog(Play(client))