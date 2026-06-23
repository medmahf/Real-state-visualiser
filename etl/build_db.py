"""Pipeline complet : raw DVF -> nettoyage -> agregats -> SQLite (backend/data/data.db)."""
import json
import sqlite3
from pathlib import Path

import pandas as pd

from aggregate import aggregate
from clean import clean, load_raw

DATA_DIR = Path(__file__).resolve().parent.parent / "backend" / "data"
DB = DATA_DIR / "data.db"
GEOJSON = DATA_DIR / "communes_94.geojson"

SCHEMA = """
CREATE TABLE commune (
  code_commune TEXT PRIMARY KEY,
  nom_commune TEXT,
  nb_parcelles INTEGER,
  surface_cadastrale_m2 INTEGER
);
CREATE TABLE indicateur (
  code_commune TEXT, annee INTEGER, type_bien TEXT,
  nb_ventes INTEGER, prix_median REAL, prix_m2_median REAL,
  surface_mediane REAL, prix_m2_p25 REAL, prix_m2_p75 REAL,
  PRIMARY KEY (code_commune, annee, type_bien)
);
"""


def load_cadastre_attrs(path: Path = GEOJSON) -> pd.DataFrame:
    """Extrait code_commune / nb_parcelles / surface_cadastrale_m2 du geojson dissous."""
    gj = json.loads(path.read_text(encoding="utf-8"))
    rows = [ft["properties"] for ft in gj["features"]]
    return pd.DataFrame(rows)[["code_commune", "nb_parcelles", "surface_cadastrale_m2"]]


def main():
    ind = aggregate(clean(load_raw())).rename(columns={"type_local": "type_bien"})
    cad = load_cadastre_attrs()

    # DVF lit code_commune en int (ex: 94001) ; le geojson le stocke en str ("94001").
    ind["code_commune"] = ind["code_commune"].astype(str).str.zfill(5)
    communes = ind[["code_commune", "nom_commune"]].drop_duplicates()
    communes = communes.merge(cad, on="code_commune", how="left")
    communes["nb_parcelles"] = communes["nb_parcelles"].astype("Int64")
    communes["surface_cadastrale_m2"] = communes["surface_cadastrale_m2"].astype("Int64")

    sans_cadastre = communes.loc[communes["nb_parcelles"].isna(), "code_commune"].tolist()
    if sans_cadastre:
        print(f"WARN: communes DVF sans cadastre : {sans_cadastre}")
    sans_ventes = sorted(set(cad["code_commune"]) - set(ind["code_commune"]))
    if sans_ventes:
        print(f"WARN: communes cadastre sans ventes DVF : {sans_ventes}")

    DB.parent.mkdir(parents=True, exist_ok=True)
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    con.executescript(SCHEMA)
    communes.to_sql("commune", con, if_exists="append", index=False)
    ind.drop(columns=["nom_commune"]).to_sql("indicateur", con, if_exists="append", index=False)
    con.commit()
    con.close()
    print(f"data.db ecrit : {len(communes)} communes, {len(ind)} lignes d'indicateurs")


if __name__ == "__main__":
    main()
