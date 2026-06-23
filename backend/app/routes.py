"""Endpoints API."""
import sqlite3
from collections import defaultdict
from statistics import median

from fastapi import APIRouter, Depends, HTTPException, Query

from .db import get_db
from .models import CommuneDetail, CommuneListItem, CompareResponse, Indicateur

router = APIRouter()

TYPES_BIEN = ("Appartement", "Maison")
FENETRE_GLISSANTE = 3
MAX_CODES_COMPARE = 5


def _median_or_none(values: list[float]) -> float | None:
    return round(median(values), 0) if values else None


def _fetch_detail(conn: sqlite3.Connection, code: str) -> CommuneDetail:
    row = conn.execute(
        "SELECT code_commune, nom_commune, nb_parcelles, surface_cadastrale_m2 "
        "FROM commune WHERE code_commune = ?",
        (code,),
    ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail=f"commune inconnue : {code}")

    indicateurs = conn.execute(
        "SELECT annee, type_bien, nb_ventes, prix_median, prix_m2_median, "
        "surface_mediane, prix_m2_p25, prix_m2_p75 "
        "FROM indicateur WHERE code_commune = ? ORDER BY annee, type_bien",
        (code,),
    ).fetchall()
    return CommuneDetail(
        code_commune=row["code_commune"],
        nom_commune=row["nom_commune"],
        nb_parcelles=row["nb_parcelles"],
        surface_cadastrale_m2=row["surface_cadastrale_m2"],
        indicateurs=[Indicateur(**dict(r)) for r in indicateurs],
    )


@router.get("/communes", response_model=list[CommuneListItem])
def list_communes(conn: sqlite3.Connection = Depends(get_db)):
    """Liste des communes + €/m² du dernier millesime et lisse sur 3 ans, par type."""
    annee_ref_row = conn.execute("SELECT MAX(annee) AS a FROM indicateur").fetchone()
    annee_ref = annee_ref_row["a"] if annee_ref_row else None
    if annee_ref is None:
        return []

    communes = conn.execute(
        "SELECT code_commune, nom_commune FROM commune ORDER BY nom_commune"
    ).fetchall()

    latest = conn.execute(
        "SELECT code_commune, type_bien, prix_m2_median, nb_ventes "
        "FROM indicateur WHERE annee = ?",
        (annee_ref,),
    ).fetchall()
    latest_by_code: dict[str, dict[str, sqlite3.Row]] = defaultdict(dict)
    for r in latest:
        latest_by_code[r["code_commune"]][r["type_bien"]] = r

    annee_min = annee_ref - (FENETRE_GLISSANTE - 1)
    raw = conn.execute(
        "SELECT code_commune, type_bien, prix_m2 FROM vente "
        "WHERE annee BETWEEN ? AND ?",
        (annee_min, annee_ref),
    ).fetchall()
    prix_3ans: dict[tuple[str, str], list[float]] = defaultdict(list)
    for r in raw:
        prix_3ans[(r["code_commune"], r["type_bien"])].append(r["prix_m2"])

    out: list[CommuneListItem] = []
    for c in communes:
        code = c["code_commune"]
        per_type: dict[str, dict] = {}
        for t in TYPES_BIEN:
            latest_row = latest_by_code.get(code, {}).get(t)
            values_3ans = prix_3ans.get((code, t), [])
            per_type[t] = {
                "prix_m2_median": latest_row["prix_m2_median"] if latest_row else None,
                "nb_ventes": latest_row["nb_ventes"] if latest_row else None,
                "prix_m2_3ans": _median_or_none(values_3ans),
                "nb_ventes_3ans": len(values_3ans) if values_3ans else None,
            }
        out.append(CommuneListItem(
            code_commune=code,
            nom_commune=c["nom_commune"],
            annee_reference=annee_ref,
            prix_m2_median_appartement=per_type["Appartement"]["prix_m2_median"],
            prix_m2_median_maison=per_type["Maison"]["prix_m2_median"],
            nb_ventes_appartement=per_type["Appartement"]["nb_ventes"],
            nb_ventes_maison=per_type["Maison"]["nb_ventes"],
            prix_m2_3ans_appartement=per_type["Appartement"]["prix_m2_3ans"],
            prix_m2_3ans_maison=per_type["Maison"]["prix_m2_3ans"],
            nb_ventes_3ans_appartement=per_type["Appartement"]["nb_ventes_3ans"],
            nb_ventes_3ans_maison=per_type["Maison"]["nb_ventes_3ans"],
        ))
    return out


@router.get("/communes/{code}", response_model=CommuneDetail)
def commune_detail(code: str, conn: sqlite3.Connection = Depends(get_db)):
    """Tous les indicateurs (annees x types) d'une commune."""
    return _fetch_detail(conn, code)


@router.get("/compare", response_model=CompareResponse)
def compare(
    codes: str = Query(..., description="codes INSEE separes par des virgules"),
    conn: sqlite3.Connection = Depends(get_db),
):
    """Payload comparatif pour 2-3 communes."""
    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    if not code_list:
        raise HTTPException(status_code=400, detail="au moins un code requis")
    if len(code_list) > MAX_CODES_COMPARE:
        raise HTTPException(
            status_code=400,
            detail=f"max {MAX_CODES_COMPARE} codes, recu {len(code_list)}",
        )
    return CompareResponse(communes=[_fetch_detail(conn, c) for c in code_list])
