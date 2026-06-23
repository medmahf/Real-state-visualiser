"""Télécharge les fichiers DVF géolocalisés du département 94 (2021->2025)."""
import os
import urllib.request

YEARS = [2021, 2022, 2023, 2024, 2025]
BASE = "https://files.data.gouv.fr/geo-dvf/latest/csv/{year}/departements/94.csv.gz"
OUT_DIR = "data/raw"


def download(out_dir: str = OUT_DIR) -> list[str]:
    os.makedirs(out_dir, exist_ok=True)
    paths = []
    for y in YEARS:
        url = BASE.format(year=y)
        dest = os.path.join(out_dir, f"dvf_94_{y}.csv.gz")
        if not os.path.exists(dest):
            print(f"-> {url}")
            urllib.request.urlretrieve(url, dest)
        paths.append(dest)
    return paths


if __name__ == "__main__":
    for p in download():
        print("OK", p)
