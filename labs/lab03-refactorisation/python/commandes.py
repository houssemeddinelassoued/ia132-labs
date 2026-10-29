# Module hérité : calcule le total, la livraison et la priorité des commandes.
# Écrit en 2017, « ça marche, on n'y touche pas ». Jusqu'à aujourd'hui.


_SEUIL_POIDS_LEGER = 2
_SEUIL_POIDS_STANDARD = 10
_TARIFS_LIVRAISON = {
    "QC": {"leger": 8, "standard": 15, "supplement": 1.5},
    "ON": {"leger": 10, "standard": 18, "supplement": 1.75},
}
_TARIF_LIVRAISON_DEFAUT = {"leger": 14, "standard": 25, "supplement": 2.5}


def _calculer_livraison(poids, region):
    """Applique les paliers de poids au tarif régional ou au tarif par défaut."""
    if region == "QC":
        tarif = _TARIFS_LIVRAISON["QC"]
    elif region == "ON":
        tarif = _TARIFS_LIVRAISON["ON"]
    else:
        tarif = _TARIF_LIVRAISON_DEFAUT

    if poids <= _SEUIL_POIDS_LEGER:
        return tarif["leger"]
    elif poids <= _SEUIL_POIDS_STANDARD:
        return tarif["standard"]
    else:
        return tarif["standard"] + (poids - _SEUIL_POIDS_STANDARD) * tarif["supplement"]


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
        frais_livraison = _calculer_livraison(commande["poids"], r)
        if p:
            frais_livraison = _appliquer_avantage_premium(frais_livraison, sous_total)
        priorite = _determiner_priorite(sous_total)
        identifiant = commande["id"]
        total_arrondi = round(sous_total + frais_livraison, 2)
        livraison_arrondie = round(frais_livraison, 2)
        resultats.append({
            "id": identifiant,
            "total": total_arrondi,
            "livraison": livraison_arrondie,
            "priorite": priorite,
        })
    return resultats
