## Chapitre 7 — Passage à l'échelle et généralisation

### 7.1. Séparer les différents coûts

Le pipeline comprend collecte réseau, lecture et décodage d'archives, extraction des représentations, apprentissage, export et inférence. Une mesure partielle ne doit pas être présentée comme le temps de toute la chaîne. La capture réseau n'est pas chronométrée par cette expérience ; les durées négatives des métadonnées brutes sont inutilisables comme chronométrage. Les temps enregistrés par les scripts concernent leurs propres opérations.

L'extraction locale des archives a duré 7 709,588847 secondes dans le journal conservé, soit environ 128,49 minutes. Cette mesure inclut lecture, décodage, contrôles et création du cache. Les entraînements des branches sont beaucoup plus courts sur ce cache et sont rapportés séparément. Leur rapidité ne signifie pas que la collecte et la préparation complètes se réalisent en quelques secondes.

Une latence d'inférence utilisateur ne se déduit pas de l'addition des durées d'entraînement. Les modèles peuvent être déjà chargés, les modalités peuvent manquer et l'archive peut nécessiter du décodage. Une mesure de latence complète et répétée à froid et à chaud pour les 28 variantes n'est pas disponible. Ce manque est identifié plutôt que remplacé par une estimation séduisante.

### 7.2. Benchmark pandas/PyArrow réellement effectué

Deux scénarios comparent les mêmes types d'opérations sur quatre fractions du volume : A écrit un fichier Parquet ; B écrit une organisation Hive par rôle. Trois répétitions fournissent 24 mesures. Lecture, validation des identifiants et classes, écriture Snappy, relecture et égalité logique sont comprises dans le périmètre. La création de l'entrée de benchmark et le démarrage d'une JVM ne le sont pas.

{{BENCHMARK_TABLE}}

Le coût B supérieur à A à certains volumes est cohérent avec des fichiers et répertoires supplémentaires à créer ; ce constat ne prouve pas un mécanisme unique. Les caches disque, le système de fichiers et l'échantillonnage de mémoire influencent les temps. Les médianes et étendues sont présentées, sans traiter trois répétitions comme une caractérisation exhaustive de la machine.

![Figure 6 — Temps pandas/PyArrow selon volume et scénario ; mesures sauvegardées, pas de courbe Spark inventée.](FIGURES_ET_RESULTATS/06_bigdata_temps.png)

Les 67 501 lignes du benchmark Parquet ne représentent pas le volume physique de tous les ZIP et images. Un petit tableau de caractéristiques peut être traité rapidement alors que le corpus brut occupe beaucoup plus d'espace. La comparaison renseigne le traitement tabulaire défini, pas une extraction distribuée des captures brutes.

### 7.3. Mémoire, fichiers et portée du débit

Les pics RSS enregistrés décrivent le processus échantillonné selon le protocole du script. Ils ne sont ni une mesure de la mémoire totale de la machine ni une promesse d'occupation pour une nouvelle exécution. Le nombre de fichiers de sortie est une propriété du scénario ; les différences d'organisation peuvent modifier les coûts d'accès ultérieurs. Une étude complète distinguerait ces étapes plutôt que de chercher un débit universel.

![Figure 7 — Débit du benchmark pandas/PyArrow local ; lignes par seconde pour les deux scénarios enregistrés.](FIGURES_ET_RESULTATS/07_bigdata_debit.png)

Le débit médian est exprimé en lignes par seconde sur ce périmètre. Il ne mesure pas le nombre de nouveaux sites inspectés en ligne. Les figures conservent les unités et les opérations pour prévenir cette interprétation. La structure Parquet est un choix de reproductibilité et de lecture sélective ; son adoption ne démontre pas à elle seule le passage à un cluster.

### 7.4. Statut Spark et réponse partielle à RQ3

Le processus Spark séparé a enregistré `BLOCKED_RESOURCE` avant démarrage de la JVM, avec environ 0,823 Go de RAM disponible au contrôle. Il n'existe donc aucun temps Spark valide à comparer aux 24 mesures pandas. La documentation officielle [9] décrit des mécanismes de partitionnement et d'optimisation ; elle ne peut être citée comme preuve qu'ils ont accéléré notre expérience.

