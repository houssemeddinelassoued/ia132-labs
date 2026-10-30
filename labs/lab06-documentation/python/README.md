# Module `geo`

## But

Ce module fournit des outils simples pour manipuler des points géographiques :

- `Point` : représente un point immuable avec un nom, une latitude et une longitude.
- `distance_km` : calcule la distance entre deux points avec la formule de Haversine.
- `dans_le_rayon` : sélectionne les points dans un rayon donné et les trie par distance croissante.
- `plus_proche` : trouve le point le plus proche d'une origine.
- `format_coordonnees` : affiche les coordonnées avec les directions N, S, E et O.

Les coordonnées sont exprimées en degrés décimaux et les distances en kilomètres.

## Installation

Python **3.10 ou plus récent** est requis. Le module utilise uniquement la bibliothèque standard : aucune dépendance externe n'est nécessaire pour l'utiliser.

Placez `geo.py` dans le même dossier que votre script, ou rendez son dossier accessible dans le chemin d'importation Python.

Pour essayer l'exemple ci-dessous, ouvrez un terminal dans le dossier contenant `geo.py`, puis lancez Python :

```sh
python
```

Selon votre installation, la commande peut être `python3` ou `py`.

## Exemple

```python
from geo import Point, distance_km, dans_le_rayon, plus_proche, format_coordonnees

origine = Point("Origine", 0.0, 0.0)
proche = Point("Proche", 0.0, 1.0)
loin = Point("Loin", 0.0, 2.0)
points = [loin, proche, origine]

print(distance_km(origine, proche))
# 111.2

print([p.nom for p in dans_le_rayon(origine, points, 150.0)])
# ['Origine', 'Proche']

voisin = plus_proche(origine, points)
print(voisin.nom if voisin is not None else "Aucun point")
# Proche

print(format_coordonnees(proche))
# 0.0000° N, 1.0000° E
```

### Vérification des exemples documentés

Depuis le dossier contenant `geo.py`, exécutez les doctests :

```sh
python -m doctest -v geo.py
```

Pour exécuter aussi les tests de `test_geo.py`, installez `pytest`, puis lancez :

```sh
python -m pip install pytest
python -m pytest test_geo.py
```

## Limites

- La Terre est modélisée par une sphère de rayon 6 371 km. Les distances sont approximatives et ne tiennent compte ni du relief, ni de l'altitude, ni des itinéraires routiers.
- Les distances sont arrondies à une décimale avant le filtrage et le classement. Cet arrondi peut influencer la sélection près de la limite d'un rayon ou créer des égalités.
- Les coordonnées ne sont pas validées. Fournissez des latitudes entre −90 et 90 degrés et des longitudes entre −180 et 180 degrés, avec des valeurs numériques finies.
- Pour des points presque antipodaux, les erreurs d'arrondi des calculs peuvent entraîner une erreur de domaine mathématique.
- `dans_le_rayon` inclut les points exactement à la limite du rayon selon la distance arrondie. Un rayon négatif déclenche une `ValueError`.
- `plus_proche` exclut les points égaux à l'origine selon leurs trois attributs (`nom`, `lat`, `lon`). Deux points de noms différents aux mêmes coordonnées restent donc des candidats. La fonction renvoie `None` sans candidat et retient le premier en cas d'égalité de distance.
- Les recherches parcourent la liste de points sans index spatial ; le module convient surtout aux petits ensembles de données.
