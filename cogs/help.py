import discord
from discord.ext import commands
from discord.ui import Select, View

class CommandSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Základní", value="Základní", description="Základní příkazy pro každého.", emoji="<:zakladni:1357420249527484486>"),
            discord.SelectOption(label="Moderace", value="Moderace", description="Příkazy pro moderování serveru.", emoji="<:moderace:1357420179180486756>"),
            discord.SelectOption(label="Hudba", value="Hudba", description="Ovládej přehrávání hudby.", emoji="<:voice:1357420197077717225>"),
            discord.SelectOption(label="Info", value="Info", description="Získej informace o uživatelích, serveru atd.", emoji="<:info:1357420049752916099>"),
            discord.SelectOption(label="Hry", value="Hry", description="Zábavné minihry pro všechny.", emoji="<:hry:1357420217516429512>"),
            discord.SelectOption(label="Zábava", value="Zábava", description="Memes, vtipy a další zábava.", emoji="<:zabava:1357420159924441118>"),
            discord.SelectOption(label="Užitečné", value="Užitečné", description="Nástroje a příkazy pro usnadnění práce.", emoji="<:uzitecne:1357420120049451260>"),
            discord.SelectOption(label="Admin", value="Admin", description="Admin příkazy – pouze pro správce!", emoji="<:admin:1357420093398716546>"),
            discord.SelectOption(label="Hledání & API", value="Hledání & API", description="Vyhledávání informací a API integrace.", emoji="<:hledaniaapi:1357420273284026388>"),
            discord.SelectOption(label="Interakce", value="Interakce", description="Reakce, tlačítka a interaktivní věci.", emoji="<:interakce:1357420141893255407>")
        ]

        super().__init__(placeholder="Vyber si kategorii...", options=options)
        self.callback = self.select_callback

    async def select_callback(self, interaction: discord.Interaction):
        category_commands = {
            "Základní": "🔹 antinuke enable - Enables AntiNuke\n🔹 antinuke disable - Disables AntiNuke",
            "Moderace": "🔹 .ban @user - Bans a user\n🔹 .kick @user - Kicks a user",
            "Hudba": "🔹 .automod enable - Enables Automod\n🔹 .automod disable - Disables Automod",
            "Info": "🔹 .logger setup - Sets up logging\n🔹 .logger disable - Disables logging",
            "Hry": "🔹 .ping - Checks bot latency\n🔹 .uptime - Shows bot uptime",
            "Zábava": "🔹 .jtc setup - Sets up Join To Create",
            "Užitečné": "🔹 .voice lock - Locks voice channel",
            "Admin": "🔹 .role create - Creates a custom role",
            "Hledání & API": "🔹 .welcome setup - Sets up the welcome system",
            "Interakce": "🔹 .ticket create - Creates a ticket system"
        }

        selected = self.values[0]
        commands_text = category_commands.get(selected, "Žádné příkazy pro tuto kategorii.")

        embed = discord.Embed(
            title=f"{selected} příkazy",
            description=commands_text,
            color=discord.Color.blurple()
        )

        await interaction.response.send_message(embed=embed, ephemeral=True)

class CommandView(View):
    def __init__(self):
        super().__init__()
        self.add_item(CommandSelect())

class BasicCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def create_embed(self, ctx):
        # Dynamické získání prefixu
        prefix = await self.bot.get_prefix(ctx.message)
        if isinstance(prefix, list):
            prefix = prefix[0]

        bot_avatar = self.bot.user.avatar.url if self.bot.user.avatar else self.bot.user.default_avatar.url

        embed = discord.Embed(
            description=f"""
<:reddot:1376267283051319456>  \u200B **Prefix pro tento server:** `{prefix}`  
<:reddot:1376267283051319456>  \u200B **Celkem příkazů:** `1`  
<:reddot:1376267283051319456>  \u200B **Začněte zadáním `{prefix}help`**""",
            color=discord.Color(0xFF0000)
        )

        embed.set_author(name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url)
        embed.add_field(
            name="",
            value="```ansi\n\u001b[0;2m\u001b[0;2m\u001b[0;34m<>\u001b[0m \u001b[0;31m- Povinný argument\u001b[0m \u001b[0;32m\u001b[0;30m|\u001b[0m\u001b[0;32m\u001b[0m \u001b[0;34m\u001b[0;34m()\u001b[0m\u001b[0;34m\u001b[0m \u001b[0;31m- Volitelný argument\u001b[0m\u001b[0m\u001b[0m \u200B\n```",
            inline=False
        )

        embed.set_thumbnail(url=bot_avatar)

        embed.add_field(name="<:slozka:1376265804928254112> __Kategorie__", value=
            "<:shield1:1376265746698600558>: **Základní**\u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B<:idk2:1376550575272890589>: \u200B **Zábava** \n"
            "<:shield:1376265707905482862>: **Moderace**\u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B<:email:1376549656858988585>: \u200B **Užitečné**\n"
            "<:voice:1376265942795026503>: **Hudba**\u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B<:admin:1376265898343665695>: \u200B **Admin**\n"
            "<:diamant1:1376549735967490068>: **Info** \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B<:idk4:1376550673319202886>: \u200B **Hledání & API**\n"
            "<:rocket:1376265855608029224>: **Hry** \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B \u200B  \u200B \u200B \u200B \u200B<:chytrablbost1:1376549774844625027>: \u200B **Interakce**"
        )
        
        embed.add_field(name="🔗 Odkazy \u200B ", value="**[pozvi mě pičo](https://discord.com/oauth2/authorize?client_id=1355766944615235655)**", inline=False)
        embed.set_footer(text="Vyvinuto se vší nenávistí Od Iniifyho")

        return embed

    @commands.command(name="help")
    async def show_commands(self, ctx):
        """Tento příkaz zobrazí seznam příkazů"""
        embed = await self.create_embed(ctx)
        await ctx.send(embed=embed, view=CommandView())

    @commands.Cog.listener()
    async def on_ready(self):
        print(f"Bot je připojený jako {self.bot.user}!")

async def setup(bot):
    await bot.add_cog(BasicCommands(bot))
