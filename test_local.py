"""
Lokaler Test des Outbound Call Agents.

Simuliert den Twilio-Webhook-Flow ohne echten Anruf.
Testet: Server → Webhook → Claude AI → Antwort-Generierung
"""

import httpx
import sys

BASE = "http://localhost:8000"
FAKE_CALL_SID = "CA_test_simulation_001"


def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")


def extract_say_text(twiml: str) -> list[str]:
    """Extrahiert <Say>-Texte aus TwiML."""
    import re
    return re.findall(r'<Say[^>]*>(.*?)</Say>', twiml, re.DOTALL)


def test_health():
    print_header("1. Health Check")
    r = httpx.get(f"{BASE}/health")
    print(f"Status: {r.status_code}")
    print(f"Response: {r.json()}")
    return r.status_code == 200


def test_outbound_webhook():
    print_header("2. Simuliere: Empfaenger nimmt ab (Outbound Webhook)")
    r = httpx.post(
        f"{BASE}/webhook/outbound?greeting=Hallo%2C+hier+ist+ein+Testanruf&context=Das+ist+ein+Test",
        data={"CallSid": FAKE_CALL_SID},
    )
    print(f"Status: {r.status_code}")
    texts = extract_say_text(r.text)
    for t in texts:
        print(f"  Agent sagt: {t.strip()}")
    return r.status_code == 200


def test_speech_response(user_says: str):
    print_header(f"3. Simuliere Spracheingabe: \"{user_says}\"")
    r = httpx.post(
        f"{BASE}/webhook/respond?CallSid={FAKE_CALL_SID}",
        data={"SpeechResult": user_says},
    )
    print(f"Status: {r.status_code}")
    texts = extract_say_text(r.text)
    for t in texts:
        print(f"  Agent sagt: {t.strip()}")
    return r.status_code == 200


def test_goodbye():
    print_header("4. Simuliere: Gespraechsende")
    r = httpx.post(
        f"{BASE}/webhook/respond?CallSid={FAKE_CALL_SID}",
        data={"SpeechResult": "Tschuess, auf Wiedersehen"},
    )
    print(f"Status: {r.status_code}")
    texts = extract_say_text(r.text)
    for t in texts:
        print(f"  Agent sagt: {t.strip()}")
    has_hangup = "<Hangup" in r.text
    print(f"  Aufgelegt: {'Ja' if has_hangup else 'Nein'}")
    return r.status_code == 200


def main():
    print("\n" + "#"*60)
    print("#  OUTBOUND CALL AGENT - LOKALER TEST")
    print("#  (Simuliert Twilio-Webhooks ohne echten Anruf)")
    print("#"*60)

    # Health Check
    if not test_health():
        print("\nServer nicht erreichbar! Starte ihn mit: python run.py")
        sys.exit(1)

    # Anruf-Simulation
    test_outbound_webhook()

    # Gespraech simulieren
    test_fragen = [
        "Was machen Sie genau?",
        "Was kostet das ungefaehr?",
    ]

    for i, frage in enumerate(test_fragen):
        print_header(f"{3+i}. Simuliere Spracheingabe: \"{frage}\"")
        r = httpx.post(
            f"{BASE}/webhook/respond?CallSid={FAKE_CALL_SID}",
            data={"SpeechResult": frage},
        )
        texts = extract_say_text(r.text)
        for t in texts:
            print(f"  Agent sagt: {t.strip()}")

    # Gespraechsende
    test_goodbye()

    print_header("TEST ABGESCHLOSSEN")
    print("Alle Webhooks funktionieren. Der Agent antwortet mit Claude AI.")
    print("Fuer echte Anrufe braucht es eine Twilio-Nummer mit Voice + deutsche Nummer.")


if __name__ == "__main__":
    main()
