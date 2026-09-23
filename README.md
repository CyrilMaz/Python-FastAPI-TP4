# Plateforme de location de matériel — FastAPI

## Le projet

Pour ce TP, nous avons choisi de créer une API de location de matériel avec FastAPI.

L'idée est simple : des utilisateurs peuvent consulter du matériel classé par catégorie, le réserver pour une période donnée et laisser un avis.

Les données sont stockées en mémoire, sans base de données, comme demandé dans le sujet.

## Les 5 ressources

Notre API contient 5 ressources principales :

- `User` : les utilisateurs de la plateforme
- `Category` : les catégories de matériel
- `Material` : le matériel disponible à la location
- `Reservation` : les réservations
- `Review` : les avis laissés par les utilisateurs

Les ressources sont liées entre elles. Un matériel appartient à une catégorie, et les réservations et avis sont liés à un utilisateur et à un matériel.

## Ce que l'API permet de faire

Chaque ressource possède son CRUD : création, liste, détail, modification et suppression.

Nous avons aussi ajouté :

- des validations Pydantic avec `Field`, `field_validator` et `model_validator`
- plusieurs `Enum`
- des champs optionnels et des valeurs par défaut
- un modèle imbriqué pour les photos d'un avis
- des `response_model` pour ne pas exposer certaines informations
- des erreurs HTTP claires
- de la recherche, du filtrage, de la pagination et du tri sur les matériels
- une route de statistiques sur les réservations

## Structure du projet

```text
Python-FastAPI-TP4/
├── main.py
├── models.py
├── reservation.py
├── store.py
├── requirements.txt
├── README.md
├── JOURNAL.md
├── TESTS.md
├── routers/
│   ├── __init__.py
│   ├── categories.py
│   └── materials.py
└── .gitignore
```

## Installation

Cloner le projet :

```bash
git clone https://github.com/CyrilMaz/Python-FastAPI-TP4.git
cd Python-FastAPI-TP4
```

Installer les dépendances :

```bash
python -m pip install -r requirements.txt
```

## Lancer l'API

```bash
python -m uvicorn main:app --reload
```

Swagger est ensuite disponible ici :

```text
http://127.0.0.1:8000/docs
```

## Routes principales

### Utilisateurs

```text
POST   /users
GET    /users
GET    /users/{user_id}
PATCH  /users/{user_id}
DELETE /users/{user_id}
```

### Avis

```text
POST   /reviews
GET    /reviews
GET    /reviews/{review_id}
PATCH  /reviews/{review_id}
DELETE /reviews/{review_id}
```

### Catégories

```text
POST   /categories
GET    /categories
GET    /categories/{category_id}
PATCH  /categories/{category_id}
DELETE /categories/{category_id}
```

### Matériels

```text
POST   /materials
GET    /materials
GET    /materials/{material_id}
PATCH  /materials/{material_id}
DELETE /materials/{material_id}
```

La liste des matériels accepte aussi des paramètres pour rechercher, filtrer, trier et paginer les résultats.

### Réservations

```text
POST   /reservations
GET    /reservations
GET    /reservations/stats
GET    /reservations/{reservation_id}
PATCH  /reservations/{reservation_id}
DELETE /reservations/{reservation_id}
```

## Documentation du projet

- `JOURNAL.md` contient nos choix de conception et les difficultés rencontrées.
- `TESTS.md` contient les principaux tests réalisés sur les routes.