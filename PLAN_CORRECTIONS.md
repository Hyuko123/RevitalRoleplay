# 🔧 Plan de Corrections - Bot Discord Revital RP

## 📋 Résumé des Problèmes Identifiés

### 1. **Commande `/bc` Non Implémentée** ❌
- La commande utilise `...` (ellipsis) ce qui fait planter le bot
- Le dictionnaire `ANNONCE_COLORS` n'est pas défini
- La classe `AnnonceModal` n'est pas implémentée
- La fonction `bc()` n'a pas de corps

### 2. **Système de Permissions Incohérent** ⚠️
- Actuellement, `is_staff()` vérifie les **administrateurs OU le rôle STAFF_ROLE**
- 8 commandes vérifient directement `administrator` au lieu d'utiliser `is_staff()`
- L'utilisateur veut que **SEUL le rôle 1516284938645798953** ait accès (pas les admins)

---

## 🎯 Objectifs

1. ✅ Implémenter complètement la commande `/bc` (broadcast)
2. ✅ Modifier le système de permissions pour n'autoriser QUE le rôle 1516284938645798953
3. ✅ Uniformiser toutes les vérifications de permissions

---

## 🔨 Modifications à Effectuer

### **Étape 1 : Modifier la fonction `is_staff()`**

**Fichier :** [`main.py`](main.py:95-100)

**Code actuel :**
```python
def is_staff(interaction: discord.Interaction) -> bool:
    if interaction.user.guild_permissions.administrator:
        return True
    staff_role = interaction.guild.get_role(STAFF_ROLE)
    return staff_role is not None and staff_role in interaction.user.roles
```

**Code modifié :**
```python
def is_staff(interaction: discord.Interaction) -> bool:
    """Vérifie si l'utilisateur possède le rôle STAFF_ROLE (1516284938645798953)."""
    staff_role = interaction.guild.get_role(STAFF_ROLE)
    return staff_role is not None and staff_role in interaction.user.roles
```

**Changement :** Suppression de la vérification des administrateurs.

---

### **Étape 2 : Remplacer les vérifications `administrator` par `is_staff()`**

Les commandes suivantes vérifient actuellement `administrator` et doivent être modifiées :

#### 2.1 **Commande `/clearwarn`** - Ligne 794
```python
# AVANT
if not interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("❌ Administrateur requis.", ephemeral=True)
    return

# APRÈS
if not is_staff(interaction):
    await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
    return
```

#### 2.2 **Commande `/clearallwarns`** - Ligne 812
```python
# AVANT
if not interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("❌ Administrateur requis.", ephemeral=True)
    return

# APRÈS
if not is_staff(interaction):
    await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
    return
```

#### 2.3 **Commande `/kick`** - Ligne 930
```python
# AVANT
if not interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("❌ Administrateur requis.", ephemeral=True)
    return

# APRÈS
if not is_staff(interaction):
    await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
    return
```

#### 2.4 **Commande `/ban`** - Ligne 947
```python
# AVANT
if not interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("❌ Administrateur requis.", ephemeral=True)
    return

# APRÈS
if not is_staff(interaction):
    await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
    return
```

#### 2.5 **Commande `/wl-revoke`** - Ligne 1047
```python
# AVANT
if not interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("❌ Administrateur requis.", ephemeral=True)
    return

# APRÈS
if not is_staff(interaction):
    await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
    return
```

#### 2.6 **Commande `/setup-tickets`** - Ligne 1093
```python
# AVANT
if not interaction.user.guild_permissions.administrator:
    await interaction.response.send_message("❌ Administrateur requis.", ephemeral=True)
    return

# APRÈS
if not is_staff(interaction):
    await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
    return
```

#### 2.7 **Whitelist Step 2 Modal** - Ligne 537
```python
# AVANT
if not interaction.user.guild_permissions.administrator and not is_staff(interaction):
    await interaction.response.send_message("❌ Tu n'as pas la permission.", ephemeral=True)
    return

# APRÈS
if not is_staff(interaction):
    await interaction.response.send_message("❌ Accès refusé.", ephemeral=True)
    return
```

---

### **Étape 3 : Implémenter la commande `/bc` (Broadcast)**

**Fichier :** [`main.py`](main.py:611-626)

#### 3.1 **Définir le dictionnaire `ANNONCE_COLORS`** - Ligne 611
```python
ANNONCE_COLORS = {
    "Bleu": discord.Color.blue(),
    "Vert": discord.Color.green(),
    "Rouge": discord.Color.red(),
    "Orange": discord.Color.orange(),
    "Violet": discord.Color.purple(),
    "Jaune": discord.Color.gold(),
    "Bleu Clair": discord.Color.blurple(),
}
```

#### 3.2 **Implémenter la classe `AnnonceModal`** - Ligne 615
```python
class AnnonceModal(discord.ui.Modal, title="📢 Créer un Broadcast"):
    titre = discord.ui.TextInput(
        label="Titre de l'annonce",
        placeholder="Ex: Maintenance serveur",
        required=True,
        max_length=100
    )
    
    message = discord.ui.TextInput(
        label="Message",
        placeholder="Votre message ici...",
        style=discord.TextStyle.paragraph,
        required=True,
        max_length=2000
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
        # Récupérer la couleur choisie
        color_name = self.couleur.value.strip().capitalize()
        color = ANNONCE_COLORS.get(color_name, discord.Color.blue())
        
        # Créer l'embed
        embed = discord.Embed(
            title=f"📢 {self.titre.value}",
            description=self.message.value,
            color=color,
            timestamp=datetime.now()
        )
        embed.set_footer(text=f"Annonce par {interaction.user.name}")
        
        # Envoyer dans le salon cible
        await self.channel.send(embed=embed)
        
        # Confirmer à l'utilisateur
        await interaction.response.send_message(
            f"✅ Broadcast envoyé dans {self.channel.mention}",
            ephemeral=True
        )
```

#### 3.3 **Implémenter la commande `/bc`** - Ligne 618
```python
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
```

---

## 📊 Récapitulatif des Changements

### Fichiers Modifiés
- ✏️ [`main.py`](main.py) - Modifications multiples

### Statistiques
- **1** fonction modifiée : [`is_staff()`](main.py:95)
- **7** vérifications `administrator` remplacées par `is_staff()`
- **1** dictionnaire ajouté : `ANNONCE_COLORS`
- **1** classe implémentée : `AnnonceModal`
- **1** commande implémentée : `/bc`

### Impact
- ✅ Le bot ne plantera plus au démarrage
- ✅ La commande `/bc` sera fonctionnelle
- ✅ **SEUL le rôle 1516284938645798953** aura accès aux commandes
- ✅ Les administrateurs Discord n'auront PLUS accès automatiquement
- ✅ Système de permissions unifié et cohérent

---

## ⚠️ Points d'Attention

1. **Rôle Requis :** Assurez-vous que le rôle `1516284938645798953` existe sur le serveur
2. **Permissions Bot :** Le bot doit avoir les permissions d'envoyer des messages dans tous les salons ciblés par `/bc`
3. **Test Recommandé :** Testez toutes les commandes après modification pour vérifier le bon fonctionnement

---

## 🚀 Prochaines Étapes

Une fois ce plan validé, nous passerons en **mode Code** pour implémenter toutes ces modifications.

**Commande suggérée :**
```
Passer en mode code pour implémenter les corrections
```

---

**Document créé le :** 2026-06-18  
**Version du bot :** Revital RP v4  
**Rôle Staff ID :** 1516284938645798953