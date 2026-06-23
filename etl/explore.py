"""EDA / visualisations de contrôle sur la donnée DVF nettoyée.

Génère des PNG dans figures/ pour vérifier la donnée et alimenter la démo :
  - entonnoir de nettoyage          figures/01_entonnoir.png
  - comparaison des communes        figures/02_comparaison_communes.png
  - appartement vs maison           figures/03_appart_vs_maison.png
  - distribution (médiane/moyenne)  figures/04_distribution.png
  - tendance temporelle             figures/05_tendance.png
  - volume de ventes par année      figures/06_volume.png

Usage :
    python explore.py                       # lit data/raw/dvf_94_*.csv
    python explore.py "/chemin/dvf_94_*.csv"
"""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from aggregate import aggregate
from clean import PRIX_M2_MAX, PRIX_M2_MIN, TYPES_LOGEMENT, clean, load_raw

FIG = Path("figures")
ANNEE_REF = 2024     # dernier millésime "plein" (2024 = creux réel du marché)
MIN_VENTES = 20      # seuil de fiabilité d'une médiane communale
TEAL, CORAL, BLUE = "#1D9E75", "#D85A30", "#185FA5"


def funnel_counts(raw: pd.DataFrame) -> dict[str, int]:
    df = raw.copy()
    ventes = df[df["nature_mutation"] == "Vente"]
    batis = ventes[ventes["type_local"].notna()]
    nb = batis.groupby("id_mutation")["type_local"].transform("size")
    logement = batis[(nb == 1) & batis["type_local"].isin(TYPES_LOGEMENT)]
    surf = logement[logement["surface_reelle_bati"] > 0]
    pm2 = surf["valeur_fonciere"] / surf["surface_reelle_bati"]
    return {
        "Lignes brutes": len(df),
        "Lignes « Vente »": len(ventes),
        "Ventes distinctes": ventes["id_mutation"].nunique(),
        "Mono-bien App/Maison": len(logement),
        "Surface bâtie > 0": len(surf),
        "Après bornage €/m²": int(pm2.between(PRIX_M2_MIN, PRIX_M2_MAX).sum()),
    }


def plot_funnel(raw):
    c = funnel_counts(raw)
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(list(c)[::-1], list(c.values())[::-1], color=TEAL)
    for i, v in enumerate(list(c.values())[::-1]):
        ax.text(v, i, f"  {v:,}".replace(",", " "), va="center", fontsize=9)
    ax.set_title("Entonnoir de nettoyage DVF (94, 2021-2025)")
    ax.margins(x=0.18)
    fig.tight_layout(); fig.savefig(FIG / "01_entonnoir.png", dpi=120); plt.close(fig)


def plot_comparaison(ind):
    d = ind[(ind["type_local"] == "Appartement") & (ind["annee"] == ANNEE_REF)
            & (ind["nb_ventes"] >= MIN_VENTES)].sort_values("prix_m2_median")
    fig, ax = plt.subplots(figsize=(8, 0.35 * len(d) + 1.5))
    ax.barh(d["nom_commune"], d["prix_m2_median"], color=BLUE)
    for y, (m, n) in enumerate(zip(d["prix_m2_median"], d["nb_ventes"])):
        ax.text(m, y, f"  {m:,.0f} € (n={n:.0f})".replace(",", " "), va="center", fontsize=8)
    ax.set_title(f"Prix médian €/m² appartement par commune ({ANNEE_REF}, n≥{MIN_VENTES})")
    ax.margins(x=0.25)
    fig.tight_layout(); fig.savefig(FIG / "02_comparaison_communes.png", dpi=120); plt.close(fig)


