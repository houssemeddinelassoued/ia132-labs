STATUT_ANNULEE = "annulee"
SEUIL_POIDS_LEGER_KG = 2
SEUIL_POIDS_MOYEN_KG = 10
SEUIL_PREMIUM_SOUS_TOTAL = 100
SEUIL_PRIORITE_HAUTE = 500
# Région -> (frais léger, frais moyen, tarif par kg au-delà du seuil moyen)
GRILLES_LIVRAISON = {"QC": (8, 15, 1.5), "ON": (10, 18, 1.75)}
GRILLE_LIVRAISON_PAR_DEFAUT = (14, 25, 2.5)


def traiter(commandes, region, est_premium):
    """Calcule le total, les frais de livraison et la priorité des commandes.

    Args:
        commandes: Commandes à traiter.
        region: Région utilisée pour calculer les frais de livraison.
        est_premium: Indique si le client bénéficie du tarif premium.

    Returns:
        Les résultats des commandes non annulées ayant un poids valide.
    """
    resultats = []
    for commande in commandes:
        if commande["statut"] != STATUT_ANNULEE:
            poids = commande["poids"]
            if poids > 0:
                sous_total = 0
                for ligne in commande["lignes"]:
                    sous_total = sous_total + ligne["prix"] * ligne["qte"]
                leger, moyen, par_kg = GRILLES_LIVRAISON.get(region, GRILLE_LIVRAISON_PAR_DEFAUT)
                if poids <= SEUIL_POIDS_LEGER_KG:
                    frais = leger
                elif poids <= SEUIL_POIDS_MOYEN_KG:
                    frais = moyen
                else:
                    frais = moyen + (poids - SEUIL_POIDS_MOYEN_KG) * par_kg
                if est_premium:
                    if sous_total > SEUIL_PREMIUM_SOUS_TOTAL:
                        frais = 0
                    else:
                        frais = frais / 2
                if sous_total > SEUIL_PRIORITE_HAUTE:
                    priorite = "haute"
                elif sous_total > SEUIL_PREMIUM_SOUS_TOTAL:
                    priorite = "normale"
                else:
                    priorite = "basse"
                resultats.append(
                    {
                        "id": commande["id"],
                        "total": round(sous_total + frais, 2),
                        "livraison": round(frais, 2),
                        "priorite": priorite,
                    }
                )
            else:
                print("poids invalide " + str(commande["id"]))
    return resultats
