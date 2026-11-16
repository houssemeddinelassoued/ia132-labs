"""Tableau de bord d'occupation des salles (reproduit le ticket INC-101).

    python tableau_de_bord.py
"""

from datetime import datetime

from reservations import Reservation, taux_occupation

SALLES = ["A-101", "A-102", "B-204"]

RESERVATIONS = [
    Reservation("A-101", datetime(2026, 11, 2, 9), datetime(2026, 11, 2, 12), 20.0),
    Reservation("A-101", datetime(2026, 11, 2, 13), datetime(2026, 11, 2, 16), 20.0),
    Reservation("A-102", datetime(2026, 11, 2, 10), datetime(2026, 11, 2, 11), 15.0),
]


def afficher() -> None:
    print("Occupation des salles · lundi 2 novembre")
    for salle in SALLES:
        try:
            print(f"  {salle} : {taux_occupation(RESERVATIONS, salle):.0%}")
        except ValueError:
            print(f"  {salle} : n/a (aucune période ouverte)")


if __name__ == "__main__":
    afficher()
