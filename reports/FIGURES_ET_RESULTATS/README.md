# Figures et résultats du mémoire scientifique

Les CSV contiennent des mesures réelles du run `77162f55317be0844ec3`, ou des agrégats d'EDA recalculés sur son cache canonique. Aucun modèle n'a été entraîné pour produire ces livrables. Les taux figurent en fractions 0–1, sauf unité explicitement indiquée. Les exemples sont pseudonymisés et les identifiants privés restent hors de ce dossier.

## Provenance des figures du mémoire

La numérotation du mémoire suit l'ordre de lecture ; les noms de fichiers hérités restent stables.

| Figure du mémoire | Fichier | Source numérique et population | Script de calcul/rendu |
|---|---|---|---|
| 1 | 08_EDA_sources_periodes.png | EDA_period.csv et EDA_source_name.csv ; 67 502 scans bruts | describe_scientific_data.py |
| 2 | 09_disponibilite_modalites.png | EDA_classes.csv et EDA_summary.json ; définition des masques, corpus brut | describe_scientific_data.py |
| 3 | 01_modeles_AP.png | table_28_common.csv ; six centraux, 13 212 cas communs | finalize_analysis.py, figure historique vérifiée |
| 4 | 02_combinaisons_heatmap.png | table_28_common.csv ; onze sous-ensembles×deux familles | finalize_analysis.py, figure historique vérifiée |
| 5 | 10_compromis_comptages.png | table_28_common.csv ; FP/FN M1 et M2 primary sur test commun | describe_scientific_data.py |
| 6 | 03_compromis_FPR_rappel.png | operating_points_frozen.csv ; points enregistrés et seuils hors test | finalize_analysis.py |
| 7 | 04_precision_recall.png | Registre privé predictions.csv, restreint aux common_cohort_ids.csv ; test commun | finalize_analysis.py ; la courbe exige les scores individuels locaux |
| 8 | 06_bigdata_temps.png | benchmark_summary.csv ; médianes de 24 répétitions de mesure | finalize_spark.py et finalize_analysis.py ; aucune JVM exécutée pour le rapport |
| 9 | 07_bigdata_debit.png | benchmark_summary.csv ; débit tabulaire mesuré | finalize_spark.py et finalize_analysis.py |

La figure historique `05_confusion_matrices.png` est également conservée comme complément. Les matrices numériques du mémoire font foi et sont entièrement vérifiées dans `verification_28.csv`.

## Principales tables

- `table_28_common.csv` : scores et matrices sur exactement les mêmes 13 212 scans.
- `six_models_full_test.csv` : six centraux sur le test complet de 13 439 scans, périmètre distinct.
- `table_22_available.csv` : couverture et résultats disponibles par variante, ne pas confondre les cohortes.
- `paired_modality_contributions.csv` : 65 contrastes appariés, 200 rééchantillonnages de groupes, sans correction de multiplicité.
- `operating_points_frozen.csv` : politiques primary et recall85 provenant de calibration ; pas de réglage sur test.
- `error_strata.csv` : agrégats par dimension, avec dénominateurs par classe ; aucun contenu de capture.
- `cas_erreurs_anonymises.csv` : 20 lignes de décisions, échantillon déterministe illustratif, sans revue humaine des labels.
- `dictionnaire_21_features.csv` : champs et opérations extraits du code réellement implémenté.
- `split_identity_audit.csv` : contrôles recalculés des huit identités disponibles.
- `EDA_*.csv` et `EDA_summary.json` : corpus brut, avant quarantaine et partitionnement.

La disponibilité d'une image n'est pas sa qualité ; les captures uniformes sont conservées dans une statistique séparée. Toutes les durées brutes fin−début négatives sont signalées, sans correction de signe. Les dates affichées au jour dans le mémoire restent complètes dans les CSV.

## Reproduction

Les scripts sont situés dans `scripts/`. Le recalcul des métriques, de l'EDA et des courbes PR requiert les artefacts privés et le cache actif. Le mémoire, les agrégats et modèles d'inférence publiables restent utilisables sans redistribuer le corpus. Les PDF de sources et rendus de contrôle sont conservés dans `artifacts/scientific_writing/`, ignoré par Git. La conversion PDF utilise ReportLab et une police Segoe UI ou DejaVu Sans ; le contrôle visuel utilise un outil PDF local optionnel.

Le manifeste `manifest.json` décrit les empreintes des fichiers de ce dossier. Il vérifie leur intégrité, sans transformer les limites scientifiques en garanties.
