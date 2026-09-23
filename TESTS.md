# Journal de tests

Les tests ci-dessous ont été effectués sur la version intégrée du projet.

Pour les catégories et les matériels, nous avons réutilisé les UUID réellement renvoyés par l'API lors de leur création.

| Route | Test effectué | Résultat obtenu |
|---|---|---|
| `POST /users` | création d'un utilisateur valide | `201` |
| `POST /users` | création avec un `id` déjà utilisé | `400` |
| `GET /users` | récupération de la liste | `200` |
| `GET /users/{id}` | utilisateur existant | `200` |
| `GET /users/{id}` | utilisateur inexistant | `404` |
| `PATCH /users/{id}` | modification du nom | `200` |
| `PATCH /users/{id}` | utilisateur inexistant | `404` |
| `PATCH /users/{id}` | email déjà utilisé par un autre compte | `400` |
| `DELETE /users/{id}` | suppression d'un utilisateur existant | `200` |
| `DELETE /users/{id}` | utilisateur inexistant | `404` |
| `POST /categories` | création d'une catégorie valide | `201` |
| `POST /categories` | catégorie avec un nom déjà utilisé | `409` |
| `GET /categories` | récupération de la liste | `200` |
| `GET /categories/{id}` | catégorie existante | `200` |
| `GET /categories/{id}` | identifiant qui n'est pas un UUID | `422` |
| `PATCH /categories/{id}` | modification de la description | `200` |
| `PATCH /categories/{id}` | UUID inexistant | `404` |
| `DELETE /categories/{id}` | catégorie non utilisée | `204` |
| `DELETE /categories/{id}` | catégorie encore utilisée par un matériel | `409` |
| `POST /materials` | création d'un matériel valide | `201` |
| `POST /materials` | catégorie inexistante | `404` |
| `GET /materials` | récupération de la liste | `200` |
| `GET /materials?limit=0` | pagination invalide | `422` |
| `GET /materials/{id}` | matériel existant | `200` |
| `GET /materials/{id}` | matériel inexistant | `404` |
| `PATCH /materials/{id}` | modification du tarif journalier | `200` |
| `PATCH /materials/{id}` | quantité disponible supérieure à la quantité totale | `422` |
| `DELETE /materials/{id}` | suppression d'un matériel existant | `204` |
| `DELETE /materials/{id}` | matériel inexistant | `404` |
| `POST /reviews` | création d'un avis valide | `201` |
| `POST /reviews` | utilisateur inexistant | `404` |
| `POST /reviews` | matériel inexistant | `404` |
| `GET /reviews` | récupération de la liste | `200` |
| `GET /reviews/{id}` | avis existant | `200` |
| `GET /reviews/{id}` | avis inexistant | `404` |
| `PATCH /reviews/{id}` | modification d'un avis valide | `200` |
| `PATCH /reviews/{id}` | avis inexistant | `404` |
| `DELETE /reviews/{id}` | suppression d'un avis existant | `200` |
| `DELETE /reviews/{id}` | avis inexistant | `404` |
| `POST /reservations` | création avec un utilisateur et un matériel existants | `201` |
| `POST /reservations` | utilisateur inexistant | `404` |
| `POST /reservations` | chevauchement avec une autre réservation | `400` |
| `GET /reservations` | récupération de la liste | `200` |
| `GET /reservations?status=BAD` | statut invalide | `422` |
| `GET /reservations/stats` | calcul des statistiques | `200` |
| `GET /reservations/{id}` | réservation existante | `200` |
| `GET /reservations/{id}` | réservation inexistante | `404` |
| `PATCH /reservations/{id}` | modification des notes | `200` |
| `PATCH /reservations/{id}` | réservation inexistante | `404` |
| `DELETE /reservations/{id}` | suppression d'une réservation existante | `204` |
| `DELETE /reservations/{id}` | réservation inexistante | `404` |

## Quelques validations vérifiées

Nous avons aussi vérifié que :

- un utilisateur avec un email contenant un espace est refusé avec une erreur `422`
- un `username` trop court est refusé avec une erreur `422`
- la réponse publique d'un utilisateur ne contient ni son email ni son téléphone
- les notes internes d'une catégorie ne sont pas exposées dans la réponse publique
- une quantité disponible supérieure à la quantité totale est refusée
- une réservation avec des dates incohérentes est refusée
- une réservation sur un matériel déjà réservé sur la même période est refusée

## Point restant à corriger

Pendant les tests, nous avons trouvé un cas particulier sur `PATCH /reviews/{review_id}`.

Si la modification fait passer la note à `1` ou `2` avec un commentaire trop court, le `model_validator` détecte bien l'erreur mais celle-ci remonte actuellement comme une erreur serveur au lieu d'une réponse HTTP de validation propre.

C'est le principal point restant à corriger avant de considérer les tests comme entièrement terminés