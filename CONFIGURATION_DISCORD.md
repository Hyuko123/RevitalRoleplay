# 🔧 Configuration des Permissions Discord - IMPORTANT

## ⚠️ Problème Identifié

Les commandes ne s'affichent pas car Discord a des **permissions d'intégration** qui bloquent `@everyone` par défaut.

**Ce n'est PAS un problème de code Python**, mais de configuration Discord !

---

## ✅ Solution : Configurer les Permissions dans Discord

### Méthode 1 : Via les Paramètres du Serveur (RECOMMANDÉ)

1. **Ouvrir les Paramètres du Serveur**
   - Clic droit sur le nom du serveur → `Paramètres du serveur`

2. **Aller dans Intégrations**
   - Menu de gauche → `Intégrations`
   - Trouver votre bot dans la liste

3. **Configurer les Permissions des Commandes**
   - Cliquer sur votre bot
   - Cliquer sur `Gérer` ou l'icône d'engrenage

4. **Autoriser @everyone pour les commandes publiques**
   
   **Pour `/verify` :**
   - Chercher la commande `verify` dans la liste
   - S'assurer que `@everyone` a la **coche verte** ✅
   - Si c'est une croix rouge ❌, cliquer dessus pour autoriser
   
   **Pour `/ticket-close` :**
   - Chercher la commande `ticket-close`
   - S'assurer que `@everyone` a la **coche verte** ✅
   
   **Pour TOUTES les autres commandes :**
   - Elles doivent avoir la **croix rouge** ❌ pour `@everyone`
   - Ajouter le rôle Staff (ID: 1516284938645798953) avec la **coche verte** ✅

5. **Sauvegarder**
   - Les changements sont automatiques
   - Fermez le menu

---

### Méthode 2 : Via le Portail Développeur Discord

1. **Aller sur le Portail Développeur**
   - https://discord.com/developers/applications

2. **Sélectionner votre Application**
   - Cliquez sur votre bot

3. **Aller dans "Installation"**
   - Menu de gauche → `Installation`

4. **Configurer les Permissions par Défaut**
   - Section `Default Install Settings`
   - Sous `Guild Install` → `Permissions`
   - Cocher : `applications.commands`

5. **Réinviter le Bot** (si nécessaire)
   - Générer un nouveau lien d'invitation
   - Expulser l'ancien bot
   - Réinviter avec le nouveau lien

---

## 🎯 Configuration Recommandée

### Commandes Publiques (@everyone autorisé)
```
✅ /verify
✅ /ticket-close
```

### Commandes Staff (Rôle 1516284938645798953 uniquement)
```
❌ @everyone (bloqué)
✅ Rôle Staff (autorisé)

Commandes concernées :
- /warn, /clearwarn, /clearallwarns, /warns, /history
- /mute, /unmute, /kick, /ban
- /bc
- /whitelist, /check-wl, /wl-history, /wl-revoke
- /setup-tickets, /ticket-add
```

---

## 🔍 Vérification

Après configuration, testez avec :

1. **Compte sans rôle staff** :
   - Devrait voir : `/verify`, `/ticket-close`
   - Ne devrait PAS voir : `/warn`, `/ban`, etc.

2. **Compte avec rôle staff** :
   - Devrait voir : TOUTES les commandes

---

## 💡 Alternative : Permissions par Salon

Si vous voulez que certaines commandes soient visibles uniquement dans certains salons :

1. Paramètres du serveur → Intégrations → Votre bot
2. Cliquer sur une commande
3. Ajouter des salons spécifiques
4. Exemple : `/verify` uniquement dans `#verification`

---

## ⚠️ Notes Importantes

- **Les permissions Discord ont priorité sur le code Python**
- Même si le code autorise une commande, Discord peut la bloquer
- Les changements de permissions sont **instantanés** (pas de cache)
- Si vous ne voyez pas les commandes après configuration, redémarrez Discord (Ctrl+R)

---

## 🐛 Dépannage

### "Je ne vois toujours pas les commandes"
1. Vérifiez que le bot est bien en ligne
2. Vérifiez les permissions d'intégration (voir ci-dessus)
3. Redémarrez Discord (Ctrl+R)
4. Attendez 2-3 minutes

### "Les commandes apparaissent mais ne fonctionnent pas"
- C'est un problème de code Python (vérifiez les logs du bot)
- Assurez-vous que le rôle 1516284938645798953 existe

### "Je veux changer les permissions plus tard"
- Retournez dans Paramètres du serveur → Intégrations
- Modifiez les permissions à tout moment
- Aucun redémarrage du bot nécessaire

---

**Bot v4 — Revital RP** 🎮