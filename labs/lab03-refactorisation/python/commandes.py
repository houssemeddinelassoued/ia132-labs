# Module hérité : calcule le total, la livraison et la priorité des commandes.
# Écrit en 2017, « ça marche, on n'y touche pas ». Jusqu'à aujourd'hui.


def _calculer_sous_total(lignes):
    """Additionne les montants des lignes dans leur ordre d'origine."""
    sous_total = 0
    for ligne in lignes:
        sous_total = sous_total + ligne["prix"] * ligne["qte"]
    return sous_total


def _appliquer_avantage_premium(frais_livraison, sous_total):
    """Applique la gratuité au-delà de 100, sinon la réduction de moitié."""
    if sous_total > 100:
        frais_livraison = 0
    else:
        frais_livraison = frais_livraison / 2
    return frais_livraison


def _determiner_priorite(sous_total):
    """Détermine la priorité à partir du sous-total avant livraison."""
    if sous_total > 500:
        priorite = "haute"
    elif sous_total > 100:
        priorite = "normale"
    else:
        priorite = "basse"
    return priorite


def traiter(c, r, p):
    """Calcule le total, la livraison et la priorité des commandes admissibles.

    Paramètres :
        c : itérable de dictionnaires de commande. Chaque commande traitée
            contient id, statut, poids (nombre) et lignes (itérable de
            dictionnaires avec prix et qte numériques).
        r : région de livraison ; "QC" et "ON" ont leurs propres tarifs,
            toute autre valeur utilise le tarif par défaut.
        p : indicateur de client premium, évalué selon sa valeur de vérité.

    Retourne une liste de dictionnaires, dans l'ordre des commandes retenues,
    avec id, total (sous-total plus livraison, arrondi à deux décimales),
    livraison (frais arrondis à deux décimales) et priorite ("haute",
    "normale" ou "basse"). Les montants et les poids doivent utiliser les
    mêmes unités que les tarifs et les seuils fixes de cette fonction.

    Les commandes de statut "annulee" sont ignorées. Les autres commandes
    dont le poids n'est pas strictement positif sont exclues avec affichage
    du message "poids invalide " suivi de leur identifiant.
    Les noms c, r et p sont conservés pour les appels par arguments nommés.
    """
    resultats = []
    for commande in c:
        if commande["statut"] == "annulee":
            continue
        if not (commande["poids"] > 0):
            print("poids invalide " + str(commande["id"]))
            continue

        sous_total = _calculer_sous_total(commande["lignes"])
        if r == "QC":
            if commande["poids"] <= 2:
                frais_livraison = 8
            else:
                if commande["poids"] <= 10:
                    frais_livraison = 15
                else:
                    frais_livraison = 15 + (commande["poids"] - 10) * 1.5
        elif r == "ON":
            if commande["poids"] <= 2:
                frais_livraison = 10
            else:
                if commande["poids"] <= 10:
                    frais_livraison = 18
                else:
                    frais_livraison = 18 + (commande["poids"] - 10) * 1.75
        else:
            if commande["poids"] <= 2:
                frais_livraison = 14
            else:
                if commande["poids"] <= 10:
                    frais_livraison = 25
                else:
                    frais_livraison = 25 + (commande["poids"] - 10) * 2.5
        if p:
            frais_livraison = _appliquer_avantage_premium(frais_livraison, sous_total)
        priorite = _determiner_priorite(sous_total)
        resultats.append({"id": commande["id"], "total": round(sous_total + frais_livraison, 2), "livraison": round(frais_livraison, 2), "priorite": priorite})
    return resultats
