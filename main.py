import discord
from discord import app_commands
from discord.ext import commands, tasks
import json
import os
from datetime import datetime, timedelta
import asyncio
import random
import string

# Configuration
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True
intents.reactions = True

bot = commands.Bot(command_prefix="?", intents=intents)

# ========== CONFIGURATION SERVEUR ==========
GUILD_ID = 123456789  # À REMPLACER
LOGS_CHANNEL = 987654321  # Canal logs modération
LOGS_WL_CHANNEL = 987654322  # Canal logs whitelist
TICKETS_CHANNEL = 987654323  # Canal création tickets
VERIFICATION_CHANNEL = 987654324  # Canal vérification

CITOYEN_WL_ROLE = 987654325  # Rôle à assigner
MUTED_ROLE = 987654326  # Rôle pour les mute
VERIFIED_ROLE = 987654327  # Rôle pour les vérifiés

# ========== FICHIERS DE DONNÉES ==========
def create_data_files():
    os.makedirs("data", exist_ok=True)
    
    files = {
        "data/warns.json": {},
        "data/mutes.json": {},
        "data/whitelist.json": {},
        "data/tickets.json": {},
        "data/captchas.json": {}
    }
    
    for file, default in files.items():
        if not os.path.exists(file):
            with open(file, 'w') as f:
                json.dump(default, f, indent=2)

def load_data(file):
    try:
        with open(file, 'r') as f:
            return json.load(f)
    except:
        return {}

def save_data(file, data):
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)

# ========== ÉVÉNEMENTS ==========

@bot.event
async def on_ready():
    print(f"✅ Bot connecté en tant que {bot.user}")
    check_mutes.start()
    await bot.change_presence(activity=discord.Game(name="Revital RP"))
    
    # Sync slash commands with Discord on startup
    try:
        synced = await bot.tree.sync()
        print(f"✅ {len(synced)} commande(s) slash synchronisée(s) avec Discord")
        for cmd in synced:
            print(f"  ➜ /{cmd.name}")
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation des commandes slash: {e}")

@bot.event
async def on_member_join(member):
    """Envoie le captcha au nouveau membre"""
    guild = member.guild
    try:
        embed = discord.Embed(
            title="🔐 Vérification Revital RP",
            description="Bienvenue sur le serveur ! Pour accéder au serveur, tu dois compléter la vérification.",
            color=discord.Color.green()
        )
        embed.add_field(name="Instructions", value="Clique sur le bouton ci-dessous pour obtenir ton captcha", inline=False)
        
        view = VerificationView(member)
        await member.send(embed=embed, view=view)
    except:
        print(f"❌ Impossible d'envoyer un DM à {member}")

# ========== VUES (BUTTONS) ==========

class VerificationView(discord.ui.View):
    def __init__(self, member):
        super().__init__(timeout=None)
        self.member = member
    
    @discord.ui.button(label="Obtenir le Captcha", style=discord.ButtonStyle.green)
    async def verify_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        
        # Génère un captcha
        captcha_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        
        captchas = load_data("data/captchas.json")
        captchas[str(self.member.id)] = {
            "code": captcha_code,
            "created": datetime.now().isoformat(),
            "attempts": 0
        }
        save_data("data/captchas.json", captchas)
        
        embed = discord.Embed(
            title="🔐 Code de Vérification",
            description=f"Ton code de vérification est: **{captcha_code}**\n\nEntre ce code avec la commande:\n`?verify {captcha_code}`",
            color=discord.Color.blue()
        )
        
        await interaction.followup.send(embed=embed, ephemeral=True)

class TicketView(discord.ui.View):
    def __init__(self, bot):
        super().__init__(timeout=None)
        self.bot = bot
    
    @discord.ui.button(label="📩 Créer un Ticket", style=discord.ButtonStyle.blurple)
    async def create_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        
        tickets = load_data("data/tickets.json")
        ticket_num = len(tickets) + 1
        
        # Crée le channel
        channel = await guild.create_text_channel(
            name=f"ticket-{ticket_num}",
            category=None
        )
        
        tickets[str(channel.id)] = {
            "creator": interaction.user.id,
            "created": datetime.now().isoformat(),
            "status": "open"
        }
        save_data("data/tickets.json", tickets)
        
        embed = discord.Embed(
            title=f"📩 Ticket #{ticket_num}",
            description=f"Ticket créé par {interaction.user.mention}",
            color=discord.Color.blurple()
        )
        
        view = TicketCloseView()
        await channel.send(embed=embed, view=view)
        
        await interaction.response.send_message(f"✅ Ticket créé: {channel.mention}", ephemeral=True)

