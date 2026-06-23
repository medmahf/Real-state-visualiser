"""Nettoyage DVF -> 1 ligne = 1 vente mono-bien exploitable au €/m².

Pipeline validé sur les 5 millésimes du 94 (2021->2025) :
    250 810 lignes brutes  ->  18 768 ventes exploitables.

L'idée : une "mutation" (vente) est éclatée en plusieurs lignes (lots, dépendances,
parcelles) qui répètent toutes le prix TOTAL. On ne garde que les ventes d'un seul
logement, pour lesquelles valeur_fonciere / surface a un sens.
"""
import glob
import sys

import pandas as pd

USECOLS = [
    "id_mutation", "date_mutation", "nature_mutation", "valeur_fonciere",
    "code_commune", "nom_commune", "type_local", "surface_reelle_bati",
]
TYPES_LOGEMENT = ["Appartement", "Maison"]
PRIX_M2_MIN, PRIX_M2_MAX = 800, 25000  # bornes anti-aberrations (Ile-de-France)


def load_raw(pattern: str = "data/raw/dvf_94_*.csv") -> pd.DataFrame:
    """Charge et concatène les fichiers DVF géolocalisés (1 par millésime)."""
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(f"Aucun fichier DVF pour le motif {pattern!r}")
    frames = [pd.read_csv(f, usecols=USECOLS, low_memory=False) for f in files]
    return pd.concat(frames, ignore_index=True)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    """Renvoie les ventes mono-bien (Appartement/Maison) avec un €/m² fiable."""
    df = df.copy()
    df["annee"] = pd.to_datetime(df["date_mutation"]).dt.year

    # 1. Ventes uniquement (exclut VEFA, échanges, expropriations, adjudications...).
    ventes = df[df["nature_mutation"] == "Vente"]

    # 2. On ne raisonne que sur les locaux bâtis (type_local renseigné).
    batis = ventes[ventes["type_local"].notna()]

    # 3. Mono-bien STRICT : la mutation ne contient qu'UN seul local bâti.
    #    (sinon valeur_fonciere mélange plusieurs biens -> €/m² faussé).
    nb_locaux = batis.groupby("id_mutation")["type_local"].transform("size")
    mono = batis[nb_locaux == 1]

    # 4. Ce local doit être un logement (Appartement ou Maison).
    mono = mono[mono["type_local"].isin(TYPES_LOGEMENT)]

    # 5. Surface bâtie strictement positive.
    mono = mono[mono["surface_reelle_bati"] > 0].copy()

    # 6. Prix au m2 + bornage des aberrations.
    mono["prix_m2"] = mono["valeur_fonciere"] / mono["surface_reelle_bati"]
    mono = mono[mono["prix_m2"].between(PRIX_M2_MIN, PRIX_M2_MAX)]

    return mono[[
        "id_mutation", "annee", "code_commune", "nom_commune",
        "type_local", "valeur_fonciere", "surface_reelle_bati", "prix_m2",
    ]].reset_index(drop=True)


if __name__ == "__main__":
    pattern = sys.argv[1] if len(sys.argv) > 1 else "data/raw/dvf_94_*.csv"
    raw = load_raw(pattern)
    out = clean(raw)
    print(f"{len(raw):>7} lignes brutes  ->  {len(out):>6} ventes exploitables")
    print(out.head())
