import discord
from discord.ext import commands
from discord.ui import Button, View, Select, Modal, TextInput

created_channels = {}  # channel_id: owner_user_id

class TempVoice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.bot.add_listener(self.on_voice_state_update)
        self.join_to_create_ids = set()  # Ukládá všechny Join To Create ID

    @commands.command()
    async def tempvoice(self, ctx):
        guild = ctx.guild

        overwrite = {
         guild.default_role: discord.PermissionOverwrite(send_messages=False, view_channel=True),
         guild.me: discord.PermissionOverwrite(send_messages=True, view_channel=True)
         }
        interface = await guild.create_text_channel("interface", overwrites=overwrite)

        join_to_create = await guild.create_voice_channel("Join To Create")

        await interface.send("Voice channel controls:", view=VoiceControlButtons(self.bot))

        self.join_to_create_ids.add(join_to_create.id)  # Přidá nový Join To Create do seznamu

    async def on_voice_state_update(self, member, before, after):
        guild = member.guild

        # Vytvoření nového VC při připojení do libovolného Join To Create kanálu
        if after.channel and after.channel.id in self.join_to_create_ids:
            category = after.channel.category
            new_vc = await guild.create_voice_channel(f"{member.name} VC", category=category)
            await member.move_to(new_vc)
            created_channels[new_vc.id] = member.id

        # Smazání VC pokud je prázdný a byl vytvořen botem
        if before.channel and before.channel.id in created_channels:
            vc = before.channel
            if len(vc.members) == 0:
                try:
                    await vc.delete()
                    del created_channels[vc.id]
                except discord.NotFound:
                    pass


