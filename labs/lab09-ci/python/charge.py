"""Test de charge simple : N requêtes en parallèle sur l'API, puis latences et taux d'erreur.

    python charge.py                        # 2 000 requêtes, 20 utilisateurs simultanés
    python charge.py 5000 50                # 5 000 requêtes, 50 utilisateurs
    python charge.py 5000 100 1.0           # scénario « pic » : 100 % de créations

Scénario par défaut : 1 création de lien pour 4 visites (80 % de lectures).
Le 3e argument règle la part de créations (0 à 1). L'API démarre dans le processus.
Objectif de service (à vérifier) : p95 < 50 ms et moins de 1 % d'erreurs.
"""

import json
import random
import statistics
import sys
import threading
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor

from api import creer_serveur

P95_MAX_MS = 50
ERREURS_MAX = 0.01


class SansRedirection(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *args, **kwargs):
        return None


ouvrir = urllib.request.build_opener(SansRedirection).open


def appel(base: str, codes: list[str], part_creations: float = 0.2) -> tuple[float, bool]:
    t0 = time.perf_counter()
    try:
        if not codes or random.random() < part_creations:  # noqa: S311 (simulation, pas de cryptographie)
            corps = json.dumps({"url": f"https://exemple.ca/{random.randrange(10**6)}"}).encode()  # noqa: S311
            req = urllib.request.Request(base + "/liens", data=corps, method="POST")
            with ouvrir(req, timeout=5) as r:
                codes.append(json.loads(r.read())["code"])
        else:
            try:
                ouvrir(base + "/l/" + random.choice(codes), timeout=5)  # noqa: S311
            except urllib.error.HTTPError as e:
                if e.code != 302:
                    raise
        ok = True
    except (urllib.error.URLError, OSError, KeyError, ValueError):
        ok = False
    return (time.perf_counter() - t0) * 1000, ok


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    total = int(sys.argv[1]) if len(sys.argv) > 1 else 2_000
    utilisateurs = int(sys.argv[2]) if len(sys.argv) > 2 else 20
    part_creations = float(sys.argv[3]) if len(sys.argv) > 3 else 0.2
    if not 0 <= part_creations <= 1:
        raise ValueError(f"part de créations hors de [0, 1] : {part_creations}")
    srv = creer_serveur()
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{srv.server_address[1]}"
    codes: list[str] = []

    t0 = time.perf_counter()
    with ThreadPoolExecutor(utilisateurs) as pool:
        resultats = list(pool.map(lambda _: appel(base, codes, part_creations), range(total)))
    duree = time.perf_counter() - t0
    srv.shutdown()

    latences = sorted(ms for ms, _ in resultats)
    erreurs = sum(not ok for _, ok in resultats) / total
    p50, p95, p99 = (latences[int(len(latences) * q) - 1] for q in (0.50, 0.95, 0.99))
    print(f"{total} requêtes · {utilisateurs} utilisateurs · {duree:.1f} s · {total / duree:.0f} req/s")
    print(f"latence  p50 {p50:.1f} ms · p95 {p95:.1f} ms · p99 {p99:.1f} ms · moyenne {statistics.mean(latences):.1f} ms")
    print(f"erreurs  {erreurs:.2%}")
    ok = p95 < P95_MAX_MS and erreurs < ERREURS_MAX
    print("Objectif de service : " + ("respecté" if ok else f"NON respecté (p95 < {P95_MAX_MS} ms, erreurs < 1 %)"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
