# ⚡ Guide Rapide - 5 Minutes

## 1️⃣ Créer le Bot Discord (2 min)

1. Va sur https://discord.com/developers/applications
2. Clique "New Application" → donne un nom
3. Onglet "Bot" → clique "Add Bot"
4. Sous TOKEN, clique "Copy" (GARDE CETTE CLÉE SECRÈTE!)
5. Onglet "OAuth2" → URL Generator
6. Selectionne: `bot` + `Administrator`
7. Copie l'URL générée et ouvre-la pour inviter le bot

## 2️⃣ Créer les Rôles (1 min)

Dans ton serveur Discord:
1. Paramètres → Rôles → "Créer un rôle"
2. Crée ces rôles:
   - `citoyen-wl`
   - `Muted`
   - `Verified`

## 3️⃣ Créer les Channels (1 min)

1. Paramètres → Salons → "Créer un salon"
2. Crée:
   - `#logs-moderation`
   - `#logs-wl`
   - `#tickets`
   - `#verification`

## 4️⃣ Configurer le Bot (1 min)

**Récupérer les IDs:**
- Active le Mode Développeur: Paramètres Discord → Avancé → Mode Développeur ✅
- Clic droit sur les channels/rôles → "Copier l'ID"

**Remplir config.py:**
```python
TOKEN = "ton_token_discord_ici"
GUILD_ID = 1234567890  # ID de ton serveur
LOGS_CHANNEL = xxx
LOGS_WL_CHANNEL = xxx
TICKETS_CHANNEL = xxx
VERIFICATION_CHANNEL = xxx
CITOYEN_WL_ROLE = xxx
MUTED_ROLE = xxx
VERIFIED_ROLE = xxx
```

## 5️⃣ Installer et Lancer (1 min)

```bash
pip install -r requirements.txt
python main.py
```

Si tu vois: `✅ Bot connecté en tant que...` → C'est bon! 🎉

---

## 🎯 Premières Commandes à Tester

Dans ton serveur Discord:

```
?setup-tickets
```
Cela configure le système de tickets

```
?whitelist @testuser legal ok ok Test
```
Cela whiteliste quelqu'un

```
?warn @testuser Comportement suspect
```
Cela ajoute un warn

```
?mute @testuser 30m Raison
```
Cela mute quelqu'un pendant 30 minutes

---

## ✅ Checklist Finale

- [ ] Bot créé sur Discord Developer Portal
- [ ] Bot invité sur le serveur
- [ ] Rôles créés (citoyen-wl, Muted, Verified)
- [ ] Channels créés (4 channels)
- [ ] config.py rempli avec tous les IDs
- [ ] discord.py installé
- [ ] Bot lancé et connecté
- [ ] ?setup-tickets exécuté
- [ ] Prêt à modérer! 🚀

---

Pour plus de détails, voir README.md
