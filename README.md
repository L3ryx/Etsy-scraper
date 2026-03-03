# Etsy Shop Analyzer

## Deploiement sur Render

1. Creez un compte sur render.com
2. Creez un "New Web Service"
3. Connectez votre repo GitHub ou uploadez les fichiers
4. Choisissez Docker comme environnement
5. Ajoutez la variable d'environnement SCRAPERAPI_KEY avec votre cle
6. Cliquez sur Deploy

## Deploiement manuel

```bash
pip install -r render_requirements.txt
streamlit run app.py --server.port 5000 --server.address 0.0.0.0 --server.headless true
```

## Variables d'environnement

- SCRAPERAPI_KEY : votre cle ScraperAPI (scraperapi.com)
