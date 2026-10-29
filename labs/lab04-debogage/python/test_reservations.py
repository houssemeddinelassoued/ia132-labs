"""Les 4 premiers tests passent. Les 5 suivants reproduisent les tickets INC-101 à INC-105."""

from datetime import datetime

import pytest

from reservations import Reservation, cout, duree_heures, paginer, peut_reserver, taux_occupation


def resa(salle, debut, fin, tarif=20.0):
    return Reservation(salle, datetime.fromisoformat(debut), datetime.fromisoformat(fin), tarif)


A = resa("A-101", "2026-11-02 09:00", "2026-11-02 10:00")
B = resa("A-101", "2026-11-02 13:00", "2026-11-02 16:00")
C = resa("B-204", "2026-11-02 09:00", "2026-11-02 11:30")


# ── Ce qui fonctionne ──────────────────────────────────────────────────────
def test_duree_simple():
    assert duree_heures(C) == 2.5


def test_conflit_detecte():
    assert not peut_reserver([A], resa("A-101", "2026-11-02 09:30", "2026-11-02 10:30"))


def test_cout_simple():
    assert cout(C) == 50.0


def test_taux_occupation_simple():
    assert taux_occupation([A, B, C], "A-101") == 0.4


# ── Les tickets du support ─────────────────────────────────────────────────
@pytest.mark.parametrize("reservations", [[], [A, B]])
def test_inc101_salle_sans_reservation(reservations):
    assert taux_occupation(reservations, "B-204") == 0


def test_inc102_pas_de_doublon_entre_deux_pages():
    items = list(range(25))
    assert paginer(items, 1) == list(range(10))
    assert paginer(items, 2) == list(range(10, 20))
    assert paginer(items, 3) == list(range(20, 25))


def test_inc103_reservations_bout_a_bout_autorisees():
    suivante = resa("A-101", "2026-11-02 10:00", "2026-11-02 11:00")
    assert peut_reserver([A], suivante)
    assert peut_reserver([suivante], A)


@pytest.mark.parametrize("tarif, attendu", [(31.15, 46.73), (31.11, 46.67), (31.14, 46.71)])
def test_inc104_arrondi_au_cent_superieur(tarif, attendu):
    r = resa("A-101", "2026-11-02 09:00", "2026-11-02 10:30", tarif=tarif)
    assert cout(r) == attendu


def test_inc105_reservation_sur_deux_jours():
    r = resa("C-310", "2026-11-06 09:00", "2026-11-07 11:00")
    assert duree_heures(r) == 26
    assert cout(r) == 520.0
