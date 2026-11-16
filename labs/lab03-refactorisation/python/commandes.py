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
        if commande["statut"] != "annulee":
            if commande["poids"] > 0:
                sous_total = 0
                for ligne in commande["lignes"]:
                    sous_total = sous_total + ligne["prix"] * ligne["qte"]
                if region == "QC":
                    if commande["poids"] <= 2:
                        frais = 8
                    else:
                        if commande["poids"] <= 10:
                            frais = 15
                        else:
                            frais = 15 + (commande["poids"] - 10) * 1.5
                elif region == "ON":
                    if commande["poids"] <= 2:
                        frais = 10
                    else:
                        if commande["poids"] <= 10:
                            frais = 18
                        else:
                            frais = 18 + (commande["poids"] - 10) * 1.75
                else:
                    if commande["poids"] <= 2:
                        frais = 14
                    else:
                        if commande["poids"] <= 10:
                            frais = 25
                        else:
                            frais = 25 + (commande["poids"] - 10) * 2.5
                if est_premium:
                    if sous_total > 100:
                        frais = 0
                    else:
                        frais = frais / 2
                if sous_total > 500:
                    priorite = "haute"
                elif sous_total > 100:
                    priorite = "normale"
                else:
                    priorite = "basse"
                resultats.append({"id": commande["id"], "total": round(sous_total + frais, 2), "livraison": round(frais, 2), "priorite": priorite})
            else:
                print("poids invalide " + str(commande["id"]))
    return resultats