class TicketCloseView(discord.ui.View):
    @discord.ui.button(label="Fermer le Ticket", style=discord.ButtonStyle.red)
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        tickets = load_data("data/tickets.json")
        
        if str(interaction.channel.id) in tickets:
            del tickets[str(interaction.channel.id)]
            save_data("data/tickets.json", tickets)
        
        await interaction.response.defer()
        await interaction.channel.delete()

# ========== COMMANDE SYNC ==========

@bot.command(name="sync")
@commands.has_permissions(administrator=True)
async def sync(ctx):
    """Synchronise manuellement les commandes slash avec Discord (?sync)"""
    await ctx.send("🔄 Synchronisation des commandes slash en cours...")
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ {len(synced)} commande(s) slash synchronisée(s) avec Discord.")
        print(f"✅ Sync manuel: {len(synced)} commande(s) synchronisée(s) par {ctx.author}")
    except Exception as e:
        await ctx.send(f"❌ Erreur lors de la synchronisation: {e}")
        print(f"❌ Erreur sync manuel: {e}")

# ========== COMMANDES MODÉRATION ==========

@bot.command(name="warn")
@commands.has_permissions(administrator=True)
async def warn(ctx, member: discord.Member, *, reason="Aucune raison"):
    """Ajouter un warn (IG ou Discord)"""
    
    warns = load_data("data/warns.json")
    user_id = str(member.id)
    
    if user_id not in warns:
        warns[user_id] = []
    
    warn_data = {
        "reason": reason,
        "moderator": ctx.author.name,
        "date": datetime.now().isoformat(),
        "type": "Discord"
    }
    
    warns[user_id].append(warn_data)
    save_data("data/warns.json", warns)
    
    warn_count = len(warns[user_id])
    
    # Embed logs
    embed = discord.Embed(
        title="⚠️ Warn Ajouté",
        description=f"Utilisateur: {member.mention}\nModérateur: {ctx.author.mention}\nRaison: {reason}\nNombre de warns: {warn_count}",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await ctx.send(f"✅ Warn ajouté à {member.mention} (Total: {warn_count})")

@bot.tree.command(name="warn", description="Ajouter un warn à un utilisateur")
@app_commands.describe(member="L'utilisateur à warn", reason="La raison du warn")
@app_commands.default_permissions(administrator=True)
async def slash_warn(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison"):
    """Slash command: /warn"""
    
    warns = load_data("data/warns.json")
    user_id = str(member.id)
    
    if user_id not in warns:
        warns[user_id] = []
    
    warn_data = {
        "reason": reason,
        "moderator": interaction.user.name,
        "date": datetime.now().isoformat(),
        "type": "Discord"
    }
    
    warns[user_id].append(warn_data)
    save_data("data/warns.json", warns)
    
    warn_count = len(warns[user_id])
    
    embed = discord.Embed(
        title="⚠️ Warn Ajouté",
        description=f"Utilisateur: {member.mention}\nModérateur: {interaction.user.mention}\nRaison: {reason}\nNombre de warns: {warn_count}",
        color=discord.Color.orange(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await interaction.response.send_message(f"✅ Warn ajouté à {member.mention} (Total: {warn_count})")

@bot.command(name="warns")
async def warns(ctx, member: discord.Member = None):
    """Voir les warns d'un utilisateur"""
    
    target = member or ctx.author
    warns = load_data("data/warns.json")
    user_warns = warns.get(str(target.id), [])
    
    embed = discord.Embed(
        title=f"⚠️ Warns de {target.name}",
        description=f"Total: {len(user_warns)} warn(s)",
        color=discord.Color.orange()
    )
    
    if user_warns:
        for i, warn in enumerate(user_warns, 1):
            embed.add_field(
                name=f"Warn #{i}",
                value=f"Raison: {warn['reason']}\nModérateur: {warn['moderator']}\nDate: {warn['date']}\nType: {warn['type']}",
                inline=False
            )
    
    await ctx.send(embed=embed)

@bot.tree.command(name="warns", description="Voir les warns d'un utilisateur")
@app_commands.describe(member="L'utilisateur dont voir les warns (optionnel)")
async def slash_warns(interaction: discord.Interaction, member: discord.Member = None):
    """Slash command: /warns"""
    
    target = member or interaction.user
    warns = load_data("data/warns.json")
    user_warns = warns.get(str(target.id), [])
    
    embed = discord.Embed(
        title=f"⚠️ Warns de {target.name}",
        description=f"Total: {len(user_warns)} warn(s)",
        color=discord.Color.orange()
    )
    
    if user_warns:
        for i, warn in enumerate(user_warns, 1):
            embed.add_field(
                name=f"Warn #{i}",
                value=f"Raison: {warn['reason']}\nModérateur: {warn['moderator']}\nDate: {warn['date']}\nType: {warn['type']}",
                inline=False
            )
    
    await interaction.response.send_message(embed=embed)

@bot.command(name="kick")
@commands.has_permissions(administrator=True)
async def kick(ctx, member: discord.Member, *, reason="Aucune raison"):
    """Kick un utilisateur"""
    
    embed = discord.Embed(
        title="👢 Kick",
        description=f"Utilisateur: {member.mention}\nModérateur: {ctx.author.mention}\nRaison: {reason}",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await member.kick(reason=reason)
    await ctx.send(f"✅ {member.mention} a été kick (Raison: {reason})")

@bot.tree.command(name="kick", description="Kick un utilisateur du serveur")
@app_commands.describe(member="L'utilisateur à kick", reason="La raison du kick")
@app_commands.default_permissions(administrator=True)
async def slash_kick(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison"):
    """Slash command: /kick"""
    
    embed = discord.Embed(
        title="👢 Kick",
        description=f"Utilisateur: {member.mention}\nModérateur: {interaction.user.mention}\nRaison: {reason}",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await member.kick(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} a été kick (Raison: {reason})")

@bot.command(name="ban")
@commands.has_permissions(administrator=True)
async def ban(ctx, member: discord.Member, *, reason="Aucune raison"):
    """Ban un utilisateur"""
    
    embed = discord.Embed(
        title="🔨 Ban",
        description=f"Utilisateur: {member.mention}\nModérateur: {ctx.author.mention}\nRaison: {reason}",
        color=discord.Color.dark_red(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await member.ban(reason=reason)
    await ctx.send(f"✅ {member.mention} a été banni (Raison: {reason})")

@bot.tree.command(name="ban", description="Bannir un utilisateur du serveur")
@app_commands.describe(member="L'utilisateur à bannir", reason="La raison du ban")
@app_commands.default_permissions(administrator=True)
async def slash_ban(interaction: discord.Interaction, member: discord.Member, reason: str = "Aucune raison"):
    """Slash command: /ban"""
    
    embed = discord.Embed(
        title="🔨 Ban",
        description=f"Utilisateur: {member.mention}\nModérateur: {interaction.user.mention}\nRaison: {reason}",
        color=discord.Color.dark_red(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await member.ban(reason=reason)
    await interaction.response.send_message(f"✅ {member.mention} a été banni (Raison: {reason})")

@bot.command(name="mute")
@commands.has_permissions(administrator=True)
async def mute(ctx, member: discord.Member, time: str, *, reason="Aucune raison"):
    """Mute temporaire: ?mute @user 1h Raison"""
    
    # Parse le temps (5m, 1h, 1d)
    time_multipliers = {
        's': 1,
        'm': 60,
        'h': 3600,
        'd': 86400
    }
    
    try:
        amount = int(time[:-1])
        unit = time[-1].lower()
        seconds = amount * time_multipliers.get(unit, 60)
    except:
        await ctx.send("❌ Format de temps invalide (ex: 1h, 5m, 1d)")
        return
    
    mutes = load_data("data/mutes.json")
    mutes[str(member.id)] = {
        "unmute_time": (datetime.now() + timedelta(seconds=seconds)).isoformat(),
        "reason": reason
    }
    save_data("data/mutes.json", mutes)
    
    # Ajoute le rôle mute
    mute_role = ctx.guild.get_role(MUTED_ROLE)
    if mute_role:
        await member.add_roles(mute_role)
    
    embed = discord.Embed(
        title="🔇 Mute",
        description=f"Utilisateur: {member.mention}\nModérateur: {ctx.author.mention}\nDurée: {time}\nRaison: {reason}",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await ctx.send(f"✅ {member.mention} a été mute pour {time}")

@bot.tree.command(name="mute", description="Mute temporaire un utilisateur (ex: 1h, 5m, 1d)")
@app_commands.describe(member="L'utilisateur à mute", time="Durée (ex: 1h, 5m, 1d)", reason="La raison du mute")
@app_commands.default_permissions(administrator=True)
async def slash_mute(interaction: discord.Interaction, member: discord.Member, time: str, reason: str = "Aucune raison"):
    """Slash command: /mute"""
    
    time_multipliers = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    
    try:
        amount = int(time[:-1])
        unit = time[-1].lower()
        seconds = amount * time_multipliers.get(unit, 60)
    except Exception:
        await interaction.response.send_message("❌ Format de temps invalide (ex: 1h, 5m, 1d)", ephemeral=True)
        return
    
    mutes = load_data("data/mutes.json")
    mutes[str(member.id)] = {
        "unmute_time": (datetime.now() + timedelta(seconds=seconds)).isoformat(),
        "reason": reason
    }
    save_data("data/mutes.json", mutes)
    
    mute_role = interaction.guild.get_role(MUTED_ROLE)
    if mute_role:
        await member.add_roles(mute_role)
    
    embed = discord.Embed(
        title="🔇 Mute",
        description=f"Utilisateur: {member.mention}\nModérateur: {interaction.user.mention}\nDurée: {time}\nRaison: {reason}",
        color=discord.Color.red(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await interaction.response.send_message(f"✅ {member.mention} a été mute pour {time}")

@bot.command(name="unmute")
@commands.has_permissions(administrator=True)
async def unmute(ctx, member: discord.Member):
    """Unmute un utilisateur"""
    
    mutes = load_data("data/mutes.json")
    if str(member.id) in mutes:
        del mutes[str(member.id)]
        save_data("data/mutes.json", mutes)
    
    mute_role = ctx.guild.get_role(MUTED_ROLE)
    if mute_role:
        await member.remove_roles(mute_role)
    
    embed = discord.Embed(
        title="🔊 Unmute",
        description=f"Utilisateur: {member.mention}\nModérateur: {ctx.author.mention}",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await ctx.send(f"✅ {member.mention} a été unmute")

@bot.tree.command(name="unmute", description="Unmute un utilisateur")
@app_commands.describe(member="L'utilisateur à unmute")
@app_commands.default_permissions(administrator=True)
async def slash_unmute(interaction: discord.Interaction, member: discord.Member):
    """Slash command: /unmute"""
    
    mutes = load_data("data/mutes.json")
    if str(member.id) in mutes:
        del mutes[str(member.id)]
        save_data("data/mutes.json", mutes)
    
    mute_role = interaction.guild.get_role(MUTED_ROLE)
    if mute_role:
        await member.remove_roles(mute_role)
    
    embed = discord.Embed(
        title="🔊 Unmute",
        description=f"Utilisateur: {member.mention}\nModérateur: {interaction.user.mention}",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    
    logs_channel = bot.get_channel(LOGS_CHANNEL)
    if logs_channel:
        await logs_channel.send(embed=embed)
    
    await interaction.response.send_message(f"✅ {member.mention} a été unmute")

# ========== COMMANDES WHITELIST ==========

@bot.command(name="whitelist")
@commands.has_permissions(administrator=True)
async def whitelist(ctx, member: discord.Member, legal: str, background: str, rules: str, *, note=""):
    """
    Whitelist: ?whitelist @user légal/illégal ok/non-ok ok/non-ok Note
    """
    
    if legal.lower() not in ["legal", "illegale"]:
        await ctx.send("❌ Légal doit être: legal ou illegale")
        return
    
    if background.lower() not in ["ok", "non-ok"]:
        await ctx.send("❌ Background doit être: ok ou non-ok")
        return
    
    if rules.lower() not in ["ok", "non-ok"]:
        await ctx.send("❌ Règlement doit être: ok ou non-ok")
        return
    
    whitelist = load_data("data/whitelist.json")
    whitelist[str(member.id)] = {
        "name": member.name,
        "legal": legal.lower(),
        "background": background.lower(),
        "rules": rules.lower(),
        "note": note,
        "date": datetime.now().isoformat(),
        "moderator": ctx.author.name
    }
    save_data("data/whitelist.json", whitelist)
    
    # Ajoute le rôle
    wl_role = ctx.guild.get_role(CITOYEN_WL_ROLE)
    if wl_role:
        await member.add_roles(wl_role)
    
    # Log
    embed = discord.Embed(
        title="✅ Whitelist Acceptée",
        description=f"Utilisateur: {member.mention}\nModérateur: {ctx.author.mention}",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    embed.add_field(name="Légal", value=legal, inline=True)
    embed.add_field(name="Background OK", value=background, inline=True)
    embed.add_field(name="Règlement OK", value=rules, inline=True)
    embed.add_field(name="Note", value=note or "Aucune", inline=False)
    
    logs_wl = bot.get_channel(LOGS_WL_CHANNEL)
    if logs_wl:
        await logs_wl.send(embed=embed)
    
    await ctx.send(f"✅ {member.mention} a été whitelisté")

@bot.tree.command(name="whitelist", description="Whitelister un utilisateur")
@app_commands.describe(
    member="L'utilisateur à whitelister",
    legal="legal ou illegale",
    background="ok ou non-ok",
    rules="ok ou non-ok",
    note="Note optionnelle"
)
@app_commands.default_permissions(administrator=True)
async def slash_whitelist(interaction: discord.Interaction, member: discord.Member, legal: str, background: str, rules: str, note: str = ""):
    """Slash command: /whitelist"""
    
    if legal.lower() not in ["legal", "illegale"]:
        await interaction.response.send_message("❌ Légal doit être: legal ou illegale", ephemeral=True)
        return
    
    if background.lower() not in ["ok", "non-ok"]:
        await interaction.response.send_message("❌ Background doit être: ok ou non-ok", ephemeral=True)
        return
    
    if rules.lower() not in ["ok", "non-ok"]:
        await interaction.response.send_message("❌ Règlement doit être: ok ou non-ok", ephemeral=True)
        return
    
    whitelist = load_data("data/whitelist.json")
    whitelist[str(member.id)] = {
        "name": member.name,
        "legal": legal.lower(),
        "background": background.lower(),
        "rules": rules.lower(),
        "note": note,
        "date": datetime.now().isoformat(),
        "moderator": interaction.user.name
    }
    save_data("data/whitelist.json", whitelist)
    
    wl_role = interaction.guild.get_role(CITOYEN_WL_ROLE)
    if wl_role:
        await member.add_roles(wl_role)
    
    embed = discord.Embed(
        title="✅ Whitelist Acceptée",
        description=f"Utilisateur: {member.mention}\nModérateur: {interaction.user.mention}",
        color=discord.Color.green(),
        timestamp=datetime.now()
    )
    embed.add_field(name="Légal", value=legal, inline=True)
    embed.add_field(name="Background OK", value=background, inline=True)
    embed.add_field(name="Règlement OK", value=rules, inline=True)
    embed.add_field(name="Note", value=note or "Aucune", inline=False)
    
    logs_wl = bot.get_channel(LOGS_WL_CHANNEL)
    if logs_wl:
        await logs_wl.send(embed=embed)
    
    await interaction.response.send_message(f"✅ {member.mention} a été whitelisté")

@bot.command(name="check-wl")
async def check_wl(ctx, member: discord.Member = None):
    """Vérifier le statut whitelist"""
    
    target = member or ctx.author
    whitelist = load_data("data/whitelist.json")
    
    if str(target.id) in whitelist:
        wl_data = whitelist[str(target.id)]
        embed = discord.Embed(
            title=f"✅ {target.name} - Whitelist",
            color=discord.Color.green()
        )
        embed.add_field(name="Légal", value=wl_data['legal'], inline=True)
        embed.add_field(name="Background OK", value=wl_data['background'], inline=True)
        embed.add_field(name="Règlement OK", value=wl_data['rules'], inline=True)
        embed.add_field(name="Note", value=wl_data['note'] or "Aucune", inline=False)
        embed.add_field(name="Date", value=wl_data['date'], inline=False)
        embed.add_field(name="Modérateur", value=wl_data['moderator'], inline=False)
        
        await ctx.send(embed=embed)
    else:
        await ctx.send(f"❌ {target.mention} n'est pas whitelisté")

@bot.tree.command(name="check-wl", description="Vérifier le statut whitelist d'un utilisateur")
@app_commands.describe(member="L'utilisateur à vérifier (optionnel)")
async def slash_check_wl(interaction: discord.Interaction, member: discord.Member = None):
    """Slash command: /check-wl"""
    
    target = member or interaction.user
    whitelist = load_data("data/whitelist.json")
    
    if str(target.id) in whitelist:
        wl_data = whitelist[str(target.id)]
        embed = discord.Embed(
            title=f"✅ {target.name} - Whitelist",
            color=discord.Color.green()
        )
        embed.add_field(name="Légal", value=wl_data['legal'], inline=True)
        embed.add_field(name="Background OK", value=wl_data['background'], inline=True)
        embed.add_field(name="Règlement OK", value=wl_data['rules'], inline=True)
        embed.add_field(name="Note", value=wl_data['note'] or "Aucune", inline=False)
        embed.add_field(name="Date", value=wl_data['date'], inline=False)
        embed.add_field(name="Modérateur", value=wl_data['moderator'], inline=False)
        
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message(f"❌ {target.mention} n'est pas whitelisté")

# ========== COMMANDES TICKETS ==========

@bot.command(name="setup-tickets")
@commands.has_permissions(administrator=True)
async def setup_tickets(ctx):
    """Setup le système de tickets"""
    
    embed = discord.Embed(
        title="📩 Système de Tickets",
        description="Clique sur le bouton ci-dessous pour créer un ticket",
        color=discord.Color.blurple()
    )
    
    view = TicketView(bot)
    await ctx.send(embed=embed, view=view)
    await ctx.send("✅ Système de tickets configuré!")

@bot.tree.command(name="setup-tickets", description="Configurer le système de tickets dans ce salon")
@app_commands.default_permissions(administrator=True)
async def slash_setup_tickets(interaction: discord.Interaction):
    """Slash command: /setup-tickets"""
    
    embed = discord.Embed(
        title="📩 Système de Tickets",
        description="Clique sur le bouton ci-dessous pour créer un ticket",
        color=discord.Color.blurple()
    )
    
    view = TicketView(bot)
    await interaction.channel.send(embed=embed, view=view)
    await interaction.response.send_message("✅ Système de tickets configuré!", ephemeral=True)

# ========== COMMANDES VÉRIFICATION ==========

@bot.command(name="verify")
async def verify(ctx, code: str):
    """Vérifier avec le captcha: ?verify CODE"""
    
    captchas = load_data("data/captchas.json")
    user_id = str(ctx.author.id)
    
    if user_id not in captchas:
        await ctx.send("❌ Tu n'as pas de captcha actif. Utilise ?getcaptcha", delete_after=5)
        return
    
    if captchas[user_id]["code"] == code:
        del captchas[user_id]
        save_data("data/captchas.json", captchas)
        
        # Ajoute le rôle vérifié
        guild = ctx.guild
        verified_role = guild.get_role(VERIFIED_ROLE)
        if verified_role:
            await ctx.author.add_roles(verified_role)
        
        embed = discord.Embed(
            title="✅ Vérification Réussie!",
            description="Tu peux maintenant accéder au serveur",
            color=discord.Color.green()
        )
        await ctx.send(embed=embed, delete_after=10)
    else:
        captchas[user_id]["attempts"] = captchas[user_id].get("attempts", 0) + 1
        save_data("data/captchas.json", captchas)
        
        await ctx.send("❌ Code incorrect! Essaye à nouveau.", delete_after=5)

@bot.tree.command(name="verify", description="Vérifier ton compte avec le code captcha")
@app_commands.describe(code="Le code captcha reçu")
async def slash_verify(interaction: discord.Interaction, code: str):
    """Slash command: /verify"""
    
    captchas = load_data("data/captchas.json")
    user_id = str(interaction.user.id)
    
    if user_id not in captchas:
        await interaction.response.send_message("❌ Tu n'as pas de captcha actif. Utilise /getcaptcha", ephemeral=True)
        return
    
    if captchas[user_id]["code"] == code:
        del captchas[user_id]
        save_data("data/captchas.json", captchas)
        
        verified_role = interaction.guild.get_role(VERIFIED_ROLE)
        if verified_role:
            await interaction.user.add_roles(verified_role)
        
        embed = discord.Embed(
            title="✅ Vérification Réussie!",
            description="Tu peux maintenant accéder au serveur",
            color=discord.Color.green()
        )
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        captchas[user_id]["attempts"] = captchas[user_id].get("attempts", 0) + 1
        save_data("data/captchas.json", captchas)
        
        await interaction.response.send_message("❌ Code incorrect! Essaye à nouveau.", ephemeral=True)

@bot.command(name="getcaptcha")
async def getcaptcha(ctx):
    """Obtenir un nouveau captcha"""
    
    captcha_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    captchas = load_data("data/captchas.json")
    captchas[str(ctx.author.id)] = {
        "code": captcha_code,
        "created": datetime.now().isoformat(),
        "attempts": 0
    }
    save_data("data/captchas.json", captchas)
    
    embed = discord.Embed(
        title="🔐 Nouveau Captcha",
        description=f"Ton code: **{captcha_code}**\n\nEntre: `?verify {captcha_code}`",
        color=discord.Color.blue()
    )
    
    await ctx.send(embed=embed, delete_after=30)

@bot.tree.command(name="getcaptcha", description="Obtenir un nouveau code captcha de vérification")
async def slash_getcaptcha(interaction: discord.Interaction):
    """Slash command: /getcaptcha"""
    
    captcha_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    captchas = load_data("data/captchas.json")
    captchas[str(interaction.user.id)] = {
        "code": captcha_code,
        "created": datetime.now().isoformat(),
        "attempts": 0
    }
    save_data("data/captchas.json", captchas)
    
    embed = discord.Embed(
        title="🔐 Nouveau Captcha",
        description=f"Ton code: **{captcha_code}**\n\nEntre: `/verify {captcha_code}`",
        color=discord.Color.blue()
    )
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# ========== BOUCLE MUTES ==========

@tasks.loop(seconds=10)
async def check_mutes():
    """Vérifie et retire les mutes expirés"""
    
    mutes = load_data("data/mutes.json")
    guild = bot.get_guild(GUILD_ID)
    now = datetime.now()
    
    to_remove = []
    
    for user_id, mute_info in mutes.items():
        unmute_time = datetime.fromisoformat(mute_info["unmute_time"])
        
        if now >= unmute_time:
            try:
                member = await guild.fetch_member(int(user_id))
                mute_role = guild.get_role(MUTED_ROLE)
                
                if mute_role and mute_role in member.roles:
                    await member.remove_roles(mute_role)
                
                to_remove.append(user_id)
            except:
                pass
    
    for user_id in to_remove:
        del mutes[user_id]
    
    save_data("data/mutes.json", mutes)

# ========== DÉMARRAGE ==========

if __name__ == "__main__":
    create_data_files()
    
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        print("❌ ERREUR: DISCORD_TOKEN non défini !")
        exit(1)
    
    bot.run(token)
