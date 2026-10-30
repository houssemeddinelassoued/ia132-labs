"""Tests d'intégration : un VRAI serveur HTTP, de vraies requêtes.

La fixture `serveur` démarre l'API sur un port libre et l'arrête à la fin du module.
"""

import json
import threading
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

import pytest

from api import ALPHABET, LONGUEUR_CODE, TAILLE_MAX_URL, creer_serveur


class SansRedirection(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None  # pour lire la réponse 302 elle-même


ouvrir = urllib.request.build_opener(SansRedirection).open


@pytest.fixture(scope="module")
def serveur():
    srv = creer_serveur()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()
    srv.server_close()


def requete(base, methode, chemin, corps=None, *, corps_brut=None):
    """Retourne (statut, en-têtes, JSON ou None) ; corps_brut permet d'envoyer du JSON mal formé."""
    donnees = json.dumps(corps).encode() if corps is not None else None
    if corps_brut is not None:
        donnees = corps_brut
    req = urllib.request.Request(base + chemin, data=donnees, method=methode, headers={"Content-Type": "application/json"})
    try:
        with ouvrir(req, timeout=5) as r:
            brut = r.read()
            return r.status, r.headers, json.loads(brut) if brut else None
    except urllib.error.HTTPError as e:
        brut = e.read()
        return e.code, e.headers, json.loads(brut) if brut else None


def test_sante(serveur):
    statut, _, corps = requete(serveur, "GET", "/sante")
    assert (statut, corps) == (200, {"statut": "ok"})


@pytest.mark.parametrize("url", ["http://exemple.ca/a?b=1", "https://exemple.ca/chemin"])
def test_creer_rediriger_et_compter_les_visites(serveur, url):
    statut, entetes, corps = requete(serveur, "POST", "/liens", {"url": url})
    assert statut == 201
    assert entetes.get_content_type() == "application/json"
    code = corps["code"]
    assert corps == {"code": code, "url": url}
    assert len(code) == LONGUEUR_CODE
    assert all(caractere in ALPHABET for caractere in code)

    for clics in range(4):
        statut, _, stats = requete(serveur, "GET", f"/stats/{code}")
        assert (statut, stats) == (200, {"code": code, "url": url, "clics": clics})
        if clics < 3:
            statut, entetes, corps = requete(serveur, "GET", f"/l/{code}")
            assert statut == 302
            assert entetes["Location"] == url
            assert corps is None


@pytest.mark.parametrize("corps", [
    {}, {"url": ""}, {"url": None}, {"url": 42}, {"url": []},
    {"url": "ftp://exemple.ca"}, {"url": "https://"},
    {"url": "https://a.ca/" + "x" * TAILLE_MAX_URL},
    [], "https://exemple.ca", 42, None,
])
def test_corps_ou_url_invalide(serveur, corps):
    statut, _, reponse = requete(serveur, "POST", "/liens", corps)
    assert (statut, reponse) == (400, {"erreur": "url invalide : http(s)://… attendu"})


@pytest.mark.parametrize("brut", [b'{"url":', b'pas du JSON', b'{"url": "https://exemple.ca",}'])
def test_json_mal_forme(serveur, brut):
    statut, _, corps = requete(serveur, "POST", "/liens", corps_brut=brut)
    assert (statut, corps) == (400, {"erreur": "JSON invalide"})


@pytest.mark.parametrize("chemin", ["/l/inconnu", "/stats/inconnu"])
def test_code_inconnu(serveur, chemin):
    statut, _, corps = requete(serveur, "GET", chemin)
    assert (statut, corps) == (404, {"erreur": "lien inconnu"})


@pytest.mark.parametrize("methode, chemin", [("GET", "/inconnue"), ("POST", "/inconnue"), ("GET", "/liens")])
def test_route_inconnue(serveur, methode, chemin):
    statut, _, corps = requete(serveur, methode, chemin)
    assert (statut, corps) == (404, {"erreur": "route inconnue"})


def test_creations_concurrentes(serveur):
    urls = [f"https://exemple.ca/concurrent/{i}" for i in range(200)]

    def creer(url):
        return requete(serveur, "POST", "/liens", {"url": url})

    with ThreadPoolExecutor(max_workers=4) as pool:
        reponses = list(pool.map(creer, urls))

    codes = []
    for url, (statut, _, corps) in zip(urls, reponses, strict=True):
        assert statut == 201
        assert corps["url"] == url
        codes.append(corps["code"])
        statut, _, stats = requete(serveur, "GET", f"/stats/{corps['code']}")
        assert (statut, stats) == (200, {"code": corps["code"], "url": url, "clics": 0})
    assert len(codes) == 200
    assert len(set(codes)) == 200


def test_visites_concurrentes_sans_perte_de_clics(serveur):
    url = "https://exemple.ca/visites"
    statut, _, corps = requete(serveur, "POST", "/liens", {"url": url})
    assert statut == 201
    code = corps["code"]

    def visiter(_):
        return requete(serveur, "GET", f"/l/{code}")

    with ThreadPoolExecutor(max_workers=4) as pool:
        reponses = list(pool.map(visiter, range(40)))
    for statut, entetes, corps in reponses:
        assert statut == 302
        assert entetes["Location"] == url
        assert corps is None
    statut, _, stats = requete(serveur, "GET", f"/stats/{code}")
    assert (statut, stats) == (200, {"code": code, "url": url, "clics": 40})