def plot_app_vs_maison(ind):
    piv = (ind[ind["annee"] == ANNEE_REF]
           .pivot_table(index="nom_commune", columns="type_local", values="prix_m2_median")
           .dropna())
    piv = piv.sort_values("Appartement", ascending=False).head(8)
    x = range(len(piv))
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.bar([i - 0.2 for i in x], piv["Appartement"], 0.4, label="Appartement", color=TEAL)
    ax.bar([i + 0.2 for i in x], piv["Maison"], 0.4, label="Maison", color=CORAL)
    ax.set_xticks(list(x)); ax.set_xticklabels(piv.index, rotation=45, ha="right", fontsize=8)
    ax.set_ylabel("€/m² médian"); ax.legend()
    ax.set_title(f"Appartement vs maison ({ANNEE_REF}) : pourquoi séparer les types")
    fig.tight_layout(); fig.savefig(FIG / "03_appart_vs_maison.png", dpi=120); plt.close(fig)


def plot_distribution(ventes):
    s = ventes[(ventes["type_local"] == "Appartement") & (ventes["annee"] == ANNEE_REF)]["prix_m2"]
    fig, ax = plt.subplots(figsize=(8, 4.5))
    ax.hist(s, bins=40, color=TEAL, alpha=0.8)
    ax.axvline(s.mean(), color=CORAL, lw=2, label=f"Moyenne {s.mean():,.0f} €".replace(",", " "))
    ax.axvline(s.median(), color=BLUE, lw=2, label=f"Médiane {s.median():,.0f} €".replace(",", " "))
    ax.set_xlabel("€/m²"); ax.set_ylabel("Nombre de ventes"); ax.legend()
    ax.set_title(f"Distribution €/m² appartement ({ANNEE_REF}) : asymétrie -> médiane")
    fig.tight_layout(); fig.savefig(FIG / "04_distribution.png", dpi=120); plt.close(fig)


def plot_tendance(ventes):
    app = ventes[ventes["type_local"] == "Appartement"]
    top = (app[app["annee"] == ANNEE_REF].groupby("nom_commune")["prix_m2"]
           .agg(["median", "size"]).query("size >= @MIN_VENTES").sort_values("median"))
    choix = [top.index[-1], top.index[len(top) // 2], top.index[0]]  # chère / médiane / abordable
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for nom in choix:
        serie = app[app["nom_commune"] == nom].groupby("annee")["prix_m2"].median()
        ax.plot(serie.index, serie.values, marker="o", label=nom)
    ax.set_xlabel("Année"); ax.set_ylabel("€/m² médian appartement"); ax.legend()
    ax.set_title("Tendance €/m² par commune (2021-2025)")
    fig.tight_layout(); fig.savefig(FIG / "05_tendance.png", dpi=120); plt.close(fig)


def plot_volume(raw):
    ventes = raw[raw["nature_mutation"] == "Vente"].copy()
    vol = ventes.drop_duplicates("id_mutation").groupby("annee").size()
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(vol.index.astype(str), vol.values, color=BLUE)
    for i, v in enumerate(vol.values):
        ax.text(i, v, f"{v:,}".replace(",", " "), ha="center", va="bottom", fontsize=9)
    ax.set_ylabel("Ventes distinctes")
    ax.set_title("Volume de ventes par année (creux = 2024, pas 2025)")
    fig.tight_layout(); fig.savefig(FIG / "06_volume.png", dpi=120); plt.close(fig)


def main():
    pattern = sys.argv[1] if len(sys.argv) > 1 else "data/raw/dvf_94_*.csv"
    FIG.mkdir(exist_ok=True)
    raw = load_raw(pattern)
    raw["annee"] = pd.to_datetime(raw["date_mutation"]).dt.year
    ventes = clean(raw)
    ind = aggregate(ventes)

    for k, v in funnel_counts(raw).items():
        print(f"  {k:<24} {v:>8,}".replace(",", " "))

    plot_funnel(raw)
    plot_comparaison(ind)
    plot_app_vs_maison(ind)
    plot_distribution(ventes)
    plot_tendance(ventes)
    plot_volume(raw)
    print(f"\n6 figures écrites dans {FIG.resolve()}")


if __name__ == "__main__":
    main()
