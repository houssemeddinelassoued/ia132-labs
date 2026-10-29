"""Lab 01 — Convertisseur d'unités.

Complétez chaque fonction avec votre assistant, en suivant les 4 étapes du README :
complétion en ligne, chat, édition, agent.
"""

import sys

ZERO_ABSOLU_C = -273.15
KM_PAR_MILE = 1.609344


def celsius_vers_fahrenheit(c: float) -> float:
    """Convertit des degrés Celsius en degrés Fahrenheit.

    Lève ValueError si la température est sous le zéro absolu.
    """
    if c < ZERO_ABSOLU_C:
        raise ValueError("La température est sous le zéro absolu.")
    return c * 9 / 5 + 32


def fahrenheit_vers_celsius(f: float) -> float:
    """Convertit des degrés Fahrenheit en degrés Celsius.

    Lève ValueError si le résultat est sous le zéro absolu.
    """
    c = (f - 32) * 5 / 9
    if c < ZERO_ABSOLU_C:
        raise ValueError("La température est sous le zéro absolu.")
    return c


def km_vers_miles(km: float) -> float:
    """Convertit des kilomètres en miles. Lève ValueError si la distance est négative."""
    if km < 0:
        raise ValueError("La distance ne peut pas être négative.")
    return km / KM_PAR_MILE


def miles_vers_km(miles: float) -> float:
    """Convertit des miles en kilomètres. Lève ValueError si la distance est négative."""
    if miles < 0:
        raise ValueError("La distance ne peut pas être négative.")
    return miles * KM_PAR_MILE


def convertir(valeur: float, de: str, vers: str) -> float:
    """Convertit `valeur` de l'unité `de` vers l'unité `vers`.

    Unités prises en charge : "C", "F", "km", "mi".
    Même unité des deux côtés : la valeur est retournée telle quelle.
    Paire non prise en charge (ex. "C" vers "km") : ValueError.
    """
    if de == vers:
        return valeur

    conversions = {
        ("C", "F"): celsius_vers_fahrenheit,
        ("F", "C"): fahrenheit_vers_celsius,
        ("km", "mi"): km_vers_miles,
        ("mi", "km"): miles_vers_km,
    }
    try:
        conversion = conversions[(de, vers)]
    except KeyError as erreur:
        raise ValueError(f"Conversion non prise en charge : {de} vers {vers}.") from erreur
    return conversion(valeur)


def main(argv: list[str]) -> str:
    """Interprète les arguments de conversion et retourne le message à afficher.

    Args:
        argv: Valeur, unité de départ et unité d’arrivée, sans le nom du script.

    Returns:
        Résultat avec deux décimales, message d’usage ou message d’erreur.
    """
    if len(argv) != 3:
        return "Usage : python convertisseur.py <valeur> <de> <vers>"

    valeur, de, vers = argv
    try:
        resultat = convertir(float(valeur), de, vers)
    except ValueError as erreur:
        return f"Erreur : {erreur}"
    return f"{resultat:.2f} {vers}"


if __name__ == "__main__":
    print(main(sys.argv[1:]))
