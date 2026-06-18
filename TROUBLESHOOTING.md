# 🔧 Dépannage - Bot Discord Revital RP

## ❌ Problème : Les commandes ne s'affichent pas pour les joueurs

### Causes possibles

1. **Cache Discord** : Discord met en cache les commandes slash et peut prendre jusqu'à 1 heure pour les mettre à jour
2. **Bot non redémarré** : Après modification du code, le bot doit être redémarré
3. **Permissions Discord** : Le bot doit avoir la permission "applications.commands" sur le serveur

---

## ✅ Solutions

### Solution 1 : Forcer la synchronisation des commandes

```bash
python sync_commands.py
```

Ce script force Discord à mettre à jour toutes les commandes. Attendez ensuite quelques minutes.

### Solution 2 : Vider le cache Discord (côté utilisateur)

**Sur PC :**
- Appuyez sur `Ctrl + R` pour recharger Discord
- Ou fermez complètement Discord et relancez-le

**Sur navigateur :**
- Appuyez sur `Ctrl + Shift + R` pour vider le cache
- Ou videz le cache du navigateur

### Solution 3 : Redémarrer le bot

```bash
# Arrêter le bot (Ctrl+C)
# Puis relancer :
python main.py
```

### Solution 4 : Vérifier les permissions du bot

Le bot doit avoir ces permissions sur Discord :
- ✅ `applications.commands` (Commandes d'application)
- ✅ `Manage Roles` (Gérer les rôles)
- ✅ `Manage Channels` (Gérer les salons)
- ✅ `Send Messages` (Envoyer des messages)
- ✅ `Embed Links` (Intégrer des liens)
- ✅ `Attach Files` (Joindre des fichiers)
- ✅ `Read Message History` (Lire l'historique des messages)
- ✅ `Add Reactions` (Ajouter des réactions)
- ✅ `Kick Members` (Expulser des membres)
- ✅ `Ban Members` (Bannir des membres)

---

## 📋 Commandes accessibles à TOUS les joueurs

Ces commandes sont visibles et utilisables par n'importe qui :

| Commande | Description |
|----------|-------------|
| `/verify CODE` | Vérifier son compte avec le code captcha |
| `/ticket-close` | Fermer un ticket (dans un salon de ticket) |

---

## 🔐 Commandes réservées au STAFF (Rôle 1516284938645798953)

Toutes les autres commandes nécessitent le rôle staff :

**Modération :**
- `/warn`, `/clearwarn`, `/clearallwarns`
- `/warns`, `/history`
- `/mute`, `/unmute`
- `/kick`, `/ban`
- `/bc` (broadcast)

**Whitelist :**
- `/whitelist`, `/check-wl`
- `/wl-history`, `/wl-revoke`

**Tickets :**
- `/setup-tickets`, `/ticket-add`

---

## 🐛 Problème : Le bot ne démarre pas

### Erreur : "Invalid Token"
➜ Vérifiez que le TOKEN dans `config.py` est correct

### Erreur : "Module not found"
➜ Installez les dépendances :
```bash
pip install -r requirements.txt
```

### Erreur : "Permission denied"
➜ Le bot n'a pas les permissions nécessaires sur Discord

---

## 💡 Astuces

1. **Logs du bot** : Regardez la console où tourne le bot pour voir les erreurs
2. **Test rapide** : Utilisez `/verify test` pour vérifier que le bot répond
3. **Délai Discord** : Après une modification, attendez 5-10 minutes avant de tester
4. **Mode développeur Discord** : Activez-le pour copier les IDs facilement

---

## 📞 Support

Si le problème persiste :
1. Vérifiez que le rôle `1516284938645798953` existe sur votre serveur
2. Vérifiez que tous les IDs dans `config.py` sont corrects
3. Redémarrez complètement Discord ET le bot
4. Attendez 1 heure pour que Discord mette à jour son cache

---

**Bot v4 — Revital RP** 🎮