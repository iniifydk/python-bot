import discord
from discord.ext import commands
import random

class GayRate(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def gayrate(self, ctx):
        """Generuje náhodné číslo mezi 1 a 100 jako 'gayrate'."""
        gay_percentage = random.randint(1, 100)
        await ctx.send(f"Tvá gayrate je {gay_percentage}%!")

# Správná async verze setup funkce
async def setup(bot):
    await bot.add_cog(GayRate(bot))
