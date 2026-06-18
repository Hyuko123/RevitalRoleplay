# 🤖 Revital RP Bot - Documentation Complète

## 📋 Table des Matières
1. [Installation](#installation)
2. [Configuration](#configuration)
3. [Commandes](#commandes)
4. [Système Whitelist](#système-whitelist)
5. [FAQ](#faq)

---

## 🚀 Installation

### Prérequis
- Python 3.8 ou plus
- pip (gestionnaire de paquets Python)
- Un bot Discord créé

### Étape 1: Créer un Bot Discord

1. Va sur https://discord.com/developers/applications
2. Clique sur "New Application"
3. Donne un nom: "Revital RP Bot"
4. Va dans l'onglet "Bot"
5. Clique sur "Add Bot"
6. Sous TOKEN, clique "Copy" (c'est ton token!)

### Étape 2: Donner les Permissions

1. Va dans "OAuth2" → "URL Generator"
2. Sélectionne les scopes: `bot`
3. Sélectionne les permissions:
   - ✅ Administrator (pour facilité, ou sélectionne individuellement)
4. Copie l'URL générée et ouvre-la pour inviter le bot sur ton serveur

### Étape 3: Installer les Dépendances

```bash
pip install discord.py
```

### Étape 4: Configurer le Bot

1. Ouvre `config.py`
2. Remplace `TOKEN` par ton token Discord
3. Récupère les IDs de ton serveur (voir instructions dans config.py)
4. Remplis tous les IDs requis

### Étape 5: Lancer le Bot

```bash
python main.py
```

Si tout fonctionne, tu devrais voir:
```
✅ Bot connecté en tant que Revital RP Bot
```

---

## ⚙️ Configuration Détaillée

### Créer les Rôles Nécessaires

1. Va dans Paramètres du Serveur → Rôles
2. Crée ces rôles:
   - `citoyen-wl` (pour les whitelist)
   - `Muted` (pour les mutes)
   - `Verified` (pour les vérifiés)

### Créer les Channels Nécessaires

1. Va dans Paramètres du Serveur → Salons
2. Crée ces channels:
   - `#logs-moderation` (logs des kicks/bans/mutes)
   - `#logs-wl` (logs des whitelists)
   - `#tickets` (création des tickets)
   - `#verification` (vérification au join)

### Récupérer les IDs

**Mode Développeur:**
- Paramètres Discord → Avancé → Mode Développeur ✅

**Copier les IDs:**
- Channel: Clic droit → "Copier l'ID du salon"
- Rôle: Clic droit → "Copier l'ID du rôle"
- Serveur: Clic droit → "Copier l'ID serveur"

Exemple de `config.py` rempli:
```python
TOKEN = "MTA5ODc2NTQzMjE5NTY4Njg3MA.GzPzA0.xxxxxxxxxxxxx"
GUILD_ID = 1234567890
LOGS_CHANNEL = 1234567891
LOGS_WL_CHANNEL = 1234567892
TICKETS_CHANNEL = 1234567893
VERIFICATION_CHANNEL = 1234567894
CITOYEN_WL_ROLE = 1234567895
MUTED_ROLE = 1234567896
VERIFIED_ROLE = 1234567897
```

---

## 📝 Commandes

### 🔐 Vérification

```
?getcaptcha           → Obtenir un captcha
?verify CODE          → Vérifier avec le code
```

**Exemple:**
```
?getcaptcha
Réponse: Ton code: ABC123

?verify ABC123
✅ Vérification réussie!
```

### ⚠️ Système de Warns

```
?warn @user Raison          → Ajouter un warn
?warns [@user]              → Voir les warns (toi ou quelqu'un d'autre)
```

**Exemple:**
```
?warn @Dupont Spam dans le chat
✅ Warn ajouté à @Dupont (Total: 1)

?warns @Dupont
⚠️ Warns de Dupont (Total: 3)
```

**Important:** Les warns sont enregistrés même s'ils viennent du jeu (IG). Tu peux les ajouter manuellement avec la commande.

### 🔇 Mute Temporaire

```
?mute @user TIME RAISON

TIME: 5s, 10m, 1h, 1d
```

**Exemple:**
```
?mute @Dupont 1h Spam excessif
✅ @Dupont a été mute pour 1h

?unmute @Dupont
✅ @Dupont a été unmute
```

### 👢 Kick & Ban

```
?kick @user [Raison]        → Kick un utilisateur
?ban @user [Raison]         → Ban un utilisateur
```

**Exemple:**
```
?kick @Dupont Comportement toxique
✅ @Dupont a été kick

?ban @Dupont Spam persistant
✅ @Dupont a été banni
```

### ✅ Système Whitelist

**Ajouter quelqu'un à la whitelist:**
```
?whitelist @user legal/illegale ok/non-ok ok/non-ok [Note]

Paramètres:
- legal ou illegale
- ok ou non-ok (Background)
- ok ou non-ok (Connaissance règlement)
- Note (optionnel)
```

**Exemple:**
```
?whitelist @Dupont legal ok ok Bon candidat, très poli
✅ @Dupont a été whitelisté

?check-wl @Dupont
✅ Dupont - Whitelist
Légal: legal
Background OK: ok
Règlement OK: ok
Note: Bon candidat, très poli
```

**Vérifier son statut whitelist:**
```
?check-wl               → Vérifier ton statut
?check-wl @user        → Vérifier le statut de quelqu'un
```

### 🎫 Système de Tickets

```
?setup-tickets          → Configurer les tickets (à faire une seule fois!)
```

Après avoir fait `?setup-tickets`:
1. Un message avec un bouton apparaît
2. Les utilisateurs cliquent sur "📩 Créer un Ticket"
3. Un channel privé est créé automatiquement
4. Clique sur "Fermer le Ticket" pour supprimer

### ℹ️ Commandes Info

```
?help                   → Voir les commandes disponibles
```

---

## 🎯 Système Whitelist Détaillé

### Statuts Whitelist

**Légal / Illégale:**
- `legal` → Citoyen normal
- `illegale` → Criminel/Résistant

**Background OK:**
- `ok` → Background approuvé
- `non-ok` → Background rejeté

**Règlement OK:**
- `ok` → Connaissance du règlement approuvée
- `non-ok` → Nécessite plus d'apprentissage

### Workflow Complet

1. Nouveau joueur rejoint le serveur
2. Bot envoie le captcha en DM
3. Joueur vérifie et reçoit le rôle "Verified"
4. Admin fait `?whitelist @joueur legal ok ok Note`
5. Joueur reçoit le rôle "citoyen-wl"
6. Admin peut vérifier avec `?check-wl @joueur`

### Logs Whitelist

Tous les whitelists sont enregistrés dans `#logs-wl` avec:
- Nom du joueur
- Statut Légal
- Background OK/NON-OK
- Règlement OK/NON-OK
- Note personnelle
- Modérateur qui a approuvé
- Date et heure

---

## 🗂️ Structure des Fichiers

```
revital_rp_bot/
├── main.py             # Code principal du bot
├── config.py           # Configuration (à personnaliser)
├── requirements.txt    # Dépendances Python
└── data/
    ├── warns.json      # Enregistrement des warns
    ├── mutes.json      # Enregistrement des mutes
    ├── whitelist.json  # Enregistrement des whitelists
    ├── tickets.json    # Enregistrement des tickets
    └── captchas.json   # Captchas actifs
```

Les fichiers JSON sont créés automatiquement au premier lancement.

---

## 🛡️ Permissions Requises

Le bot a besoin de ces permissions:
- ✅ **Administrateur** (ou sélectionner individuellement:)
  - Gérer les rôles
  - Kick les membres
  - Ban les membres
  - Créer les salons
  - Gérer les salons
  - Envoyer des messages
  - Gérer les messages

---

## 🔧 Troubleshooting

### ❌ "Bot not found" ou "Invalid Token"

**Solution:** Vérifies que tu as le bon token dans `config.py`

### ❌ Erreur: "GUILD_ID not found"

**Solution:** 
1. Vérifies que le bot est sur le serveur
2. Vérifies que GUILD_ID est correct

### ❌ Les rôles/channels ne sont pas trouvés

**Solution:** Remplace les IDs dans `config.py` avec les bons

### ❌ Bot ne peut pas ajouter les rôles

**Solution:** 
1. Le rôle du bot doit être PLUS HAUT que les rôles à assigner
2. Va dans Rôles → Déplace "Revital RP Bot" plus haut

---

## 📊 Exemple de Workflow

```
╔════════════════════════════════════════════════╗
║         WORKFLOW COMPLET REVITAL RP           ║
╚════════════════════════════════════════════════╝

1️⃣  NOUVEAU JOUEUR REJOINT
    └─ Bot envoie captcha en DM

2️⃣  JOUEUR VÉRIFIE
    └─ ?verify ABC123
    └─ Reçoit rôle "Verified"

3️⃣  ADMIN CONTRÔLE
    └─ ?whitelist @joueur legal ok ok Note
    └─ Logs dans #logs-wl

4️⃣  JOUEUR REÇOIT RÔLE
    └─ Rôle "citoyen-wl" assigné

5️⃣  JOUEUR ACTIF EN JEU
    └─ Si problème: ?warn @joueur Raison
    └─ Logs dans #logs-moderation

6️⃣  MODÉRATION SI NÉCESSAIRE
    └─ ?mute @joueur 1h Raison
    └─ ou ?kick / ?ban
    └─ Logs enregistrés
```

---

## 💡 Conseils d'Utilisation

✅ **À faire:**
- Vérifies les warns régulièrement
- Log tous les avertissements
- Utilise des notes détaillées pour la whitelist
- Sauvegarde tes fichiers config et data

❌ **À ne pas faire:**
- Ne donner le token à personne
- Ne pas supprimer les fichiers JSON
- Ne pas lancer le bot deux fois

---

## 🆘 Support

Si tu as des problèmes:
1. Vérifie que Python 3.8+ est installé
2. Vérifies les IDs dans config.py
3. Vérifies les permissions du bot sur le serveur
4. Vérifies que discord.py est installé (`pip install discord.py`)

---

**Bot créé pour Revital RP** 🎮

Dernière mise à jour: 2024