La partie distribuée de RQ3 demeure bloquée dans les résultats conservés. Pour la compléter, il faudrait des ressources adaptées, des données et schémas identiques, les mêmes opérations et validations de sortie, plusieurs volumes et répétitions, une séparation explicite des coûts JVM froide/chaude et une mesure de mémoire comparable. Spark local ne constituerait toujours pas, à lui seul, une preuve d'accélération multi-nœuds.

Le statut ne doit pas être masqué par un ratio calculé avec un temps manquant ou par une barre nulle. Le rapport répond partiellement au coût local et délimite la comparaison non exécutée. Cette transparence est nécessaire pour défendre la conformité au sujet sans affirmer que toutes ses exigences expérimentales sont achevées.

### 7.5. Protocole chronologique et infaisabilité précise

Le protocole fixe des frontières temporelles historiques et purge les groupes qui les traversent. Cette purge protège les identités contrôlées, mais modifie les effectifs et la composition des partitions. Après retrait de 22 064 scans, la calibration contient 1 511 phishing et aucun bénin. Le code exige les deux classes pour définir les politiques et évaluer le compromis de décision ; le protocole s'arrête donc avec `NOT_FEASIBLE`.

{{TEMPORAL_TABLE}}

Ce résultat ne signifie pas que toutes les évaluations temporelles possibles sur ce corpus sont mathématiquement impossibles. Il signifie que le protocole actuellement défini ne fournit pas les conditions de preuve attendues. Déplacer les dates à partir des performances futures ou supprimer la purge pour obtenir un score modifierait la question. Une révision éventuelle doit être spécifiée sur l'historique et accompagnée d'un nouveau test indépendant.

Un test groupé confronte des sites ou contenus contrôlés nouveaux à une composition globale qui peut rester similaire. Un test chronologique ajoute le changement de période et souvent de source. Les deux protocoles sont complémentaires ; leurs métriques ne peuvent pas être interprétées comme deux estimations de la même population sans décrire ces différences. RQ2 reste non démontrée dans le travail final.

### 7.6. Nouvelle collecte et protocole d'évaluation indépendant

La collecte future doit représenter les deux classes à chaque période, diversifier les sources pour chaque classe et enregistrer plateforme, locataire et conditions de capture. Les mêmes règles de navigateur, réseau, délais et format devraient être appliquées autant que possible. Les indisponibilités restent enregistrées, sans élimination sélective par classe. Un échantillon de qualité fait l'objet d'une revue humaine indépendante, avec distinction réputation et contenu visible.

L'indépendance du prochain lot exige de sceller sa liste et ses labels avant toute sélection finale. Le modèle, les features, le prétraitement, la calibration et le seuil sont fixés uniquement sur l'historique. Les domaines/locataires et familles de contenus sont vérifiés sans consulter les performances du lot. La collecte doit prévoir des bénins comparables aux phishing en profondeur d'URL, plateforme et conditions, sans rendre artificiellement les classes identiques sur les facteurs qu'on cherche réellement à détecter.

Le rapport final du nouveau lot présentera prévalence, couverture, AP, ROC-AUC, rappel, précision, FPR/FNR, matrices et intervalles groupés. Des strates période, source, plateforme et disponibilité seront définies à l'avance. Après ouverture du test, les erreurs peuvent nourrir un diagnostic, mais tout ajustement crée une nouvelle version qui réclame un autre test scellé. Les futurs résultats déjà examinés pendant les audits antérieurs ne sont pas ce nouveau lot.

La robustesse reproductible inclut également plusieurs graines et plusieurs fenêtres historiques faisables. Les budgets et objectifs doivent être annoncés avant les essais, et les échecs enregistrés. La priorité est de lever les confusions de collecte et d'évaluation ; une fusion profonde plus coûteuse ne devient justifiée qu'après cette étape.
