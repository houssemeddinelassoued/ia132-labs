"""Tests fonctionnels (verts : « la PR marche ») puis tests de sécurité (rouges).

Les tests de sécurité ne sont révélés qu'APRÈS votre revue (étape 3 du README) :
votre revue les avait-elle anticipés ?
"""

import hashlib
import re
from pathlib import Path

import pytest

from notes_service import NotesService


@pytest.fixture
def service(monkeypatch):
    monkeypatch.setenv("NOTES_SECRET", "secret-de-test")
    return NotesService()


# ── Fonctionnel ────────────────────────────────────────────────────────────
def test_inscription_puis_connexion(service):
    uid = service.inscrire("ana@exemple.ca", "Correct-Cheval-42")
    assert service.connecter("ana@exemple.ca", "Correct-Cheval-42") == uid


def test_mauvais_mot_de_passe(service):
    service.inscrire("ana@exemple.ca", "Correct-Cheval-42")
    assert service.connecter("ana@exemple.ca", "mauvais") is None


def test_lire_sa_propre_note(service):
    uid = service.inscrire("ana@exemple.ca", "Correct-Cheval-42")
    nid = service.ajouter_note(uid, "Acheter du café")
    assert service.lire_note(uid, nid) == "Acheter du café"


def test_jeton_stable_et_propre_a_chaque_utilisateur(service):
    assert service.jeton(1) == service.jeton(1)
    assert service.jeton(1) != service.jeton(2)


# ── Sécurité ───────────────────────────────────────────────────────────────
def test_securite_injection_sql_a_la_connexion(service):
    service.inscrire("ana@exemple.ca", "Correct-Cheval-42")
    assert service.connecter("ana@exemple.ca' --", "n'importe quoi") is None


def test_securite_apostrophe_dans_le_courriel(service):
    uid = service.inscrire("o'brien@exemple.ca", "Correct-Cheval-42")
    assert service.connecter("o'brien@exemple.ca", "Correct-Cheval-42") == uid


def test_securite_mots_de_passe_sales_et_lents(service):
    service.inscrire("a@exemple.ca", "meme-mot-de-passe")
    service.inscrire("b@exemple.ca", "meme-mot-de-passe")
    h1, h2 = (r[0] for r in service.bd.execute("select password from users order by id"))
    assert h1 != h2, "même mot de passe, même empreinte : il manque un sel"
    assert hashlib.md5(b"meme-mot-de-passe").hexdigest() not in (h1, h2), "MD5 n'est pas fait pour les mots de passe"


def test_connexion_apres_reouverture_de_la_base(tmp_path):
    chemin = str(tmp_path / "notes.db")
    premier_service = NotesService(chemin)
    uid = premier_service.inscrire("ana@exemple.ca", "Café-Secret-42")
    premier_service.bd.close()

    second_service = NotesService(chemin)
    try:
        assert second_service.connecter("ana@exemple.ca", "Café-Secret-42") == uid
        assert second_service.connecter("ana@exemple.ca", "mauvais") is None
    finally:
        second_service.bd.close()


@pytest.mark.parametrize("empreinte", ["invalide", "pbkdf2_sha256$abc$00$00"])
def test_empreinte_invalide_refuse_la_connexion(service, empreinte):
    uid = service.inscrire("ana@exemple.ca", "Secret-42")
    service.bd.execute("update users set password = ? where id = ?", (empreinte, uid))
    assert service.connecter("ana@exemple.ca", "Secret-42") is None


def test_securite_pas_d_acces_aux_notes_des_autres(service):
    ana = service.inscrire("ana@exemple.ca", "Correct-Cheval-42")
    bob = service.inscrire("bob@exemple.ca", "Batterie-Agrafe-7")
    nid = service.ajouter_note(ana, "Mon NIP : 1234")
    assert service.lire_note(bob, nid) is None


def test_securite_aucun_secret_dans_le_code():
    source = Path(__file__).with_name("notes_service.py").read_text(encoding="utf-8")
    assert not re.search(r"SECRET\w*\s*=\s*['\"]", source), "secret en dur : lisez-le dans os.environ"
