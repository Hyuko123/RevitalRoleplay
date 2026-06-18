import discord
from discord import app_commands
import asyncio
from config import TOKEN, GUILD_ID

# Script pour réinitialiser complètement les commandes slash

intents = discord.Intents.default()
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    print(f"✅ Bot connecté : {bot.user}")
    
    try:
        # 1. Supprimer toutes les commandes globales
        print("🗑️ Suppression des commandes globales...")
        tree.clear_commands(guild=None)
        await tree.sync()
        print("✅ Commandes globales supprimées")
        
        # 2. Supprimer toutes les commandes du serveur
        guild = discord.Object(id=GUILD_ID)
        print(f"🗑️ Suppression des commandes du serveur {GUILD_ID}...")
        tree.clear_commands(guild=guild)
        await tree.sync(guild=guild)
        print("✅ Commandes du serveur supprimées")
        
        print("\n✅ Réinitialisation terminée !")
        print("⚠️ Redémarrez maintenant le bot principal avec : python main.py")
        print("💡 Les commandes seront resynchronisées au démarrage")
        
    except Exception as e:
        print(f"❌ Erreur : {e}")
    
    await bot.close()

if __name__ == "__main__":
    print("🚀 Réinitialisation des commandes Discord...")
    print("⏳ Cela peut prendre quelques secondes...\n")
    bot.run(TOKEN)

# Made with Bob
