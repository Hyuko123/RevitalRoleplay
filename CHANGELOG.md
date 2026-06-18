# 📦 Revital RP Bot v3 - Résumé des Changements

## ✨ Nouvelles Fonctionnalités

### 1️⃣ Captcha dans #verification
- ✅ S'affiche automatiquement quand un joueur rejoint
- ✅ Affiché dans le channel #verification (pas en DM)
- ✅ Joueur tape `/verify CODE` pour se vérifier

### 2️⃣ Formulaires Whitelist
- ✅ Interface interactive avec sélecteurs
- ✅ Affiche Discord ID automatiquement
- ✅ Paramètres:
  - Background: OK / PAS OK
  - Règlement: OK / PAS OK
  - Décision: Accepté / Refusé
- ✅ Logs détaillés dans #logs-wl

### 3️⃣ Formulaires Warns
- ✅ Modale pour entrer la raison
- ✅ Plus facile à utiliser
- ✅ Logs automatiques

### 4️⃣ Tickets Avancés
- ✅ 6 catégories:
  - 🎮 Problème In-Game
  - 👨‍⚖️ Plainte Staff
  - 🛍️ Problème Boutique
  - 💻 Développement
  - 📋 Dossier Légal
  - ⚖️ Dossier Illégal
- ✅ Channel renommé automatiquement: `[NomJoueur]-[categorie]`
- ✅ Chaque catégorie peut aller dans un salon Discord spécifique

### 5️⃣ Slash Commands `/`
- ✅ Toutes les commandes utilisent `/`
- ✅ Autocomplétion automatique
- ✅ Affichage des paramètres
- ✅ Interface moderne

---

## 📋 Fichiers Fournis

```
main.py              → Code principal (V3 amélioré)
config.py            → Configuration (à personnaliser)
requirements.txt     → Dépendances Python
README.md            → Documentation complète
QUICKSTART.md        → Guide rapide
.gitignore           → Pour GitHub
COMMANDS.md          → (Ancien fichier, encore fourni)
```

---

## 🔄 Migration depuis v2

Si tu viens de la v2:

1. **Sauvegarde tes données** dans `data/`
2. **Supprime** l'ancien `main.py`
3. **Utilise** le nouveau `main.py` (v3)
4. **Relance** le bot

Les données (warns, whitelists, etc.) sont compatibles! ✅

---

## 🚀 Démarrage

```bash
# 1. Installe les dépendances (si pas déjà fait)
pip install -r requirements.txt

# 2. Vérifie config.py (remplace les IDs)

# 3. Lance le bot
python main.py
```

---

## 📝 Commandes (Slash `/`)

```
/verify CODE              → Vérifier avec captcha
/warn @user               → Ajouter un warn (modale)
/warns [@user]            → Voir les warns
/mute @user 1h Raison     → Mute temporaire
/unmute @user             → Unmute
/kick @user Raison        → Kick
/ban @user Raison         → Ban
/whitelist @user          → Ouvre le formulaire
/check-wl [@user]         → Voir le statut whitelist
/setup-tickets            → Active les tickets
```

---

## 🎯 Procédure Complète

### Pour la Whitelist

```
Admin: /whitelist @joueur
  ↓
Formulaire s'ouvre:
  - Discord ID: Auto (affichage seulement)
  - Background: Sélecteur (OK/PAS OK)
  - Règlement: Sélecteur (OK/PAS OK)
  - Décision: Sélecteur (Accepté/Refusé)
  ↓
Admin clique "Soumettre"
  ↓
Logs dans #logs-wl avec tous les détails
Si Accepté → Rôle "citoyen-wl" ajouté
```

### Pour les Tickets

```
Admin: /setup-tickets
  ↓
Message avec sélecteur de catégories
  ↓
Joueur sélectionne une catégorie
  ↓
Channel créé: nomjoueur-categorie
  ↓
Logs dans #tickets
  ↓
Joueur utilise le ticket
  ↓
Clique "Fermer le Ticket" pour supprimer
```

### Pour la Vérification

```
Joueur rejoint le serveur
  ↓
Bot envoie captcha dans #verification
  ↓
Captcha: "Ton code: ABC123"
  ↓
Joueur: /verify ABC123
  ↓
Accepté → Rôle "Verified" + Accès serveur
Refusé → Message d'erreur
```

---

## ✅ Checklist Avant de Lancer

- [ ] Discord Developer Portal Intents ✅
- [ ] config.py rempli avec les bons IDs
- [ ] Rôles créés (citoyen-wl, Muted, Verified)
- [ ] Channels créés (#logs-moderation, #logs-wl, #tickets, #verification)
- [ ] discord.py 2.4.0+ installé
- [ ] Bot lancé: `python main.py`
- [ ] Message "✅ Bot connecté" visible
- [ ] Message "✅ Slash commands synchronisées!" visible

---

## 💡 Prochaines Étapes

1. **Teste les commandes** sur un channel privé
2. **Configure les permissions** des channels comme tu le veux
3. **Personnalise** les messages/emojis si besoin
4. **Upload sur GitHub** pour le versionning

---

**Bot v3 Prêt!** 🚀

Des questions? Vois le README.md complet.
