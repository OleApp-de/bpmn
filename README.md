# ProMoAI - Enterprise Deployment

Process Modeling with AI für interne Unternehmensnutzung auf Coolify Server.

## Schnellstart

1. **Repository klonen:**
```bash
git clone https://github.com/OleApp-de/bpmn.git
cd bpmn
```

2. **Umgebungsvariablen konfigurieren:**
```bash
cp .env.example .env
# API Keys in .env eintragen
```

3. **Lokal testen:**
```bash
docker-compose up --build
```

4. **Zugriff:** http://localhost:8501

## Coolify Deployment

### 1. Repository in Coolify hinzufügen
- Neue Anwendung erstellen
- Repository: `https://github.com/OleApp-de/bpmn.git`
- Build Pack: Dockerfile
- Port: 8501

### 2. Umgebungsvariablen setzen
```
OPENAI_API_KEY=sk-...
AUTH_USERNAME=admin
AUTH_PASSWORD=ihr-sicheres-passwort
ENABLE_AUTH=true
```

### 3. Traefik Labels (für bpmn.tomorrowbird.ai)
```
traefik.enable=true
traefik.http.middlewares.gzip.compress=true
traefik.http.middlewares.redirect-to-https.redirectscheme.scheme=https
traefik.http.routers.http-0-promoai.entryPoints=http
traefik.http.routers.http-0-promoai.middlewares=redirect-to-https
traefik.http.routers.http-0-promoai.rule=Host(`bpmn.tomorrowbird.ai`) && PathPrefix(`/`)
traefik.http.routers.http-0-promoai.service=http-0-promoai
traefik.http.routers.https-0-promoai.entryPoints=https
traefik.http.routers.https-0-promoai.middlewares=gzip
traefik.http.routers.https-0-promoai.rule=Host(`bpmn.tomorrowbird.ai`) && PathPrefix(`/`)
traefik.http.routers.https-0-promoai.service=https-0-promoai
traefik.http.routers.https-0-promoai.tls.certresolver=letsencrypt
traefik.http.routers.https-0-promoai.tls=true
traefik.http.services.http-0-promoai.loadbalancer.server.port=8501
traefik.http.services.https-0-promoai.loadbalancer.server.port=8501
```

## Features

- ✅ Automatische API Key Verwaltung
- ✅ Einfache Authentifizierung 
- ✅ Multi-Provider Support (OpenAI, Anthropic, Google, Cohere)
- ✅ Coolify/Traefik optimiert
- ✅ WebSocket Support für Streamlit

## Technische Details

- **Framework:** Streamlit (Python Web Framework)
- **Container:** Multi-stage Docker Build
- **Reverse Proxy:** Traefik (über Coolify)
- **Domain:** bpmn.tomorrowbird.ai
- **Port:** 8501 (intern)

## Support

Bei Problemen bitte GitHub Issues erstellen oder Administrator kontaktieren.