import discord
from discord import app_commands
import asyncio
from config import TOKEN, GUILD_ID

# Script pour forcer la synchronisation des commandes slash
# Utilise ce script si les commandes ne s'affichent pas après un redémarrage

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")
    
    try:
        # Synchronisation globale (visible partout)
        print("🔄 Synchronisation globale des commandes...")
        synced = await tree.sync()
        print(f"✅ {len(synced)} commandes synchronisées globalement")
        
        for cmd in synced:
            print(f"  ➜ /{cmd.name}")
        
        print("\n✅ Synchronisation terminée !")
        print("⏳ Les commandes peuvent prendre jusqu'à 1 heure pour apparaître dans Discord.")
        print("💡 Redémarre Discord (Ctrl+R) pour accélérer le processus.")
        
    except Exception as e:
        print(f"❌ Erreur lors de la synchronisation : {e}")
    
    await bot.close()

if __name__ == "__main__":
    print("🚀 Démarrage de la synchronisation des commandes...")
    bot.run(TOKEN)

# Made with Bob
