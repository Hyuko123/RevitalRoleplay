# 🔑 Guide : Obtenir un nouveau Token Discord

## ⚠️ Pourquoi votre token ne fonctionne pas ?

Le token `MTUxNzAwMjg3NzYzMjEyMjk4Mg.GXQ_QA.fH5T3h4P-sxh91npkNTWWnEyqUrj3I2B-iqnjA` est **invalide ou expiré**.

Vous devez créer un **NOUVEAU** token.

## 📝 Étapes pour obtenir un nouveau token :

### 1. Aller sur le portail développeur Discord

🔗 https://discord.com/developers/applications

### 2. Sélectionner votre application

- Cliquez sur votre application bot (celle que vous utilisez pour Revital)
- Si vous n'en avez pas, cliquez sur "New Application"

### 3. Aller dans l'onglet "Bot"

- Dans le menu de gauche, cliquez sur **"Bot"**

### 4. Réinitialiser le token

⚠️ **IMPORTANT** : Cliquez sur **"Reset Token"** (pas "Copy")

- Discord va vous demander de confirmer
- Confirmez en cliquant sur "Yes, do it!"
- Un **NOUVEAU** token apparaîtra

### 5. Copier le nouveau token

- Cliquez sur **"Copy"** pour copier le token
- ⚠️ **Vous ne pourrez le voir qu'une seule fois !**

### 6. Coller le token dans le fichier .env

Ouvrez le fichier `.env` et remplacez :

```env
DISCORD_TOKEN=VOTRE_NOUVEAU_TOKEN_ICI
```

Par votre nouveau token (exemple) :

```env
DISCORD_TOKEN=MTUxNzAwMjg3NzYzMjEyMjk4Mg.GaBcDe.FgHiJkLmNoPqRsTuVwXyZ1234567890
```

### 7. Sauvegarder et relancer

```bash
python main.py
```

## ✅ Vérifications importantes :

### Le token doit :
- ✅ Commencer par des lettres/chiffres
- ✅ Contenir 2 points (.)
- ✅ Faire environ 70-80 caractères
- ✅ Être tout récent (généré à l'instant)

### Exemple de token valide :
```
MTUxNzAwMjg3NzYzMjEyMjk4Mg.GaBcDe.FgHiJkLmNoPqRsTuVwXyZ1234567890
```

### ❌ Erreurs courantes :

1. **Token avec des espaces** → Supprimez les espaces
2. **Ancien token** → Générez-en un nouveau
3. **Token incomplet** → Copiez tout le token
4. **Guillemets dans le .env** → N'ajoutez PAS de guillemets

## 🔒 Sécurité :

- ⚠️ **NE PARTAGEZ JAMAIS** votre token
- ⚠️ **NE LE METTEZ PAS** sur GitHub
- ⚠️ Si vous l'avez partagé par erreur, **réinitialisez-le immédiatement**

## 🆘 Toujours pas de token ?

Si vous n'avez pas d'application bot :

1. Allez sur https://discord.com/developers/applications
2. Cliquez sur **"New Application"**
3. Donnez un nom (ex: "Revital Bot")
4. Allez dans **"Bot"**
5. Cliquez sur **"Add Bot"**
6. Suivez les étapes ci-dessus

## 📋 Permissions requises pour le bot :

Dans l'onglet "Bot", activez ces **Privileged Gateway Intents** :
- ✅ PRESENCE INTENT
- ✅ SERVER MEMBERS INTENT
- ✅ MESSAGE CONTENT INTENT

## 🔗 Inviter le bot sur votre serveur :

1. Allez dans **"OAuth2"** → **"URL Generator"**
2. Cochez **"bot"** et **"applications.commands"**
3. Sélectionnez les permissions nécessaires
4. Copiez l'URL générée
5. Ouvrez-la dans votre navigateur
6. Sélectionnez votre serveur Revital

---

**Une fois le nouveau token configuré, le bot devrait démarrer sans erreur !** 🎉