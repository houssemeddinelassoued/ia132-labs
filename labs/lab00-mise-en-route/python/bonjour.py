"""Lab 00 — Vérifie que l'environnement Python fonctionne."""


def saluer(nom: str) -> str:
    """Retourne un message de bienvenue personnalisé."""
    nom = nom.strip() or "inconnu"
    return f"Bonjour {nom}, bienvenue à la formation IA132 !"


