"""Recalcule toute la chaîne de risque de crédit sans AI, puis la compare au moteur de l'agent.

Ce script est une seconde implémentation, écrite indépendamment du moteur
agent/moteur_credit.py, des articles 2 à 5 de la politique de risque de crédit :
staging IFRS 9, PD à terme par puissances de la matrice de migration, ECL pondérée
par trois scénarios, formule IRB de Bâle (avec la loi normale de SciPy), ratio CET1
et concentrations. Il produit les réponses de référence de l'évaluation, puis vérifie
que le moteur donne exactement les mêmes résultats, à l'euro près.

Utilisation, depuis la racine du dépôt :
    pip install -r outils/requirements.txt
    python outils/verifier_credit.py
"""
import math
import os
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import norm

RACINE = Path(__file__).resolve().parent.parent
DONNEES = RACINE / "donnees"
LGD = {"Hypothèque": 0.20, "Nantissement": 0.35, "Caution": 0.40, "Aucune": 0.45}
CET1_AVANT_ECL, RWA_AUTRES = 42_300_000, 95_000_000


def euros(x):
    return f"{x:,.0f} €".replace(",", " ")


def pct(x):
    return f"{x:.2f} %".replace(".", ",")


contrats = pd.read_csv(DONNEES / "portefeuille_credits.csv")
matrice = pd.read_csv(DONNEES / "matrice_migration.csv").iloc[:, 1:].to_numpy()
scenarios = pd.read_csv(DONNEES / "scenarios_macro.csv")
poids = scenarios.ponderation_pct.to_numpy() / 100


def pd_cumulee(classe, t):
    """Probabilité d'atteindre le défaut en t ans : case D de la matrice à la puissance t."""
    if classe == "D":
        return 1.0
    return np.linalg.matrix_power(matrice, t)[int(classe[1:]) - 1, 8]


def stage(c):
    if c.notation_actuelle == "D" or c.jours_retard >= 90:
        return 3
    crans = int(c.notation_actuelle[1:]) - int(c.notation_origine[1:])
    return 2 if (c.jours_retard > 30 or crans >= 3 or c.notation_actuelle in ("N7", "N8")) else 1


def ecl_par_scenario(c, s):
    ead = c.encours_tire_eur + 0.5 * c.engagement_non_tire_eur
    resultats = []
    for _, sc in scenarios.iterrows():
        lgd = min(max(LGD[c.surete] + sc.ajustement_lgd_pts / 100, 0), 1)
        if s == 3:
            resultats.append(lgd * ead)
            continue
        horizon = 1 if s == 1 else c.maturite_restante_ans
        total = 0.0
        for t in range(1, horizon + 1):
            haut = 1 - (1 - pd_cumulee(c.notation_actuelle, t)) ** sc.multiplicateur_pd
            bas = 1 - (1 - pd_cumulee(c.notation_actuelle, t - 1)) ** sc.multiplicateur_pd
            total += (haut - bas) * (1 + c.taux_effectif_pct / 100) ** -(t - 0.5)
        resultats.append(total * lgd * ead)
    return np.array(resultats), ead


def k_irb(pd1, lgd, maturite):
    pd1 = max(pd1, 0.0005)
    m = min(max(maturite, 1), 5)
    f = (1 - math.exp(-50 * pd1)) / (1 - math.exp(-50))
    r = 0.12 * f + 0.24 * (1 - f)
    b = (0.11852 - 0.05478 * math.log(pd1)) ** 2
    queue = norm.cdf((norm.ppf(pd1) + math.sqrt(r) * norm.ppf(0.999)) / math.sqrt(1 - r))
    return lgd * (queue - pd1) * (1 + (m - 2.5) * b) / (1 - 1.5 * b)


lignes = []
for c in contrats.itertuples():
    s = stage(c)
    parts, ead = ecl_par_scenario(c, s)
    ecl = float(parts @ poids)
    k = max(0.0, LGD[c.surete] - ecl / ead) if s == 3 else k_irb(pd_cumulee(c.notation_actuelle, 1), LGD[c.surete], c.maturite_restante_ans)
    lignes.append(dict(id=c.id_contrat, nom=c.emprunteur, secteur=c.secteur, stage=s, ead=ead, ecl=ecl,
                       central=parts[0], adverse=parts[1], favorable=parts[2], rwa=12.5 * k * ead))
d = pd.DataFrame(lignes)
ead, ecl = d.ead.sum(), d.ecl.sum()
rwa_total = d.rwa.sum() + RWA_AUTRES
cet1 = CET1_AVANT_ECL - ecl
secteurs = d.groupby("secteur").ead.sum().sort_values(ascending=False)
premier = d.sort_values("ead").iloc[-1]

print("=" * 78)
print("BANQUE LORRAINE DES ENTREPRISES · portefeuille de crédits · données au 31/12/2025")
print("=" * 78)
for s in (1, 2, 3):
    x = d[d.stage == s]
    print(f"Stage {s} : {len(x)} contrats · EAD {euros(x.ead.sum())} ({pct(x.ead.sum() / ead * 100)}) · ECL {euros(x.ecl.sum())}")
print(f"ECL centrale {euros(d.central.sum())} · adverse {euros(d.adverse.sum())} · favorable {euros(d.favorable.sum())}")
print(f"Ratio CET1 : {pct(cet1 / rwa_total * 100)} · grand risque {premier.nom} : {pct(premier.ead / cet1 * 100)}")
print(f"Premier secteur : {secteurs.index[0]} · {pct(secteurs.iloc[0] / ead * 100)}")

reference = {
    "EAD totale": ead, "ECL pondérée": ecl, "ECL Stage 2": d[d.stage == 2].ecl.sum(),
    "ECL scénario adverse": d.adverse.sum(), "RWA crédit": d.rwa.sum(), "RWA totaux": rwa_total,
    "CET1": cet1, "Marge au-dessus de 12 %": cet1 - 0.12 * rwa_total,
}

print("\nCONTRÔLE CROISÉ AVEC agent/moteur_credit.py")
os.chdir(DONNEES)
moteur = {}
exec((RACINE / "agent" / "moteur_credit.py").read_text(encoding="utf-8"), moteur)
r = moteur["calculer"]()
t = r["totaux"]
pairs = {
    "EAD totale": t["ead"], "ECL pondérée": t["ecl"], "ECL Stage 2": float(r["par_stage"].loc[2, "ecl"]),
    "ECL scénario adverse": t["ecl_adverse"], "RWA crédit": t["rwa_credit"], "RWA totaux": t["rwa_total"],
    "CET1": t["fonds_propres"], "Marge au-dessus de 12 %": t["fonds_propres"] - t["cet1_requis_12"],
}
ecarts = {nom: abs(round(v) - round(reference[nom])) for nom, v in pairs.items()}
for nom, e in ecarts.items():
    print(f"  {'✓' if e == 0 else '✗'} {nom:<26} {euros(reference[nom]):>16}   écart {e} €")
print(f"\n{sum(e == 0 for e in ecarts.values())} indicateurs sur {len(ecarts)} identiques à l'euro près.")
