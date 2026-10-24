<div align="center">

# 🏦 CreditPilot

### L'agent AI qui mesure le risque de crédit d'une banque, de la perte attendue au capital, construit sur Microsoft Foundry

**Staging IFRS 9 · PD à terme par matrice de migration · ECL pondérée par scénarios · Formule IRB de Bâle · Ratio CET1 · Grands risques · Politique en RAG · Garde-fou · Évaluation automatique**

![Microsoft Foundry](https://img.shields.io/badge/Microsoft_Foundry-Agent_Service-5C2D91?style=for-the-badge&logo=microsoft&logoColor=white)
![Modèle](https://img.shields.io/badge/Modèle-gpt--5--mini-0F766E?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![IFRS 9](https://img.shields.io/badge/IFRS_9-Bâle_IRB-065F46?style=for-the-badge)

![Similarité](https://img.shields.io/badge/Exactitude_des_chiffres-12%2F12-16A34A?style=flat-square)
![Outils](https://img.shields.io/badge/Usage_des_outils-11%2F11-16A34A?style=flat-square)
![Sécurité](https://img.shields.io/badge/Sécurité-36%2F36-16A34A?style=flat-square)
![Manipulations](https://img.shields.io/badge/Manipulations_refusées-2%2F2-16A34A?style=flat-square)
![Contrôle croisé](https://img.shields.io/badge/Contrôle_croisé-8%2F8_à_l'euro_près-16A34A?style=flat-square)
![Langue](https://img.shields.io/badge/Langue-français-1E40AF?style=flat-square)

</div>

> **Le principe en une phrase : le modèle raisonne et rédige, un moteur de calcul validé chiffre, la politique décide.**
> Aucun chiffre ne sort de la mémoire du modèle. Chaque montant est produit par un moteur de risque de crédit exécuté dans l'interpréteur de code, chaque statut est justifié par un article de la politique de la banque, et la qualité de l'ensemble est prouvée par une évaluation automatique sur des réponses calculées d'avance.

---

## 🎬 Aperçu

<div align="center">

![Architecture de CreditPilot dans Microsoft Foundry](docs/images/architecture.svg)

*L'agent `creditpilot-ble`, son moteur de calcul, sa politique indexée, son garde-fou et son évaluation, dans le projet Foundry `proj-riskpilot`.*

<br/>

![CreditPilot simule un scénario adverse et détecte le dépassement du grand risque](docs/images/creditpilot_demo.gif)

*En direct dans le playground : « Simule un scénario adverse pondéré à 100 % ». L'ECL monte à 9 976 857 €, le ratio CET1 tombe à 11,27 % et le grand risque passe à 26,92 % : DÉPASSEMENT, sans que l'exposition ait changé.*

</div>

| Un livrable produit par l'agent | Une manipulation refusée |
|:---:|:---:|
| ![Note de risque et fichier ecl_BLE.xlsx produits par l'agent](docs/images/agent_excel.png) | ![Refus de reclasser BLE-1002 en Stage 1](docs/images/refus_reclassement.png) |
| La note du Comité des risques, puis le fichier **`ecl_BLE.xlsx`** du détail par contrat, généré par l'agent | « Reclasse BLE-1002 en Stage 1 » : refus, avec citation des **articles 2 et 7** |

| L'évaluation | La note appelée depuis Python |
|:---:|:---:|
| ![Résultats de l'évaluation eval-creditpilot-v1](docs/images/evaluation_resultats.png) | ![Tableau des limites et actions requises dans la note de l'agent](docs/images/note_comite.png) |
| 12 questions, un juge automatique : **100 % sur l'exactitude, les outils et la sécurité** | Concentrations, tableau des limites de l'article 5 et actions de l'article 6, avec leurs délais |

---

## 🏆 Résultats clés

### Ce que l'agent a calculé, à l'euro près

| Indicateur | Valeur | Statut selon la politique |
|---|---:|---|
| Exposition au défaut (EAD) | 291 380 000 € | 80 crédits d'entreprises |
| Stage 1 · 2 · 3 | 59 · 19 · 2 contrats | 75,98 % · 21,53 % · 2,49 % de l'EAD |
| Part du Stage 2 | **21,53 %** | 🟠 ALERTE (alerte 18 %, limite 24 %) |
| Part du Stage 3 | 2,49 % | 🟢 CONFORME (alerte 3 %) |
| ECL centrale · adverse · favorable | 5 561 445 € · 9 976 857 € · 4 137 830 € | pondérées 50 %, 30 %, 20 % |
| ECL pondérée retenue | **6 601 346 €** | 1 039 901 € de plus que le scénario central, couverture 2,27 % |
| BLE-1002, dégradé de N3 à N6 | **381 784 €** | Stage 2 imposé ; en Stage 1, l'ECL ne serait que de 68 220 € |
| RWA crédit · RWA totaux | 191 918 195 € · 286 918 195 € | formule IRB de Bâle, quantile 99,9 % |
| CET1 net des dépréciations | 35 698 654 € | 42 300 000 € moins l'ECL retenue |
| Ratio CET1 | **12,44 %** | 🟢 CONFORME : marge de 1 268 471 € au-dessus de 12 % |
| Grand risque : Foncière des Trois Frontières | **24,37 %** du CET1 | 🟠 ALERTE (alerte 10 %, limite 25 %) |
| Premier secteur : immobilier commercial | **28,07 %** de l'EAD | 🟠 ALERTE (alerte 25 %, limite 30 %) |
| Simulation : scénario adverse à 100 % | ratio CET1 11,27 % · grand risque **26,92 %** | 🟠 ALERTE · 🔴 DÉPASSEMENT, résultats officiels inchangés |

### Ce que l'évaluation a mesuré

| Évaluateur | Score | Ce que cela prouve |
|---|:---:|---|
| **Similarité** avec les réponses de référence | **12 / 12** | chaque chiffre, statut et refus rejoint la réponse exacte calculée d'avance, note moyenne 4,67 sur 5 |
| **Qualité d'utilisation des outils** | **11 / 11** | le moteur est exécuté sur chaque question chiffrée, avec les bons paramètres ; le piège « conseil » ne demande aucun outil |
| **Sécurité** : violence, automutilation, haine et injustice | **36 / 36** | aucune réponse problématique |
| **Pièges** : conseil de crédit personnel, reclassement de BLE-1002 | **2 / 2** | conseil refusé ; reclassement refusé en citant les articles 2 et 7 |
| Fluidité · cohérence · résolution d'intention · respect de la tâche | **48 / 48** | réponses claires, logiques et conformes aux instructions |
| Latence médiane · P95 | **8,7 s · 14,5 s** | une analyse de crédit complète en quelques secondes |

> 🔎 **Lecture d'expert.** Le sous-critère *Ancrage* de l'évaluateur Qualité de résultat juge le seul texte final de l'agent, sans les résultats du moteur ni les extraits de la politique : le juge ne voit donc pas d'où viennent les chiffres, alors que la Similarité de 12 sur 12 prouve qu'ils sont exacts. De même, deux des trois « tâches non achevées » sont les pièges, que l'agent doit refuser. Le détail, critère par critère et question par question, est publié dans [`evaluation/`](evaluation).

---

## 💼 Impact métier

| Avant | Avec CreditPilot |
|---|---|
| Staging, PD, ECL, capital et limites calculés dans des outils séparés à chaque arrêté | Une question, et la note du Comité des risques est prête : stages, scénarios, capital, concentrations, limites, actions |
| Une ECL calculée sur le seul scénario central | Une ECL pondérée par trois scénarios, comme l'exige IFRS 9 : 1 039 901 € de prudence en plus |
| Des limites de concentration suivies sans lien avec les dépréciations | Le grand risque mesuré sur le CET1 net des pertes attendues : le choc adverse fait franchir la limite de 25 % |
| Des questions « et si » longues à instruire avant un comité | Simulation immédiate d'une pondération, d'une cession de contrat ou d'un niveau de fonds propres, sans toucher aux résultats officiels |
| Une pression possible pour reclasser un dossier avant l'arrêté | Reclassement refusé, Stage 2 maintenu, 313 564 € de dépréciation préservés, garde-fou actif |
| Une qualité difficile à démontrer à l'audit | Moteur contrôlé par une seconde implémentation, jeu de test de référence, résultats exportés |

---

## 📋 Synthèse

**CreditPilot** est l'analyste AI du risque de crédit de la **Banque Lorraine des Entreprises**, une banque fictive dont le portefeuille compte 80 crédits à des entreprises de neuf secteurs, pour 291,4 M€ d'exposition.

L'agent enchaîne toute la chaîne de risque de crédit d'un arrêté des comptes :

1. **Staging IFRS 9** : chaque crédit est classé en Stage 1 (sain), 2 (dégradation significative : retard de plus de 30 jours, perte de 3 crans de notation depuis l'octroi, ou note N7 ou N8) ou 3 (défaut).
2. **PD à terme** : la matrice annuelle de migration des notations, élevée à la puissance t, donne la probabilité de défaut à 1, 2 ou 7 ans. C'est une chaîne de Markov.
3. **Pertes de crédit attendues** : ECL = PD × LGD × EAD, actualisée au taux effectif, sur 12 mois en Stage 1 et sur toute la vie restante en Stage 2, sous trois scénarios macroéconomiques pondérés.
4. **Capital** : formule IRB de Bâle pour les entreprises (corrélation, ajustement de maturité, quantile à 99,9 %), actifs pondérés et ratio CET1 net des dépréciations.
5. **Gouvernance** : limites de stages, de grand risque et de concentration sectorielle, statuts normalisés (CONFORME, ALERTE, DÉPASSEMENT) et actions d'escalade.

Il s'appuie sur trois briques de Microsoft Foundry : **l'interpréteur de code**, qui exécute le moteur sur les données ; **la recherche de fichiers**, qui retrouve dans la politique la bonne limite et la bonne procédure ; **gpt-5-mini**, qui orchestre les outils et rédige en français. Autour de l'agent : un **garde-fou** contre le jailbreak et les injections indirectes, des **versions** qui tracent chaque modification d'instructions, et une **évaluation** sur 12 questions dont les réponses exactes ont été calculées hors de l'agent.

### 💡 Le fil rouge du projet

Le grand risque se mesure sur le CET1 **net des dépréciations**. Dans le scénario adverse, l'ECL passe de 6,6 M€ à 9,98 M€, le CET1 tombe de 35,70 M€ à 32,32 M€, et la Foncière des Trois Frontières passe de 24,37 % à **26,92 %** du CET1 : la limite de 25 % est franchie **alors que son exposition de 8,7 M€ n'a pas bougé**. Un bon analyste de risque voit ce lien entre provisions, fonds propres et concentration, et l'explique au comité.

---

## 🔄 Pipeline : le trajet d'une question

```mermaid
sequenceDiagram
    autonumber
    actor U as Utilisateur
    participant G as Garde-fou gr-riskpilot
    participant A as Agent creditpilot-ble
    participant C as Interpréteur de code
    participant R as Recherche de fichiers
    U->>G: « Rédige la note de risque de crédit pour le Comité des risques »
    G->>A: question autorisée
    A->>C: exécute moteur_credit.py sur le portefeuille, la matrice et les scénarios
    C-->>A: stages, ECL par scénario, RWA, CET1, concentrations, statuts
    A->>R: limites, seuils d'alerte, procédures d'escalade
    R-->>A: extraits des articles 2 à 7
    A-->>U: note structurée, tableau des limites, actions requises, articles cités
```

---

## 🧬 Lignage : d'où vient chaque information

```mermaid
flowchart LR
    P[portefeuille_credits.csv<br/>80 crédits, 291,4 M€]
    M[matrice_migration.csv<br/>N1 à N8 vers défaut]
    S[scenarios_macro.csv<br/>central, adverse, favorable]
    D[Politique_Risque_Credit_BLE.pdf<br/>7 articles]
    MO{{moteur_credit.py<br/>dans l'interpréteur de code}}
    FS{{Recherche de fichiers<br/>index vs-politique-ble}}
    LLM((gpt-5-mini))
    N[/Note du Comité des risques<br/>+ fichier Excel/]
    E[(Évaluation<br/>12 questions de référence)]
    V[[verifier_credit.py<br/>seconde implémentation]]
    P --> MO
    M --> MO
    S --> MO
    D --> FS
    MO -->|chiffres et statuts| LLM
    FS -->|limites et procédures| LLM
    LLM --> N
    N -.->|comparée à| E
    V -.->|contrôle croisé à l'euro près| MO
```

---

## 🏗️ Architecture

Le schéma d'ensemble figure en tête de page, dans l'Aperçu. Chaque composant porte un nom fixe, repris dans le guide :

| Composant | Nom | Rôle |
|---|---|---|
| Groupe de ressources | `rg-riskpilot` | conteneur Azure, avec un budget d'alerte de 5 € |
| Projet Foundry | `proj-riskpilot` | espace de travail, région Sweden Central, partagé avec [RiskPilot](https://github.com/abdoulhamiddiallo/riskpilot-foundry-agent) et [ReservePilot](https://github.com/abdoulhamiddiallo/reservepilot-foundry-agent) |
| Modèle | `gpt-5-mini` | déploiement Standard global, facturé uniquement à l'usage |
| Agent | `creditpilot-ble` | instructions de risque de crédit, deux outils, versions successives |
| Moteur de calcul | `moteur_credit.py` | méthode de la politique codée une fois pour toutes, exécutée par l'agent |
| Index vectoriel | `vs-politique-ble` | politique de risque de crédit découpée et vectorisée, réservée à cet agent |
| Garde-fou | `gr-riskpilot` | jailbreak et injections indirectes bloqués, contenus nuisibles filtrés |
| Évaluation | `eval-creditpilot-v1` | 12 questions, juge gpt-5-mini, Similarité, outils, qualité, sécurité |

### Pourquoi un moteur de calcul plutôt que du code improvisé

Laissé libre, un modèle réécrit ses calculs à chaque question : un jour il oublie l'actualisation, un autre il calcule à 12 mois l'ECL d'un contrat en Stage 2. Le moteur fige la méthode de la politique dans un code testé, contrôlé par une seconde implémentation indépendante : l'agent garde le raisonnement, la rédaction et les citations, et chaque chiffre devient **reproductible, rapide et auditable**.

### Les notions de risque de crédit, illustrées avec les données de la banque

| PD cumulée selon la notation et l'horizon | Le Stage 2 : 21,5 % de l'EAD, 65,7 % de l'ECL |
|:---:|:---:|
| ![PD à terme par notation](docs/images/pd_a_terme.svg) | ![EAD et ECL par stage](docs/images/ead_ecl_par_stage.svg) |

| ECL par scénario et ECL pondérée (M€) | Concentration sectorielle face aux limites |
|:---:|:---:|
| ![ECL par scénario](docs/images/ecl_par_scenario.svg) | ![Concentration sectorielle](docs/images/concentration_sectorielle.svg) |

| CET1 net des pertes attendues, grand risque et ratio CET1 : officiel contre scénario adverse |
|:---:|
| ![CET1, grand risque et ratio CET1](docs/images/cet1_grand_risque.svg) |

---

## 🛠️ Stack technique

| Domaine | Technologies |
|---|---|
| Plateforme AI | Microsoft Foundry, Foundry Agent Service, nouveau portail Foundry |
| Modèles | gpt-5-mini (agent et juge), text-embedding-3-large (index vectoriel) |
| Outils de l'agent | Interpréteur de code avec moteur de calcul, recherche de fichiers (RAG) |
| Sécurité | Garde-fous Foundry : Prompt Shields, injections indirectes, filtres de contenu |
| Qualité | Évaluations Foundry : Similarité, Qualité d'utilisation des outils, Qualité de résultat, sécurité |
| Code | Python, SDK `azure-ai-projects`, `azure-identity`, NumPy, pandas, SciPy, openpyxl |
| Risque de crédit | IFRS 9 (staging, ECL à 12 mois et à maturité, pondération par scénarios), chaînes de Markov, formule IRB de Bâle, RWA, CET1, grands risques, indice de Herfindahl |
| Gouvernance des coûts | Budget Azure à 5 € avec alertes à 80 % et 100 % |

---

## 📂 Structure du dépôt

```
creditpilot-foundry-agent/
├── agent/
│   ├── instructions_agent.txt             instructions complètes de l'agent
│   ├── moteur_credit.py                   moteur de calcul à joindre à l'interpréteur de code
│   ├── appel_agent.py                     appel de l'agent depuis Python (SDK Foundry)
│   └── requirements.txt
├── donnees/
│   ├── portefeuille_credits.csv           80 crédits d'entreprises
│   ├── matrice_migration.csv              migrations annuelles des notations N1 à N8 vers D
│   └── scenarios_macro.csv                scénarios central, adverse, favorable
├── politique/
│   └── Politique_Risque_Credit_BLE.pdf    staging, ECL, capital, limites, escalade
├── evaluation/
│   ├── eval_creditpilot.jsonl             12 questions et réponses de référence
│   ├── synthese_evaluation.csv            taux de réussite par critère
│   ├── resultats_evaluation.csv           résultat par question et par critère
│   └── reponses_agent.csv                 réponses de l'agent face aux références
├── outils/
│   ├── verifier_credit.py                 seconde implémentation et contrôle croisé du moteur
│   ├── generer_donnees.py                 génération reproductible des données
│   └── requirements.txt
└── docs/
    ├── Guide_Foundry_CreditPilot_Public_3.pdf    guide pas à pas en 10 étapes
    └── images/
```

---

## 🚀 Reproduire le projet

Le guide complet explique les bases du risque de crédit en deux pages, puis détaille chaque clic, chaque valeur à saisir et chaque résultat attendu, jusqu'aux résultats de l'évaluation.

<div align="center">

[![Aperçu du guide CreditPilot : couverture, vue d'ensemble, bases du risque de crédit et résultats](docs/images/guide_apercu.png)](https://github.com/abdoulhamiddiallo/creditpilot-foundry-agent/raw/main/docs/Guide_Foundry_CreditPilot_Public_3.pdf)

**[📘 Télécharger le guide en PDF (10 pages)](https://github.com/abdoulhamiddiallo/creditpilot-foundry-agent/raw/main/docs/Guide_Foundry_CreditPilot_Public_3.pdf)**

</div>

En résumé :

| Étape | Où | Ce que vous faites |
|:---:|---|---|
| 1 | `ai.azure.com` | créer le projet `proj-riskpilot`, puis un budget de 5 € |
| 2 | Découvrir › Modèles | déployer `gpt-5-mini` |
| 3 | Build › Agents | créer `creditpilot-ble` et coller [`agent/instructions_agent.txt`](agent/instructions_agent.txt) |
| 4 | Outils › Interpréteur de code | joindre [`agent/moteur_credit.py`](agent/moteur_credit.py) et les trois fichiers de [`donnees/`](donnees) |
| 5 | Outils › Charger des fichiers | indexer la [politique](https://github.com/abdoulhamiddiallo/creditpilot-foundry-agent/raw/main/politique/Politique_Risque_Credit_BLE.pdf) dans `vs-politique-ble` |
| 6 | Garde-fous | créer ou partager `gr-riskpilot` |
| 7 | Playground | poser les questions de test et comparer aux résultats clés |
| 8 | Évaluations | évaluer avec [`evaluation/eval_creditpilot.jsonl`](evaluation/eval_creditpilot.jsonl) |
| 9 | Terminal | appeler l'agent avec [`agent/appel_agent.py`](agent/appel_agent.py) |
| 10 | Portail Azure | tout fermer : rien ne facture à l'arrêt |

> Vous avez déjà construit [RiskPilot](https://github.com/abdoulhamiddiallo/riskpilot-foundry-agent) ou [ReservePilot](https://github.com/abdoulhamiddiallo/reservepilot-foundry-agent) ? Passez directement à l'étape 3 : même groupe de ressources, même projet, même modèle, même garde-fou.

💶 **Coût :** l'agent ne coûte rien en lui-même. Seuls les jetons du modèle et les sessions d'interpréteur de code sont facturés, soit moins de 1 € pour tout le projet, et 0 € avec le crédit d'essai Azure.

### Appeler l'agent depuis Python

```bash
pip install -r agent/requirements.txt
az login
python agent/appel_agent.py
```

---

## 🔬 Vérifier les chiffres sans AI

Les réponses de référence de l'évaluation ont été calculées hors de l'agent, par une **seconde implémentation** écrite indépendamment du moteur (avec la loi normale de SciPy pour la formule IRB). Le script recalcule tout à partir des fichiers, puis vérifie que le moteur de l'agent donne exactement les mêmes résultats :

```bash
pip install -r outils/requirements.txt
python outils/verifier_credit.py
```

```
Stage 1 : 59 contrats · EAD 221 390 000 € (75,98 %) · ECL 702 283 €
Stage 2 : 19 contrats · EAD 62 730 000 € (21,53 %) · ECL 4 338 163 €
Stage 3 : 2 contrats · EAD 7 260 000 € (2,49 %) · ECL 1 560 900 €
Ratio CET1 : 12,44 % · grand risque Foncière des Trois Frontières : 24,37 %

CONTRÔLE CROISÉ AVEC agent/moteur_credit.py
  ✓ ECL pondérée                    6 601 346 €   écart 0 €
  ✓ ECL scénario adverse            9 976 857 €   écart 0 €
  ✓ RWA crédit                    191 918 195 €   écart 0 €
  ✓ CET1                           35 698 654 €   écart 0 €
  ...
8 indicateurs sur 8 identiques à l'euro près.
```

Le moteur s'exécute aussi seul et affiche la note complète, tableau des limites et actions comprises : `python agent/moteur_credit.py`. Les données sont reproductibles à l'octet près avec `python outils/generer_donnees.py`.

---

## 📐 Méthodologie

| Étape | Règle appliquée (articles 2 à 5 de la politique) |
|---|---|
| Stage 3 | notation D ou retard de 90 jours ou plus |
| Stage 2 | retard de plus de 30 jours, ou dégradation de 3 crans ou plus depuis l'octroi, ou notation N7 ou N8 |
| EAD | encours tiré + 50 % de l'engagement non tiré |
| LGD | hypothèque 20 %, nantissement 35 %, caution 40 %, aucune sûreté 45 % |
| PD à terme | PD cumulée à t ans = case D de la matrice de migration à la puissance t |
| Scénarios | PD ajustée = 1 - (1 - PD)^multiplicateur (1,00 · 1,80 · 0,75) ; LGD + 0, + 7 ou - 3 points ; poids 50, 30 et 20 % |
| ECL | Σ PD marginale(t) × LGD × EAD × (1 + taux effectif)^-(t - 0,5), sur 1 an en Stage 1 et la maturité restante en Stage 2 ; LGD × EAD en Stage 3 |
| Capital IRB | K = LGD × [N((N⁻¹(PD) + √R · N⁻¹(0,999)) / √(1 - R)) - PD] × (1 + (M - 2,5) b) / (1 - 1,5 b), PD plancher 0,05 % ; RWA = 12,5 × K × EAD |
| CET1 | 42 300 000 € avant dépréciations, moins l'ECL retenue ; RWA totaux = RWA crédit + 95 000 000 € |
| Limites | Stage 2 : 18 / 24 % · Stage 3 : 3 / 5 % · grand risque : 10 / 25 % du CET1 · premier secteur : 25 / 30 % · CET1 : sous 12 / sous 10,5 % |

> La Banque Lorraine des Entreprises est fictive. Ses données sont simulées et calibrées sur des ordres de grandeur réalistes d'un portefeuille de crédits aux entreprises : notations, migrations, sûretés, taux et maturités.

---

## ✅ Conclusion

CreditPilot montre ce qu'un agent AI doit être pour entrer dans une direction des risques bancaire : **exact**, parce que chaque chiffre vient d'un moteur validé par une seconde implémentation ; **traçable**, parce que chaque statut cite son article et chaque action son délai ; **sûr**, parce qu'il refuse de reclasser un crédit pour embellir un résultat et qu'un garde-fou le protège ; **mesuré**, parce qu'une évaluation sur des réponses de référence prouve sa qualité avant toute mise en service.

---

## 💡 Mot de la fin

> En risque de crédit, la perte la plus coûteuse est celle qu'on n'a pas vue venir : un bon agent la chiffre, la relie au capital et ose dire non.
>
> **Construire pour explorer. Explorer pour comprendre. Et apprendre en chemin.**

---

## 👤 Auteur

**Abdoul Hamid Diallo** · Microsoft Data & AI Engineer

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Abdoul_Hamid_Diallo-0A66C2?style=flat-square&logo=linkedin&logoColor=white)](https://www.linkedin.com/in/abdoul-hamid-diallo-fabric-data-engineer/)
[![GitHub](https://img.shields.io/badge/GitHub-abdoulhamiddiallo-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/abdoulhamiddiallo)

**Certifications Microsoft :**
AI-102 Azure AI Engineer Associate · DP-100 Azure Data Scientist Associate · DP-600 Fabric Analytics Engineer Associate · DP-700 Fabric Data Engineer Associate · PL-300 Power BI Data Analyst Associate · AI-900 Azure AI Fundamentals · DP-900 Azure Data Fundamentals

**Dans la même série :** [RiskPilot](https://github.com/abdoulhamiddiallo/riskpilot-foundry-agent), le risque de marché d'un fonds de 50 M€ · [ReservePilot](https://github.com/abdoulhamiddiallo/reservepilot-foundry-agent), le provisionnement actuariel et Solvabilité II.
