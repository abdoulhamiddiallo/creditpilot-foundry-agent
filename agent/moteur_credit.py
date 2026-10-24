"""Moteur de risque de crédit de CreditPilot : la méthode de la politique, codée une fois pour toutes.

Ce module applique exactement les articles 2 à 5 de la Politique_Risque_Credit_BLE :
classement IFRS 9 en Stage 1, 2 ou 3, probabilités de défaut à terme par la matrice de
migration, pertes de crédit attendues (ECL) pondérées par trois scénarios, exigence de
capital selon l'approche IRB de Bâle, ratio CET1 et limites de concentration.

Utilisation dans l'interpréteur de code de l'agent :
    import glob
    exec(open(glob.glob("/mnt/data/*moteur_credit.py")[0]).read())
    r = calculer()                                   # hypothèses de la politique
    afficher(r)                                      # tous les résultats, en français
    s = calculer(ponderations={"Adverse": 40, "Central": 40, "Favorable": 20})   # simulation
    contrat(r, "BLE-1002")                           # détail d'un contrat
    exporter_excel(r, "/mnt/data/ecl_BLE.xlsx")

Utilisation locale, depuis la racine du dépôt :
    python agent/moteur_credit.py
"""
import glob
import math
import os

import numpy as np
import pandas as pd

LGD_SURETE = {"Hypothèque": 0.20, "Nantissement": 0.35, "Caution": 0.40, "Aucune": 0.45}   # article 3
CCF = 0.50                     # article 3 : facteur de conversion des engagements non tirés
PLANCHER_PD = 0.0005           # article 4 : plancher de PD pour le capital
FONDS_PROPRES_AVANT_ECL = 42_300_000   # article 4 : CET1 avant dépréciations IFRS 9
RWA_AUTRES = 95_000_000            # article 4 : risques de marché et opérationnel
LIMITES = {                    # article 5 : (seuil d'alerte, limite)
    "part_stage2": (18.0, 24.0),
    "part_stage3": (3.0, 5.0),
    "grand_risque": (10.0, 25.0),
    "concentration_sectorielle": (25.0, 30.0),
    "ratio_cet1": (12.0, 10.5),
}
CLASSES = [f"N{k}" for k in range(1, 9)]


def _trouver(nom):
    """Retrouve un fichier, même renommé par Foundry (préfixe assistant-...)."""
    for motif in (f"/mnt/data/*{nom}", f"/mnt/data/**/*{nom}", nom, f"*{nom}"):
        trouves = glob.glob(motif, recursive=True)
        if trouves:
            return trouves[0]
    raise FileNotFoundError(f"Fichier introuvable : {nom}")


def statut(valeur, alerte, limite, vers_le_bas=False):
    """Statuts de l'article 5. Pour le ratio CET1, les seuils s'appliquent vers le bas."""
    if vers_le_bas:
        if valeur < limite:
            return "DÉPASSEMENT"
        if valeur < alerte:
            return "ALERTE"
        return "CONFORME"
    if valeur > limite:
        return "DÉPASSEMENT"
    if valeur >= alerte:
        return "ALERTE"
    return "CONFORME"


def classer(ligne):
    """Article 2 : Stage 3 si défaut ou 90 jours de retard ; Stage 2 si dégradation significative."""
    if ligne.notation_actuelle == "D" or ligne.jours_retard >= 90:
        return 3
    crans = int(ligne.notation_actuelle[1:]) - int(ligne.notation_origine[1:])
    if ligne.jours_retard > 30 or crans >= 3 or ligne.notation_actuelle in ("N7", "N8"):
        return 2
    return 1


def capital_irb(pd_1an, lgd, maturite):
    """Article 4 : formule IRB de Bâle pour les entreprises (exigence K par euro d'exposition)."""
    p = max(pd_1an, PLANCHER_PD)
    m = min(max(maturite, 1), 5)
    r = 0.12 * (1 - math.exp(-50 * p)) / (1 - math.exp(-50)) + 0.24 * (1 - (1 - math.exp(-50 * p)) / (1 - math.exp(-50)))
    b = (0.11852 - 0.05478 * math.log(p)) ** 2
    n = 0.5 * (1 + math.erf(((1 - r) ** -0.5 * _ninv(p) + (r / (1 - r)) ** 0.5 * _ninv(0.999)) / math.sqrt(2)))
    return lgd * (n - p) * (1 + (m - 2.5) * b) / (1 - 1.5 * b)


