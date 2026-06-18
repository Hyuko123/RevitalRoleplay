# 🤖 Revital RP Bot - Pense-bête des Commandes

## 🔐 VÉRIFICATION

| Commande | Description | Exemple |
|----------|-------------|---------|
| `?getcaptcha` | Obtenir un code de vérification | `?getcaptcha` |
| `?verify CODE` | Vérifier avec le captcha | `?verify ABC123` |

---

## ⚠️ WARNS (Avertissements)

| Commande | Permission | Description | Exemple |
|----------|-----------|-------------|---------|
| `?warn @user Raison` | Admin | Ajouter un warn | `?warn @Dupont Spam` |
| `?warns [@user]` | Everyone | Voir les warns (toi ou autre) | `?warns` ou `?warns @Dupont` |

**📌 Important:** Les warns IG et Discord sont ensemble!

---

## 🔇 MUTE (Réduire au silence)

| Commande | Permission | Description | Exemple |
|----------|-----------|-------------|---------|
| `?mute @user TIME Raison` | Admin | Mute temporaire | `?mute @Dupont 1h Spam` |
| `?unmute @user` | Admin | Unmute un utilisateur | `?unmute @Dupont` |

**Formats de temps:** `5s`, `10m`, `1h`, `1d` (secondes, minutes, heures, jours)

---

## 👢 KICK & BAN

| Commande | Permission | Description | Exemple |
|----------|-----------|-------------|---------|
| `?kick @user [Raison]` | Admin | Expulser du serveur | `?kick @Dupont Toxique` |
| `?ban @user [Raison]` | Admin | Bannir du serveur | `?ban @Dupont Spammeur` |

---

## ✅ WHITELIST

| Commande | Permission | Description | Exemple |
|----------|-----------|-------------|---------|
| `?whitelist @user legal/illegale ok/non-ok ok/non-ok [Note]` | Admin | Ajouter à la whitelist | `?whitelist @Dupont legal ok ok Bon joueur` |
| `?check-wl [@user]` | Everyone | Vérifier le statut whitelist | `?check-wl` ou `?check-wl @Dupont` |

**Paramètres whitelist:**
- **Légal:** `legal` ou `illegale`
- **Background:** `ok` ou `non-ok`
- **Règlement:** `ok` ou `non-ok`

---

## 🎫 TICKETS

| Commande | Permission | Description | Exemple |
|----------|-----------|-------------|---------|
| `?setup-tickets` | Admin | Configurer le système | `?setup-tickets` (1 fois seulement) |

**Utilisation:**
1. Admin exécute `?setup-tickets`
2. Embed apparaît avec bouton
3. Utilisateurs cliquent pour créer un ticket
4. Ticket = channel privé
5. Clique "Fermer" pour supprimer

---

## 📊 RÉSUMÉ RAPIDE

```
MODÉRATION:
  ?warn @user Raison          ← Avertir
  ?warns [@user]              ← Voir avertissements
  ?mute @user 1h Raison       ← Mute temporaire
  ?unmute @user               ← Unmute
  ?kick @user Raison          ← Expulser
  ?ban @user Raison           ← Bannir

WHITELIST:
  ?whitelist @user legal ok ok Note    ← Whitelister
  ?check-wl [@user]                    ← Vérifier

VÉRIFICATION:
  ?getcaptcha                 ← Obtenir captcha
  ?verify CODE                ← Vérifier

TICKETS:
  ?setup-tickets              ← Configurer (1 fois)
```

---

## 🔐 PERMISSIONS

- `Admin` = Administrateur requis
- `Everyone` = Tout le monde peut utiliser

---

## 📝 LOGS AUTOMATIQUES

Tous les actions sont loggées dans:
- `#logs-moderation` → Kicks, Bans, Mutes, Warns
- `#logs-wl` → Whitelists approuvées

---

## 💡 TIPS

✅ Utilise `?warns @user` avant de bannir quelqu'un
✅ Mets toujours une raison dans tes actions
✅ Utilise les notes whitelist pour documenter
✅ Vérifie `#logs-moderation` régulièrement

---

**Dernière mise à jour:** 2024
**Préfixe du bot:** `?`
