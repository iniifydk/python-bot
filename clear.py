import discord
from discord.ext import commands

class Clear(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_messages=True)
    async def clear(self, ctx, amount: int):
        if amount <= 0:
            await ctx.send("Počet zpráv musí být větší než 0.")
            return

        deleted = await ctx.channel.purge(limit=amount + 1)
        deleted_count = len(deleted) - 1
        confirmation = await ctx.send(f'✅ Smazáno {deleted_count} zpráv.')
        await confirmation.delete(delay=3)

    @clear.error
    async def clear_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send("🚫 Nemáš oprávnění pro mazání zpráv.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("⚠️ Použij příkaz ve formátu: `.clear <počet>`")
        elif isinstance(error, commands.BadArgument):
            await ctx.send("⚠️ Počet zpráv musí být číslo.")

async def setup(bot):
    await bot.add_cog(Clear(bot))