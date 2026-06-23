# Comparateur de territoires — Val-de-Marne (94)

Application full-stack pour comparer les communes du 94 sur des indicateurs immobiliers
(DVF), avec carte choroplèthe et comparaison côte à côte.

**Stack :** FastAPI · React (Vite) · SQLite · Leaflet · Recharts · Docker (mono-conteneur).

## Données
- DVF géolocalisé : `https://files.data.gouv.fr/geo-dvf/latest/csv/{annee}/departements/94.csv.gz`
- Cadastre parcellaire du 94 (dissous en contours de communes) → `backend/data/communes_94.geojson`

## Lancer en local

### 1. Données (une fois)
```bash
cd etl
pip install -r requirements.txt
python download.py          # télécharge les csv.gz du 94
python build_db.py          # nettoie, agrège, écrit backend/data/data.db
```

### 2. Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload   # http://localhost:8000  (docs: /docs)
```

### 3. Frontend (dev)
```bash
cd frontend
npm install
npm run dev                  # http://localhost:5173 (proxy /api -> 8000)
```

## Tout-en-un (conteneur)
```bash
docker build -t compa94 .
docker run -p 8000:8000 compa94   # http://localhost:8000
```

## Méthode de nettoyage DVF (résumé)
Ventes uniquement, déduplication par mutation, mutations mono-bien (Appartement/Maison)
avec surface bâtie > 0, €/m² borné contre les aberrations, puis agrégats
commune × année × type (médiane, p25/p75).
