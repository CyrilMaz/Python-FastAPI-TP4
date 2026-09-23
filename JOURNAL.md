# Journal de bord

## Notre idée

Nous avons choisi de faire une plateforme de location de matériel parce que le thème permettait facilement de créer plusieurs ressources liées entre elles.

Nous sommes partis sur cinq ressources : `User`, `Category`, `Material`, `Reservation` et `Review`.

Le principe est qu'un utilisateur peut réserver un matériel, que chaque matériel appartient à une catégorie et qu'un utilisateur peut ensuite laisser un avis sur ce matériel.

## Répartition du travail

Nous avons séparé le projet en plusieurs parties pour pouvoir travailler en parallèle.

Une partie s'occupait principalement du catalogue avec `Material` et `Category`, une autre de `User` et `Review`, et la dernière de `Reservation` et des fonctionnalités plus transversales.

Nous avons utilisé plusieurs branches Git et fait des commits régulièrement avant de fusionner les différentes parties sur `main`.

## Validations que nous avons ajoutées

Nous avons essayé de mettre des validations qui avaient un sens pour notre projet, pas seulement pour remplir les critères du TP.

Pour les utilisateurs, le nom doit avoir une longueur correcte, l'email ne doit pas contenir d'espace et un compte professionnel doit avoir un numéro de téléphone.

Pour les avis, la note est comprise entre 1 et 5. Un commentaire vide ou composé uniquement d'espaces est refusé. Pour une mauvaise note, nous demandons aussi un commentaire un peu plus détaillé.

Pour le matériel, nous vérifions notamment les quantités : la quantité disponible ne peut pas être supérieure à la quantité totale.

Pour les réservations, la date de fin doit être après la date de début, la réservation ne peut pas commencer dans le passé et deux réservations du même matériel ne doivent pas se chevaucher.

## Fonctionnalités avancées

Sur les matériels, nous avons ajouté la recherche, le filtrage, la pagination et le tri.

Nous avons également ajouté une route de statistiques sur les réservations. Elle calcule les résultats à partir des données réellement présentes en mémoire, par exemple le nombre de réservations, leur durée moyenne ou le matériel le plus réservé.

## Difficulté rencontrée

La principale difficulté est apparue au moment de réunir les différentes parties.

Nous avions développé les ressources en parallèle et les types d'identifiants n'étaient pas toujours les mêmes. Les matériels utilisaient des `UUID`, alors que les avis et les réservations utilisaient au départ des entiers pour référencer un matériel.

La partie réservation utilisait aussi temporairement de fausses données pour les utilisateurs et les matériels.

Nous avons donc harmonisé les identifiants et relié les réservations et les avis aux vraies données du projet. Cela permet maintenant de créer un utilisateur et un matériel, puis de réutiliser réellement leurs identifiants pour créer un avis ou une réservation.

Cette étape d'intégration nous a surtout montré qu'il est important de se mettre d'accord très tôt sur les types d'identifiants et les relations entre les ressources.