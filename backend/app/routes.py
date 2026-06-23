"""Endpoints API."""
from fastapi import APIRouter, Query

from .db import get_conn

router = APIRouter()


@router.get("/communes")
def list_communes():
    """Liste des communes + prix_m2_median du dernier millesime (tous types) pour la carte."""
    # TODO : SELECT code_commune, nom_commune, prix_m2_median au max(annee).
    raise NotImplementedError


@router.get("/communes/{code}")
def commune_detail(code: str):
    """Tous les indicateurs (annees x types) d'une commune."""
    # TODO : SELECT * FROM indicateur WHERE code_commune = ? ORDER BY annee, type_bien.
    raise NotImplementedError


@router.get("/compare")
def compare(codes: str = Query(..., description="codes INSEE separes par des virgules")):
    """Payload comparatif pour 2-3 communes."""
    code_list = [c.strip() for c in codes.split(",") if c.strip()]
    # TODO : series temporelles €/m2 + agregats par type + derniers chiffres, par commune.
    raise NotImplementedError
