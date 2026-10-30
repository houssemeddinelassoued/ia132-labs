"""Service de notes personnelles — pull request n° 42, « prêt pour la prod ».

Votre mission : la REVUE de cette PR, avec l'aide de l'IA (voir README).
"""

import hashlib
import hmac
import secrets
import sqlite3

SECRET_KEY = "s3cr3t-prod-2026"
ITERATIONS_MOT_DE_PASSE = 600_000

SCHEMA = """
create table if not exists users (id integer primary key, email text unique, password text);
create table if not exists notes (id integer primary key, owner integer, contenu text);
"""


def _empreinte_mot_de_passe(mot_de_passe: str) -> str:
    """Calcule une empreinte PBKDF2 avec un nouveau sel aléatoire."""
    sel = secrets.token_bytes(16)
    empreinte = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode(), sel, ITERATIONS_MOT_DE_PASSE
    )
    return (
        f"pbkdf2_sha256${ITERATIONS_MOT_DE_PASSE}"
        f"${sel.hex()}${empreinte.hex()}"
    )


def _verifier_mot_de_passe(mot_de_passe: str, valeur_stockee: str) -> bool:
    """Vérifie une empreinte salée sans comparaison dépendant de son contenu."""
    try:
        algorithme, iterations, sel, empreinte = valeur_stockee.split("$")
        if algorithme != "pbkdf2_sha256" or int(iterations) != ITERATIONS_MOT_DE_PASSE:
            return False
        sel_decode = bytes.fromhex(sel)
        empreinte_attendue = bytes.fromhex(empreinte)
        if len(sel_decode) != 16 or len(empreinte_attendue) != 32:
            return False
    except (ValueError, AttributeError):
        return False
    empreinte_calculee = hashlib.pbkdf2_hmac(
        "sha256", mot_de_passe.encode(), sel_decode, int(iterations)
    )
    return hmac.compare_digest(empreinte_calculee, empreinte_attendue)


class NotesService:
    def __init__(self, chemin_bd: str = ":memory:"):
        self.bd = sqlite3.connect(chemin_bd)
        self.bd.executescript(SCHEMA)

    def inscrire(self, email, mot_de_passe):
        h = _empreinte_mot_de_passe(mot_de_passe)
        cur = self.bd.execute(
            "insert into users (email, password) values (?, ?)", (email, h)
        )
        self.bd.commit()
        return cur.lastrowid

    def connecter(self, email, mot_de_passe):
        try:
            row = self.bd.execute(
                "select id, password from users where email = ?", (email,)
            ).fetchone()
        except Exception:
            return None
        if row is None or not _verifier_mot_de_passe(mot_de_passe, row[1]):
            return None
        return row[0]

    def ajouter_note(self, user_id, contenu):
        cur = self.bd.execute("insert into notes (owner, contenu) values (?, ?)", (user_id, contenu))
        self.bd.commit()
        return cur.lastrowid

    def lire_note(self, user_id, note_id):
        row = self.bd.execute(
            "select contenu from notes where id = ? and owner = ?", (note_id, user_id)
        ).fetchone()
        return row[0] if row else None

    def jeton(self, user_id):
        return hashlib.sha256(f"{user_id}:{SECRET_KEY}".encode()).hexdigest()
