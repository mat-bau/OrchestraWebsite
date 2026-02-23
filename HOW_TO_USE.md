# Guide de gestion du site OrchestraKot

## Introduction

Comment gérer le contenu du site, surtout l'ajout des nouveaux et la mise à jour de la galerie. J'ai essayé de rendre l'ajout du site le plus automatique, surtout pour les photos donc à part changer par-ci par-là du texte,, ça ira.

---
## TO-DO début d'année

- [ ] Créer le dossier `images/team/team{année}/`
- [ ] Prendre la photo d'équipe et la nommer `lequipe{année}.jpg`
- [ ] Prendre les photos individuelles des nouveaux membres (généralement du concert à la FDB donc vous avez le temps)
- [ ] Ajouter la photo d'équipe dans `team{année}`
- [ ] Ajouter/mettre à jour les membres dans `members` du fichier `team-profiles.json`
- [ ] Mettre à jour les rôles et études pour la nouvelle année (et l'année)
- [ ] Relancer `python3 start.py`
- [ ] Vérifier que tout s'affiche correctement sur le site
- [ ] Mettre à jour les événements de la page `Home`
- [ ] Mettre à jour le paragraphe sur le concert dans `About` 
- [ ] ? 

## Ajouter un nouveau membre à l'équipe

### 1. Préparer les photos

**Emplacement des photos :**
- Photos individuelles : `images/team/team{année}/{nom}.jpg`
- Photo d'équipe : `images/team/team{année}/lequipe{année}.jpg`
- je vous laisse découvrir les autres dossiers et leurs utilité

**Exemple pour 2024-2025 :**
```
images/team/team2024/
├── lequipe2024.jpg          # Photo de toute l'équipe
├── julien.jpg               # Photo de Julien
├── antoine.jpg              # Photo d'Antoine
└── ...
```

**Important :** Utilisez des noms de fichiers simples (prénom en minuscules, pas d'espaces ni d'accents).

---

### 2. Modifier le fichier `team-profiles.json`

Ce fichier se trouve à la **racine du projet** et contient toutes les informations sur les membres.

#### Structure du fichier
```json
{
  "team_photos": {
    "2024-2025": "images/team/team2024/lequipe2024.jpg",
    "2025-2026": "images/team/team2025/lequipe2025.jpg"
  },
  "members": [
    {
      "name": "Prénom Nom",
      "instruments": ["Instrument1", "Instrument2"],
      "roles": {"2024-2025": "Président","2025-2026": ""},
      "etudes": {
        "2024-2025": "Bac 3 Ingénieur civil",
        "2025-2026": "Master 1 Ingénieur civil"
      },
      "annee_debut": 2024,
      "annee_fin": 2026,
      "images": [
        "images/team/team2024/prenom.jpg",
        "images/team/team2025/prenom.jpg"
      ]
    }
  ]
}
```

#### Ajouter un nouveau membre

1. **Ajouter la photo d'équipe** (si nouvelle année) :
```json
"team_photos": {
  "2026-2027": "images/team/team2025/lequipe2026.jpg"
}
```

2. **Ajouter le membre dans `members`** :
```json
{
  "name": "Dupont Dupont",
  "instruments": ["Piano", "Chant"],
  "roles": {
    "2025-2026": "Trésorier"
  },
  "etudes": {
    "2025-2026": "Bac 2 Sciences politiques"
  },
  "annee_debut": 2025,
  "annee_fin": 2027,
  "images": [
    "images/team/team2025/dupont.jpg"
  ]
}
```

#### Explications des champs

- **`name`** : Prénom et nom du membre
- **`instruments`** : Liste des instruments joués (sera utilisé pour organiser par instrument)
- **`roles`** : Dictionnaire (donc à chaque année est associé un role) année → rôle (Président, Vice-président, Trésorier/Trésorière, Secrétaire, ou "" si autre)
- **`etudes`** : Dictionnaire année → études en cours (pour voir l'évolution des études dans la gallerie)
- **`annee_debut`** : Première année académique (ex: 2024 pour 2024-2025)
- **`annee_fin`** : Année de fin +1 (ex: 2026 si le membre quitte après 2025-2026)
- **`images`** : Liste des photos, **une par année** dans l'ordre chronologique

#### Points importants

- **Les rôles sont triés automatiquement** : Président → Vice-président → Trésorier(ère) → autres membres (il faudra peut-être vous occuper de changer Vice-président par Co-président, je pense que juste changer le nom suffit pcq changer la priorité n'a pas bcp de sens il y aura d'office qlq en dessous de l'autre)
- **Virgules** : N'oubliez pas les virgules entre les membres, mais pas après le dernier !

---

### 3. Mettre à jour le site

Après avoir modifié `team-profiles.json`, pour voir en local vos modifications vous pouvez lancer sur macOS :
```bash
python3 start.py
```
ou sur windows / linux
```bash
python start.py
```
Et rendez vous sur le lien donné normalement genre 
```bash
Running on http://127.0.0.1:5050
# ou
http://localhost:5050
```

Le script va automatiquement :

- Générer la structure de l'équipe organisée par année et par instrument  
- Scanner la galerie d'images  
- Fusionner le tout dans `frontend/gallery-structure.json`  
- Démarrer le serveur  

---

## Gérer la galerie photo

### Ajouter des photos dans la galerie

1. **Placez vos photos dans** `images/public/`
2. **Organisez par dossiers** selon vos besoins (ex: `images/public/Concert 2024/`)
3. **Relancez le script** : `python3 start.py`

Le script scanne automatiquement tous les dossiers et génère la structure de navigation.

## Liens dynamiques vers la galerie
Normalement tout est fait automatiquement il n'y a pas besoin de toucher au code, juste le fichier `team-profiles.json` mais si jamais ...

Le site utilise des URLs avec paramètres pour naviguer directement vers un dossier spécifique :
```
gallery.html?path=Nos équipes/Par années/2024-2025
gallery.html?path=Nos équipes/Par instrument/Piano
```

**Pour créer un lien vers une section de la galerie** il faut convertir l'url pour ca il faut demander à google ou passer par *"{encodeURIComponent()}"* : 
```html
<a href="gallery.html?path=Nos équipes/Par années/2025-2026">Voir l'équipe 2025-2026</a>
```

---

## Personnalisation

### Changer la photo d'équipe sur la page About

La photo s'actualise automatiquement en fonction de l'année scolaire actuelle. Assurez-vous que :
1. La photo existe dans `images/team/team{année}/lequipe{année}.jpg`
2. Elle est référencée dans `team_photos` du fichier `team-profiles.json`

### Modifier le contenu texte

Les pages HTML se trouvent dans `frontend/` :
- `frontend/index.html` - Page d'accueil
- `frontend/about.html` - Page À propos
- `frontend/contact.html` - Page Contact
- etc.

---

## Résolution de problèmes

### La galerie ne s'affiche pas

1. Vérifiez que `frontend/gallery-structure.json` existe
2. Relancez `python3 start.py`
3. Vérifiez la console du navigateur (F12) ou *Inspecter la navigateur* pour voir les erreurs
4. ChatGPT et Claude.ai est votre meilleur ami pour debugger les erreurs et la console

### Les photos d'équipe n'apparaissent pas en premier dans le dossier de l'équipe

1. Vérifiez que `team_photos` est bien dans `team-profiles.json`
2. Relancez `python3 start.py`
3. Vérifiez que `gallery-structure.json` contient le champ `team_photos` à la racine

### Un membre n'apparaît pas

1. Vérifiez la syntaxe JSON (virgules, guillemets)
2. Vérifiez que `annee_debut` et `annee_fin` couvrent l'année actuelle
3. Vérifiez que le chemin de l'image est correct
4. Vérifier le format de l'image (jpeg au lieu de jpg par exemple)

---
## Ajout au site internet final 
L'orchestra loue un serveur au Louvain-li-nux et depuis quelque temps possède un repo sur leur GitLab ce qui permet de mettre à jour le site automatiquement
en pushant sur le repo de l'Orchestra de leur GitLab ! 
```bash
git push gitlab main 
# ou
git push gitlab main --force
```

---

## Contact technique

Si vous rencontrez des problèmes techniques que vous ne pouvez pas résoudre, contactez l'ancien responsable du site ou consultez ce guide ou pour toutes questions relative au déploiement du site sur internet contactez le Linux (ils sont très réactifs sur Discord)

**Bon courage pour cette belle année!**