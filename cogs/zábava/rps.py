import discord
from discord.ext import commands
from discord.ui import Button, View
import random

RED = discord.Color.from_str("#FF0000")  # 🔴 jednotná barva pro všechny embedy

class RPS_View(View):
    optionValue: int = 0

    async def disable_all(self):
        for item in self.children:
            item.disabled = True
        await self.message.edit(view=self)

    async def on_timeout(self):
        timeout_embed = discord.Embed(
            title="⏱️ Čas vypršel!",
            description="Hráč nezareagoval včas. Hra byla zrušena.",
            color=RED
        )
        await self.message.channel.send(embed=timeout_embed)
        await self.disable_all()

    @discord.ui.button(label="🪨 Kámen", style=discord.ButtonStyle.primary)
    async def rock(self, interaction: discord.Interaction, button: Button):
        self.optionValue = 4
        await interaction.response.send_message(embed=self.get_choice_embed("Kámen 🪨"), ephemeral=True)
        self.stop()

    @discord.ui.button(label="📄 Papír", style=discord.ButtonStyle.success)
    async def paper(self, interaction: discord.Interaction, button: Button):
        self.optionValue = 5
        await interaction.response.send_message(embed=self.get_choice_embed("Papír 📄"), ephemeral=True)
        self.stop()

    @discord.ui.button(label="✂️ Nůžky", style=discord.ButtonStyle.danger)
    async def scissors(self, interaction: discord.Interaction, button: Button):
        self.optionValue = 6
        await interaction.response.send_message(embed=self.get_choice_embed("Nůžky ✂️"), ephemeral=True)
        self.stop()

    def get_choice_embed(self, choice: str):
        return discord.Embed(
            title="✅ Vybral jsi možnost",
            description=f"Zvolil jsi **{choice}**",
            color=RED
        )

async def RPS(challenger: discord.User, defender: discord.User):
    embed = discord.Embed(
        title="📢 Výzva na Kámen–Nůžky–Papír!",
        description=f"{defender.mention}, byl jsi vyzván hráčem **{challenger.display_name}**!",
        color=RED
    )
    c_embed = discord.Embed(
        title="🕹️ Hra spuštěna",
        description=f"Vyzval jsi **{defender.display_name}** k souboji!",
        color=RED
    )

    view = RPS_View(timeout=30)
    c_view = RPS_View(timeout=30)

    d_msg = await defender.send(embed=embed, view=view)
    c_msg = await challenger.send(embed=c_embed, view=c_view)

    view.message = d_msg
    c_view.message = c_msg

    await view.wait()
    await c_view.wait()

    await view.disable_all()
    await c_view.disable_all()

    if view.optionValue != 0 and c_view.optionValue != 0:
        result_text = determine_winner(view.optionValue, c_view.optionValue, challenger, defender)
    else:
        result_text = "⚠️ Někdo z hráčů nevybral možnost – hra nebyla dokončena."

    result_embed = discord.Embed(
        title="🏁 Výsledek hry",
        description=result_text,
        color=RED
    )

    return result_embed

def determine_winner(defender_choice, challenger_choice, challenger, defender):
    if defender_choice == challenger_choice:
        return "🤝 Remíza! Oba zvolili stejnou možnost."

    outcomes = {
        (4, 6): f"🪨 Kámen drtí ✂️ Nůžky – **{defender.display_name} vyhrává!**",
        (4, 5): f"📄 Papír přikryje 🪨 Kámen – **{challenger.display_name} vyhrává!**",
        (5, 4): f"📄 Papír přikryje 🪨 Kámen – **{defender.display_name} vyhrává!**",
        (5, 6): f"✂️ Nůžky stříhají 📄 Papír – **{challenger.display_name} vyhrává!**",
        (6, 5): f"✂️ Nůžky stříhají 📄 Papír – **{defender.display_name} vyhrává!**",
        (6, 4): f"🪨 Kámen drtí ✂️ Nůžky – **{challenger.display_name} vyhrává!**",
    }

    return outcomes.get((defender_choice, challenger_choice), "🤝 Remíza!")

class RPSCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="challenge", aliases=["challange"])
    async def challenge(self, ctx, user: discord.User = None):
        if user is None:
            embed = discord.Embed(
                title="❗ Chyba",
                description="Musíš označit uživatele, kterého chceš vyzvat. Použij `!challenge @uživatel`",
                color=RED
            )
            await ctx.send(embed=embed)
            return
        if user == ctx.author:
            embed = discord.Embed(
                title="😅 Nelze",
                description="Nemůžeš vyzvat sám sebe!",
                color=RED
            )
            await ctx.send(embed=embed)
            return
        try:
            result_embed = await RPS(ctx.author, user)
            await ctx.send(embed=result_embed)
        except discord.Forbidden:
            error_embed = discord.Embed(
                title="❌ Chyba",
                description="Uživatel má zavřené soukromé zprávy – nelze ho vyzvat.",
                color=RED
            )
            await ctx.send(embed=error_embed)

    @commands.command()
    async def roll(self, ctx, dice: str):
        try:
            rolls, limit = map(int, dice.lower().split('d'))
        except Exception:
            embed = discord.Embed(
                title="⚠️ Chybný formát",
                description="Formát musí být `NdN` (např. `2d6`).",
                color=RED
            )
            await ctx.send(embed=embed)
            return

        result = ', '.join(str(random.randint(1, limit)) for _ in range(rolls))
        embed = discord.Embed(
            title="🎲 Hod kostkou",
            description=f"`{result}`",
            color=RED
        )
        await ctx.send(embed=embed)

    @commands.command()
    @commands.is_owner()
    async def shutdown(self, ctx):
        embed = discord.Embed(
            title="🛑 Bot se vypíná",
            description="Děkujeme za hraní!",
            color=RED
        )
        await ctx.send(embed=embed)
        await self.bot.close()

async def setup(bot):
    await bot.add_cog(RPSCog(bot))
