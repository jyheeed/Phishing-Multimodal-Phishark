# Checklist finale — PhiShark2026

**Note de traçabilité, 26 novembre 2026 :** cette checklist conserve la validation historique de la restitution précédente. Le mémoire scientifique enrichi, son export PDF et leurs contrôles actuels sont décrits dans [VERIFICATION_SCIENTIFIQUE.md](VERIFICATION_SCIENTIFIQUE.md). Les anciennes indications de pagination ou d'export ci-dessous ne décrivent pas la nouvelle version.

24novembre2026. Les livrables de restitution sont produits. Les limites restantes sont déclarées ; aucun entraînement répété, aucun seuil ni label changé.

| Contrôle | Statut | Preuve | Correction / vérification | Limite restante |
|---|---|---|---|---|
| 28 configurations présentes | PASS | table_28_common.csv ; artifact_inventory.csv | 28 métriques recalculées depuis prédictions | Comparaisons internes exploratoires, pas de gagnant final indépendant |
| Même cohorte et mêmes labels | PASS | common_cohort_ids.csv :13212 identifiants uniques ; alignement des28 registres | Cohorte reconstruite depuis la disponibilité réelle des quatre modalités | Test complet13439 présenté séparément |
| Cohortes disponibles et couverture séparées | PASS | table_22_available.csv ; table_28_common.csv | 22 métriques propres recalculées ; abstentions conservées | Ne pas comparer directement des populations différentes |
| Seuils issus de calibration | PASS | calibration_verification.csv :56 politiques concordantes | Recalcul sur calibration sauvegardée ; seule inférence M2, aucun fit | Tolérance numérique absolue1e-6 ; seuils inchangés |
| Checkpoints et résultats existants préservés | PASS | preserved_run_hashes.json ; source historique archivée | Aucune écriture dans le run entraîné ; originaux conservés | Empreintes des artefacts inventoriés vérifiées |
| Implémentation FULL et signature conservées | PASS | artifacts/provenance/executed_full_code.json ; frozen.json | Copie intégrale exécutée107cellules ; reprise explicite dans même environnement | FULL_REPLAY non lancé lors de la finalisation |
| Notebook unique PRESENTATION exécuté sans modèles | PASS | presentation_test.json ; unified_notebook.json ; notebook principal avec sorties | 225cellules,122decode ; aucun import du code projet ou des modèles requis | Démo enregistrée sur test, pas une nouvelle capture ; calcul FULL visible mais non relancé |
| Tests légers | PASS | final_tests.xml :12réussites,0échec | Artefacts, cohortes, unification, opt-in FULL historique, démo, signatures et structure PPTX testés | Ne remplace pas une nouvelle expérience scientifique |
| Cinq figures scientifiques et deux Big Data | PASS | reports/figures ; scripts/finalize_analysis.py | Même table et mêmes scores vérifiés ; formats PNG220dpi et PDF | Les graphiques Big Data n’inventent aucune série Spark |
| Soutenance15diapositives | PASS | PPTX ; SCRIPT_ORAL.md ; QUESTIONS_JURY.md | 15rendus inspectés ;4graphiques natifs, textes et notes éditables | Graphiques arrondis pour lecture ; chiffres exacts dans CSV |
| Conclusions cohérentes et références vérifiées | PASS | PHISHARK2026_RAPPORT_FINAL.md ; ANALYSE_MODALITES.md | Cohortes distinguées ; limites de multiplicité et de causalité explicites | Références scientifiques ne servent pas de résultats locaux |
| Sujet enseignant inspecté | PASS | artifacts/specification/subject.pdf et subject.txt | Copie locale intégrale lue, trois RQ reprises | Nom exact Downloads Projet_1_Phishing_multimodal(1).pdf indisponible ; copie locale utilisée |
| RQ2 — généralisation temporelle | BLOCKED | temporal_feasibility.json ; temporal_class_counts_before_after_purge.csv | Protocole reproduit sans réseaux ;1511phishing et0bénin en calibration | La généralisation temporelle n’a pas pu être démontrée avec le corpus actuel |
| RQ3 — Spark | BLOCKED | bd3/status.json ; scripts/finalize_spark.py | Contrôle en processus séparé sans PyTorch ; JVM non lancée | RAM disponible 0.82Go <2Go requis ; aucun temps Spark |
| Pandas/PyArrow existant | PASS | benchmark_summary.csv ; run/bd2/measurements.csv | 24mesures conservées, médianes et étendues | Cache OS non contrôlé ; entrée Parquet dérivée, pas ZIPbruts |
| Interface locale et parité des scores | PASS | artifacts/interface/tests.xml ; status.json ; reports/TESTER_INTERFACE.md | 8tests réussis ;6modèles et22combinaisons concordent sur une vraie capture ; serveur local sain | Les exemples historiques ne constituent pas un nouveau lot indépendant ; URL seule = U1uniquement |
| Validation externe prospective | BLOCKED | Rapport section13 et perspectives | Plan de collecte équilibrée et lot scellé proposé | Aucun nouveau lot indépendant disponible dans le projet |

## Utilisation

Ouvrir uniquement le notebook final principal, en mode PRESENTATION, sélectionner my_env et redémarrer le noyau avant Tout exécuter. Le fichier contient désormais aussi le code FULL et l’analyse finale, sans import de src/ ni exécution d’un autre notebook. Les copies historiques sont conservées sans être nécessaires à son exécution. Un FULL volontairement demandé est une nouvelle version signée distinctement ; les anciens checkpoints ne sont pas falsifiés pour lui attribuer une compatibilité fictive. Aucun FULL requis pour la soutenance.

Pour Spark :fermer les applications inutiles ou utiliser une machine suffisante, puis exécuter scripts/finalize_spark.py dans un processus séparé. Le contrôle de ressources reste actif. Les rapports actuels n’annoncent pas une comparaison Spark réalisée.

Le nom exact du PDF enseignant cité n’étant plus accessible dans Downloads, la copie du sujet conservée dans le projet a été utilisée. Les références scientifiques du rapport ont été vérifiées sur leurs sources primaires.
