# Outbound Call Agent

KI-gestuetzter Outbound Call Agent mit **Twilio** und **Claude AI (Anthropic)**.

Der Agent kann automatisiert ausgehende Anrufe taetigen und intelligente Gespraeche fuehren – komplett auf Deutsch.

## Architektur

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  REST API    │────▶│   Twilio     │────▶│  Telefon     │
│  (FastAPI)   │◀────│   Voice API  │◀────│  (Empfaenger)│
└──────┬───────┘     └──────────────┘     └──────────────┘
       │
       ▼
┌──────────────┐
│  Claude AI   │
│  (Anthropic) │
└──────────────┘
```

## Voraussetzungen

- Python 3.11+
- [Twilio-Account](https://www.twilio.com/) mit Telefonnummer
- [Anthropic API Key](https://console.anthropic.com/)
- Oeffentlich erreichbare URL (z.B. via ngrok fuer Entwicklung)

## Installation

```bash
# Repository klonen
git clone <repo-url>
cd neu

# Virtuelle Umgebung erstellen
python -m venv .venv
source .venv/bin/activate

# Abhaengigkeiten installieren
pip install -r requirements.txt

# Umgebungsvariablen konfigurieren
cp .env.example .env
# .env mit eigenen Werten befuellen
```

## Konfiguration

Bearbeite die `.env`-Datei mit deinen Zugangsdaten:

| Variable | Beschreibung |
|---|---|
| `TWILIO_ACCOUNT_SID` | Twilio Account SID |
| `TWILIO_AUTH_TOKEN` | Twilio Auth Token |
| `TWILIO_PHONE_NUMBER` | Deine Twilio-Telefonnummer |
| `ANTHROPIC_API_KEY` | Anthropic API Key |
| `BASE_URL` | Oeffentliche URL des Servers |
| `AGENT_LANGUAGE` | Sprache des Agenten (Standard: `de`) |
| `AGENT_SYSTEM_PROMPT` | System-Prompt fuer die KI |

## Starten

```bash
python run.py
```

Fuer die Entwicklung mit ngrok:

```bash
# In einem separaten Terminal
ngrok http 8000

# BASE_URL in .env auf die ngrok-URL setzen
```

## API-Endpunkte

### Anruf starten

```bash
curl -X POST http://localhost:8000/calls/outbound \
  -H "Content-Type: application/json" \
  -d '{
    "to": "+49123456789",
    "greeting": "Hallo, ich rufe wegen Ihres Termins an.",
    "context": "Terminbestaetigung fuer Dr. Mueller am 15. Maerz um 10 Uhr"
  }'
```

### Anruf-Status abfragen

```bash
curl http://localhost:8000/calls/status/{call_sid}
```

### Anruf beenden

```bash
curl -X POST http://localhost:8000/calls/end/{call_sid}
```

### Health Check

```bash
curl http://localhost:8000/health
```

## Ablauf eines Anrufs

1. **POST /calls/outbound** – Anruf wird ueber Twilio gestartet
2. Empfaenger nimmt ab → Twilio ruft **POST /webhook/outbound** auf
3. Agent begruesst den Empfaenger und wartet auf Spracheingabe
4. Spracheingabe → Twilio ruft **POST /webhook/respond** auf
5. Claude AI generiert eine Antwort → wird vorgelesen
6. Schleife wiederholt sich bis "Tschuess" oder Timeout
7. **POST /webhook/status** – Statusupdates werden geloggt

## Projektstruktur

```
neu/
├── app/
│   ├── __init__.py
│   ├── config.py            # Konfiguration (Pydantic Settings)
│   ├── main.py              # FastAPI App
│   ├── models/
│   │   ├── __init__.py
│   │   └── call.py          # Datenmodelle
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── calls.py         # REST API fuer Anrufe
│   │   └── webhooks.py      # Twilio Webhooks
│   └── services/
│       ├── __init__.py
│       ├── ai_service.py    # Claude AI Integration
│       └── call_service.py  # Twilio Call Management
├── .env.example
├── .gitignore
├── requirements.txt
├── run.py                   # Einstiegspunkt
└── README.md
```
