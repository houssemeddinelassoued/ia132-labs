"""Vos tests du panier. Remplacez ce test par les vôtres (voir README).

    pytest labs/lab08-tests --cov=panier --cov-branch --cov-report=term-missing
    python labs/lab08-tests/python/mutants.py
"""

import pytest

from panier import Panier, Produit, StockInsuffisant

CLAVIER = Produit("KB-01", "Clavier", 4_999, stock=10)


def test_panier_vide():
    assert Panier().total() == 0


def test_ajouter_un_article():
    panier = Panier()
    panier.ajouter(CLAVIER)
    assert panier.nombre_articles() == 1


@pytest.fixture
def panier():
    return Panier()


@pytest.fixture
def produit():
    return Produit("P1", "Produit", 1_001, stock=200)


def test_un_panier_neuf_a_des_collections_vides_et_des_montants_nuls(panier):
    assert panier.lignes == {}
    assert panier.catalogue == {}
    assert panier.code_promo is None
    assert panier.nombre_articles() == 0
    assert panier.sous_total() == 0
    assert panier.rabais() == 0
    assert panier.livraison() == 0
    assert panier.total() == 0


def test_deux_paniers_ne_partagent_pas_leurs_collections(panier, produit):
    autre = Panier()
    panier.ajouter(produit)
    assert autre.lignes == {}
    assert autre.catalogue == {}


def test_les_ajouts_cumulent_les_quantites_et_distinguent_les_references(panier, produit):
    panier.ajouter(produit)
    panier.ajouter(produit, 2)
    panier.ajouter(Produit("P2", "Autre", 500, stock=10), 2)
    assert panier.lignes == {"P1": 3, "P2": 2}
    assert panier.catalogue["P1"] == produit
    assert panier.nombre_articles() == 5
    assert panier.sous_total() == 4_003


@pytest.mark.parametrize("quantite", [1, 98, 99])
def test_une_quantite_jusqua_99_est_acceptee(panier, produit, quantite):
    panier.ajouter(produit, quantite)
    assert panier.lignes == {"P1": quantite}


@pytest.mark.parametrize("quantite", [0, -1, -99, 100])
def test_une_quantite_invalide_est_refusee_sans_modifier_le_panier(panier, produit, quantite):
    with pytest.raises(ValueError):
        panier.ajouter(produit, quantite)
    assert panier.lignes == {}
    assert panier.catalogue == {}


def test_la_limite_de_99_sapplique_a_la_quantite_cumulee(panier, produit):
    panier.ajouter(produit, 98)
    panier.ajouter(produit)
    assert panier.nombre_articles() == 99
    with pytest.raises(ValueError, match="maximum 99"):
        panier.ajouter(produit)
    assert panier.lignes == {"P1": 99}


def test_le_stock_exact_est_accepte_et_son_depassement_est_refuse(panier, produit):
    produit.stock = 3
    panier.ajouter(produit, 2)
    panier.ajouter(produit)
    assert panier.lignes == {"P1": 3}
    remplacement = Produit("P1", "Remplacement", 9_999, stock=3)
    with pytest.raises(StockInsuffisant):
        panier.ajouter(remplacement)
    assert panier.lignes == {"P1": 3}
    assert panier.catalogue["P1"] is produit


@pytest.mark.parametrize("stock, quantite", [(0, 1), (3, 4)])
def test_un_stock_insuffisant_ne_cree_aucune_ligne(panier, produit, stock, quantite):
    produit.stock = stock
    with pytest.raises(StockInsuffisant):
        panier.ajouter(produit, quantite)
    assert panier.lignes == {}
    assert panier.catalogue == {}


def test_un_ajout_de_meme_reference_actualise_le_produit(panier, produit):
    panier.ajouter(produit)
    remplacement = Produit("P1", "Remplacement", 2_000, stock=10)
    panier.ajouter(remplacement)
    assert panier.catalogue["P1"] is remplacement
    assert panier.sous_total() == 4_000