def _ninv(p):
    """Inverse de la loi normale centrée réduite (algorithme d'Acklam, précision 1e-9)."""
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    if p < 0.02425:
        q = math.sqrt(-2 * math.log(p))
        x = (((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    elif p > 1 - 0.02425:
        q = math.sqrt(-2 * math.log(1 - p))
        x = -(((((c[0] * q + c[1]) * q + c[2]) * q + c[3]) * q + c[4]) * q + c[5]) / ((((d[0] * q + d[1]) * q + d[2]) * q + d[3]) * q + 1)
    else:
        q = p - 0.5
        t = q * q
        x = (((((a[0] * t + a[1]) * t + a[2]) * t + a[3]) * t + a[4]) * t + a[5]) * q / (((((b[0] * t + b[1]) * t + b[2]) * t + b[3]) * t + b[4]) * t + 1)
    e = 0.5 * math.erfc(-x / math.sqrt(2)) - p
    u = e * math.sqrt(2 * math.pi) * math.exp(x * x / 2)
    return x - u / (1 + x * u / 2)


def calculer(ponderations=None, fonds_propres_avant_ecl=FONDS_PROPRES_AVANT_ECL, exclure=None):
    """Enchaîne toute la chaîne crédit et renvoie un dictionnaire de résultats.

    ponderations : dictionnaire {scénario: poids en %} pour une simulation ;
    fonds_propres_avant_ecl : CET1 avant déduction des dépréciations (article 4) ;
    exclure : liste d'identifiants de contrats à retirer (simulation de cession).
    """
    port = pd.read_csv(_trouver("portefeuille_credits.csv"))
    mat = pd.read_csv(_trouver("matrice_migration.csv")).set_index("classe_depart")
    scen = pd.read_csv(_trouver("scenarios_macro.csv"))
    if exclure:
        port = port[~port.id_contrat.isin(exclure)].reset_index(drop=True)
    if ponderations:
        scen["ponderation_pct"] = scen.scenario.map(ponderations).fillna(0)
    poids = scen.ponderation_pct.to_numpy(float) / scen.ponderation_pct.sum()

    M = mat.to_numpy(float)
    puissances = [np.eye(9)]
    for _ in range(10):
        puissances.append(puissances[-1] @ M)
    pd_cumulee = {c: np.array([puissances[t][i, 8] for t in range(11)]) for i, c in enumerate(CLASSES)}

    port["stage"] = port.apply(classer, axis=1)
    port["ead"] = port.encours_tire_eur + CCF * port.engagement_non_tire_eur
    port["lgd"] = port.surete.map(LGD_SURETE)
    port["pd_1an"] = [pd_cumulee[c][1] if c != "D" else 1.0 for c in port.notation_actuelle]

    ecl_scen = np.zeros((len(port), len(scen)))
    for k, ligne in port.iterrows():
        for s, sc in scen.iterrows():
            lgd_s = min(max(ligne.lgd + sc.ajustement_lgd_pts / 100, 0), 1)
            if ligne.stage == 3:
                ecl_scen[k, s] = lgd_s * ligne.ead
                continue
            horizon = 1 if ligne.stage == 1 else int(ligne.maturite_restante_ans)
            cum = 1 - (1 - pd_cumulee[ligne.notation_actuelle][: horizon + 1]) ** sc.multiplicateur_pd
            marginales = np.diff(cum)
            actualisation = (1 + ligne.taux_effectif_pct / 100) ** -(np.arange(1, horizon + 1) - 0.5)
            ecl_scen[k, s] = (marginales * actualisation).sum() * lgd_s * ligne.ead
    port["ecl"] = ecl_scen @ poids
    for s, sc in scen.iterrows():
        port[f"ecl_{sc.scenario.lower()}"] = ecl_scen[:, s]

    # Article 4 : en défaut, K = max(0, LGD - taux de provision) ; sinon formule IRB
    k_irb = [max(0.0, l.lgd - l.ecl / l.ead) if l.stage == 3 else capital_irb(l.pd_1an, l.lgd, l.maturite_restante_ans)
             for l in port.itertuples()]
    port["rwa"] = 12.5 * np.array(k_irb) * port.ead

    ead = port.ead.sum()
    par_stage = port.groupby("stage").agg(contrats=("id_contrat", "count"), ead=("ead", "sum"), ecl=("ecl", "sum"))
    par_stage = par_stage.reindex([1, 2, 3], fill_value=0)
    par_secteur = port.groupby("secteur").agg(ead=("ead", "sum"), ecl=("ecl", "sum")).sort_values("ead", ascending=False)
    par_secteur["part_pct"] = par_secteur.ead / ead * 100
    hhi = float(((par_secteur.ead / ead) ** 2).sum() * 10000)
    premier = port.sort_values("ead", ascending=False).iloc[0]
    rwa_credit = float(port.rwa.sum())
    rwa_total = rwa_credit + RWA_AUTRES
    fonds_propres = fonds_propres_avant_ecl - float(port.ecl.sum())   # article 4 : CET1 net des ECL
    ratio = fonds_propres / rwa_total * 100

    valeurs = {
        "part_stage2": par_stage.loc[2, "ead"] / ead * 100,
        "part_stage3": par_stage.loc[3, "ead"] / ead * 100,
        "grand_risque": premier.ead / fonds_propres * 100,
        "concentration_sectorielle": float(par_secteur.part_pct.iloc[0]),
        "ratio_cet1": ratio,
    }
    statuts = {k: statut(v, *LIMITES[k], vers_le_bas=(k == "ratio_cet1")) for k, v in valeurs.items()}
    return {
        "contrats": port,
        "par_stage": par_stage,
        "par_secteur": par_secteur,
        "scenarios": scen,
        "totaux": {
            "contrats": len(port), "ead": float(ead), "ecl": float(port.ecl.sum()),
            "taux_couverture_pct": float(port.ecl.sum() / ead * 100),
            **{f"ecl_{sc.scenario.lower()}": float(port[f"ecl_{sc.scenario.lower()}"].sum()) for _, sc in scen.iterrows()},
            "rwa_credit": rwa_credit, "rwa_total": rwa_total, "fonds_propres_avant_ecl": fonds_propres_avant_ecl,
            "fonds_propres": fonds_propres, "ratio_cet1_pct": ratio, "cet1_requis_12": 0.12 * rwa_total,
            "hhi_sectoriel": hhi, "premier_emprunteur": premier.emprunteur, "premier_ead": float(premier.ead),
            "premier_secteur": par_secteur.index[0],
        },
        "valeurs": valeurs,
        "statuts": statuts,
    }


def euros(x):
    return f"{x:,.0f} €".replace(",", " ")


def pct(x):
    return f"{x:.2f} %".replace(".", ",")


def contrat(r, identifiant):
    """Affiche le détail d'un contrat : stage, EAD, LGD, PD à 1 an, ECL par scénario."""
    c = r["contrats"].set_index("id_contrat").loc[identifiant]
    print(f"{identifiant} · {c.emprunteur} · {c.secteur}")
    print(f"Notation {c.notation_origine} vers {c.notation_actuelle} · retard {c.jours_retard} jours · Stage {c.stage}")
    print(f"EAD {euros(c.ead)} · LGD {pct(c.lgd * 100)} · PD à 1 an {pct(c.pd_1an * 100)} · maturité {c.maturite_restante_ans} ans")
    print(f"ECL pondérée {euros(c.ecl)} · central {euros(c.ecl_central)} · adverse {euros(c.ecl_adverse)} · favorable {euros(c.ecl_favorable)}")


def afficher(r):
    """Affiche tous les résultats au format de la politique."""
    t, s, v = r["totaux"], r["statuts"], r["valeurs"]
    print(f"PORTEFEUILLE : {t['contrats']} contrats · EAD {euros(t['ead'])} · ECL {euros(t['ecl'])} · couverture {pct(t['taux_couverture_pct'])}")
    print("\nSTAGE | CONTRATS | EAD | PART EAD | ECL | COUVERTURE")
    for st, l in r["par_stage"].iterrows():
        couv = l.ecl / l.ead * 100 if l.ead else 0
        print(f"Stage {st} | {int(l.contrats)} | {euros(l.ead)} | {pct(l.ead / t['ead'] * 100)} | {euros(l.ecl)} | {pct(couv)}")
    print("\nSCÉNARIO | PONDÉRATION | ECL")
    for _, sc in r["scenarios"].iterrows():
        print(f"{sc.scenario} | {pct(sc.ponderation_pct)} | {euros(t['ecl_' + sc.scenario.lower()])}")
    print(f"ECL pondérée : {euros(t['ecl'])} (écart avec le scénario central : {euros(t['ecl'] - t['ecl_central'])})")
    print("\nSECTEUR | EAD | PART | ECL")
    for nom, l in r["par_secteur"].iterrows():
        print(f"{nom} | {euros(l.ead)} | {pct(l.part_pct)} | {euros(l.ecl)}")
    print(f"Indice de Herfindahl sectoriel : {t['hhi_sectoriel']:,.0f}".replace(",", " "))
    print(f"\nCAPITAL (article 4) : RWA crédit {euros(t['rwa_credit'])} · RWA autres {euros(RWA_AUTRES)} · RWA total {euros(t['rwa_total'])}")
    print(f"CET1 avant dépréciations {euros(t['fonds_propres_avant_ecl'])} - ECL {euros(t['ecl'])} = CET1 {euros(t['fonds_propres'])}")
    print(f"Ratio CET1 {pct(t['ratio_cet1_pct'])} · {s['ratio_cet1']} · marge au-dessus du seuil de 12 % : {euros(t['fonds_propres'] - t['cet1_requis_12'])}")
    print("\nTABLEAU DES LIMITES (article 5)")
    print("INDICATEUR | VALEUR | SEUIL D'ALERTE | LIMITE | STATUT")
    noms = {"part_stage2": "Part du Stage 2 dans l'EAD", "part_stage3": "Part du Stage 3 dans l'EAD",
            "grand_risque": f"Grand risque : {t['premier_emprunteur']} / CET1",
            "concentration_sectorielle": f"Premier secteur : {t['premier_secteur']}", "ratio_cet1": "Ratio CET1"}
    for k in v:
        a, l = LIMITES[k]
        seuils = (f"inférieur à {pct(a)}", f"inférieur à {pct(l)}") if k == "ratio_cet1" else (pct(a), pct(l))
        print(f"{noms[k]} | {pct(v[k])} | {seuils[0]} | {seuils[1]} | {s[k]}")
    print("\nACTIONS REQUISES (article 6)")
    actions = {
        "part_stage2": "Part du Stage 2 : revue des dossiers dégradés par le Comité de crédit sous 30 jours et plan de suivi renforcé.",
        "part_stage3": "Part du Stage 3 : plan de réduction des créances douteuses présenté au Comité des risques sous 30 jours.",
        "grand_risque": "Grand risque : gel de tout nouvel engagement sur ce groupe et proposition de réduction ou de partage du risque sous 15 jours.",
        "concentration_sectorielle": "Concentration sectorielle : arrêt de la production nouvelle dans le secteur hors dérogation du Comité de crédit.",
        "ratio_cet1": "Ratio CET1 : information du Directeur général et du Comité des risques sous 5 jours ouvrés et plan de rétablissement.",
    }
    liste = [f"{actions[k]} ({s[k]})" for k in v if s[k] != "CONFORME"]
    if "DÉPASSEMENT" in s.values():
        liste.append("DÉPASSEMENT : information immédiate du Directeur général et du Conseil d'administration ; notification au superviseur si le ratio CET1 passe sous 10,5 %.")
    for k, a in enumerate(liste or ["Aucune action d'escalade requise."], 1):
        print(f"{k}. {a}")


def exporter_excel(r, chemin="/mnt/data/ecl_BLE.xlsx"):
    """Écrit le fichier Excel : détail par contrat, synthèse par stage et par secteur."""
    c = r["contrats"]
    detail = pd.DataFrame({
        "Contrat": c.id_contrat, "Emprunteur": c.emprunteur, "Secteur": c.secteur,
        "Notation origine": c.notation_origine, "Notation actuelle": c.notation_actuelle, "Jours de retard": c.jours_retard,
        "Stage": c.stage, "EAD (€)": c.ead.round(0), "LGD (%)": (c.lgd * 100).round(2), "PD à 1 an (%)": (c.pd_1an * 100).round(3),
        "ECL pondérée (€)": c.ecl.round(0), "ECL centrale (€)": c.ecl_central.round(0), "ECL adverse (€)": c.ecl_adverse.round(0),
        "ECL favorable (€)": c.ecl_favorable.round(0), "RWA (€)": c.rwa.round(0),
    })
    stages = r["par_stage"].reset_index().rename(columns={"stage": "Stage", "contrats": "Contrats", "ead": "EAD (€)", "ecl": "ECL (€)"})
    secteurs = r["par_secteur"].reset_index().rename(columns={"secteur": "Secteur", "ead": "EAD (€)", "ecl": "ECL (€)", "part_pct": "Part (%)"})
    with pd.ExcelWriter(chemin) as classeur:
        detail.to_excel(classeur, sheet_name="Contrats", index=False)
        stages.round(2).to_excel(classeur, sheet_name="Stages", index=False)
        secteurs.round(2).to_excel(classeur, sheet_name="Secteurs", index=False)
    return chemin


if __name__ == "__main__" and globals().get("__file__", "").endswith("moteur_credit.py"):
    ici = os.path.dirname(os.path.abspath(__file__))
    donnees = os.path.join(ici, "..", "donnees")
    os.chdir(donnees if os.path.isdir(donnees) and not os.path.exists(os.path.join(ici, "portefeuille_credits.csv")) else ici)
    afficher(calculer())
