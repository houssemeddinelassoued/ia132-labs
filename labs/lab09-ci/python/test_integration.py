"""Tests d'intégration : un VRAI serveur HTTP, de vraies requêtes. À compléter (voir README).

La fixture `serveur` démarre l'API sur un port libre et l'arrête à la fin du module.
"""

import json
import threading
import urllib.error
import urllib.request

import pytest

from api import creer_serveur


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


def requete(base, methode, chemin, corps=None):
    """Retourne (statut, en-têtes, corps JSON ou None) sans lever d'exception sur 4xx."""
    donnees = json.dumps(corps).encode() if corps is not None else None
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


URL = "https://exemple.org/page"


def creer(serveur, url=URL):
    statut, _, corps = requete(serveur, "POST", "/liens", {"url": url})
    assert statut == 201
    return corps["code"]


def test_creer_puis_suivre_un_lien(serveur):
    statut, _, corps = requete(serveur, "POST", "/liens", {"url": URL})
    assert statut == 201
    assert corps["url"] == URL
    assert len(corps["code"]) == 6

    statut, entetes, _ = requete(serveur, "GET", f"/l/{corps['code']}")
    assert statut == 302
    assert entetes["Location"] == URL


def test_statistiques_apres_trois_visites(serveur):
    code = creer(serveur)
    for _ in range(3):
        requete(serveur, "GET", f"/l/{code}")
    statut, _, corps = requete(serveur, "GET", f"/stats/{code}")
    assert statut == 200
    assert corps == {"code": code, "url": URL, "clics": 3}


@pytest.mark.parametrize("corps", [{"url": "ftp://exemple.org"}, {"url": "pas une url"}, {"url": 42}, {}, []])
def test_url_invalide_renvoie_400(serveur, corps):
    statut, _, reponse = requete(serveur, "POST", "/liens", corps)
    assert statut == 400
    assert "erreur" in reponse


def test_url_trop_longue_renvoie_400(serveur):
    statut, _, _ = requete(serveur, "POST", "/liens", {"url": "https://exemple.org/" + "a" * 2_048})
    assert statut == 400


def test_json_invalide_renvoie_400(serveur):
    req = urllib.request.Request(serveur + "/liens", data=b"{pas du json", method="POST")
    with pytest.raises(urllib.error.HTTPError) as exc:
        ouvrir(req, timeout=5)
    assert exc.value.code == 400


@pytest.mark.parametrize("chemin", ["/l/inconnu", "/stats/inconnu"])
def test_code_inconnu_renvoie_404(serveur, chemin):
    statut, _, _ = requete(serveur, "GET", chemin)
    assert statut == 404


def test_route_inconnue_renvoie_404(serveur):
    assert requete(serveur, "GET", "/nimporte")[0] == 404
    assert requete(serveur, "POST", "/autre", {"url": URL})[0] == 404


def test_200_creations_concurrentes_donnent_200_codes_uniques(serveur):
    from concurrent.futures import ThreadPoolExecutor

    with ThreadPoolExecutor(max_workers=20) as pool:
        codes = list(pool.map(lambda _: creer(serveur), range(200)))
    assert len(set(codes)) == 200