def test_un_retrait_partiel_diminue_la_quantite_et_le_sous_total(panier, produit):
    panier.ajouter(produit, 3)
    panier.retirer("P1", 1)
    assert panier.lignes == {"P1": 2}
    assert panier.nombre_articles() == 2
    assert panier.sous_total() == 2_002


@pytest.mark.parametrize("quantite", [None, 3, 4])
def test_un_retrait_complet_supprime_la_ligne_et_ses_montants(panier, produit, quantite):
    panier.ajouter(produit, 3)
    panier.retirer("P1", quantite)
    assert "P1" not in panier.lignes
    assert panier.catalogue["P1"] == produit
    assert panier.nombre_articles() == 0
    assert panier.sous_total() == 0
    assert panier.total() == 0


def test_retirer_une_reference_absente_declenche_une_erreur(panier):
    with pytest.raises(KeyError) as erreur:
        panier.retirer("ABSENT")
    assert erreur.value.args == ("ABSENT",)


@pytest.mark.parametrize("quantite, attendu", [(0, 3), (-1, 4)])
def test_un_retrait_non_positif_documente_le_comportement_actuel(panier, produit, quantite, attendu):
    # Anomalie actuelle : une quantité négative augmente le contenu du panier.
    panier.ajouter(produit, 3)
    panier.retirer("P1", quantite)
    assert panier.lignes == {"P1": attendu}


@pytest.mark.parametrize("code, attendu", [
    ("MOINS10", "MOINS10"), ("moins10", "MOINS10"), ("MoInS10", "MOINS10"),
    ("LIVRAISON", "LIVRAISON"), ("livraison", "LIVRAISON"),
])
def test_les_codes_valides_sont_insensibles_a_la_casse(panier, code, attendu):
    panier.appliquer_code(code)
    assert panier.code_promo == attendu


@pytest.mark.parametrize("code", ["", "INCONNU", " MOINS10", "LIVRAISON "])
def test_un_code_invalide_conserve_la_promotion_precedente(panier, code):
    panier.appliquer_code("MOINS10")
    with pytest.raises(ValueError, match="code inconnu"):
        panier.appliquer_code(code)
    assert panier.code_promo == "MOINS10"


@pytest.mark.parametrize("premier, second, rabais, frais", [
    ("MOINS10", "LIVRAISON", 0, 0), ("LIVRAISON", "MOINS10", 100, 799),
])
def test_un_nouveau_code_remplace_le_precedent(panier, produit, premier, second, rabais, frais):
    panier.ajouter(produit)
    panier.appliquer_code(premier)
    panier.appliquer_code(second)
    assert panier.rabais() == rabais
    assert panier.livraison() == frais


@pytest.mark.parametrize("prix, attendu", [(0, 0), (9, 0), (10, 1), (19, 1), (1_001, 100), (9_998, 999)])
def test_le_rabais_est_arrondi_au_cent_inferieur(panier, produit, prix, attendu):
    produit.prix = prix
    panier.ajouter(produit)
    panier.appliquer_code("MOINS10")
    assert panier.rabais() == attendu


@pytest.mark.parametrize("code", [None, "MOINS10", "LIVRAISON"])
def test_un_panier_vide_reste_gratuit_avec_ou_sans_promotion(panier, code):
    if code:
        panier.appliquer_code(code)
    assert panier.rabais() == 0
    assert panier.livraison() == 0
    assert panier.total() == 0


@pytest.mark.parametrize("prix, code, frais, total", [
    (0, None, 799, 799), (4_999, None, 799, 5_798),
    (5_000, None, 0, 5_000), (5_001, None, 0, 5_001),
    (5_000, "MOINS10", 799, 5_299), (5_554, "MOINS10", 799, 5_798),
    (5_555, "MOINS10", 0, 5_000), (5_556, "MOINS10", 0, 5_001),
    (1_001, "LIVRAISON", 0, 1_001),
])
def test_la_livraison_et_le_total_utilisent_le_montant_apres_rabais(panier, produit, prix, code, frais, total):
    produit.prix = prix
    panier.ajouter(produit)
    if code:
        panier.appliquer_code(code)
    assert panier.sous_total() == prix
    assert panier.livraison() == frais
    assert panier.total() == total
