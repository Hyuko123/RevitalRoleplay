import discord
from discord import app_commands
from discord.ext import tasks
import json
import os
from datetime import datetime, timedelta
import asyncio
import random
import string
from config import (
    TOKEN, GUILD_ID,
    LOGS_CHANNEL, LOGS_WL_CHANNEL, LOGS_TICKETS_CHANNEL, LOGS_REMBOURSEMENT_CHANNEL,
    VERIFICATION_CHANNEL, WELCOME_CHANNEL,
    CITOYEN_WL_ROLE, MUTED_ROLE, UNVERIFIED_ROLE, VERIFIED_ROLE,
    STAFF_ROLE,
    TICKET_CATEGORY_ID,
    TICKET_CHANNELS,
)

# ======================================================
#  INTENTS & BOT
# ======================================================

intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# ======================================================
#  DONNÉES JSON
# ======================================================

DATA_FILES = {
    "data/warns.json":     {},
    "data/mutes.json":     {},
    "data/whitelist.json": {},
    "data/tickets.json":   {},
    "data/captchas.json":  {},
    "data/sanctions.json": {},
    "data/ticket_counter.json": {"count": 0},
    "data/remboursements.json": {},
}

def create_data_files():
    """Crée les dossiers et fichiers JSON nécessaires."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("data/transcripts", exist_ok=True)
    
    for path, default in DATA_FILES.items():
        if not os.path.exists(path):
            try:
                with open(path, "w", encoding="utf-8") as f:
                    json.dump(default, f, indent=2, ensure_ascii=False)
                print(f"✅ Fichier créé : {path}")
            except Exception as e:
                print(f"❌ Erreur création {path} : {e}")

def load_data(path: str):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}

def save_data(path: str, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def next_ticket_number() -> int:
    counter = load_data("data/ticket_counter.json")
    n = counter.get("count", 0) + 1
    save_data("data/ticket_counter.json", {"count": n})
    return n

# ======================================================
#  HELPERS
# ======================================================

def parse_duration(time_str: str) -> int | None:
    """Convertit '1h', '30m', '7d' en secondes. Retourne None si invalide."""
    multipliers = {"s": 1, "m": 60, "h": 3600, "d": 86400}
    try:
        amount = int(time_str[:-1])
        unit = time_str[-1].lower()
        return amount * multipliers[unit]
    except Exception:
        return None

def fmt_duration(seconds: int) -> str:
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        return f"{seconds // 60}m"
    elif seconds < 86400:
        return f"{seconds // 3600}h"
    else:
        return f"{seconds // 86400}j"

def is_staff(interaction: discord.Interaction) -> bool:
    """Vérifie si l'utilisateur possède le rôle STAFF_ROLE."""
    staff_role = interaction.guild.get_role(STAFF_ROLE)
    return staff_role is not None and staff_role in interaction.user.roles

CATEGORY_LABELS = {
    "boutique":    "💎 Boutique / Remboursement",
    "superviseur": "⚜️ Superviseur",
    "recrutement": "🔵 Recrutement Staff",
    "legal":       "🟢 Dossier Légal",
    "illegal":     "🔴 Dossier Illégal",
    "wiperp":      "💀 Wipe / Mort RP",
}

# ======================================================
#  TRANSCRIPT HTML
# ======================================================

async def generate_transcript(channel: discord.TextChannel, ticket_data: dict) -> str | None:
    """Génère un fichier HTML avec la prise en charge et fermeture du ticket."""
    try:
        number = ticket_data.get("number", "?")
        category = ticket_data.get("category", "")
        category_label = CATEGORY_LABELS.get(category, category or "?")
        creator_name = ticket_data.get("creator_name", "?")
        created_at = ticket_data.get("created_at", "")
        claimed_by_name = ticket_data.get("claimed_by_name") or "Non assigné"
        closed_by = ticket_data.get("closed_by") or "?"
        closed_at = ticket_data.get("closed_at") or datetime.now().isoformat()

        def fmt_dt(iso_str: str) -> str:
            try:
                return datetime.fromisoformat(iso_str).strftime("%d/%m/%Y %H:%M")
            except Exception:
                return iso_str or "?"

        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<title>Transcript - {channel.name}</title>
