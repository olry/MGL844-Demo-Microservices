# Tests d'intégration : on lance des requêtes HTTP réelles sur le gateway
# qui tourne dans Docker. Pour que ces tests passent, il faut d'abord
# démarrer la stack avec : docker compose up -d --build
#
# Ces tests vérifient que les services se parlent bien entre eux,
# que le gateway transfère correctement les requêtes et que NATS
# transmet les événements d'un service à l'autre.

import time

import httpx

# URL publique du gateway (port mappé sur localhost dans docker-compose).
BASE = "http://localhost:8000"


# Le gateway doit transférer GET /hello/health vers hello-service
# et renvoyer la réponse avec le code 200 et le nom du service.
def test_gateway_proxies_hello_health() -> None:
    r = httpx.get(f"{BASE}/hello/health", timeout=10.0)
    assert r.status_code == 200
    assert r.json() == {"status": "ok", "name": "hello-service"}


# Si on appelle un service inconnu, le gateway doit renvoyer 404.
def test_gateway_unknown_service_returns_404() -> None:
    r = httpx.get(f"{BASE}/nope/health", timeout=10.0)
    assert r.status_code == 404


# Test du parcours "créer un utilisateur, puis le récupérer" via le gateway.
# 1. POST /hello/users : crée un utilisateur "Acceptance".
# 2. GET /hello/users/{id} : récupère l'utilisateur avec sa salutation.
def test_gateway_user_create_then_greet() -> None:
    r = httpx.post(f"{BASE}/hello/users", json={"name": "Acceptance"}, timeout=10.0)
    assert r.status_code == 201
    uid = r.json()["id"]

    r = httpx.get(f"{BASE}/hello/users/{uid}", timeout=10.0)
    assert r.status_code == 200
    assert r.json()["message"] == "Bonjour Acceptance !"


# Test du flot événementiel : un POST sur hello-service doit déclencher
# une notification dans notification-service via NATS.
# 1. On crée un utilisateur "Eventbus" dans hello-service.
# 2. hello-service publie l'événement "user.created" sur NATS.
# 3. notification-service reçoit le message et stocke une notification.
# 4. On vérifie côté notification-service que la notification est bien arrivée.
# Comme NATS est asynchrone, on attend jusqu'à 5 secondes que le message arrive.
def test_user_created_event_lands_in_notifications() -> None:
    r = httpx.post(f"{BASE}/hello/users", json={"name": "Eventbus"}, timeout=10.0)
    assert r.status_code == 201
    uid = r.json()["id"]

    expected = f"Bonjour Eventbus ! (id={uid})"
    deadline = time.time() + 5.0
    while time.time() < deadline:
        r = httpx.get(f"{BASE}/notify/notifications", timeout=10.0)
        assert r.status_code == 200
        if any(n["message"] == expected for n in r.json()):
            return
        time.sleep(0.1)
    raise AssertionError(f"notification {expected!r} never arrived")
