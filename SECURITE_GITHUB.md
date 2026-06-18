# 🔒 Sécurité GitHub - Protéger Votre Token Discord

## ⚠️ IMPORTANT : Votre Token est Actuellement Exposé !

Votre fichier `config.py` contient votre token Discord en clair. **C'est dangereux !**

## 🛡️ Solution : Utiliser .gitignore

J'ai créé un fichier `.gitignore` qui empêche Git d'envoyer vos fichiers sensibles sur GitHub.

### Fichiers Protégés

- ✅ `config.py` - Contient votre token
- ✅ `.env` - Fichier de configuration (si vous l'utilisez)
- ✅ `data/` - Toutes vos données JSON
- ✅ `__pycache__/` - Fichiers Python compilés

## 📋 Étapes à Suivre MAINTENANT

### 1. Vérifier que .gitignore est Actif

```bash
git status
```

Vous ne devriez **PAS** voir `config.py` dans la liste des fichiers à commit.

### 2. Si config.py est Déjà sur GitHub

**⚠️ URGENT : Votre token est compromis !**

1. **Régénérer votre token Discord** :
   - Allez sur https://discord.com/developers/applications
   - Sélectionnez votre application
   - Bot → Reset Token
   - Copiez le nouveau token

2. **Mettre à jour config.py** avec le nouveau token

3. **Supprimer config.py de GitHub** :
```bash
git rm --cached config.py
git commit -m "Remove config.py from repository"
git push
```

### 3. Créer un Fichier d'Exemple

J'ai créé `.env.example` que vous POUVEZ mettre sur GitHub.

**À faire :**
```bash
# Ajouter .gitignore et .env.example à Git
git add .gitignore .env.example
git commit -m "Add .gitignore and .env.example for security"
git push
```

## 🔍 Vérification

### Avant de Push sur GitHub

```bash
# Vérifier ce qui sera envoyé
git status

# config.py NE DOIT PAS apparaître
# Si il apparaît, c'est qu'il n'est pas ignoré !
```

### Fichiers qui DOIVENT être sur GitHub

- ✅ `main.py`
- ✅ `.gitignore`
- ✅ `.env.example`
- ✅ `README.md`
- ✅ `requirements.txt`

### Fichiers qui NE DOIVENT PAS être sur GitHub

- ❌ `config.py` (contient le token)
- ❌ `.env` (contient les secrets)
- ❌ `data/` (données sensibles)
- ❌ `__pycache__/` (fichiers temporaires)

## 🚨 Si Votre Token a Été Exposé

1. **Régénérez-le IMMÉDIATEMENT** sur Discord Developer Portal
2. **Ne commitez JAMAIS** le nouveau token
3. **Vérifiez** que `.gitignore` fonctionne

## 💡 Alternative : Utiliser des Variables d'Environnement

Si vous voulez être encore plus sécurisé, vous pouvez utiliser un fichier `.env` :

1. Installez python-dotenv :
```bash
pip install python-dotenv
```

2. Créez un fichier `.env` (déjà dans .gitignore) :
```
DISCORD_TOKEN=votre_token_ici
GUILD_ID=123456789012345678
```

3. Modifiez `config.py` pour lire depuis `.env`

## ✅ Checklist de Sécurité

- [ ] `.gitignore` créé et actif
- [ ] `config.py` n'apparaît pas dans `git status`
- [ ] Token régénéré si déjà exposé
- [ ] `.env.example` créé pour la documentation
- [ ] Vérifié avant chaque `git push`

---

**⚠️ Ne partagez JAMAIS votre token Discord publiquement !**