<style>
  body {{ font-family: 'Segoe UI', sans-serif; background: #36393f; color: #dcddde; margin: 0; padding: 20px; }}
  h1 {{ color: #ffffff; border-bottom: 2px solid #5865f2; padding-bottom: 8px; }}
  .row {{ display: flex; gap: 12px; padding: 10px 0; border-bottom: 1px solid #40444b; }}
  .label {{ font-weight: bold; color: #ffffff; min-width: 180px; }}
  .value {{ color: #dcddde; }}
</style>
</head>
<body>
<h1>📋 Transcript — Ticket #{number:04d} — {category_label}</h1>
<div class="row"><div class="label">Créé par</div><div class="value">{creator_name}</div></div>
<div class="row"><div class="label">Date de création</div><div class="value">{fmt_dt(created_at)}</div></div>
<div class="row"><div class="label">Pris en charge par</div><div class="value">{claimed_by_name}</div></div>
<div class="row"><div class="label">Fermé par</div><div class="value">{closed_by}</div></div>
<div class="row"><div class="label">Date de fermeture</div><div class="value">{fmt_dt(closed_at)}</div></div>
</body>
</html>"""

        # Assurer que le dossier existe
        os.makedirs("data/transcripts", exist_ok=True)
        
        # Créer un nom de fichier sûr et unique
        filename = f"ticket_{number:04d}_{int(datetime.now().timestamp())}.html"
        path = os.path.join("data/transcripts", filename)
        
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        
        print(f"[TRANSCRIPT] ✅ Créé : {path}")
        return path
        
    except Exception as e:
        print(f"[TRANSCRIPT] ❌ Erreur : {e}")
        import traceback
        traceback.print_exc()
        return None

# ======================================================
#  TICKETS
# ======================================================

class TicketCategorySelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="💎 Boutique / Remboursement", value="boutique",    description="Problème d'achat, remboursement, item manquant"),
            discord.SelectOption(label="⚜️ Superviseur",              value="superviseur", description="Contacter un superviseur"),
            discord.SelectOption(label="🔵 Recrutement Staff",        value="recrutement", description="Candidature ou question recrutement"),
            discord.SelectOption(label="🟢 Dossier Légal",            value="legal",       description="Affaire légale RP"),
            discord.SelectOption(label="🔴 Dossier Illégal",          value="illegal",     description="Affaire criminelle / illégale RP"),
            discord.SelectOption(label="💀 Wipe / Mort RP",           value="wiperp",      description="Demande de wipe ou mort RP officielle"),
        ]
        super().__init__(placeholder="📂 Choisir la catégorie du ticket...", options=options, min_values=1, max_values=1)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        category = self.values[0]
        guild = interaction.guild
        creator = interaction.user
        ticket_num = next_ticket_number()

        # Récupérer la catégorie par défaut
        ticket_category = guild.get_channel(TICKET_CATEGORY_ID) if TICKET_CATEGORY_ID else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            creator: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True, manage_channels=True),
        }
        staff_role = guild.get_role(STAFF_ROLE)
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True)

        # Récupérer l'ID de la catégorie spécifique pour ce type de ticket
        target_cat_id = TICKET_CHANNELS.get(category, 0)

        # Si une catégorie spécifique existe, l'utiliser, sinon utiliser la catégorie par défaut
        if target_cat_id and target_cat_id != 0:
            target_category = guild.get_channel(target_cat_id)
            # Si la catégorie spécifique n'existe pas, utiliser la catégorie par défaut
            if target_category is None:
                print(f"[TICKET] ⚠️ Catégorie {target_cat_id} introuvable pour {category}, utilisation par défaut")
                target_category = ticket_category
        else:
            target_category = ticket_category

        print(f"[TICKET] Création ticket {category} dans : {target_category.name if target_category else 'Aucune'}")

        channel = await guild.create_text_channel(
            name=f"{category}-{ticket_num:04d}-{creator.name[:10]}",
            category=target_category,
            overwrites=overwrites,
            topic=f"Ticket #{ticket_num:04d} • {CATEGORY_LABELS[category]} • Créé par {creator.name}"
        )

        tickets = load_data("data/tickets.json")
        tickets[str(channel.id)] = {
            "number":       ticket_num,
            "creator_id":   creator.id,
            "creator_name": creator.name,
            "category":     category,
            "status":       "open",
            "claimed_by":   None,
            "created_at":   datetime.now().isoformat(),
            "closed_at":    None,
            "messages":     [],
        }
        save_data("data/tickets.json", tickets)

        embed = discord.Embed(
            title=f"🎫 Ticket #{ticket_num:04d} — {CATEGORY_LABELS[category]}",
            description=(
                f"Bienvenue {creator.mention} !\n\n"
                f"Un membre du staff prendra en charge ta demande rapidement.\n"
                f"**Décris ton problème en détail** ci-dessous.\n\n"
                f"_Pour fermer ce ticket, clique sur le bouton rouge._"
            ),
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Revital RP • {CATEGORY_LABELS[category]}")

        view = TicketPanelView(channel.id)
        await channel.send(embed=embed, view=view)
        await channel.send(f"{creator.mention}", delete_after=2)

        # 🔔 PING DU STAFF
        staff_role = guild.get_role(STAFF_ROLE)
        if staff_role:
            await channel.send(f"🔔 {staff_role.mention} — Nouveau ticket à traiter !")
            print(f"[TICKET] ✅ Staff ping envoyé")

        log_ch = bot.get_channel(LOGS_TICKETS_CHANNEL)
        if log_ch:
            log_embed = discord.Embed(
                title="🎫 Nouveau Ticket",
                description=f"**#{ticket_num:04d}** créé par {creator.mention}\nCatégorie: {CATEGORY_LABELS[category]}\nSalon: {channel.mention}",
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            await log_ch.send(embed=log_embed)
        else:
            print(f"[TICKET] ⚠️ Canal logs introuvable : {LOGS_TICKETS_CHANNEL}")

        await interaction.followup.send(f"✅ Ton ticket a été créé : {channel.mention}", ephemeral=True)


class TicketOpenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(TicketCategorySelect())


class TicketPanelView(discord.ui.View):
    def __init__(self, channel_id: int):
        super().__init__(timeout=None)
        self.channel_id = channel_id

    @discord.ui.button(label="✅ Claim", style=discord.ButtonStyle.green, custom_id="ticket_claim")
    async def claim(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_staff(interaction):
            await interaction.response.send_message("❌ Réservé au staff.", ephemeral=True)
            return
        tickets = load_data("data/tickets.json")
        key = str(interaction.channel.id)
        if key not in tickets:
            await interaction.response.send_message("❌ Ticket introuvable.", ephemeral=True)
            return
        ticket_data = tickets[key]
        ticket_data["claimed_by"] = interaction.user.id
        ticket_data["claimed_by_name"] = interaction.user.name
        save_data("data/tickets.json", tickets)
        await interaction.response.send_message(
            f"✅ **{interaction.user.mention}** a pris en charge ce ticket.", ephemeral=False
        )

        try:
            log_ch = bot.get_channel(LOGS_TICKETS_CHANNEL)
            if log_ch is None:
                try:
                    log_ch = await bot.fetch_channel(LOGS_TICKETS_CHANNEL)
                except Exception as fetch_err:
                    print(f"[TICKET CLAIM] ❌ Salon logs introuvable (ID: {LOGS_TICKETS_CHANNEL}) : {fetch_err}")
                    log_ch = None

            if log_ch:
                number = ticket_data.get("number", "?")
                number_str = f"#{number:04d}" if isinstance(number, int) else f"#{number}"
                category_label = CATEGORY_LABELS.get(ticket_data.get("category", ""), "?")
                await log_ch.send(
                    f"✅ Ticket {number_str} ({category_label}) — {interaction.channel.mention} pris en charge par {interaction.user.mention}"
                )
            else:
                print(f"[TICKET CLAIM] ❌ Impossible d'envoyer le log : salon {LOGS_TICKETS_CHANNEL} inaccessible")
        except Exception as e:
            print(f"[TICKET CLAIM] ❌ Erreur lors de l'envoi du log : {e}")
            import traceback
            traceback.print_exc()

    @discord.ui.button(label="👤 Ajouter membre", style=discord.ButtonStyle.blurple, custom_id="ticket_add_member")
    async def add_member(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_staff(interaction):
            await interaction.response.send_message("❌ Réservé au staff.", ephemeral=True)
            return
        modal = AddMemberModal(interaction.channel)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🔄 Réassigner", style=discord.ButtonStyle.grey, custom_id="ticket_reassign")
    async def reassign(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_staff(interaction):
            await interaction.response.send_message("❌ Réservé au staff.", ephemeral=True)
            return
        modal = ReassignModal(interaction.channel)
        await interaction.response.send_modal(modal)

    @discord.ui.button(label="🔒 Fermer", style=discord.ButtonStyle.red, custom_id="ticket_close")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_data("data/tickets.json")
        key = str(interaction.channel.id)
        if key not in tickets:
            await interaction.response.send_message("❌ Ticket introuvable.", ephemeral=True)
            return

        ticket_data = tickets[key]
        confirm_view = TicketCloseConfirmView(interaction.channel, ticket_data)
        await interaction.response.send_message(
            "⚠️ Es-tu sûr de vouloir fermer ce ticket ?",
            view=confirm_view,
            ephemeral=True
        )


class TicketCloseConfirmView(discord.ui.View):
    def __init__(self, channel: discord.TextChannel, ticket_data: dict):
        super().__init__(timeout=60)
        self.channel = channel
        self.ticket_data = ticket_data

    @discord.ui.button(label="✅ Confirmer la fermeture", style=discord.ButtonStyle.red)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer(ephemeral=True)

        tickets = load_data("data/tickets.json")
        key = str(self.channel.id)
        if key in tickets:
            tickets[key]["status"] = "closed"
            tickets[key]["closed_at"] = datetime.now().isoformat()
            tickets[key]["closed_by"] = interaction.user.name
            self.ticket_data = tickets[key]
        save_data("data/tickets.json", tickets)

        try:
            # Générer la transcription
            path = await generate_transcript(self.channel, self.ticket_data)

            log_ch = bot.get_channel(LOGS_TICKETS_CHANNEL)
            if log_ch is None:
                try:
                    log_ch = await bot.fetch_channel(LOGS_TICKETS_CHANNEL)
                except Exception as fetch_err:
                    print(f"[TICKET CLOSE] ❌ Salon logs introuvable (ID: {LOGS_TICKETS_CHANNEL}) : {fetch_err}")
                    log_ch = None

            if log_ch:
                number = self.ticket_data.get("number", "?")
                number_str = f"#{number:04d}" if isinstance(number, int) else f"#{number}"
                embed = discord.Embed(
                    title="🔒 Ticket Fermé",
                    description=(
                        f"**{number_str}** — {CATEGORY_LABELS.get(self.ticket_data.get('category', ''), '?')}\n"
                        f"Créé par : **{self.ticket_data.get('creator_name', '?')}**\n"
                        f"Fermé par : **{interaction.user.name}**\n"
                        f"Pris en charge par : **{self.ticket_data.get('claimed_by_name', 'Non assigné')}**"
                    ),
                    color=discord.Color.red(),
                    timestamp=datetime.now()
                )
                
                # Envoyer avec le fichier si créé avec succès
                if path and os.path.exists(path):
                    try:
                        await log_ch.send(embed=embed, file=discord.File(path))
                        print(f"[TICKET CLOSE] ✅ Log + transcript envoyés pour {number_str}")
                    except Exception as file_err:
                        print(f"[TICKET CLOSE] ⚠️ Erreur envoi fichier : {file_err}")
                        await log_ch.send(embed=embed)
                else:
                    await log_ch.send(embed=embed)
                    print(f"[TICKET CLOSE] ⚠️ Log envoyé (transcript indisponible)")
            else:
                print(f"[TICKET CLOSE] ❌ Canal logs inaccessible")
                
        except Exception as e:
            print(f"[TICKET CLOSE] ❌ Erreur : {e}")
            import traceback
            traceback.print_exc()

        await self.channel.delete(reason=f"Ticket fermé par {interaction.user.name}")

    @discord.ui.button(label="❌ Annuler", style=discord.ButtonStyle.grey)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Fermeture annulée.", ephemeral=True)
        self.stop()


class AddMemberModal(discord.ui.Modal, title="Ajouter un membre au ticket"):
    user_id = discord.ui.TextInput(label="ID Discord du membre", placeholder="123456789012345678", required=True)

    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await interaction.guild.fetch_member(int(self.user_id.value.strip()))
            await self.channel.set_permissions(member, view_channel=True, send_messages=True, read_message_history=True)
            await interaction.response.send_message(f"✅ **{member.mention}** a été ajouté au ticket.", ephemeral=False)
        except Exception:
            await interaction.response.send_message("❌ Membre introuvable. Vérifie l'ID.", ephemeral=True)


class ReassignModal(discord.ui.Modal, title="Réassigner le ticket"):
    user_id = discord.ui.TextInput(label="ID Discord du staff", placeholder="123456789012345678", required=True)

    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            member = await interaction.guild.fetch_member(int(self.user_id.value.strip()))
            tickets = load_data("data/tickets.json")
            key = str(self.channel.id)
            if key in tickets:
                tickets[key]["claimed_by"] = member.id
                tickets[key]["claimed_by_name"] = member.name
                save_data("data/tickets.json", tickets)
            await self.channel.set_permissions(member, view_channel=True, send_messages=True, read_message_history=True)
            await interaction.response.send_message(
                f"🔄 Ticket réassigné à **{member.mention}**.", ephemeral=False
            )
        except Exception:
            await interaction.response.send_message("❌ Membre introuvable.", ephemeral=True)


# ======================================================
#  WHITELIST
# ======================================================

WL_ROLES = {
    "legal":   "Citoyen légal",
    "illegal": "Criminel / Illégal",
}

class WhitelistStep1Modal(discord.ui.Modal, title="Whitelist — Étape 1 / 2 : Infos RP"):
    nom_rp    = discord.ui.TextInput(label="Nom & Prénom RP",       placeholder="Jean Dupont",         required=True, max_length=80)
    age_rp    = discord.ui.TextInput(label="Âge du personnage",     placeholder="28",                  required=True, max_length=3)
    notes     = discord.ui.TextInput(label="Notes du staff (optionnel)", placeholder="Comportement, points forts...", required=False, max_length=300, style=discord.TextStyle.paragraph)

    def __init__(self, member: discord.Member):
        super().__init__()
        self.member = member

    async def on_submit(self, interaction: discord.Interaction):
        view = WhitelistStep2View(
            self.member,
            {
                "nom_rp":     self.nom_rp.value,
                "age_rp":     self.age_rp.value,
                "background": "",
                "notes":      self.notes.value,
            }
        )
        embed = discord.Embed(
            title="📋 Whitelist — Étape 2 / 2 : Évaluation",
            description=(
                f"**Joueur :** {self.member.mention} (`{self.member.id}`)\n"
                f"**Nom RP :** {self.nom_rp.value}\n\n"
                "Sélectionne les évaluations ci-dessous puis clique **Soumettre**."
            ),
            color=discord.Color.gold()
        )
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


class WhitelistStep2View(discord.ui.View):
    def __init__(self, member: discord.Member, step1_data: dict):
        super().__init__(timeout=300)
        self.member    = member
        self.step1     = step1_data
        self.type_wl   = None
        self.background_ok = None
        self.reglement_ok  = None
        self.decision       = None

    @discord.ui.select(
        placeholder="Type de personnage",
        options=[
            discord.SelectOption(label="⚖️ Légal",   value="legal",   description="Citoyen, commerçant..."),
            discord.SelectOption(label="🔫 Illégal", value="illegal", description="Criminel, gang..."),
        ]
    )
    async def select_type(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.type_wl = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="Background validé ?",
        options=[
            discord.SelectOption(label="✅ Background OK",      value="ok"),
            discord.SelectOption(label="❌ Background insuffisant", value="non-ok"),
        ]
    )
    async def select_background(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.background_ok = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="Règlement connu ?",
        options=[
            discord.SelectOption(label="✅ Règlement maîtrisé",  value="ok"),
            discord.SelectOption(label="❌ Règlement insuffisant", value="non-ok"),
        ]
    )
    async def select_reglement(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.reglement_ok = select.values[0]
        await interaction.response.defer()

    @discord.ui.select(
        placeholder="Décision finale",
        options=[
            discord.SelectOption(label="✅ ACCEPTÉ",  value="accepte",  emoji="✅"),
            discord.SelectOption(label="❌ REFUSÉ",   value="refuse",   emoji="❌"),
            discord.SelectOption(label="⏳ EN ATTENTE", value="attente", emoji="⏳"),
        ]
    )
    async def select_decision(self, interaction: discord.Interaction, select: discord.ui.Select):
        self.decision = select.values[0]
        await interaction.response.defer()

    @discord.ui.button(label="📨 Soumettre la Whitelist", style=discord.ButtonStyle.green, row=4)
    async def submit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not all([self.type_wl, self.background_ok, self.reglement_ok, self.decision]):
            await interaction.response.send_message("❌ Tu dois remplir **tous** les champs avant de soumettre.", ephemeral=True)
            return

        if not is_staff(interaction):
            await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
            return

        wl_data = load_data("data/whitelist.json")
        user_key = str(self.member.id)

        if user_key not in wl_data:
            wl_data[user_key] = {"entries": [], "current": None}

        entry = {
            "nom_rp":       self.step1["nom_rp"],
            "age_rp":       self.step1["age_rp"],
            "background":   self.step1["background"],
            "type_wl":      self.type_wl,
            "background_ok": self.background_ok,
            "reglement_ok": self.reglement_ok,
            "decision":     self.decision,
            "notes":        self.step1["notes"],
            "moderator":    interaction.user.name,
            "moderator_id": interaction.user.id,
            "date":         datetime.now().isoformat(),
        }

        wl_data[user_key]["entries"].append(entry)
        wl_data[user_key]["current"] = entry
        save_data("data/whitelist.json", wl_data)

        if self.decision == "accepte":
            wl_role = interaction.guild.get_role(CITOYEN_WL_ROLE)
            if wl_role:
                try:
                    await self.member.add_roles(wl_role)
                except Exception:
                    pass

        colors = {"accepte": discord.Color.green(), "refuse": discord.Color.red(), "attente": discord.Color.gold()}
        icons  = {"accepte": "✅", "refuse": "❌", "attente": "⏳"}

        log_embed = discord.Embed(
            title=f"{icons[self.decision]} Whitelist {self.decision.upper()} — {self.step1['nom_rp']}",
            color=colors[self.decision],
            timestamp=datetime.now()
        )
        log_embed.add_field(name="👤 Joueur",        value=f"{self.member.mention} (`{self.member.id}`)", inline=False)
        log_embed.add_field(name="🎭 Nom RP",        value=self.step1["nom_rp"],        inline=True)
        log_embed.add_field(name="🎂 Âge RP",        value=self.step1["age_rp"],        inline=True)
        log_embed.add_field(name="⚖️ Type",          value=WL_ROLES.get(self.type_wl, self.type_wl), inline=True)
        log_embed.add_field(name="📖 Background",    value="✅ OK" if self.background_ok == "ok" else "❌ NON", inline=True)
        log_embed.add_field(name="📜 Règlement",     value="✅ OK" if self.reglement_ok == "ok" else "❌ NON", inline=True)
        if self.step1["notes"]:
            log_embed.add_field(name="🗒️ Notes staff", value=self.step1["notes"], inline=False)
        log_embed.add_field(name="👮 Modérateur",    value=interaction.user.mention, inline=False)
        log_embed.set_thumbnail(url=self.member.display_avatar.url)
        log_embed.set_footer(text=f"Entrée #{len(wl_data[user_key]['entries'])} pour ce joueur")

        logs_wl = bot.get_channel(LOGS_WL_CHANNEL)
        if logs_wl is None:
            try:
                logs_wl = await bot.fetch_channel(LOGS_WL_CHANNEL)
            except Exception as fetch_err:
                print(f"[WHITELIST] ❌ Salon logs introuvable (ID: {LOGS_WL_CHANNEL}) : {fetch_err}")
                logs_wl = None
        
        if logs_wl:
            await logs_wl.send(embed=log_embed)
            print(f"[WHITELIST] ✅ Log envoyé pour {self.member.name}")
        else:
            print(f"[WHITELIST] ❌ Canal WL inaccessible")

        await interaction.response.send_message(
            f"{icons[self.decision]} Whitelist de {self.member.mention} : **{self.decision.upper()}**",
            ephemeral=True
        )

# ======================================================
#  BROADCAST
# ======================================================

ANNONCE_COLORS = {
    "Bleu": discord.Color.blue(),
    "Vert": discord.Color.green(),
    "Rouge": discord.Color.red(),
    "Orange": discord.Color.orange(),
    "Violet": discord.Color.purple(),
    "Jaune": discord.Color.gold(),
    "Bleu Clair": discord.Color.blurple(),
}


class AnnonceModal(discord.ui.Modal, title="📢 Créer un Broadcast"):
    titre = discord.ui.TextInput(
        label="Titre de l'annonce",
        placeholder="Ex: Maintenance serveur",
        required=True,
        max_length=256
    )

    message = discord.ui.TextInput(
        label="Message principal",
        placeholder="Votre message ici...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=4000
    )

    image_url = discord.ui.TextInput(
        label="URL de l'image (optionnel)",
        placeholder="https://exemple.com/image.png",
        required=False,
        max_length=500
    )

    couleur = discord.ui.TextInput(
        label="Couleur (Bleu/Vert/Rouge/Orange/Violet/Jaune)",
        placeholder="Bleu",
        required=False,
        max_length=20,
        default="Bleu"
    )

    def __init__(self, channel: discord.TextChannel):
        super().__init__()
        self.channel = channel

    async def on_submit(self, interaction: discord.Interaction):
        try:
            color_name = self.couleur.value.strip().capitalize()
            color = ANNONCE_COLORS.get(color_name, discord.Color.blue())

            embed = discord.Embed(
                title=f"📢 {self.titre.value}",
                description=self.message.value,
                color=color,
                timestamp=datetime.now()
            )

            if self.image_url.value and self.image_url.value.strip():
                embed.set_image(url=self.image_url.value.strip())

            if interaction.guild and interaction.guild.icon:
                embed.set_thumbnail(url=interaction.guild.icon.url)

            embed.set_footer(
                text=f"📣 Annonce officielle • Par {interaction.user.name}",
                icon_url=interaction.user.display_avatar.url
            )

            await self.channel.send(embed=embed)
            await interaction.response.send_message(
                f"✅ Broadcast envoyé dans {self.channel.mention}",
                ephemeral=True
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erreur : {str(e)}",
                ephemeral=True
            )


@tree.command(
    name="bc",
    description="Envoyer un broadcast dans un salon"
)
@app_commands.describe(
    salon="Le salon où envoyer le broadcast"
)
async def bc(interaction: discord.Interaction, salon: discord.TextChannel):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        return

    modal = AnnonceModal(salon)
    await interaction.response.send_modal(modal)

# ======================================================
#  REMBOURSEMENT
# ======================================================

class RemboursementModal(discord.ui.Modal, title="💰 Remboursement"):
    nom_prenom_rp = discord.ui.TextInput(
        label="Nom Prénom RP (ID Discord)",
        placeholder="Ex: John Doe (123456789012345678)",
        required=True,
        max_length=150
    )

    date_heure = discord.ui.TextInput(
        label="Date et Heure",
        placeholder="Ex: 18/06/2026 à 14h30",
        required=True,
        max_length=100
    )

    note_remboursement = discord.ui.TextInput(
        label="Note de remboursement",
        placeholder="Raison du remboursement...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=1000
    )

    async def on_submit(self, interaction: discord.Interaction):
        remboursements = load_data("data/remboursements.json")

        timestamp = datetime.now().isoformat()
        entry = {
            "nom_prenom_rp": self.nom_prenom_rp.value,
            "date_heure": self.date_heure.value,
            "note": self.note_remboursement.value,
            "staff_name": interaction.user.name,
            "staff_id": interaction.user.id,
            "date_creation": timestamp,
        }

        if "all" not in remboursements:
            remboursements["all"] = []

        remboursements["all"].append(entry)
        save_data("data/remboursements.json", remboursements)

        embed = discord.Embed(
            title="💰 Nouveau Remboursement",
            color=discord.Color.gold(),
            timestamp=datetime.now()
        )
        embed.add_field(name="🎭 Nom Prénom RP", value=self.nom_prenom_rp.value, inline=False)
        embed.add_field(name="📅 Date et Heure", value=self.date_heure.value, inline=True)
        embed.add_field(name="📝 Note", value=self.note_remboursement.value, inline=False)
        embed.add_field(name="👮 Traité par", value=f"{interaction.user.mention}", inline=False)
        embed.set_footer(text=f"Remboursement #{len(remboursements['all'])}")

        logs_channel = bot.get_channel(LOGS_REMBOURSEMENT_CHANNEL)
        if logs_channel is None:
            try:
                logs_channel = await bot.fetch_channel(LOGS_REMBOURSEMENT_CHANNEL)
            except Exception as fetch_err:
                print(f"[REMBOURSEMENT] ❌ Salon logs introuvable (ID: {LOGS_REMBOURSEMENT_CHANNEL}) : {fetch_err}")
                logs_channel = None
        
        if logs_channel:
            await logs_channel.send(embed=embed)
            print(f"[REMBOURSEMENT] ✅ Log envoyé")
        else:
            print(f"[REMBOURSEMENT] ❌ Canal remboursement inaccessible")

        await interaction.response.send_message(
            "✅ Remboursement enregistré",
            ephemeral=True
        )


@tree.command(
    name="remboursement",
    description="Créer une demande de remboursement"
)
async def remboursement(interaction: discord.Interaction):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        return

    modal = RemboursementModal()
    await interaction.response.send_modal(modal)


# ======================================================
#  CLEAR MESSAGES
# ======================================================

@tree.command(
    name="clear",
    description="Supprimer un nombre de messages dans le salon actuel"
)
@app_commands.describe(
    nombre="Nombre de messages à supprimer (1-100)"
)
async def clear(interaction: discord.Interaction, nombre: int):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        return

    if nombre < 1 or nombre > 100:
        await interaction.response.send_message(
            "❌ Le nombre doit être entre 1 et 100.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        f"🗑️ Suppression de {nombre} message(s) en cours...",
        ephemeral=True
    )

    try:
        deleted = await interaction.channel.purge(limit=nombre)

        confirm_msg = await interaction.channel.send(
            f"✅ {len(deleted)} message(s) supprimé(s) par {interaction.user.mention}"
        )

        await asyncio.sleep(5)
        await confirm_msg.delete()

    except Exception as e:
        await interaction.followup.send(
            f"❌ Erreur lors de la suppression : {str(e)}",
            ephemeral=True
        )

# ======================================================
#  ÉVÉNEMENTS
# ======================================================

@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")

    try:
        guild = discord.Object(id=GUILD_ID)
        tree.copy_global_to(guild=guild)
        synced = await tree.sync(guild=guild)

        print(f"✅ {len(synced)} commandes synchronisées sur le serveur")

        for cmd in synced:
            print(f"➜ /{cmd.name}")

    except Exception as e:
        print(f"❌ Erreur sync : {e}")

    if not check_mutes.is_running():
        check_mutes.start()

    await bot.change_presence(
        activity=discord.Game(name="Revital RP")
    )

@bot.event
async def on_member_join(member: discord.Member):
    print(f"[JOIN] {member.name} a rejoint le serveur")
    try:
        # IDs fixes
        VERIF_CH_ID   = 1517020243975864442
        UNVERIF_ROLE_ID = 1517043612892926002

        # 1. Rôle non-vérifié
        unverified_role = member.guild.get_role(UNVERIF_ROLE_ID)
        if unverified_role:
            await member.add_roles(unverified_role)
            print(f"[JOIN] ✅ Rôle non-vérifié assigné à {member.name}")
        else:
            print(f"[JOIN] ❌ Rôle non-vérifié introuvable (ID: {UNVERIF_ROLE_ID})")

        # 2. Générer le captcha
        captcha_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        captchas = load_data("data/captchas.json")
        captchas[str(member.id)] = {
            "code":     captcha_code,
            "created":  datetime.now().isoformat(),
            "attempts": 0,
            "msg_id":   None,
        }
        save_data("data/captchas.json", captchas)
        print(f"[JOIN] Captcha généré pour {member.name} : {captcha_code}")

        # 3. Envoyer dans #verification
        verification_channel = bot.get_channel(VERIF_CH_ID)
        if not verification_channel:
            print(f"[JOIN] ❌ Salon vérification introuvable (ID: {VERIF_CH_ID})")
            return

        embed_verif = discord.Embed(
            title="🔐 Vérification — Revital RP",
            description=(
                f"Bienvenue {member.mention} sur **Revital RP** !\n\n"
                f"Pour accéder au serveur, tu dois te vérifier.\n\n"
                f"📋 **Ton code de vérification :** `{captcha_code}`\n\n"
                f"✅ **Tape dans ce salon :**\n"
                f"```/verify {captcha_code}```\n\n"
                f"⏱️ _Ce code est valable 30 minutes._"
            ),
            color=discord.Color.blurple(),
            timestamp=datetime.now()
        )
        embed_verif.set_thumbnail(url=member.display_avatar.url)
        embed_verif.set_footer(text="Revital RP • Système de vérification automatique")

        sent = await verification_channel.send(content=f"👋 {member.mention}", embed=embed_verif)
        print(f"[JOIN] ✅ Message captcha envoyé (ID: {sent.id})")

        # Sauvegarder l'ID du message pour le supprimer après vérif
        captchas = load_data("data/captchas.json")
        if str(member.id) in captchas:
            captchas[str(member.id)]["msg_id"] = sent.id
            save_data("data/captchas.json", captchas)

        # 4. Message de bienvenue
        welcome_channel = bot.get_channel(WELCOME_CHANNEL)
        if welcome_channel:
            welcome_embed = discord.Embed(
                title="👋 Bienvenue sur Revital RP !",
                description=(
                    f"**{member.mention}** vient de rejoindre le serveur !\n\n"
                    f"🎉 Nous sommes maintenant **{member.guild.member_count}** membres !\n\n"
                    f"N'oublie pas de te vérifier dans <#1517020243975864442> pour accéder au serveur."
                ),
                color=discord.Color.green(),
                timestamp=datetime.now()
            )
            welcome_embed.set_thumbnail(url=member.display_avatar.url)
            welcome_embed.set_footer(text="Revital RP • Bienvenue !")
            await welcome_channel.send(content=f"👋 {member.mention}", embed=welcome_embed)

    except Exception as e:
        print(f"[on_member_join] ❌ Erreur : {e}")
        import traceback
        traceback.print_exc()

@bot.event
async def on_member_remove(member: discord.Member):
    """Envoie un message de départ dans le salon dédié."""
    try:
        welcome_channel = bot.get_channel(WELCOME_CHANNEL)
        if not welcome_channel:
            return

        leave_embed = discord.Embed(
            title="👋 Au revoir !",
            description=(
                f"**{member.name}** vient de quitter le serveur.\n\n"
                f"😢 Nous sommes maintenant **{member.guild.member_count}** membres."
            ),
            color=discord.Color.red(),
            timestamp=datetime.now()
        )
        leave_embed.set_thumbnail(url=member.display_avatar.url)
        leave_embed.set_footer(text="Revital RP • À bientôt !")

        await welcome_channel.send(embed=leave_embed)

    except Exception as e:
        print(f"[on_member_remove] Erreur : {e}")

# ======================================================
#  VÉRIFICATION
# ======================================================

@tree.command(name="verify", description="Vérifier ton compte avec le code captcha")
@app_commands.describe(code="Le code reçu dans #verification")
async def verify(interaction: discord.Interaction, code: str):
    VERIF_CH_ID    = 1517020243975864442
    UNVERIF_ROLE_ID = 1517043612892926002
    VERIF_ROLE_ID  = 1516284942064025661

    captchas = load_data("data/captchas.json")
    uid = str(interaction.user.id)
    print(f"[VERIFY] {interaction.user.name} tente : {code}")

    if uid not in captchas:
        await interaction.response.send_message(
            "❌ Aucun captcha actif. Quitte et rejoins le serveur à nouveau.",
            ephemeral=True
        )
        return

    if captchas[uid]["code"] == code.upper().strip():
        msg_id = captchas[uid].get("msg_id")
        del captchas[uid]
        save_data("data/captchas.json", captchas)

        # Retirer rôle non-vérifié
        unverified_role = interaction.guild.get_role(UNVERIF_ROLE_ID)
        if unverified_role and unverified_role in interaction.user.roles:
            await interaction.user.remove_roles(unverified_role)
            print(f"[VERIFY] ✅ Rôle non-vérifié retiré à {interaction.user.name}")

        # Ajouter rôle vérifié
        verified_role = interaction.guild.get_role(VERIF_ROLE_ID)
        if verified_role:
            await interaction.user.add_roles(verified_role)
            print(f"[VERIFY] ✅ Rôle vérifié ajouté à {interaction.user.name}")
        else:
            print(f"[VERIFY] ❌ Rôle vérifié introuvable (ID: {VERIF_ROLE_ID})")

        embed = discord.Embed(
            title="✅ Vérification réussie !",
            description="Bienvenue sur **Revital RP** !\n\nTu as maintenant accès à l'ensemble du serveur. 🎉",
            color=discord.Color.green()
        )
        embed.set_footer(text="Bon jeu sur Revital RP !")
        await interaction.response.send_message(embed=embed, ephemeral=True)

        # Supprimer le message captcha
        if msg_id:
            verif_channel = bot.get_channel(VERIF_CH_ID)
            if verif_channel:
                try:
                    msg_to_del = await verif_channel.fetch_message(msg_id)
                    await msg_to_del.delete()
                    print(f"[VERIFY] ✅ Message captcha supprimé")
                except Exception as e:
                    print(f"[VERIFY] ❌ Suppression message : {e}")

    else:
        captchas[uid]["attempts"] = captchas[uid].get("attempts", 0) + 1
        save_data("data/captchas.json", captchas)
        attempts = captchas[uid]["attempts"]
        print(f"[VERIFY] ❌ Code incorrect pour {interaction.user.name} ({attempts}/5)")

        if attempts >= 5:
            del captchas[uid]
            save_data("data/captchas.json", captchas)
            await interaction.response.send_message(
                "❌ Trop de tentatives. Quitte et rejoins le serveur pour un nouveau code.",
                ephemeral=True
            )
        else:
            await interaction.response.send_message(
                f"❌ Code incorrect. Tentative **{attempts}/5**.",
                ephemeral=True
            )


# ======================================================
#  MODÉRATION
# ======================================================

@tree.command(name="warn", description="Ajouter un warn à un membre")
@app_commands.describe(member="Le membre à avertir", raison="Raison de l'avertissement", type_warn="Discord ou IG")
@app_commands.choices(type_warn=[
    app_commands.Choice(name="Discord", value="Discord"),
    app_commands.Choice(name="In-Game", value="In-Game"),
])
async def warn(interaction: discord.Interaction, member: discord.Member, raison: str, type_warn: app_commands.Choice[str] = None):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Permission refusée.", ephemeral=True)
        return

    warns_data = load_data("data/warns.json")
    uid = str(member.id)
    if uid not in warns_data:
        warns_data[uid] = []

    entry = {
        "reason":    raison,
        "moderator": interaction.user.name,
        "mod_id":    interaction.user.id,
        "date":      datetime.now().isoformat(),
        "type":      type_warn.value if type_warn else "Discord",
    }
    warns_data[uid].append(entry)
    save_data("data/warns.json", warns_data)
    count = len(warns_data[uid])

    embed = discord.Embed(
        title="⚠️ Warn Ajouté",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    embed.add_field(name="Utilisateur",  value=member.mention, inline=True)
    embed.add_field(name="Modérateur",   value=interaction.user.mention, inline=True)
    embed.add_field(name="Total warns",  value=str(count), inline=True)
    embed.add_field(name="Type",         value=entry["type"], inline=True)
    embed.add_field(name="Raison",       value=raison, inline=False)

    log_ch = bot.get_channel(LOGS_CHANNEL)
    if log_ch:
        await log_ch.send(embed=embed)

    await interaction.response.send_message(embed=embed)


@tree.command(name="warns", description="Voir les warns d'un membre")
@app_commands.describe(member="Le membre (toi par défaut)")
async def warns_cmd(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    warns_data = load_data("data/warns.json")
    user_warns = warns_data.get(str(target.id), [])

    embed = discord.Embed(
        title=f"⚠️ Warns — {target.display_name}",
        description=f"**{len(user_warns)} avertissement(s)** au total",
        color=discord.Color.orange()
    )
    for i, w in enumerate(user_warns[-10:], 1):
        embed.add_field(
            name=f"Warn #{i} — {w.get('type', 'Discord')}",
            value=f"📋 {w['reason']}\n👮 {w['moderator']} • 📅 {w['date'][:10]}",
            inline=False
        )
    if not user_warns:
        embed.description = "✅ Aucun avertissement."
    await interaction.response.send_message(embed=embed)


@tree.command(name="clearwarn", description="Supprimer un warn spécifique d'un membre")
@app_commands.describe(member="Le membre", numero="Numéro du warn (voir /warns)")
async def clearwarn(interaction: discord.Interaction, member: discord.Member, numero: int):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        return
    warns_data = load_data("data/warns.json")
    uid = str(member.id)
    lst = warns_data.get(uid, [])
    if numero < 1 or numero > len(lst):
        await interaction.response.send_message(f"❌ Warn #{numero} introuvable (total: {len(lst)}).", ephemeral=True)
        return
    removed = lst.pop(numero - 1)
    warns_data[uid] = lst
    save_data("data/warns.json", warns_data)
    await interaction.response.send_message(f"✅ Warn #{numero} de {member.mention} supprimé (`{removed['reason']}`).")


@tree.command(name="clearallwarns", description="Supprimer TOUS les warns d'un membre")
@app_commands.describe(member="Le membre")
async def clearallwarns(interaction: discord.Interaction, member: discord.Member):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        return
    warns_data = load_data("data/warns.json")
    warns_data[str(member.id)] = []
    save_data("data/warns.json", warns_data)
    await interaction.response.send_message(f"✅ Tous les warns de {member.mention} ont été supprimés.")


@tree.command(name="history", description="Voir l'historique complet des sanctions d'un membre")
@app_commands.describe(member="Le membre")
async def history(interaction: discord.Interaction, member: discord.Member):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Réservé au staff.", ephemeral=True)
        return

    warns_data = load_data("data/warns.json")
    wl_data    = load_data("data/whitelist.json")
    mutes_data = load_data("data/mutes.json")

    embed = discord.Embed(
        title=f"📁 Historique — {member.display_name}",
        description=f"ID : `{member.id}`",
        color=discord.Color.blurple(),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=member.display_avatar.url)

    user_warns = warns_data.get(str(member.id), [])
    warn_text = "\n".join(
        [f"• [{w.get('type','?')}] {w['reason']} — {w['date'][:10]} (par {w['moderator']})" for w in user_warns[-5:]]
    ) or "Aucun warn"
    embed.add_field(name=f"⚠️ Warns ({len(user_warns)})", value=warn_text, inline=False)

    wl = wl_data.get(str(member.id))
    if wl:
        current = wl.get("current", {})
        nb = len(wl.get("entries", []))
        embed.add_field(
            name=f"✅ Whitelist ({nb} entrée(s))",
            value=(
                f"Décision actuelle : **{current.get('decision','?').upper()}**\n"
                f"Type : {current.get('type_wl','?')} | Nom RP : {current.get('nom_rp','?')}\n"
                f"Date : {current.get('date','?')[:10]}"
            ),
            inline=False
        )
    else:
        embed.add_field(name="✅ Whitelist", value="Non whitelisté", inline=False)

    mute = mutes_data.get(str(member.id))
    if mute:
        embed.add_field(
            name="🔇 Mute actif",
            value=f"Fin : {mute['unmute_time'][:16].replace('T',' ')}\nRaison : {mute['reason']}",
            inline=False
        )

    await interaction.response.send_message(embed=embed)


@tree.command(name="mute", description="Mute temporaire un membre")
@app_commands.describe(member="Le membre", duree="Durée (ex: 30m, 1h, 7d)", raison="Raison")
async def mute(interaction: discord.Interaction, member: discord.Member, duree: str, raison: str = "Aucune raison"):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Permission refusée.", ephemeral=True)
        return
    seconds = parse_duration(duree)
    if seconds is None:
        await interaction.response.send_message("❌ Format invalide. Ex : `30m`, `1h`, `7d`", ephemeral=True)
        return

    mutes = load_data("data/mutes.json")
    mutes[str(member.id)] = {
        "unmute_time": (datetime.now() + timedelta(seconds=seconds)).isoformat(),
        "reason":      raison,
        "moderator":   interaction.user.name,
    }
    save_data("data/mutes.json", mutes)

    mute_role = interaction.guild.get_role(MUTED_ROLE)
    if mute_role:
        await member.add_roles(mute_role)

    embed = discord.Embed(title="🔇 Mute", color=discord.Color.red(), timestamp=datetime.now())
    embed.add_field(name="Membre",      value=member.mention)
    embed.add_field(name="Durée",       value=fmt_duration(seconds))
    embed.add_field(name="Modérateur",  value=interaction.user.mention)
    embed.add_field(name="Raison",      value=raison, inline=False)

    log_ch = bot.get_channel(LOGS_CHANNEL)
    if log_ch:
        await log_ch.send(embed=embed)
    await interaction.response.send_message(embed=embed)


@tree.command(name="unmute", description="Unmute un membre")
@app_commands.describe(member="Le membre")
async def unmute(interaction: discord.Interaction, member: discord.Member):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Permission refusée.", ephemeral=True)
        return
    mutes = load_data("data/mutes.json")
    if str(member.id) in mutes:
        del mutes[str(member.id)]
        save_data("data/mutes.json", mutes)
    mute_role = interaction.guild.get_role(MUTED_ROLE)
    if mute_role:
        await member.remove_roles(mute_role)
    await interaction.response.send_message(f"✅ {member.mention} a été unmute.")


@tree.command(name="kick", description="Expulser un membre")
@app_commands.describe(member="Le membre", raison="Raison")
async def kick(interaction: discord.Interaction, member: discord.Member, raison: str = "Aucune raison"):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        return
    embed = discord.Embed(title="👢 Kick", color=discord.Color.red(), timestamp=datetime.now())
    embed.add_field(name="Membre", value=member.mention)
    embed.add_field(name="Modérateur", value=interaction.user.mention)
    embed.add_field(name="Raison", value=raison, inline=False)
    log_ch = bot.get_channel(LOGS_CHANNEL)
    if log_ch:
        await log_ch.send(embed=embed)
    await member.kick(reason=raison)
    await interaction.response.send_message(embed=embed)


@tree.command(name="ban", description="Bannir un membre")
@app_commands.describe(member="Le membre", raison="Raison", duree="Durée du ban (optionnel : 7d, 30d...)")
async def ban(interaction: discord.Interaction, member: discord.Member, raison: str = "Aucune raison", duree: str = None):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        return
    embed = discord.Embed(title="🔨 Ban", color=discord.Color.dark_red(), timestamp=datetime.now())
    embed.add_field(name="Membre",     value=member.mention)
    embed.add_field(name="Modérateur", value=interaction.user.mention)
    embed.add_field(name="Durée",      value=duree or "Permanent")
    embed.add_field(name="Raison",     value=raison, inline=False)
    log_ch = bot.get_channel(LOGS_CHANNEL)
    if log_ch:
        await log_ch.send(embed=embed)
    await member.ban(reason=raison)
    await interaction.response.send_message(embed=embed)


# ======================================================
#  WHITELIST COMMANDS
# ======================================================

@tree.command(name="whitelist", description="Ouvrir le formulaire de whitelist pour un joueur")
@app_commands.describe(member="Le joueur à whitelister")
async def whitelist_cmd(interaction: discord.Interaction, member: discord.Member):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Réservé au staff.", ephemeral=True)
        return
    modal = WhitelistStep1Modal(member)
    await interaction.response.send_modal(modal)


@tree.command(name="check-wl", description="Vérifier le statut whitelist d'un joueur")
@app_commands.describe(member="Le joueur (toi par défaut)")
async def check_wl(interaction: discord.Interaction, member: discord.Member = None):
    target = member or interaction.user
    wl_data = load_data("data/whitelist.json")
    entry   = wl_data.get(str(target.id))

    if not entry or not entry.get("current"):
        await interaction.response.send_message(f"❌ {target.mention} n'est pas whitelisté.", ephemeral=True)
        return

    c = entry["current"]
    nb_entries = len(entry.get("entries", []))
    icons = {"accepte": "✅", "refuse": "❌", "attente": "⏳"}
    colors = {"accepte": discord.Color.green(), "refuse": discord.Color.red(), "attente": discord.Color.gold()}
    decision = c.get("decision", "?")

    embed = discord.Embed(
        title=f"{icons.get(decision,'?')} Whitelist — {target.display_name}",
        color=colors.get(decision, discord.Color.grey()),
        timestamp=datetime.now()
    )
    embed.set_thumbnail(url=target.display_avatar.url)
    embed.add_field(name="🎭 Nom RP",        value=c.get("nom_rp","?"),   inline=True)
    embed.add_field(name="🎂 Âge RP",        value=c.get("age_rp","?"),   inline=True)
    embed.add_field(name="⚖️ Type",          value=WL_ROLES.get(c.get("type_wl",""),"?"), inline=True)
    embed.add_field(name="📖 Background",    value="✅" if c.get("background_ok")=="ok" else "❌", inline=True)
    embed.add_field(name="📜 Règlement",     value="✅" if c.get("reglement_ok")=="ok" else "❌",  inline=True)
    embed.add_field(name="🗓️ Date",         value=c.get("date","?")[:10], inline=True)
    embed.add_field(name="👮 Modérateur",    value=c.get("moderator","?"), inline=True)
    if c.get("notes"):
        embed.add_field(name="🗒️ Notes",    value=c["notes"], inline=False)
    embed.set_footer(text=f"{nb_entries} entrée(s) au total dans l'historique")
    await interaction.response.send_message(embed=embed)


@tree.command(name="wl-history", description="Voir tout l'historique de whitelist d'un joueur")
@app_commands.describe(member="Le joueur")
async def wl_history(interaction: discord.Interaction, member: discord.Member):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Réservé au staff.", ephemeral=True)
        return
    wl_data = load_data("data/whitelist.json")
    entry   = wl_data.get(str(member.id))

    if not entry or not entry.get("entries"):
        await interaction.response.send_message(f"❌ Aucun historique pour {member.mention}.", ephemeral=True)
        return

    embed = discord.Embed(
        title=f"📚 Historique WL — {member.display_name}",
        description=f"{len(entry['entries'])} entrée(s) au total",
        color=discord.Color.blurple()
    )
    for i, e in enumerate(entry["entries"][-8:], 1):
        icons = {"accepte": "✅", "refuse": "❌", "attente": "⏳"}
        embed.add_field(
            name=f"Entrée #{i} — {icons.get(e.get('decision','?'),'?')} {e.get('decision','?').upper()}",
            value=(
                f"Nom RP : {e.get('nom_rp','?')} | Type : {e.get('type_wl','?')}\n"
                f"BG : {'✅' if e.get('background_ok')=='ok' else '❌'} | Règl : {'✅' if e.get('reglement_ok')=='ok' else '❌'}\n"
                f"👮 {e.get('moderator','?')} • 📅 {e.get('date','?')[:10]}"
            ),
            inline=False
        )
    await interaction.response.send_message(embed=embed)


@tree.command(name="wl-revoke", description="Révoquer la whitelist d'un joueur")
@app_commands.describe(member="Le joueur", raison="Raison de la révocation")
async def wl_revoke(interaction: discord.Interaction, member: discord.Member, raison: str):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        return

    wl_data = load_data("data/whitelist.json")
    uid = str(member.id)
    if uid not in wl_data:
        await interaction.response.send_message(f"❌ {member.mention} n'est pas whitelisté.", ephemeral=True)
        return

    revoke_entry = {
        "nom_rp":    wl_data[uid].get("current", {}).get("nom_rp", "?"),
        "decision":  "revoque",
        "raison":    raison,
        "moderator": interaction.user.name,
        "date":      datetime.now().isoformat(),
    }
    wl_data[uid]["entries"].append(revoke_entry)
    wl_data[uid]["current"] = revoke_entry
    save_data("data/whitelist.json", wl_data)

    wl_role = interaction.guild.get_role(CITOYEN_WL_ROLE)
    if wl_role and wl_role in member.roles:
        await member.remove_roles(wl_role)

    embed = discord.Embed(
        title="🚫 Whitelist Révoquée",
        description=f"{member.mention} (`{member.id}`)\nRaison : {raison}\nPar : {interaction.user.mention}",
        color=discord.Color.dark_red(),
        timestamp=datetime.now()
    )
    logs_wl = bot.get_channel(LOGS_WL_CHANNEL)
    if logs_wl is None:
        try:
            logs_wl = await bot.fetch_channel(LOGS_WL_CHANNEL)
        except Exception as fetch_err:
            print(f"[WL-REVOKE] ❌ Salon logs introuvable (ID: {LOGS_WL_CHANNEL}) : {fetch_err}")
            logs_wl = None
    
    if logs_wl:
        await logs_wl.send(embed=embed)
        print(f"[WL-REVOKE] ✅ Log envoyé pour {member.name}")
    else:
        print(f"[WL-REVOKE] ❌ Canal WL inaccessible")
    
    await interaction.response.send_message(embed=embed)


# ======================================================
#  TICKET COMMANDS
# ======================================================

@tree.command(name="setup-tickets", description="Configurer le panneau de création de tickets")
async def setup_tickets(interaction: discord.Interaction):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎫 Système de Tickets — Revital RP",
        description=(
            "Besoin d'aide ou d'un suivi particulier ?\n\n"
            "**Sélectionne une catégorie** dans le menu ci-dessous pour ouvrir un ticket privé.\n"
            "Un membre du staff te répondra dès que possible.\n\n"
            "📋 Disponible : Support, Plainte, Boutique, Dev, Dossiers RP, Recours ban..."
        ),
        color=discord.Color.blurple()
    )
    embed.set_footer(text="Revital RP • Un seul ticket à la fois svp")

    view = TicketOpenView()
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Panneau de tickets envoyé !", ephemeral=True)


@tree.command(name="ticket-add", description="Ajouter un membre à un ticket (dans le salon du ticket)")
@app_commands.describe(member="Le membre à ajouter")
async def ticket_add(interaction: discord.Interaction, member: discord.Member):
    if not is_staff(interaction):
        await interaction.response.send_message("❌ Réservé au staff.", ephemeral=True)
        return
    await interaction.channel.set_permissions(member, view_channel=True, send_messages=True, read_message_history=True)
    await interaction.response.send_message(f"✅ {member.mention} ajouté au ticket.")


@tree.command(name="ticket-close", description="Fermer le ticket actuel (avec transcript)")
async def ticket_close(interaction: discord.Interaction):
    tickets = load_data("data/tickets.json")
    key = str(interaction.channel.id)
    if key not in tickets:
        await interaction.response.send_message("❌ Ce salon n'est pas un ticket.", ephemeral=True)
        return
    ticket_data = tickets[key]
    confirm_view = TicketCloseConfirmView(interaction.channel, ticket_data)
    await interaction.response.send_message("⚠️ Confirmer la fermeture ?", view=confirm_view, ephemeral=True)


# ======================================================
#  MUTES EXPIRÉS
# ======================================================

@tasks.loop(seconds=15)
async def check_mutes():
    mutes = load_data("data/mutes.json")
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return
    now = datetime.now()
    to_remove = []

    for uid, info in mutes.items():
        try:
            unmute_time = datetime.fromisoformat(info["unmute_time"])
            if now >= unmute_time:
                member = await guild.fetch_member(int(uid))
                mute_role = guild.get_role(MUTED_ROLE)
                if mute_role and mute_role in member.roles:
                    await member.remove_roles(mute_role)
                to_remove.append(uid)
        except Exception:
            to_remove.append(uid)

    for uid in to_remove:
        del mutes[uid]
    save_data("data/mutes.json", mutes)


# ======================================================
#  DÉMARRAGE
# ======================================================

if __name__ == "__main__":
    create_data_files()

    if not TOKEN:
        print("❌ ERREUR: Le token Discord n'est pas configuré!")
        print("📝 Créez un fichier .env et ajoutez votre token Discord")
        print("💡 Voir .env.example pour un exemple")
        exit(1)

    bot.run(TOKEN)
