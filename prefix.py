import discord
from discord.ext import commands
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

class Prefix(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        mongo_url = os.getenv("MONGODB_URI")
        self.cluster = MongoClient(mongo_url)
        self.db = self.cluster["discord_bot"]
        self.prefixes = self.db["prefixes"]
        self.default_prefix = os.getenv("COMMAND_PREFIX") or "."

    @commands.command(name="prefix")
    @commands.has_permissions(administrator=True)
    async def change_prefix(self, ctx, new_prefix: str):
        """Změní prefix pro tento server (pouze administrátor)."""
        self.prefixes.update_one(
            {"guild_id": str(ctx.guild.id)},
            {"$set": {"prefix": new_prefix}},
            upsert=True
        )
        await ctx.send(f"✅ Prefix změněn na `{new_prefix}`")

    @commands.command(name="currentprefix")
    async def current_prefix(self, ctx):
        """Zobrazí aktuální prefix na tomto serveru."""
        guild_data = self.prefixes.find_one({"guild_id": str(ctx.guild.id)})
        prefix = guild_data["prefix"] if guild_data and "prefix" in guild_data else self.default_prefix
        await ctx.send(f"ℹ️ Aktuální prefix je: `{prefix}`")

    @commands.command(name="resetprefix")
    @commands.has_permissions(administrator=True)
    async def reset_prefix(self, ctx):
        """Resetuje prefix na výchozí."""
        self.prefixes.delete_one({"guild_id": str(ctx.guild.id)})
        await ctx.send(f"🔄 Prefix byl resetován na výchozí: `{self.default_prefix}`")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Nastaví výchozí prefix při připojení na nový server."""
        self.prefixes.update_one(
            {"guild_id": str(guild.id)},
            {"$setOnInsert": {"prefix": self.default_prefix}},
            upsert=True
        )

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        """Odstraní prefix z databáze při odchodu bota ze serveru."""
        self.prefixes.delete_one({"guild_id": str(guild.id)})

async def setup(bot):
    await bot.add_cog(Prefix(bot))
