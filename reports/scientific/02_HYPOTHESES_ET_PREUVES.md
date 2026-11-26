# Hypothèses, expériences et force des preuves

Source principale : `artifacts/published/table_28_common.csv`, recomputée depuis les prédictions dans `../FIGURES_ET_RESULTATS/verification_28.csv`. Population : 13 212 scans communs, 6 544 phishing et 6 668 bénins. Le mot « confirmée » désigne ci-dessous une propriété de cette exécution interne ; il ne vaut pas validation externe.

## Matrice de décision

| ID / RQ | Proposition réfutable | Expérience et preuve | Résultat vérifié | Statut et limites |
|---|---|---|---|---|
| H1 / RQ1 | Les fusions centrales améliorent le classement et la décision face aux unimodaux. | Comparaison appariée des six centraux, même cohorte et seuils de calibration ; table_28_common et paired_modality_contributions. | AP M1=0,972201, M2=0,978963 contre 0,933933 pour le meilleur unimodal en AP, U2. F1 M1=0,911366 ; M2=0,906161. | **Partiellement soutenue** : gain interne observé ; ne pas confondre gain de classement, gain à seuil et universalité. M2 n'améliore pas le F1 de M1. |
| H2 / RQ1 | Trois modalités égalent quatre. | URL+HTML+TECH, avec et sans IMAGE, à famille de fusion fixée. | LATE trois=0,972918 contre quatre=0,972201 ; LINEAR_EMBED trois=0,979434 contre quatre=0,975514. | **Non confirmée comme équivalence** : proximité ou avantage ponctuel, sans marge d'équivalence préétablie. |
| H3 / RQ1 | HTML apporte de l'information à URL. | LATE URL+HTML vs U1 ; analyse appariée et erreurs. | AP 0,951510 contre 0,904653. | **Partiellement soutenue** en AP interne ; l'explication des cas ambigus requiert une revue de contenu, pas le seul score global. |
| H4 / auxiliaire | L'image apporte un gain systématique. | U3 et contrastes +IMAGE à ensemble de départ fixé. | U3 AP=0,592764 ; l'ajout à URL en LATE descend à environ 0,8762. | **Non confirmée dans cette architecture**. Qualité, résolution et optimisation restent des explications ouvertes, non des causes démontrées. |
| H5 / auxiliaire | Les features techniques reflètent à la fois signal et collecte. | U4, masques, corrélations source/classe et audit des champs autorisés. | U4 AP=0,905998 ; présence explicite des 21 masques. | **Partiellement soutenue** pour l'existence de signal ; fraction causale attribuable aux artefacts **non mesurée**. |
| H6 / RQ1 | M1 et M2 ont des compromis d'erreur différents. | Matrices communes aux seuils gelés. | M1 FP=807/FN=390 ; M2 FP=141/FN=1 006. | **Confirmée en interne** : 666 FP évités, 616 FN supplémentaires ; pas une preuve de dominance de M2. |
| H7 / RQ1 | Changer la politique de seuil change le compromis sans changer l'AP. | primary et recall85 figés sur calibration, operating_points_frozen. | Mêmes scores, décisions différentes ; 56 politiques vérifiées historiquement. | **Confirmée en interne**. Le rappel cible sur calibration n'est pas garanti sur test. |
| H8 / validité | Les groupes empêchent le recouvrement des identités contrôlées. | Manifeste et empreintes site/URL/HTML/image/entrée encodée. | Contrôles de disjonction du pipeline et du rapport d'analyse. | **Confirmée pour les clés effectivement contrôlées**, sans preuve d'absence de quasi-doublons sémantiques. |
| H9 / validité | Source et période sont associées aux classes. | Tables source×classe, période×classe de l'EDA actuelle. | Association observée, à quantifier dans les tableaux générés. | **Confirmée descriptivement** ; causalité des raccourcis dans le modèle **ouverte**. |
| H10 / RQ2 | Le protocole chronologique défini permet une comparaison valide. | temporal_feasibility.json. | Après purge de 22 064 scans : calibration=1 511 phishing, 0 bénin. | **Non testable pour ce protocole** ; RQ2 non démontrée, pas un score nul. |
| H11 / labels | Une capture 404 contredit automatiquement un label phishing. | Sémantique réputation/contenu et revue des cas HTTP. | Le label et la capture ne mesurent pas le même instant ou objet. | **Non confirmée** ; aucun relabel automatique. La correction individuelle exige des éléments indépendants. |
| H12 / RQ3 | Spark est plus rapide que pandas sur ce périmètre. | Benchmark équivalent, statut bd3 sauvegardé. | 24 mesures pandas/PyArrow ; Spark BLOCKED_RESOURCE. | **Non testable comparativement** dans l'exécution disponible. |
| H13 / coût | Trois modalités réduisent le coût à performance comparable. | Architecture et AP, puis chronométrage contrôlé souhaité. | Réduction structurelle du nombre de branches ; latence comparée **NON MESURÉE**. | **Partiellement soutenue conceptuellement**, compromis empirique complet ouvert. |
| H14 / RQ2 | Un bon test groupé garantit le transfert futur/externe. | Distinction de population et absence de nouveau test indépendant. | Aucun résultat final externe exploitable pour cette affirmation. | **Non confirmée** ; nouveau lot requis. |
| H15 / architecture | Le CNN compact est équivalent aux encodeurs de référence. | Inspection des couches et littérature. | CNN 96×96 sans préentraînement, distinct de ResNet et de la reconnaissance de marque. | **Non confirmée**, architectures et tâches différentes. |

## Règles d'interprétation

Les contrastes doivent conserver la même famille de fusion. Comparer M2/MLP à une régression logistique trimodale modifie simultanément la modalité et la tête ; ce contraste ne mesure pas un effet causal de l'image. Les intervalles appariés par groupes décrivent une incertitude d'échantillonnage conditionnelle aux poids existants. Ils n'intègrent pas la variabilité entre graines ni un changement de source.

La table ci-dessus est un registre de conclusions, pas une liste d'hypothèses toutes confirmées. Les décimales détaillées sont générées depuis les CSV et vérifiées dans le rapport final ; aucun seuil ou choix de modèle n'est ajusté sur ce test déjà consulté.
