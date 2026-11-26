"""Scientific report and defense narrative generated from verified current-run tables."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.runtime'))
import pandas as pd


def md(table):
    def val(x):
        if pd.isna(x):return '—'
        return (f'{x:.4f}' if isinstance(x,float) else str(x)).replace('|','/')
    return '\n'.join(['| '+' | '.join(table.columns)+' |','| '+' | '.join(['---']*len(table.columns))+' |']+
        ['| '+' | '.join(val(x) for x in r)+' |' for r in table.itertuples(index=False,name=None)])


def main():
    out=ROOT/'artifacts/finalization';reports=ROOT/'reports';presentation=ROOT/'presentation'
    presentation.mkdir(exist_ok=True)
    data=pd.read_csv(out/'table_28_common.csv');six=pd.read_csv(out/'six_models_full_test.csv')
    paired=pd.read_csv(out/'paired_modality_contributions.csv');bench=pd.read_csv(out/'benchmark_summary.csv')
    summary=json.loads((out/'analysis_summary.json').read_text());temporal=json.loads((out/'temporal_feasibility.json').read_text());spark=json.loads((out/'bd3/status.json').read_text())
    run=ROOT/summary['run'];idx=data.set_index('model');fidx=six.set_index('model')
    selected=['LATE__URL+HTML','LINEAR_EMBED__URL+HTML','LATE__URL+IMAGE','LINEAR_EMBED__URL+IMAGE',
        'LATE__HTML+IMAGE','LINEAR_EMBED__HTML+IMAGE','LATE__URL+TECH','LINEAR_EMBED__URL+TECH',
        'LATE__HTML+TECH','LINEAR_EMBED__HTML+TECH','LATE__URL+HTML+TECH','LINEAR_EMBED__URL+HTML+TECH',
        'LATE__URL+HTML+IMAGE','LINEAR_EMBED__URL+HTML+IMAGE','LATE__URL+HTML+IMAGE+TECH','LINEAR_EMBED__URL+HTML+IMAGE+TECH']
    keypairs=paired.loc[((paired.model.isin(['M1','M2']))&paired.reference.isin(['U2','M1']))|
        (paired.added_modality.eq('IMAGE')&paired.reference.str.endswith('URL+HTML+TECH'))]
    scope=f"Cohorte commune : {summary['common_n']} scans, {summary['group_count']} groupes sites/contenus, prévalence phishing {summary['common_prevalence']:.4f}. Test complet distinct : {summary['test_n']} scans."
    training=pd.DataFrame(summary['training'])[['model','best_epoch','validation_AP','train_seconds','parameters','device']]
    text=f'''# PhiShark2026 — Rapport technique final

Détection multimodale du phishing · CRISP-DM · 24 novembre 2026

**Périmètre :** uniquement le FULL exécuté dans le nouveau projet, run `77162f55317be0844ec3`. Aucun entraînement relancé pour cette finalisation. Les anciennes expériences externes au projet ne sont pas utilisées. Les valeurs ci-dessous sont recalculées depuis les prédictions et les seuils gelés.

## 1. Introduction et problématique

Une URL peut présenter des indices suspects alors que sa capture montre une erreur HTTP ou une page inactive. À l'inverse, une page visuellement ordinaire peut collecter des identifiants. Le problème étudié consiste à combiner plusieurs sources d'information sans confondre la réputation annotée de l'URL, le contenu capturé et les conditions de collecte. Un faux positif interrompt l'accès à un site légitime ; un faux négatif laisse passer un site étiqueté phishing.

Le système produit une classification binaire à partir des preuves déjà capturées. Il ne démontre pas qu'un phishing est actif à l'instant de la soutenance. Aucun téléchargement de site ni exécution de JavaScript n'est nécessaire à l'analyse finale. Une AP élevée ne suffit pas à certifier un système déployable : le rappel, les fausses alertes, la couverture et les écarts de population doivent être discutés.

## 2. Objectifs et questions de recherche

Le sujet local `artifacts/specification/subject.pdf` formule trois questions. La copie téléchargée sous le nom exact `Projet_1_Phishing_multimodal(1).pdf` n'est plus disponible à son ancien emplacement ; la copie du sujet conservée dans le projet a été lue intégralement.

- **RQ1 :** la fusion multimodale surpasse-t-elle chaque modalité prise isolément ?
- **RQ2 :** généralise-t-elle mieux dans le temps sur des campagnes ultérieures ?
- **RQ3 :** quel coût de preprocessing, d'entraînement et de traitement selon le volume et le moteur Big Data ?

Le critère n'est pas d'obtenir une valeur prédéfinie proche de1. Il est de produire une comparaison contrôlée et reproductible, avec des limites explicites. Le test a déjà été examiné : les 28 comparaisons restent exploratoires. Aucun gagnant final n'est choisi rétroactivement pour annoncer une validation indépendante.

## 3. État de l'art et architectures retenues

Le papier PhiShark2026 [1] décrit un corpus de preuves multi-couches et distingue les preuves indisponibles des observations négatives. Cette conception motive la conservation des modalités manquantes et des métadonnées de capture. L'effectif et les classes utilisés ici sont vérifiés localement, sans supposer que l'article garantit l'intégrité de chaque archive de cette copie.

Aljofey et al. [2] combinent des représentations URL et HTML avec XGBoost. Cette étude justifie d'examiner leur complémentarité, sans importer leurs scores dans notre benchmark. Phishpedia [3] utilise la reconnaissance de logos et la comparaison avec des marques légitimes ; PhishIntention [4] ajoute une analyse de l'intention de collecte d'identifiants et des interactions avec la page. Notre CNN global entraîné sur petites images n'implémente ni cette reconnaissance de marque ni ces interactions. Sa faible performance ne contredit donc pas ces travaux.

Nous retenons des réseaux compacts et deux familles de fusion pour rendre le protocole explicable avec les ressources locales. Aucun résultat d'article n'est présenté comme un score obtenu sur PhiShark2026. Les références de cette section ont été vérifiées sur les pages des éditeurs ou des auteurs ; les autres titres suggérés dans le sujet ne sont pas cités comme preuves sans vérification.

## 4. Méthodologie CRISP-DM

La démarche comporte les six phases décrites par CRISP-DM [5]. Business Understanding définit la cible et les coûts d'erreur. Data Understanding recense classes, périodes, sources et captures. Data Preparation extrait, aligne et partitionne. Modeling entraîne les branches puis les fusions selon les rôles autorisés. Evaluation compare métriques, erreurs et incertitude. Deployment fournit un prototype local et prépare une évaluation indépendante.

Le notebook final unique contient225cellules, dont122decode : pipeline FULL, analyses finales et restitution. Il privilégie `PRESENTATION`, qui recharge les artefacts vérifiés sans importer ni entraîner les réseaux. En `FULL_EXPERIMENT`, le code intégré s'exécute directement, sans importer src/ ni exécuter un autre notebook. Cette nouvelle enveloppe possède sa propre signature et produit une expérience distincte ; elle ne falsifie pas la compatibilité des anciens checkpoints. Les copies historiques et les résultats déjà exécutés sont conservés en sauvegarde avec leur provenance d'origine.

## 5. Présentation du dataset PhiShark2026

Le CSV contient 67 502 scans uniques : 34 115 bénins et 33 387 phishing. Les observations s'étendent du23avril au15août2026. Les 67 502 archives sont présentes. Une archive en désaccord avec le manifeste d'origine est en quarantaine logique, sans modification de son label : 67 501 observations sont admissibles avant la partition groupée.

Les sources de collecte et la classe sont parfaitement associées dans l'audit CSV global (V de Cramér=1). La période est également très associée au label. Ces relations sont des avertissements sur la composition du corpus, pas des features autorisées. Elles peuvent se refléter indirectement dans les URL, les captures et la disponibilité des preuves. On ne peut pas attribuer une fraction causale précise de l'AP aux artefacts avec ces seules associations.

Les durées négatives entre les horodatages enregistrés sont conservées comme anomalies de sémantique ou d'instrumentation à clarifier ; les dates ne sont ni inversées ni remplacées. Les pages indisponibles, uniformes ou HTTP404 ne sont pas requalifiées automatiquement en bénignes. Le label décrit la réputation de l'URL au moment de son annotation.

## 6. Préparation des données et traitement Big Data

Le pipeline lit les ZIP originaux en contrôlant les membres, les tailles et les empreintes. Il extrait le texte visible du HTML sans exécuter les scripts, transforme les captures en RGB96×96 et calcule21variables techniques JSON selon une allowlist. Les données absentes deviennent des NaN et des masques explicites, pas des zéros inventés. Le statut HTTP, la source, l'identifiant, la classe, les dates et l'hébergeur sont hors X technique.

Les21features couvrent la présence ou le nombre de preuves DNS, WHOIS, IP, ports, TLS, métadonnées de page, technologies, liens, redirections et fichiers de conformité. Les champs de date WHOIS sont des indicateurs de présence, pas des âges de domaine calculés. Les définitions exactes et les rapports de corrélation sont conservés dans le notebook FULL et `feature_audit/`.

Les URL du CNN sont transformées en hôte+chemin+query, sans schéma HTTP/HTTPS ni fragment. La même transformation sert au vocabulaire, aux empreintes d'entrée, à l'entraînement et à l'inférence. Cela retire un raccourci précis ; l'hôte reste observable et les biais d'hébergement ne disparaissent pas.

Parquet/PyArrow fournit un stockage typé et compressé. Les groupes relient sites/locataires, URL normalisées, contenus et entrées encodées identiques. Les collisions après vocabulaire sont traitées par des fusions monotones de groupes ; l'algorithme ne s'arrête plus arbitrairement après huit passages. Aucun identifiant de groupe contrôlé ne traverse les cinq rôles. Les quasi-doublons non exacts restent une limite : un contrôle d'empreintes ne prouve pas leur absence.

Les médianes, moyennes, écarts-types et vocabulaires sont ajustés exclusivement sur train_encoder. Les embeddings de fusion sont normalisés sur train_fusion. Les lignes et labels sont vérifiés contre le manifeste et le CSV originaux.

## 7. Modèles unimodaux

**U1 et U2 :** embedding de dimension24, convolution1D24→48 de noyau5 puis48→32 de noyau3, ReLU, réduction de longueur par stride2, max-pooling adaptatif et tête de classification avec dropout0,25. U1 encode des caractères d'URL de longueur256 ; U2 encode jusqu'à1024tokens de texte visible, avec vocabulaire limité à16000 et symboles PAD/UNK.

**U3 :** trois convolutions2D3→24→48→64, BatchNorm et ReLU, pooling adaptatif2×2 puis projection256→64→32 avec dropout0,2. L'entrée96×96 permet une extraction visuelle compacte, sans préentraînement sur des logos ou un grand corpus d'images.

**U4 :** les21mesures numériques et21indicateurs manquants forment42entrées. Un MLP42→64→32→1 produit un score. Les sorties des quatre branches fournissent chacune32valeurs d'embedding.

Optimisation : AdamW, learning rate0,001, weight decay0,0001, BCEWithLogits pondérée selon la proportion de classes du train propre à la branche, batch32, au plus10époques et patience2. Le meilleur checkpoint maximise l'AP de validation. Aucun checkpoint n'est choisi sur le test.

{md(training)}

Les temps ci-dessus proviennent des journaux d'entraînement, pas d'un nouveau chronométrage. Ils ne sont pas le coût complet de capture ni le coût d'extraction des représentations de fusion.

## 8. Méthodes de fusion multimodale

**M1 : fusion tardive.** Les probabilités des modalités disponibles sont moyennées avec des poids égaux renormalisés. Aucun poids supplémentaire n'est appris.

**M2 : fusion intermédiaire.** Quatre embeddings gelés de32valeurs et quatre masques donnent132entrées. Un MLP132→64→32→1 est entraîné uniquement sur train_fusion, disjoint du train des encodeurs. Il ne s'agit pas d'un entraînement profond conjoint de toutes les branches.

**Études supplémentaires.** Six paires, quatre triplets et le quadruplet sont traités par LATE et LINEAR_EMBED. La seconde méthode est une régression logistique sur embeddings gelés, après StandardScaler ajusté sur train_fusion, avec C=1, max_iter=500 et class_weight=balanced. Cela donne22configurations additionnelles, pas22CNN nouvellement entraînés.

Les combinaisons utilisent les modalités demandées réellement disponibles. Si aucune n'est présente, elles s'abstiennent. La cohorte complète élimine cette différence de disponibilité pour la comparaison principale. La liste des configurations et les hyperparamètres sont fixés dans le code ; l'évaluation ne désigne pas un vainqueur final.

## 9. Protocole expérimental et métriques

Les fractions cibles sont50/15/10/5/20% pour train_encoder/train_fusion/validation/calibration/test. Les groupes indivisibles peuvent modifier les effectifs exacts.

{md(pd.DataFrame(summary['class_counts']))}

Le seuil primary maximise le F1 sur calibration ; en cas d'égalité exacte, le seuil le plus élevé est conservé. Le point recall85 est le seuil le plus élevé maintenant un rappel de calibration d'au moins85%. Il ne garantit pas85% sur le test. Toutes les têtes et politiques des22combinaisons sont sauvegardées avant leur inférence de test.

AP est l'average precision calculée à partir du classement des scores, non une aire trapézoïdale. ROC-AUC complète cette mesure. Précision=TP/(TP+FP), rappel=TP/(TP+FN), FPR=FP/(FP+TN), FNR=FN/(FN+TP). Le F1 combine précision et rappel. La prévalence fournit la référence de la courbe PR ; le choix de cette représentation suit notamment [6]. Les scores sigmoid ne sont pas certifiés comme probabilités calibrées : le rôle calibration sert ici aux seuils, sans calibrateur probabiliste supplémentaire.

Les56seuils gelés (28configurations ×2politiques) ont été recalculés à partir des représentations de calibration sauvegardées et concordent à1e-6près. Seule une inférence de la petite tête M2gelée a été nécessaire ; aucune optimisation ni modification des seuils n'a été effectuée. Les preuves sont dans `calibration_verification.csv`.

Les nouveaux intervalles sont appariés sur5230groupes sites/contenus, avec200tirages et graine42. Les rangs sont conservés et les groupes rééchantillonnés avec remise. Ces intervalles sont descriptifs, non corrigés pour les nombreuses comparaisons, sans réplication multi-graines des entraînements. L'incertitude d'un changement de corpus ou de campagne n'est pas couverte.

## 10. Résultats des28configurations

{scope} La cohorte commune contient6544phishing et6668bénins, couverture98,31%. Les tableaux des observations disponibles sont fournis séparément dans `artifacts/finalization/table_22_available.csv`.

{md(data[['model','modalities','fusion','AP','ROC_AUC','precision','recall','F1','FPR','FNR','FP','FN','coverage']])}

![Figure 1 — AP des six modèles sur les mêmes scans](figures/01_modeles_AP.png)

![Figure 2 — AP des11sous-ensembles et deux méthodes](figures/02_combinaisons_heatmap.png)

Les six modèles ont également été mesurés sur le test complet de13439scans. À titre de distinction, M1 y a AP0,97122, contre0,97220 sur la cohorte commune ; M2 a AP0,97853, contre0,97896. Ces valeurs ne doivent pas être mélangées avec une comparaison calculée sur une autre population.

## 11. Analyse des modalités, erreurs et seuils — réponse à RQ1

### 11.1 Complémentarité et incertitude

{md(data.set_index('model').loc[selected,['AP','precision','recall','FPR','FN']].reset_index())}

L'URL encode des motifs d'adresse et reste sensible au domaine et au chemin. Le HTML apporte du contenu visible et obtient la meilleure AP unimodale sur la cohorte commune (0,93393). La combinaison URL+HTML améliore le classement, ce qui soutient leur complémentarité sur ce test interne. Les signaux techniques apportent un contexte complémentaire ; la présence de champs peut aussi refléter la collecte.

Le CNN image seul obtient AP0,59276 sur la cohorte commune, pour une référence de prévalence0,49531. Sa représentation est donc peu discriminante dans cette expérience. Les captures compressées96×96, le réseau compact entraîné depuis zéro et les pages uniformes/erreurs constituent des hypothèses d'explication ; aucune n'est isolée causalement. Les recherches visuelles utilisant logos et marques ne sont pas reproduites par ce CNN global.

{md(keypairs[['model','reference','AP_difference','lower95','upper95']])}

Ajouter IMAGE à URL+HTML+TECH diminue l'AP moyenne tardive de0,00072, avec un intervalle englobant zéro. Dans LINEAR_EMBED, la diminution observée est0,00392, intervalle approximatif[-0,00879;-0,00037]. Cette dernière observation suggère une dégradation locale du classement, sans démonstration universelle ni correction de multiplicité. L'AP0,97943 de la tête linéaire à trois modalités est proche de M2à0,97896 ; l'écart d'environ0,00047 n'est pas une preuve de supériorité.

Deux modalités peuvent déjà approcher quatre : URL+HTML par embeddings linéaires est à AP0,97035, tandis que le quadruplet linéaire est à0,97551. « Proche » signifie ici un écart descriptif d'AP, pas une équivalence statistique démontrée ni un compromis d'erreurs identique.

### 11.2 Faux positifs et faux négatifs

Sur le test complet, M1 produit842FP et401FN ; M2 produit148FP et1023FN. Passer de l'un à l'autre évite694fausses alertes mais laisse622phishing supplémentaires non détectés, aux seuils déjà gelés. L'AP plus élevée de M2 ne suffit donc pas à le déclarer meilleur pour toutes les applications. Les mêmes conclusions qualitatives apparaissent sur la cohorte commune (M1:807FP/390FN ; M2:141FP/1006FN).

![Figure 3 — Compromis FPR et rappel aux seuils figés](figures/03_compromis_FPR_rappel.png)

![Figure 4 — Courbes PR et prévalence de référence](figures/04_precision_recall.png)

![Figure 5 — Matrices de confusion, cohorte commune](figures/05_confusion_matrices.png)

`error_strata.csv` rapporte les erreurs par hébergeur, statut HTTP, mois, source, état HTML et screenshot, avec dénominateurs bénins/phishing. Les dimensions source et classe étant confondues, un taux de faux positifs sur une source entièrement phishing n'est pas défini. Les petits sous-groupes ne doivent pas être interprétés à partir de seuls nombres d'erreurs.

Une file de48exemples de revue humaine est fournie dans `manual_error_review_queue.csv`. Elle distingue l'erreur de prédiction d'une éventuelle erreur d'annotation ; aucun label n'est changé. Pour chaque cas, examiner la réputation de l'URL, la date et le contenu réellement capturé. Un404ne prouve pas que le label est faux. Les points de fonctionnement supplémentaires sont ceux déjà figés sur calibration, dans `operating_points_frozen.csv`, sans nouveau seuil optimisé sur test.

### 11.3 RQ1 — conclusion

**Oui pour le classement AP sur ce benchmark interne groupé :** M1etM2 dépassent les quatre unimodaux sur les mêmes13212scans. Les intervalles appariés de leur différence avec U2 sont strictement positifs dans les200rééchantillonnages. **Aucune supériorité générale n'est démontrée :** l'intervalle de M2−M1recouvre zéro ; les seuils produisent des compromis FP/FN différents ; les comparaisons sont exploratoires et le test n'est pas externe. L'image n'apporte pas un gain systématique ; URL, HTML et technique forment une combinaison particulièrement informative dans cette exécution.

## 12. Comparaison pandas/PySpark et coût — RQ3

L'extraction Python des archives est une phase distincte :7709,59secondes enregistrées (environ128,49minutes), incluant lecture, décodage, extraction, contrôles et création du cache. Les temps d'entraînement ci-dessus ne doivent pas lui être additionnés pour prétendre mesurer une latence d'inférence. Les coûts complets de capture réseau et des sources opérationnelles ne sont pas mesurés.

Le benchmark pandas/PyArrow comporte24mesures : quatre fractions (10,25,50,100%), trois répétitions et deux scénarios. Chaque mesure lit le même Parquet, valide les identifiants/classes, applique le même schéma, écrit en Snappy, relit et vérifie l'égalité logique exacte. Aproduit un fichier de données ; Bproduit des répertoires Hive split=role. Les temps excluent la création du fichier d'entrée et le démarrage d'un éventuel Spark ; ils incluent la validation de sortie.

{md(bench[['engine','scenario','n','repetitions','seconds_median','seconds_min','seconds_max','throughput_median','peak_rss_bytes','input_bytes','output_bytes','data_files']])}

![Temps selon le volume — pandas mesuré](figures/06_bigdata_temps.png)

![Débit selon le volume — pandas mesuré](figures/07_bigdata_debit.png)

À67501lignes, Aest mesuré à0,3075s de médiane, contre0,4048s pour B. La sortie est d'environ2,96Mo pour Aet3,09Mo pour B. Les fichiers Parquet sont beaucoup plus petits que les archives originales : ce benchmark ne mesure pas un déplacement de28Go de ZIP. Le pic RSS échantillonné vaut environ240Mo ; les pages partagées peuvent être comptées plusieurs fois et le cache OS n'est pas contrôlé. Il ne s'agit pas d'un pic matériel garanti.

PySpark4.0.5etJava17sont installés. Un processus séparé sans import PyTorch a été exécuté pour finaliser Spark. Il a constaté seulement{spark['resources']['available_ram_gb']:.2f}Go disponibles sur8,36Go physiques : **BLOCKED_RESOURCE**. Aucune JVM n'a été démarrée et aucun temps Spark n'est annoncé. La configuration préparée est local[1], heap512Mo, shuffle2partitions, UI désactivée et trois répétitions, avec au moins2Go réellement disponibles ; cette réserve ne se réduit pas à la taille du heap.

Le script `scripts/finalize_spark.py` pourra effectuer les deux moteurs sur la même configuration lorsque les ressources seront suffisantes. Il préservera les anciennes mesures. La documentation Spark [7] motive le contrôle des partitions et des petits fichiers ; elle n'est pas une preuve de vitesse sur cette machine. **RQ3 : le coût de l'extraction, des entraînements et de pandas est documenté, mais l'avantage ou le désavantage de Spark n'est pas mesuré.** local[1]oulocal[2]ne constitue pas un cluster multi-nœuds. À ce volume et pour ce périmètre, pandas est opérationnel ; il serait abusif d'affirmer une préférence de performance face à un Spark non exécuté.

## 13. Généralisation temporelle et limites — RQ2

Les frontières temporelles proviennent des quantiles fixes du corpus admissible :6juin202622:02:32UTC,14juin06:14:47UTC,28juin10:03:54UTC et7juillet22:02:17UTC. Les groupes traversant plusieurs rôles sont purgés :22064observations dans cette reconstitution du protocole initial, avant tout fitting.

{md(pd.DataFrame([dict(role=k,benign=v.get('0',0),phishing=v.get('1',0)) for k,v in temporal['counts'].items()]))}

La calibration du28juin au7juillet ne conserve que1511phishing et aucun bénin. Elle ne permet donc pas de choisir et d'évaluer un compromis binaire représentatif. La période et la composition des sources rendent les classes inégalement disponibles après purge. Déplacer les dates ou ajouter des bénins sélectionnés pour obtenir un beau score changerait le protocole après observation des résultats.

**La généralisation temporelle n'a pas pu être démontrée avec le corpus actuel.** Le résultat NOT_FEASIBLE concerne la faisabilité de ce protocole, pas l'incapacité intrinsèque des réseaux. Le test groupé protège les identités contrôlées mais mélange les périodes ; il ne démontre pas une robustesse face à de nouvelles campagnes ou à une évolution des hébergeurs.

Une future collecte doit échantillonner les deux classes chaque semaine et, autant que possible, par source, plateforme et condition de capture. Documenter URL annotée, délai avant capture, statuts, tentatives et preuves indisponibles. Éviter qu'une source unique détermine une classe. Réserver un nouveau lot postérieur jamais utilisé pour sélectionner architectures, features, calibration, seuils ou exemples de démonstration. Les entités et familles de contenus doivent rester indépendantes ; la revue humaine des labels et une nouvelle calibration historique précèdent l'ouverture finale du lot scellé.

## 14. Démonstration et déploiement local

Le notebook de présentation affiche une inférence réelle du test sauvegardé, clairement étiquetée comme telle. Le notebook FULL conservé contient predict_url pour une URL seule et predict_scan pour une archive de capture, utilisant les checkpoints et seuils gelés. Ces fonctions ne visitent pas la page. Un déploiement réel demanderait une acquisition isolée, une gestion du délai de capture, des erreurs et des modalités absentes, puis une validation prospective.

Une interface Streamlit locale est également disponible sur `http://127.0.0.1:8502`. L'onglet URL exécute réellement U1sans télécharger le site. L'onglet capture accepte un ZIPPhiShark et calcule les branches disponibles, M1/M2et, sur demande, les22combinaisons. L'onglet exemples réanalyse des scans identifiés du test historique et affiche les résultats du projet. Les scores, seuils, désaccords et abstentions sont explicites ; aucune accuracy de nouveaux sites n'est déduite de ces démonstrations.

Le chargement des poids est différé jusqu'à la première analyse. Les définitions d'inférence proviennent du notebook final unique, attestées comme identiques à celles du FULL exécuté ; le CNNimage96n'est pas remplacé par l'ancien module64. Les tests vérifient la concordance des28scores sur une vraie capture du test, la gestion des preuves absentes et le fonctionnement de l'interface, sans modifier les checkpoints ni les seuils. Les détails et commandes sont dans `reports/TESTER_INTERFACE.md` ; il s'agit d'un prototype local de recherche, sans certification de sécurité.

La soutenance ne nécessite pas de charger les réseaux ou d'ouvrir des sites malveillants. Il faut pouvoir expliquer la transformation URL, le rôle des masques, le sens du seuil et la distinction entre prédiction et vérité terrain. Les rapports de permutation technique restent des diagnostics d'influence, pas des explications causales de chaque erreur.

## 15. Conclusion et perspectives

Le projet fournit quatre branches, deux fusions centrales et22combinaisons exécutées, avec comparaisons communes vérifiées et analyse des erreurs. Le gain AP des fusions est soutenu sur ce test interne ; le compromis opérationnel reste à choisir selon des coûts métier définis avant une nouvelle évaluation. Les modalités visuelles n'apportent pas un bénéfice systématique, ce qui constitue un résultat scientifique utile et non un résultat à masquer.

Les limites principales sont la confusion source/classe, les périodes déséquilibrées, les proxies de disponibilité, les quasi-doublons non exacts non exhaustivement vérifiés, l'absence de validation externe et la comparaison Spark bloquée par la mémoire. La baseline disponibilité a AP0,6868sur validation ; retirer les quatre masques explicites change peu l'AP de la tête diagnostique, sans retirer les proxies implicites des autres représentations. Aucune part précise de performance n'est attribuée causalement aux artefacts.

Prochaines étapes justifiées : terminer Spark sur un environnement suffisant sans réentraîner les modèles ; revue humaine de la file d'erreurs ; collecte prospective équilibrée ; lot indépendant scellé et protocole d'évaluation préenregistré. Les entraînements ne sont pas recommencés pour gonfler les scores.

## 16. Références bibliographiques vérifiées

[1] Çolhak,F., Demirkıran,F., Dağ,H., Iliev,A. (2026). *PhiShark2026: A Multi-Layer Active-Web Raw-Evidence Dataset for Phishing Website Research*. arXiv:2608.23199. https://arxiv.org/abs/2608.23199

[2] Aljofey,A. etal. (2022). *An effective detection approach for phishing websites using URL and HTML features*. Scientific Reports12,8842. https://doi.org/10.1038/s41598-022-10841-5

[3] Lin,Y. etal. (2021). *Phishpedia: A Hybrid Deep Learning Based Approach to Visually Identify Phishing Webpages*. USENIX Security,3793–3810. https://www.usenix.org/conference/usenixsecurity21/presentation/lin

[4] Liu,R. etal. (2022). *Inferring Phishing Intention via Webpage Appearance and Dynamics: A Deep Vision Based Approach*. USENIX Security,1633–1650. https://www.usenix.org/conference/usenixsecurity22/presentation/liu-ruofan

[5] IBM. *CRISP-DM Guide*. https://public.dhe.ibm.com/software/analytics/spss/documentation/modeler/14.2/fr/CRISP-DM.pdf

[6] Saito,T., Rehmsmeier,M. (2015). *The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets*. PLOS ONE10:e0118432. https://doi.org/10.1371/journal.pone.0118432

[7] Apache Spark. *Performance Tuning, documentation4.0.1* (version documentaire de la même série4.0 ; environnement exécuté4.0.5). https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html

Sources locales de preuve : artefacts du run exécuté, inventaire et empreintes dans `artifacts/finalization/`, notebook FULL préservé et copie locale du sujet. Références web consultées le24novembre2026. Les temps et métriques de ce rapport proviennent des fichiers locaux, pas des publications.
'''
    # Restore conventional French spacing around numbers without changing the metric values.
    import re
    chunks=re.split(r'(`[^`]+`|https?://\S+)',text)
    text=''.join(part if i%2 else re.sub(r'(?<=[a-zà-ÿ])(?=\d)|(?<=\d)(?=[a-zà-ÿ])',' ',part) for i,part in enumerate(chunks))
    (reports/'PHISHARK2026_RAPPORT_FINAL.md').write_text(text,encoding='utf-8')
    # Deck narrative is linked to exact same-cohort metrics.
    slide_specs=[
      ('PhiShark2026','Détecter le phishing par la complémentarité des preuves','cover',
       ['4 modalités','28 configurations exécutées','Un compromis rappel / fausses alertes'],
       "Je présente PhiShark2026, un projet de détection multimodale du phishing. Mon objectif n'est pas d'afficher le score le plus élevé, mais de vérifier ce que la combinaison des preuves apporte et à quel coût en erreurs. Le travail suit CRISP-DM. Je présenterai les réseaux, les fusions et leurs limites. Les résultats proviennent d'un FULL exécuté et vérifié ; aucun entraînement n'est lancé pendant cette soutenance."),
      ('Une URL ne raconte pas toute la page','Réputation annotée et contenu capturé sont deux informations différentes.','cards',
       ['URL : motifs d’adresse','HTML et image : contenu capturé','Technique : preuves réseau et transport'],
       "Le phishing peut être visible dans une adresse, dans le texte d'une page ou dans son apparence. Une seule preuve peut manquer ou être trompeuse. Il faut aussi distinguer le label d'une URL et ce que la capture a effectivement enregistré. Une erreur404 ne rend pas automatiquement la réputation bénigne. Les faux positifs bloquent des sites légitimes ; les faux négatifs laissent passer des phishing. C'est ce compromis que je mesure."),
      ('Trois questions, trois niveaux de preuve','Les réponses doivent rester proportionnées aux expériences réalisables.','cards',
       ['RQ1 · La fusion améliore-t-elle les unimodaux ?','RQ2 · Généralise-t-elle vers des campagnes ultérieures ?','RQ3 · Quel coût selon le volume et le moteur ?'],
       "Le sujet pose trois questions. La première concerne la complémentarité des modalités et sera étudiée par des comparaisons appariées. La deuxième concerne le temps : un test groupé ne suffit pas à démontrer une robustesse à de nouvelles campagnes. La troisième porte sur le coût Big Data. Je distinguerai les mesures réellement exécutées des expériences bloquées. Une réponse non démontrée est une limite du protocole, pas une invitation à fabriquer une métrique."),
      ('67 502 scans, des sources très structurées','34 115 bénins · 33 387 phishing · une archive en quarantaine','dataset',
       ['URL, HTML, screenshot, JSON techniques','Source et classe : association parfaite dans le CSV','Le corpus est un benchmark interne déjà exploré'],
       "Le corpus compte67502scans. Une archive diverge du manifeste d'origine et reste en quarantaine, avec son label intact. Les captures sont riches, mais la composition du dataset crée une limite forte : source et classe sont parfaitement associées dans le CSV. Même si ces colonnes ne sont pas utilisées directement comme features, leurs effets peuvent se refléter dans les captures ou les URL. Cela empêche de confondre un bon score interne et une certification externe."),
      ('CRISP-DM organise le raisonnement','De la cible métier jusqu’aux limites de déploiement','crisp',
       ['Comprendre le problème','Auditer les données','Préparer et partitionner','Modéliser','Évaluer les erreurs','Restituer et démontrer'],
       "CRISP-DM structure le projet en six phases. Je définis d'abord la cible et les coûts d'erreur, puis j'audite le corpus. La préparation ne consiste pas seulement à nettoyer : elle empêche qu'un site ou un contenu identique soit partagé entre les rôles. Les modèles sont ensuite entraînés, puis évalués avec des seuils gelés. Enfin, le déploiement reste un prototype local accompagné de limites et d'un plan de validation future."),
      ('Un pipeline traçable, pas seulement un modèle','Extraction Python → stockage Parquet → rôles indépendants','pipeline',
       ['ZIP / CSV originaux','JSON21 · HTML visible · RGB96×96','Groupes sites / locataires / contenus','Train encodeurs · train fusion · validation · calibration · test'],
       "L'extraction lit les archives originales sans visiter les sites. Elle produit les entrées techniques, le texte visible et les images. Parquet conserve une représentation typée et réutilisable. Les groupes réunissent les entités et les contenus contrôlés. Cinq rôles distincts évitent d'apprendre les encodeurs et la fusion sur les mêmes observations. Les vocabulaires et normalisations voient uniquement leur train autorisé. Les labels et les dates ne sont pas modifiés pour obtenir de meilleurs résultats."),
      ('Quatre branches, une représentation commune','Chaque encodeur fournit un embedding de 32 valeurs.','models',
       ['U1 · CNN1D caractères URL · sans HTTP/HTTPS','U2 · CNN1D tokens du texte HTML visible','U3 · CNN2D screenshot96×96 · entraîné depuis zéro','U4 · MLP21mesures techniques +21masques'],
       "Les convolutions1D apprennent des motifs locaux dans les caractères d'URL ou les tokens du HTML. Le CNN2D traite l'image globale, sans reconnaissance de logo spécialisée. Le MLP technique traite des mesures numériques normalisées et leurs indicateurs manquants. Les quatre branches fournissent chacune32valeurs. Les checkpoints sont choisis sur validation avec early stopping. Le schéma HTTP/HTTPS a été retiré des entrées d'U1 pour éviter ce raccourci particulier, mais les biais d'hébergement peuvent subsister."),
      ('Deux fusions centrales, 22 études complémentaires','Les encodeurs restent gelés pour apprendre les têtes de fusion.','fusion',
       ['M1 · moyenne des probabilités disponibles','M2 · embeddings128 +4masques → MLP','11 sous-ensembles × LATE / LINEAR_EMBED','Seuils gelés sur calibration, jamais ajustés sur test'],
       "M1 combine les probabilités à poids égaux, en tenant compte des modalités disponibles. M2 concatène les quatre embeddings et les masques, puis apprend un MLP sur un train de fusion indépendant. Les22études supplémentaires testent six paires, quatre triplets et le quadruplet, par moyenne et par régression logistique sur embeddings. Ce ne sont donc pas22nouveaux CNN. Toutes les politiques sont définies avant leur évaluation ; le test ne choisit pas rétroactivement un gagnant final."),
      ('RQ1 · Les fusions améliorent le classement interne',f'Mêmes {summary["common_n"]:,} scans complets · prévalence49,53%'.replace(',',' '),'central_chart',
       ['M1 : AP0,9722','M2 : AP0,9790','Les deux dépassent les quatre unimodaux sur ce test'],
       "Les six modèles sont comparés sur exactement13212scans. M1 et M2 améliorent l'AP par rapport aux unimodaux, dont le meilleur est le HTML. Les différences avec HTML ont des intervalles bootstrap groupés positifs dans cette analyse exploratoire. En revanche, l'intervalle de la différence entre M2 et M1 recouvre zéro : je ne peux pas affirmer leur supériorité générale l'un sur l'autre. Le CNN image est faible ; je conserve ce résultat au lieu de le masquer."),
      ('Trois modalités peuvent rivaliser avec quatre','URL + HTML + technique : une combinaison informative, pas un gagnant scellé.','combo_chart',
       ['Linéaire3modalités : AP0,97943','Linéaire4modalités : AP0,97551','Ajouter l’image ne donne pas un gain systématique'],
       "La comparaison commune montre que trois modalités peuvent rivaliser avec quatre. La tête linéaire URL, HTML et technique obtient une AP légèrement supérieure à sa version avec image. Le bootstrap de cet ajout d'image suggère une baisse locale, mais les multiples comparaisons ne sont pas corrigées. Dans la moyenne tardive, le petit écart avec ou sans image reste compatible avec zéro. Je n'en conclus pas que les images sont inutiles en général : mon petit CNN n'analyse ni logo ni intention de saisie."),
      ('Une meilleure AP ne décide pas du bon seuil','Mêmes scans · seuils choisis sur calibration','tradeoff',
       [f'M1 : rappel{idx.loc["M1","recall"]*100:.2f}% · FPR{idx.loc["M1","FPR"]*100:.2f}%',
        f'M2 : rappel{idx.loc["M2","recall"]*100:.2f}% · FPR{idx.loc["M2","FPR"]*100:.2f}%',
        'Réduire les fausses alertes peut augmenter les phishing manqués'],
       f"Sur la cohorte commune, M1 produit{int(idx.loc['M1','FP'])}faux positifs et{int(idx.loc['M1','FN'])}faux négatifs. M2 produit{int(idx.loc['M2','FP'])}faux positifs et{int(idx.loc['M2','FN'])}faux négatifs. La forte réduction des fausses alertes s'accompagne donc de phishing supplémentaires manqués. L'AP décrit le classement des scores, pas ce point d'exploitation. Le choix métier doit fixer à l'avance le coût acceptable de ces erreurs, puis être confirmé sur une collecte indépendante."),
      ('RQ3 · pandas mesuré, Spark bloqué par la mémoire','24 mesures pandas · mêmes transformations et relecture vérifiée','bigdata',
       ['67 501 lignes :0,3075s non partitionné','67 501 lignes :0,4048s partitionné','Spark :BLOCKED_RESOURCE · aucun temps inventé'],
       "Le benchmark stocke les mêmes colonnes et réalise la même chaîne logique. Les médianes pandas au volume maximal sont d'environ0,31seconde et0,40seconde selon le scénario. Ces valeurs portent sur un Parquet tabulaire de quelques mégaoctets, pas sur l'extraction des28Go d'archives. L'extraction complète a duré environ128minutes. Un processus séparé sans réseaux a contrôlé Spark, mais moins d'un gigaoctet restait disponible. Je ne présente donc aucune comparaison de vitesse Spark, ni une exécution locale comme un cluster."),
      ('RQ2 · La généralisation temporelle reste non démontrée','Calibration après purge :1 511 phishing, aucun bénin','limits',
       ['Frontières temporelles fixées par quantiles','Groupes traversant les périodes purgés','Collecte future équilibrée et lot indépendant nécessaires'],
       "Le protocole temporel applique des frontières fixes et purge les groupes partagés entre périodes. Après cette opération, la calibration contient1511phishing et aucun bénin. Il est impossible d'y fixer un compromis binaire représentatif. Je n'ai pas déplacé les dates ni changé les labels. La généralisation temporelle n'a donc pas pu être démontrée avec le corpus actuel. Cela constitue une limite méthodologique documentée, qui motive une collecte où chaque période contient les deux classes dans des conditions comparables."),
      ('Démonstration : comprendre une décision sauvegardée','Sans réseau, sans entraînement, avec les seuils du FULL','demo',
       ['Scan du registre de test réellement exécuté','Six scores et leurs seuils gelés','Une prédiction n’est pas une nouvelle vérité terrain'],
       "La démonstration charge une décision déjà calculée, plutôt que de dépendre d'un site vivant pendant la soutenance. On voit les six scores, leurs seuils et leurs décisions, qui peuvent différer. Cette démonstration ne crée pas un nouvel exemple indépendant et ne prouve pas que le phishing est actif aujourd'hui. Pour un nouveau site, il faudrait produire une capture contrôlée, puis appeler les fonctions d'inférence du notebook FULL avec les checkpoints figés. L'acquisition et la validation prospective restent nécessaires."),
      ('Ce que le projet démontre — et ce qu’il reste à valider','Complémentarité interne établie ; généralisation externe ouverte.','closing',
       ['RQ1 · gain AP interne, compromis FP/FN explicite','RQ2 · non démontrée avec ce corpus','RQ3 · pandas mesuré ; Spark à compléter','Suite · revue humaine, collecte équilibrée, lot scellé'],
       "Le projet est terminé pour ses entraînements et son analyse multimodale. La fusion améliore le classement interne, mais aucune architecture n'est universellement meilleure au seuil opérationnel. Les limites importantes sont les sources, les périodes, les captures et l'absence de nouveau lot indépendant. Je propose donc une suite ciblée : finir Spark sur une machine suffisante, revoir les erreurs humaines prioritaires et collecter un lot équilibré puis scellé. Il ne s'agit pas de recommencer les réseaux pour augmenter artificiellement leurs scores.")]
    spec=[];oral=['# Script oral — 15 diapositives, environ10–15minutes','\nLes chiffres des modèles proviennent de la cohorte commune13212, sauf indication explicite. Les questions de coût portent sur leur périmètre réellement mesuré.\n']
    for i,(title,subtitle,kind,points,notes) in enumerate(slide_specs,1):
        # Normalize prose spacing, avoiding unreadable digit/word concatenations.
        points=[re.sub(r'(?<=[A-Za-zÀ-ÿ])(?=\d)|(?<=\d)(?=[A-Za-zÀ-ÿ])',' ',p) for p in points]
        notes=re.sub(r'(?<=[A-Za-zÀ-ÿ])(?=\d)|(?<=\d)(?=[A-Za-zÀ-ÿ])',' ',notes)
        spec.append(dict(number=i,title=title,subtitle=subtitle,kind=kind,points=points,notes=notes))
        oral += [f'## {i}. {title}',notes,'']
    (out/'slide_spec.json').write_text(json.dumps(spec,ensure_ascii=False,indent=2),encoding='utf-8')
    (presentation/'SCRIPT_ORAL.md').write_text('\n\n'.join(oral),encoding='utf-8')
    questions=[
      ('Pourquoi quatre modalités ?','Elles décrivent des indices différents : adresse, contenu textuel, apparence et contexte technique. Les ablations mesurent leur complémentarité réelle ; quatre ne garantit pas mieux que trois.'),
      ('Pourquoi CNN1D sur URL et HTML ?','Les convolutions repèrent des motifs locaux dans les caractères ou tokens. Les embeddings sont appris sur le train, avec PAD/UNK. Cette simplicité ne remplace pas un modèle sémantique complet du navigateur.'),
      ('Pourquoi un MLP technique ?','Les entrées sont tabulaires, numériques, normalisées et accompagnées de masques. Un MLP compact permet une représentation32dimensions compatible avec les autres branches.'),
      ('Fusion tardive ou intermédiaire ?','La tardive moyenne les scores. L’intermédiaire apprend à combiner les représentations gelées. M2 utilise un MLP ; les variantes LINEAR_EMBED utilisent une régression logistique. Ce ne sont pas les mêmes capacités.'),
      ('Pourquoi l’image est moins performante ?','L’observation est confirmée, pas sa cause unique. Le CNN global96×96sans préentraînement spécialisé peut perdre des détails ; pages vides et conditions de capture sont des hypothèses. Il faudrait une expérience dédiée pour isoler ces causes.'),
      ('Pourquoi AP élevée et beaucoup de faux positifs ?','AP évalue l’ordre des scores sur tous les seuils. Le FPR dépend d’un seuil précis et de la distribution des bénins. Une AP élevée n’impose ni une bonne calibration probabiliste ni le bon seuil opérationnel.'),
      ('Quelle combinaison donne le meilleur compromis ?','Il n’existe pas de réponse universelle sans coût métier préenregistré. Sur la cohorte commune, M1 rappelle94,04%avec FPR12,10%, M2 rappelle84,63%avec FPR2,11%. Ces points viennent de calibration, pas d’un réglage sur test.'),
      ('Pourquoi trois modalités rivalisent-elles avec quatre ?','Une modalité faible ou redondante peut introduire du bruit. Le linéaire URL+HTML+TECH est proche du MLP complet et au-dessus de son quadruplet linéaire dans cette expérience. Cela reste exploratoire et non une preuve d’inutilité générale de l’image.'),
      ('Comment éviter les fuites ?','Groupes sites/locataires/contenus et encodages, cinq rôles indépendants, vocabulaires et normalisations sur train seulement, têtes sur train_fusion, checkpoints sur validation et seuils sur calibration. Les contrôles exacts ne prouvent pas l’absence de tous les quasi-doublons.'),
      ('Pourquoi le temporel n’est pas réalisable ?','Après frontières fixes et purge des groupes, calibration ne contient que1511phishing. Modifier les dates après observation changerait le protocole. La conclusion honnête est non démontrée, sans score inventé.'),
      ('Pourquoi Spark pour67500scans ?','Le nombre de scans ne suffit pas : il faut considérer les28Go bruts, les représentations et le périmètre. Python réalise l’extraction ; le benchmark mesure un petit Parquet dérivé. Spark est une piste de passage à l’échelle, pas un avantage démontré ici.'),
      ('Comment prédire un nouveau site ?','Une acquisition isolée produit l’archive et ses modalités. predict_scan charge les checkpoints gelés ; predict_url exécute U1 pour une URL seule. La démo de soutenance relit un scan existant et ne doit pas être présentée comme nouveau test.'),
      ('Le meilleur score observé est-il votre modèle final ?','Non. Les28configurations ont déjà été examinées sur test. Un choix final exige un protocole explicite et un nouveau lot indépendant qui ne sert ni au choix, ni à la calibration, ni au seuil.'),
      ('Quel biais explique les AP élevées ?','Source et classe sont confondues dans le CSV. Des proxies peuvent subsister dans les modalités. Les audits et la baseline de disponibilité montrent des signaux, mais ne quantifient pas une part causale précise de l’AP totale.'),
      ('Les404sont-ils mal étiquetés ?','Pas automatiquement : réputation de l’URL et contenu capturé sont différents. La revue humaine doit examiner dates, preuves et contexte. Aucun label n’a été changé automatiquement.'),
      ('Les intervalles prouvent-ils la supériorité ?','Ils décrivent l’incertitude de rééchantillonnage des groupes sur le test interne, avec200répétitions. Ils ne couvrent pas une nouvelle campagne, une autre collecte ou l’incertitude de multiples graines et ne sont pas corrigés pour toutes les comparaisons.'),
      ('Le projet est-il complètement validé ?','Les artefacts,28comparaisons et notebook de présentation sont validés dans leur périmètre. La généralisation temporelle n’est pas démontrée et Spark reste bloqué par les ressources. Ces limites sont explicites dans la checklist.')]
    (presentation/'QUESTIONS_JURY.md').write_text('# Questions du jury — réponses défendables\n\n'+'\n\n'.join(f'## {q}\n\n{a}' for q,a in questions)+'\n',encoding='utf-8')
    # Small, exact saved example for editable slide table.
    ledger=pd.read_csv(run/'predictions.csv',dtype={'scan_id':str});sample=sorted(ledger.loc[ledger.split.eq('test')].scan_id.unique())[0]
    demo=ledger.loc[ledger.scan_id.eq(sample)&ledger.split.eq('test'),['scan_id','model','label_id','probability']].copy()
    frozen=json.loads((run/'frozen.json').read_text());demo['threshold']=demo.model.map({k:v['primary'] for k,v in frozen['policies'].items()});demo['prediction']=demo.probability.ge(demo.threshold)
    demo.to_csv(out/'demo_predictions.csv',index=False)
    from enrich_defense_report import enrich
    enrich()
    print('Report, oral script, jury questions, slide specification written.')


if __name__=='__main__':main()
