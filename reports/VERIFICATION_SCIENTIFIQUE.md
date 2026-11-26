# Vérification scientifique — 26 novembre 2026

## Périmètre et réalisation

Le mémoire courant comporte **52 pages**, dont **8 pages d'annexes**. Il comprend huit chapitres, 31 tableaux et neuf figures ; son corps principal est distinct des résumés, sommaire et bibliographie. La cible de volume reste indicative : aucun contenu artificiel n'a été ajouté pour atteindre un quota de pages. Les quatre documents de cadrage, la bibliographie, les données des illustrations et les supports oraux demandés sont présents.

Le rapport précédent, son PDF et les anciennes questions du jury sont conservés localement dans `artifacts/scientific_writing/before_scientific_revision/`. Les résultats historiques ne sont pas écrasés. Le notebook, les poids, les seuils, le cache et les partitions n'ont pas été modifiés pour la rédaction. Aucun réseau n'a été entraîné.

## Contrôles exécutés

| Élément | Statut | Preuve et portée |
|---|---|---|
| Bibliographie | PASS | Dix entrées, dont le sujet local ; trois PDF scientifiques complets lus par sections ciblées, notices officielles et DOI vérifiés pour les références complémentaires. Pas de reproduction prétendue des articles. |
| Source des métriques | PASS | 28 configurations recomputées depuis les registres individuels sur exactement 13 212 IDs ; AP, ROC-AUC, précision, rappel, F1, FPR/FNR et matrices concordent à 1e-10. |
| Architectures | PASS | Définitions du notebook inspectées : 21 features, 42 entrées U4, 132 entrées M2 ; HTML textuel, sans GCN ; couches décrites et paramètres du run. |
| Figures et tableaux | PASS | Neuf figures intégrées avec sources explicites ; 31 tableaux numérotés ; tables de toutes les métriques et matrices des 28 en annexe ; manifeste des fichiers. |
| CRISP-DM | PASS | Les six phases sont reliées aux huit chapitres, aux artefacts et aux questions de recherche. |
| M1/M2 | PASS | 807/390 contre 141/1 006 FP/FN ; 666 FP évités et 616 FN supplémentaires ; intervalle apparié M2−M1 contenant zéro correctement discuté. |
| RQ1 | PARTIAL | Gain interne et exploratoire des fusions centrales ; pas de validation indépendante d'une supériorité générale ni d'équivalence trimodale. |
| RQ2 | BLOCKED | NOT_FEASIBLE pour le protocole chronologique défini : calibration 1 511 phishing/0 bénin après purge. Aucun score futur inventé. |
| RQ3 | PARTIAL | 24 mesures pandas/PyArrow et coûts partiels sauvegardés ; Spark BLOCKED_RESOURCE avant JVM, comparaison distribuée non démontrée. |
| Erreurs et confidentialité | PASS | Vingt décisions pseudonymisées, sans URL ni ID privé ; échantillon illustratif déterministe, pas une revue humaine de labels. Mapping conservé uniquement localement. |
| Préservation | PASS | 42 empreintes protégées identiques ; empreintes supplémentaires du CSV original, cache canonique et manifeste de partitions conformes à la préparation. Aucun changement de label ou de seuil. |
| Export et mise en page | PASS | Texte PDF extractible, sommaire paginé, signets, police Unicode ; toutes les pages rendues, planches et pages détaillées inspectées. Aucune page vide ni caractère manquant détecté. |
| Soutenance | PASS | Argumentaire de 12–15 minutes proposé et 24 questions/réponses ; chiffres rattachés à la cohorte commune. Aucun PPTX historique modifié. |

## Sources effectivement consultées

- Sujet de l'enseignante : copie locale de deux pages, lue intégralement ; RQ1–RQ3.
- Yoon, Buu et Kim 2024 : PDF officiel de 21 pages, méthodes et résultats, §§3–4 et tableaux identifiés.
- Thèse Almakhamreh 2024 : PDF complet de 130 pages physiques obtenu par l'API officielle Hacettepe ; lecture ciblée des méthodes, datasets et chapitre d'évaluation. La première copie tronquée a été remplacée et n'est pas citée comme preuve.
- CrossPhire 2026 : PDF officiel de 45 pages, notamment §§5–7 et tables de protocoles internes/inter-corpus.
- Phishpedia et PhishIntention : notices, résumés et métadonnées USENIX officiels ; aucune affirmation de relecture intégrale des deux articles.
- CRISP-DM : document officiel du consortium hébergé par IBM ; notice arXiv PhiShark vérifiée ; source PLOS des métriques PR et documentation Spark versionnée vérifiées.

Les copies de lecture et leurs empreintes sont locales dans `artifacts/scientific_writing/sources/`. La bibliographie publique conserve DOI/URL et statut des publications ; aucune donnée brute n'est redistribuée avec les figures.

## Limites non levées par la rédaction

Les sources sont parfaitement associées aux labels dans cette copie, et les périodes sont déséquilibrées. Le retrait de colonnes de provenance n'établit pas l'absence de proxys indirects. La fraction causale de l'AP due aux artefacts n'est pas mesurée. Les durées brutes fin−début sont toutes négatives et ne sont pas utilisées comme temps physiques ; la sémantique des horodatages reste à clarifier.

Le bootstrap apparié est conditionnel aux poids et au corpus, avec 200 tirages de groupes ; il ne remplace pas plusieurs graines et ses nombreuses comparaisons ne sont pas corrigées. Les contrôles exacts de contenu ne garantissent pas l'absence de quasi-doublons sémantiques. Les cas FP/FN ne sont pas des labels corrigés ni une expertise humaine. Une nouvelle collecte équilibrée et un test scellé restent nécessaires.

Le PDF comporte 44 pages avant les annexes et 8 pages d'annexes ; le nombre total ne doit pas être présenté comme un nombre de pages de résultats nouveaux. Le projet est un prototype local reproductible ; certaines exigences expérimentales de généralisation et distribution demeurent partielles ou bloquées.
