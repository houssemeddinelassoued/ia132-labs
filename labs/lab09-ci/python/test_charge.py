"""Tests du scénario de charge : la part de créations est respectée (serveur réel, port libre)."""

import threading

import pytest

from api import creer_serveur
from charge import appel


@pytest.fixture
def serveur():
    srv = creer_serveur()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    yield f"http://127.0.0.1:{srv.server_address[1]}"
    srv.shutdown()


def test_pic_creations_seulement(serveur):
    codes: list[str] = []
    resultats = [appel(serveur, codes, part_creations=1.0) for _ in range(30)]
    assert all(ok for _, ok in resultats)
    assert len(codes) == 30  # chaque appel a créé un lien, aucune lecture


def test_sans_creation_apres_le_premier_lien(serveur):
    codes: list[str] = []
    appel(serveur, codes, part_creations=0.0)  # le premier appel crée toujours (aucun code connu)
    assert len(codes) == 1
    resultats = [appel(serveur, codes, part_creations=0.0) for _ in range(30)]
    assert all(ok for _, ok in resultats)
    assert len(codes) == 1  # uniquement des lectures ensuite
