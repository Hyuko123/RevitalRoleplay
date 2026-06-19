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
GUILD_ID = _int("GUILD_ID")

# ── CHANNELS LOGS ────────────────────────────────────────────
LOGS_CHANNEL = _int("LOGS_CHANNEL")
LOGS_WL_CHANNEL = _int("LOGS_WL_CHANNEL")
LOGS_TICKETS_CHANNEL = _int("LOGS_TICKETS_CHANNEL")
LOGS_REMBOURSEMENT_CHANNEL = _int("LOGS_REMBOURSEMENT_CHANNEL")

# ── CHANNELS FONCTIONNELS ────────────────────────────────────
VERIFICATION_CHANNEL = _int("VERIFICATION_CHANNEL")
WELCOME_CHANNEL = _int("WELCOME_CHANNEL")

# ── CATÉGORIE / TICKETS ──────────────────────────────────────
TICKET_CATEGORY_ID = _int("TICKET_CATEGORY_ID")

# Sous-catégories optionnelles par type de ticket (0 = utilise TICKET_CATEGORY_ID)
TICKET_CHANNELS = {
    "boutique": _int("TICKET_CHANNEL_BOUTIQUE"),
    "superviseur": _int("TICKET_CHANNEL_SUPERVISEUR"),
    "recrutement": _int("TICKET_CHANNEL_RECRUTEMENT"),
    "legal": _int("TICKET_CHANNEL_LEGAL"),
    "illegal": _int("TICKET_CHANNEL_ILLEGAL"),
    "wiperp": _int("TICKET_CHANNEL_WIPERP"),
}

# ── RÔLES ────────────────────────────────────────────────────
CITOYEN_WL_ROLE = _int("CITOYEN_WL_ROLE")
MUTED_ROLE = _int("MUTED_ROLE")
UNVERIFIED_ROLE = _int("UNVERIFIED_ROLE")
VERIFIED_ROLE = _int("VERIFIED_ROLE")
STAFF_ROLE = _int("STAFF_ROLE")

# ── SANCTIONS AUTOMATIQUES ───────────────────────────────────
AUTO_SANCTION_MUTE_DURATION = _int("AUTO_SANCTION_MUTE_DURATION", 3600)
