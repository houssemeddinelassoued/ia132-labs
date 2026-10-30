"""Fournit des outils de calcul et de présentation de coordonnées géographiques.

Les points utilisent des latitudes et longitudes en degrés. Les distances sont
calculées en kilomètres sur une Terre sphérique et arrondies à une décimale.

Examples:
    >>> origine = Point("Origine", 0.0, 0.0)
    >>> destination = Point("Est", 0.0, 1.0)
    >>> distance_km(origine, destination)
    111.2
"""

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

RAYON_TERRE_KM = 6371.0


@dataclass(frozen=True)
class Point:
    """Représente un point géographique immuable.

    Attributes:
        nom (str): Nom du point.
        lat (float): Latitude en degrés, positive au nord et négative au sud.
        lon (float): Longitude en degrés, positive à l'est et négative à l'ouest.

    Examples:
        >>> point = Point("Montréal", 45.5017, -73.5673)
        >>> point.nom
        'Montréal'
    """

    nom: str
    lat: float
    lon: float


def distance_km(a: Point, b: Point) -> float:
    """Calcule la distance entre deux points avec la formule de Haversine.

    La Terre est modélisée par une sphère de rayon ``RAYON_TERRE_KM``.

    Args:
        a (Point): Point de départ, avec latitude et longitude en degrés.
        b (Point): Point d'arrivée, avec latitude et longitude en degrés.

    Returns:
        float: Distance en kilomètres, arrondie à une décimale.

    Examples:
        >>> depart = Point("Origine", 0.0, 0.0)
        >>> arrivee = Point("Est", 0.0, 1.0)
        >>> distance_km(depart, arrivee)
        111.2
    """
    dlat = radians(b.lat - a.lat)
    dlon = radians(b.lon - a.lon)
    h = sin(dlat / 2) ** 2 + cos(radians(a.lat)) * cos(radians(b.lat)) * sin(dlon / 2) ** 2
    return round(2 * RAYON_TERRE_KM * asin(sqrt(h)), 1)


def dans_le_rayon(centre: Point, points: list[Point], rayon_km: float) -> list[Point]:
    """Sélectionne les points situés dans un rayon donné autour du centre.

    La limite est incluse et les distances comparées sont arrondies à une
    décimale par ``distance_km``.

    Args:
        centre (Point): Point servant de centre à la recherche.
        points (list[Point]): Points à examiner.
        rayon_km (float): Rayon de recherche en kilomètres, positif ou nul.

    Returns:
        list[Point]: Points retenus, triés par distance croissante au centre.

    Raises:
        ValueError: Si le rayon est négatif.

    Examples:
        >>> centre = Point("Centre", 0.0, 0.0)
        >>> proche = Point("Proche", 0.0, 1.0)
        >>> loin = Point("Loin", 0.0, 2.0)
        >>> [p.nom for p in dans_le_rayon(centre, [loin, proche, centre], 111.2)]
        ['Centre', 'Proche']
        >>> dans_le_rayon(centre, [], -1)
        Traceback (most recent call last):
            ...
        ValueError: rayon négatif
    """
    if rayon_km < 0:
        raise ValueError("rayon négatif")
    return sorted((p for p in points if distance_km(centre, p) <= rayon_km), key=lambda p: distance_km(centre, p))


def plus_proche(origine: Point, points: list[Point]) -> Point | None:
    """Trouve le point le plus proche de l'origine parmi les candidats.

    Les points égaux à l'origine sont exclus. Les distances sont arrondies
    à une décimale par ``distance_km`` ; en cas d'égalité, le premier point
    rencontré est retenu.

    Args:
        origine (Point): Point servant de référence pour les distances.
        points (list[Point]): Points candidats à examiner.

    Returns:
        Point | None: Point le plus proche, ou ``None`` si aucun candidat
        distinct de l'origine n'est disponible.

    Examples:
        >>> origine = Point("Origine", 0.0, 0.0)
        >>> proche = Point("Proche", 0.0, 1.0)
        >>> loin = Point("Loin", 0.0, 2.0)
        >>> plus_proche(origine, [origine, loin, proche]) == proche
        True
        >>> plus_proche(origine, [origine]) is None
        True
    """
    candidats = [p for p in points if p != origine]
    return min(candidats, key=lambda p: distance_km(origine, p), default=None)


def format_coordonnees(p: Point) -> str:
    """Formate les coordonnées en degrés avec les directions cardinales.

    Les valeurs absolues sont affichées avec quatre décimales. Une latitude
    nulle est associée au nord et une longitude nulle à l'est.

    Args:
        p (Point): Point dont la latitude et la longitude sont en degrés.

    Returns:
        str: Latitude suivie de N ou S, puis longitude suivie de E ou O.

    Examples:
        >>> format_coordonnees(Point("Montréal", 45.5017, -73.5673))
        '45.5017° N, 73.5673° O'
        >>> format_coordonnees(Point("Origine", 0.0, 0.0))
        '0.0000° N, 0.0000° E'
    """
    ns = "N" if p.lat >= 0 else "S"
    eo = "E" if p.lon >= 0 else "O"
    return f"{abs(p.lat):.4f}° {ns}, {abs(p.lon):.4f}° {eo}"