class VoiceControlButtons(View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
        self.create_buttons()

    def create_buttons(self):
        controls = [
            ("Transfer Ownership", discord.ButtonStyle.primary, 0),
            ("Change Bitrate", discord.ButtonStyle.primary, 0),
            ("User Limit", discord.ButtonStyle.primary, 0),
            ("Channel Name", discord.ButtonStyle.primary, 0),
            ("Lock", discord.ButtonStyle.secondary, 1),
            ("Unlock", discord.ButtonStyle.secondary, 1),
            ("Hide", discord.ButtonStyle.secondary, 1),
            ("Unhide", discord.ButtonStyle.secondary, 1),
            ("VC Mute", discord.ButtonStyle.danger, 2),
            ("VC Unmute", discord.ButtonStyle.danger, 2),
            ("VC Deafen", discord.ButtonStyle.danger, 2),
            ("VC Undeafen", discord.ButtonStyle.danger, 2),
            ("VC Ban", discord.ButtonStyle.danger, 3),
            ("VC Kick", discord.ButtonStyle.danger, 3),
        ]

        for label, style, row in controls:
            self.add_item(ControlButton(label=label, style=style, bot=self.bot, row=row))


class ControlButton(Button):
    def __init__(self, label, style, bot, row):
        super().__init__(label=label, style=style, custom_id=label.replace(" ", "_").lower(), row=row)
        self.bot = bot

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        guild = interaction.guild
        vc_channel = None

        for channel_id, owner_id in created_channels.items():
            if owner_id == user.id:
                vc_channel = guild.get_channel(channel_id)
                break

        if not vc_channel:
            await interaction.response.send_message("Nemáš vytvořený voice kanál.", ephemeral=True)
            return

        members = vc_channel.members

        async def ask_member_selection(action_id):
            options = [
                discord.SelectOption(label=m.display_name, value=str(m.id)) for m in members if m != user
            ]
            if not options:
                await interaction.response.send_message("Nikdo jiný není ve VC.", ephemeral=True)
                return

            class MemberSelect(Select):
                def __init__(self):
                    super().__init__(placeholder="Vyber uživatele...", min_values=1, max_values=1, options=options)

                async def callback(inner_self, inner_interaction):
                    target_id = int(inner_self.values[0])
                    target = guild.get_member(target_id)
                    if not target:
                        await inner_interaction.response.send_message("Uživatel nenalezen.", ephemeral=True)
                        return

                    msg = ""
                    if action_id == "vc_mute":
                        await target.edit(mute=True)
                        msg = f"{target.mention} byl ztlumen."
                    elif action_id == "vc_unmute":
                        await target.edit(mute=False)
                        msg = f"{target.mention} byl odtlumen."
                    elif action_id == "vc_deafen":
                        await target.edit(deafen=True)
                        msg = f"{target.mention} byl ohlušen."
                    elif action_id == "vc_undeafen":
                        await target.edit(deafen=False)
                        msg = f"{target.mention} byl odhlušen."
                    elif action_id == "vc_kick":
                        await target.move_to(None)
                        msg = f"{target.mention} byl vyhozen z VC."
                    elif action_id == "vc_ban":
                        await vc_channel.set_permissions(target, connect=False)
                        await target.move_to(None)
                        msg = f"{target.mention} byl zabanován z VC."
                    elif action_id == "transfer_ownership":
                        created_channels[vc_channel.id] = target.id
                        msg = f"Vlastnictví kanálu předáno {target.mention}."

                    await inner_interaction.response.send_message(msg, ephemeral=True)

            view = View()
            view.add_item(MemberSelect())
            await interaction.response.send_message("Vyber uživatele:", view=view, ephemeral=True)

        if self.custom_id in [
            "vc_mute", "vc_unmute", "vc_deafen", "vc_undeafen",
            "vc_kick", "vc_ban", "transfer_ownership"
        ]:
            await ask_member_selection(self.custom_id)

        elif self.custom_id == "lock":
            await vc_channel.set_permissions(guild.default_role, connect=False)
            await interaction.response.send_message("Kanál byl uzamčen.", ephemeral=True)

        elif self.custom_id == "unlock":
            await vc_channel.set_permissions(guild.default_role, connect=True)
            await interaction.response.send_message("Kanál byl odemčen.", ephemeral=True)

        elif self.custom_id == "hide":
            await vc_channel.set_permissions(guild.default_role, view_channel=False)
            await interaction.response.send_message("Kanál byl skryt.", ephemeral=True)

        elif self.custom_id == "unhide":
            await vc_channel.set_permissions(guild.default_role, view_channel=True)
            await interaction.response.send_message("Kanál byl odhalen.", ephemeral=True)

        elif self.custom_id == "channel_name":
            class NameModal(Modal, title="Změna názvu kanálu"):
                new_name = TextInput(label="Nový název", placeholder="Zadej nový název...", max_length=100)

                async def on_submit(modal_self, interaction2: discord.Interaction):
                    await vc_channel.edit(name=modal_self.new_name.value)
                    await interaction2.response.send_message(f"Název změněn na **{modal_self.new_name.value}**.", ephemeral=True)

            await interaction.response.send_modal(NameModal())

        elif self.custom_id == "change_bitrate":
            class BitrateModal(Modal, title="Změna bitrate"):
                new_bitrate = TextInput(label="Bitrate (8000 - 96000)", placeholder="Např. 64000")

                async def on_submit(modal_self, interaction2: discord.Interaction):
                    try:
                        bitrate = int(modal_self.new_bitrate.value)
                        if 8000 <= bitrate <= 96000:
                            await vc_channel.edit(bitrate=bitrate)
                            await interaction2.response.send_message(f"Bitrate změněn na **{bitrate}**.", ephemeral=True)
                        else:
                            await interaction2.response.send_message("Bitrate musí být mezi 8000 a 96000.", ephemeral=True)
                    except ValueError:
                        await interaction2.response.send_message("Zadej platné číslo!", ephemeral=True)

            await interaction.response.send_modal(BitrateModal())

        elif self.custom_id == "user_limit":
            class LimitModal(Modal, title="Limit uživatelů"):
                new_limit = TextInput(label="Limit (0 = neomezeně, max 99)", placeholder="Např. 5")

                async def on_submit(modal_self, interaction2: discord.Interaction):
                    try:
                        limit = int(modal_self.new_limit.value)
                        if 0 <= limit <= 99:
                            await vc_channel.edit(user_limit=limit)
                            await interaction2.response.send_message(f"Limit nastaven na **{limit}**.", ephemeral=True)
                        else:
                            await interaction2.response.send_message("Limit musí být mezi 0 a 99.", ephemeral=True)
                    except ValueError:
                        await interaction2.response.send_message("Zadej platné číslo!", ephemeral=True)

            await interaction.response.send_modal(LimitModal())

        else:
            await interaction.response.send_message(f"Tlačítko **{self.label}** zatím není implementováno.", ephemeral=True)


async def setup(bot):
    await bot.add_cog(TempVoice(bot))
