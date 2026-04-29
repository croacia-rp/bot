# CENTRAL CROÁCIA - FASE 6 REAL COMPLETA

Este pacote usa seu bot real enviado e o site completo Fase 5.

## Inclui

- Bot real em `bot/main.py`
- Site completo em `site/app.py`
- Mapa tático funcional
- Embed Studio / Gestão / Admin conforme a base Fase 5
- `dados.json` único na raiz
- Logo da Croácia
- Pronto para GitHub/Railway

## Rodar local

```bash
pip install -r requirements.txt
copy .env.example .env
python run.py
```

Abra:

```text
http://127.0.0.1:5000
```

## Railway

Start command:

```bash
python run.py
```

Variáveis:

```text
DISCORD_TOKEN
DISCORD_CLIENT_ID
DISCORD_CLIENT_SECRET
DISCORD_REDIRECT_URI=https://SEU-DOMINIO.up.railway.app/callback
FLASK_SECRET_KEY
ADMIN_PASSWORD
GUILD_ID=1442149654971027488
```

## Dados unificados

Bot e site usam o mesmo arquivo:

```text
dados.json
```

Controlado por:

```text
ARQUIVO_DADOS
```
