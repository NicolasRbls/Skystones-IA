# Skystones - IA et Joueur

## Description
**Skystones** est une implémentation du jeu de cartes inspiré de Triple Triad où deux joueurs (un humain et une IA) s'affrontent en posant des cartes sur un plateau de 3x3 cases. Chaque carte possède des "lames" sur ses côtés, représentant sa force. Une carte posée peut capturer des cartes adjacentes si elle a une valeur de lame supérieure à celle de la carte voisine.

Le joueur et l'IA placent leurs cartes à tour de rôle, et l'objectif est de capturer le plus grand nombre de cartes possible à la fin de la partie.

---

## Fonctionnalités

- **Affichage graphique en Pygame** avec un plateau, des cartes et un système de sélection visuelle.
- **Système de capture bidirectionnelle** :
  - Une carte posée peut capturer ses cartes voisines si elle a plus de lames sur les côtés adjacents.
  - Une carte déjà en place peut capturer une carte nouvellement posée si elle a plus de lames.
  - Deux cartes du même propriétaire ne peuvent pas se capturer entre elles.
- **Système de jeu fluide et interactif** avec une IA qui joue automatiquement à son tour.
- **Effets d'animation** lors des captures de cartes.
- **Annonce du vainqueur à la fin du jeu** en fonction du nombre de cartes contrôlées.

---

## Technologies utilisées

- **Python 3**
- **Pygame** (pour l'affichage et l'interaction utilisateur)

---

## Installation
### Prérequis
Assurez-vous d'avoir Python 3 installé sur votre machine. Vous pouvez vérifier votre version de Python avec :

```sh
python --version
```

### Installation de Pygame
Si vous n'avez pas encore installé Pygame, utilisez la commande suivante :

```sh
pip install pygame
```

### Lancer le jeu
Clonez ou téléchargez le projet, puis exécutez le fichier principal :

```sh
python skystones.py
```

---

## Règles du jeu
1. Chaque joueur possède un deck de cartes :
   - **Le joueur** commence avec **4 cartes**.
   - **L'IA** commence avec **5 cartes**.
2. Les joueurs posent leurs cartes à tour de rôle sur une case libre du plateau **3x3**.
3. Lorsqu'une carte est posée, elle **peut capturer les cartes adjacentes** si elle a un nombre de lames supérieur sur le côté correspondant.
4. Une carte **déjà en place** peut aussi capturer une carte nouvellement posée si elle a plus de lames.
5. **Les cartes du même joueur ne peuvent pas se capturer entre elles**.
6. La partie prend fin lorsque toutes les cases du plateau sont remplies.
7. Le joueur ayant **le plus de cartes sous son contrôle** à la fin remporte la partie.

---

## Commandes et interaction
- **Sélectionner une carte** : Cliquez sur une carte dans votre deck.
- **Placer une carte** : Cliquez sur une case vide du plateau.
- **Le tour passe automatiquement** après chaque action.
- **L'IA joue automatiquement** lorsqu'elle a la main.
- **Le score final est affiché à la fin de la partie**.

---

## Évolutions futures
Voici quelques améliorations prévues :
- Amélioration des **animations** pour les captures.
- Personnalisation des **cartes avec des illustrations et des effets spéciaux**.

---

## Contributions
Les contributions sont les bienvenues ! Si vous souhaitez améliorer le jeu ou corriger un bug, vous pouvez :
1. Cloner le dépôt.
2. Créer une branche.
3. Faire vos modifications.
4. Soumettre une pull request.

---

## Auteurs
- **Nicolas, Badre, Thomas** - Développement et conception du jeu

Merci d'avoir testé **Skystones** ! 🚀 Amusez-vous bien !

