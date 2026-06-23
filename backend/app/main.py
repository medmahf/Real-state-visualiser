"""Point d'entree FastAPI : API + GeoJSON + front statique, dans un seul service."""
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .routes import router

app = FastAPI(title="Comparateur de territoires 94")
app.include_router(router, prefix="/api")

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
STATIC_DIR = Path(__file__).resolve().parent / "static"


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/communes_94.geojson")
def communes_geojson():
    return FileResponse(DATA_DIR / "communes_94.geojson", media_type="application/geo+json")


# Front monte en dernier (sinon il masque /api). Present seulement apres `vite build`.
if STATIC_DIR.exists():
    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="static")
