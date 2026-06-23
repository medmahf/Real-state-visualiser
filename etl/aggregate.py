"""Agrégats par commune x année x type de bien : la matière première de la comparaison.

On stocke TOUT (y compris les communes à faible volume) ; le filtrage par fiabilité
(seuil de nb_ventes, médiane glissante) se décide côté API/front, pas ici.
"""
import pandas as pd


def aggregate(ventes: pd.DataFrame) -> pd.DataFrame:
    g = ventes.groupby(["code_commune", "nom_commune", "annee", "type_local"])
    out = g.agg(
        nb_ventes=("prix_m2", "size"),
        prix_median=("valeur_fonciere", "median"),
        prix_m2_median=("prix_m2", "median"),
        surface_mediane=("surface_reelle_bati", "median"),
        prix_m2_p25=("prix_m2", lambda s: s.quantile(0.25)),
        prix_m2_p75=("prix_m2", lambda s: s.quantile(0.75)),
    ).reset_index()
    return out.round(0)
