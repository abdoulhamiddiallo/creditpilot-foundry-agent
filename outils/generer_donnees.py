"""Génère les trois fichiers de données de la Banque Lorraine des Entreprises (banque fictive).

- matrice_migration.csv : matrice annuelle de migration des notations N1 à N8 vers le défaut D,
  construite à partir des PD à un an (de 0,03 % en N1 à 20 % en N8) et de migrations
  d'autant plus rares qu'elles sont lointaines, un peu plus fréquentes vers le bas ;
- portefeuille_credits.csv : 80 crédits d'entreprises lorraines, avec notations d'origine et
  actuelle, retards, encours, engagements non tirés, sûretés, taux effectifs et maturités ;
- scenarios_macro.csv : scénarios central, adverse et favorable, pondérés 50, 30 et 20 %.

La graine est fixée : chaque exécution reproduit exactement les fichiers du dossier donnees/.

Utilisation, depuis la racine du dépôt :
    python outils/generer_donnees.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

D = Path(__file__).resolve().parent.parent / "donnees"
g = np.random.default_rng(3106)
CLASSES = [f"N{k}" for k in range(1, 9)]
# 1. Matrice de migration annuelle : 8 classes + défaut (D, absorbant)
pd_an = np.array([0.0003, 0.0008, 0.0020, 0.0050, 0.0120, 0.0300, 0.0800, 0.2000])
M = np.zeros((9, 9))
for i in range(8):
    reste = 1 - pd_an[i]
    stay = [0.90, 0.87, 0.84, 0.81, 0.78, 0.75, 0.72, 0.68][i]
    row = np.zeros(9)
    row[i] = stay
    autres = [j for j in range(8) if j != i]
    poids = np.array([np.exp(-1.15 * abs(j - i)) * (1.35 if j > i else 1.0) for j in autres])
    row[autres] = (1 - stay) * poids / poids.sum()
    row[:8] *= reste
    row[8] = pd_an[i]
    M[i] = row
M[8, 8] = 1.0
M = np.round(M, 5)
for i in range(9):
    M[i, i] += 1 - M[i].sum()
mat = pd.DataFrame(M, columns=CLASSES + ["D"]); mat.insert(0, "classe_depart", CLASSES + ["D"])
mat.to_csv(D / "matrice_migration.csv", index=False, float_format="%.5f")

# 2. Portefeuille : 80 contrats d'entreprises
SECTEURS = [("Immobilier commercial", 0.22), ("Industrie", 0.15), ("Commerce", 0.13), ("BTP", 0.11),
            ("Transport et logistique", 0.09), ("Santé", 0.08), ("Agroalimentaire", 0.08),
            ("Hôtellerie-restauration", 0.07), ("Services aux entreprises", 0.07)]
noms_a = ["Atelier", "Groupe", "Société", "Maison", "Compagnie", "Établissements", "Holding", "Fabrique"]
villes = ["Metz", "Nancy", "Thionville", "Épinal", "Verdun", "Forbach", "Sarreguemines", "Lunéville", "Toul", "Pont-à-Mousson",
          "Saint-Dié", "Bar-le-Duc", "Hayange", "Longwy", "Briey", "Sarrebourg", "Remiremont", "Commercy", "Vittel", "Contrexéville"]
lignes = []
noms_vus = set()
for k in range(80):
    s = g.choice(len(SECTEURS), p=[w for _, w in SECTEURS])
    secteur = SECTEURS[s][0]
    while True:
        nom = f"{g.choice(noms_a)} {g.choice(villes)}"
        if nom not in noms_vus: noms_vus.add(nom); break
    orig = int(g.choice(range(1, 8), p=[0.04, 0.10, 0.20, 0.26, 0.22, 0.13, 0.05]))
    choc = g.choice([-1, 0, 0, 0, 0, 1, 1, 2, 3], p=[0.08, 0.17, 0.17, 0.17, 0.11, 0.12, 0.08, 0.05, 0.05])
    actu = int(np.clip(orig + choc, 1, 8))
    retard = int(g.choice([0, 0, 0, 0, 0, 0, 0, 12, 35, 95], p=[0.12]*7 + [0.08, 0.055, 0.025]))
    if retard >= 90: actu = 8
    encours = float(np.round(g.lognormal(np.log(3.2e6), 0.75) / 1e4) * 1e4)
    encours = min(encours, 6.5e6)
    non_tire = float(np.round(encours * g.choice([0, 0, 0.1, 0.2, 0.35]) / 1e4) * 1e4)
    surete = g.choice(["Hypothèque", "Nantissement", "Caution", "Aucune"], p=[0.30, 0.25, 0.20, 0.25])
    if secteur == "Immobilier commercial": surete = "Hypothèque"
    taux = round(float(g.uniform(2.6, 5.4)) + 0.25 * (actu - 4), 2)
    matur = int(g.choice([1, 2, 3, 4, 5, 6, 7], p=[0.08, 0.14, 0.20, 0.20, 0.18, 0.12, 0.08]))
    lignes.append((f"BLE-{1001 + k}", nom, secteur, f"N{orig}", f"N{actu}" if retard < 90 else "D", retard, encours, non_tire, surete, taux, matur))
port = pd.DataFrame(lignes, columns=["id_contrat", "emprunteur", "secteur", "notation_origine", "notation_actuelle", "jours_retard",
                                     "encours_tire_eur", "engagement_non_tire_eur", "surete", "taux_effectif_pct", "maturite_restante_ans"])
# Le premier emprunteur : une foncière d'immobilier commercial
port.loc[0, ["emprunteur", "secteur", "notation_origine", "notation_actuelle", "jours_retard", "encours_tire_eur", "engagement_non_tire_eur", "surete", "taux_effectif_pct", "maturite_restante_ans"]] = \
    ["Foncière des Trois Frontières", "Immobilier commercial", "N3", "N4", 0, 8_400_000.0, 600_000.0, "Hypothèque", 3.85, 6]
# Un cas d'école : dégradation de 3 crans sans retard, donc Stage 2 par la notation
port.loc[1, ["emprunteur", "secteur", "notation_origine", "notation_actuelle", "jours_retard", "encours_tire_eur", "engagement_non_tire_eur", "surete", "taux_effectif_pct", "maturite_restante_ans"]] = \
    ["Transports Mosellans Saint-Nicolas", "Transport et logistique", "N3", "N6", 0, 5_200_000.0, 0.0, "Nantissement", 4.60, 5]
port.to_csv(D / "portefeuille_credits.csv", index=False, float_format="%.2f")

# 3. Scénarios macroéconomiques pondérés
pd.DataFrame({
    "scenario": ["Central", "Adverse", "Favorable"],
    "ponderation_pct": [50, 30, 20],
    "multiplicateur_pd": [1.00, 1.80, 0.75],
    "ajustement_lgd_pts": [0.0, 7.0, -3.0],
    "pib_variation_pct": [1.1, -1.8, 2.3],
    "chomage_pct": [7.6, 9.4, 6.9],
}).to_csv(D / "scenarios_macro.csv", index=False)
total = f"{port.encours_tire_eur.sum():,.0f}".replace(",", " ")
print(f"{len(port)} contrats écrits dans {D} · encours tiré total {total} €")
