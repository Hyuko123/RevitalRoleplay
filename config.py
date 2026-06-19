"""
Configuration Revital RP Bot — charge les valeurs depuis le fichier .env
Copiez .env.example vers .env et remplissez vos IDs Discord.
"""
import os
from dotenv import load_dotenv
load_dotenv()
def _int(key: str, default: int = 0) -> int:
    value = os.getenv(key, "").strip()
    if not value:
        return default
    return int(value)
# ── BOT ──────────────────────────────────────────────────────
TOKEN = os.getenv("DISCORD_TOKEN", "")
GUILD_ID = _int("GUILD_ID", 1516284708219256962)
# ── CHANNELS LOGS ────────────────────────────────────────────
LOGS_CHANNEL = _int("LOGS_CHANNEL", 1517020116737593455)
LOGS_WL_CHANNEL = _int("LOGS_WL_CHANNEL", 1516285063996899359)
LOGS_TICKETS_CHANNEL = _int("LOGS_TICKETS_CHANNEL", 1517020177508733092)
LOGS_REMBOURSEMENT_CHANNEL = _int("LOGS_REMBOURSEMENT_CHANNEL", 1517050226387714048)
# ── CHANNELS FONCTIONNELS ────────────────────────────────────
VERIFICATION_CHANNEL = _int("VERIFICATION_CHANNEL", 1517020243975864442)
WELCOME_CHANNEL = _int("WELCOME_CHANNEL", 1516285038151471255)
# ── CATÉGORIE / TICKETS ──────────────────────────────────────
TICKET_CATEGORY_ID = _int("TICKET_CATEGORY_ID")
# Sous-catégories optionnelles par type de ticket (0 = utilise TICKET_CATEGORY_ID)
TICKET_CHANNELS = {
    "boutique":    1516285006492995694,  # 💎 Boutique / pb. Remboursement
    "superviseur": 1516285007818391652,  # ⚜️ Superviseur
    "recrutement": 1516285008837611540,  # 🔵 RC STAFF & Question
    "legal":       1516285009713954906,  # 🟢 Dossier LEGAL & Question
    "illegal":     1516285011177898054,  # 🔴 Dossier ILLEGAL & Question
    "wiperp":      1516285012062900346,  # 💀 Wipe / Mort RP
}
# ── RÔLES ────────────────────────────────────────────────────
CITOYEN_WL_ROLE = _int("CITOYEN_WL_ROLE", 1517355950812692500)
MUTED_ROLE = _int("MUTED_ROLE", 1517355866964103338)
UNVERIFIED_ROLE = _int("UNVERIFIED_ROLE", 1517043612892926002)
VERIFIED_ROLE = _int("VERIFIED_ROLE", 1516284942064025661)
STAFF_ROLE = _int("STAFF_ROLE", 1516284938645798953)
# ── SANCTIONS AUTOMATIQUES ───────────────────────────────────
AUTO_SANCTION_MUTE_DURATION = _int("AUTO_SANCTION_MUTE_DURATION", 3600)
