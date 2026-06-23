"""Schemas Pydantic de reponse."""
from pydantic import BaseModel


class CommuneListItem(BaseModel):
    code_commune: str
    nom_commune: str
    prix_m2_median: float | None  # dernier millesime, tous types -> couleur carte


class Indicateur(BaseModel):
    annee: int
    type_bien: str
    nb_ventes: int
    prix_median: float
    prix_m2_median: float
    surface_mediane: float
    prix_m2_p25: float
    prix_m2_p75: float


class CommuneDetail(BaseModel):
    code_commune: str
    nom_commune: str
    indicateurs: list[Indicateur]
