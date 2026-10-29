"""Lab 05 — Analyse d'une liste de diffusion.

Correct, testé… et beaucoup trop lent sur les 200 000 abonnés de la vraie liste.
"""

from collections import Counter
from heapq import nsmallest


def normaliser(courriel: str) -> str:
    return courriel.strip().lower()


def dedoublonner(courriels: list[str]) -> list[str]:
    """Courriels uniques, normalisés, dans l'ordre de leur PREMIÈRE apparition."""
    resultat = []
    vus = set()
    for c in courriels:
        c = normaliser(c)
        if c not in vus:
            vus.add(c)
            resultat.append(c)
    return resultat


def top_domaines(courriels: list[str], n: int = 3) -> list[tuple[str, int]]:
    """Les n domaines les plus fréquents : (domaine, nombre), par nombre décroissant puis par nom."""
    frequences = Counter()
    domaines_uniques = {}
    for c in courriels:
        d = normaliser(c).split("@")[1]
        frequences[d] += 1
        # Conserver la seconde normalisation du dédoublonnage original,
        # tout en comptant les domaines avant cette normalisation.
        domaines_uniques.setdefault(normaliser(d), None)

    k = len(domaines_uniques)
    # Reproduire comptes[:n], y compris pour n nul ou négatif.
    r = min(n, k) if n >= 0 else max(0, k + n)
    return nsmallest(
        r,
        ((d, frequences[d]) for d in domaines_uniques),
        key=lambda x: (-x[1], x[0]),
    )


def communs(liste_a: list[str], liste_b: list[str]) -> list[str]:
    """Courriels présents dans les deux listes, sans doublon, dans l'ordre de liste_a."""
    b = {normaliser(c) for c in liste_b}
    return [c for c in dedoublonner(liste_a) if c in b]
