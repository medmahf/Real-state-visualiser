"""Schemas Pydantic de reponse."""
from pydantic import BaseModel


class CommuneListItem(BaseModel):
    code_commune: str
    nom_commune: str
    annee_reference: int | None
    prix_m2_median_appartement: float | None
    prix_m2_median_maison: float | None
    nb_ventes_appartement: int | None
    nb_ventes_maison: int | None
    prix_m2_3ans_appartement: float | None
    prix_m2_3ans_maison: float | None
    nb_ventes_3ans_appartement: int | None
    nb_ventes_3ans_maison: int | None


class Indicateur(BaseModel):
    annee: int
    type_bien: str
    nb_ventes: int
    prix_median: float | None
    prix_m2_median: float | None
    surface_mediane: float | None
    prix_m2_p25: float | None
    prix_m2_p75: float | None


class CommuneDetail(BaseModel):
    code_commune: str
    nom_commune: str
    nb_parcelles: int | None
    surface_cadastrale_m2: int | None
    indicateurs: list[Indicateur]


class CompareResponse(BaseModel):
    communes: list[CommuneDetail]
