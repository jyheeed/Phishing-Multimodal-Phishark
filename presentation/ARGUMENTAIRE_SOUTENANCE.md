# Argumentaire de soutenance — 12 à 15 minutes

Ce document prépare un exposé oral fondé sur le mémoire scientifique. Le diaporama existant reste un support ; sa durée n'autorise pas à lire toutes les tables. Les résultats concernent les 13 212 scans communs, sauf précision. Le temps indiqué est un objectif d'entraînement oral, pas une durée mesurée.

## Huit idées centrales

1. Nous classons une réputation historique à partir de preuves capturées ; un 404 ne réfute pas automatiquement le label.
2. La multimodalité est une hypothèse de complémentarité, pas une garantie de supériorité.
3. La qualité de la comparaison dépend des groupes, rôles de données et mêmes individus testés.
4. Quatre encodeurs partagés supportent 28 configurations ; ce ne sont pas 28 CNN indépendants.
5. La fusion améliore le classement interne, mais l'ajout d'image n'est pas systématiquement utile.
6. M2 évite 666 FP et ajoute 616 FN face à M1 ; AP et décision doivent rester distinguées.
7. RQ2 n'est pas démontrée et la comparaison Spark est bloquée ; ces limites sont explicites.
8. Le prochain progrès est une évaluation indépendante bien collectée, avant une architecture plus coûteuse.

## 0:00–1:30 — Le problème et la question scientifique

« Notre projet cherche à déterminer si plusieurs preuves du même site améliorent la classification de phishing. Une URL, un texte, une image et des informations techniques ne décrivent pas la même chose. Une longue adresse peut être légitime ; un certificat TLS n'empêche pas le phishing ; une capture peut déjà montrer une page expirée. Nous ne voulons donc pas définir une règle universelle à partir d'un seul indice.

La question pratique est aussi une question de décision : combien de faux blocages acceptons-nous pour manquer moins de phishing ? C'est pourquoi nous rapportons AP, rappel, précision et fausses alertes, avec leurs matrices. Les trois questions du sujet portent sur le gain multimodal, la généralisation temporelle et le coût de traitement. Je vais distinguer ce qui est démontré sur notre test interne de ce qui reste à valider. »

**Support :** problématique et RQ1–RQ3. **Transition :** avant de présenter un réseau, expliquer ce que les données et les labels signifient.

## 1:30–3:00 — Ce que contient le corpus

« PhiShark2026 contient localement 67 502 scans : des URL reliées à des archives contenant HTML, screenshots et JSON techniques. Le label est une annotation de réputation. Le contenu capturé n'est pas forcément une attaque active visible ; nous n'avons donc pas changé automatiquement les labels des pages 404.

L'EDA révèle des limites importantes. Les sources sont entièrement associées aux classes dans cette copie, et les périodes sont très différentes. Ces constats ne prouvent pas que toute la performance est artificielle, mais ils empêchent d'attribuer sans contrôle un score élevé à une bonne généralisation. Les durées déclarées fin−début sont aussi négatives et ne sont pas utilisées comme temps physiques. Une observation incohérente avec le manifeste d'intégrité est mise en quarantaine, sans être effacée ni relabellisée. »

**Support :** figures sources/périodes et disponibilité. **À éviter :** annoncer la fraction d'AP due aux biais, qui n'est pas mesurée.

## 3:00–4:45 — Préparation et crédibilité du protocole

« L'extraction est hors ligne : aucun HTML n'est exécuté et aucune URL suspecte n'est visitée. L'URL est normalisée sans schéma ni fragment. Le HTML devient du texte extrait, pas un graphe DOM. Les images sont réduites à 96×96. Les JSON fournissent 21 mesures et 21 indicateurs de manque : le MLP technique a donc 42 entrées.

Nous constituons des groupes à partir des identités et des empreintes contrôlées. Nous séparons ensuite cinq rôles : apprentissage des encodeurs, apprentissage des fusions, validation des checkpoints, calibration des seuils et test. Huit clés d'identité ont été revérifiées sans chevauchement entre rôles. Cette protection vise les répétitions connues ; elle ne prouve pas l'absence de toute campagne semblable.

Enfin, les 28 configurations sont comparées sur exactement 13 212 scans complets. Nous conservons un tableau distinct pour le test complet et les modalités manquantes, afin de ne pas confondre performance et couverture. »

**Support :** schéma verbal CSV→ZIP→extraction→groupes→cinq rôles ; table des effectifs. **Transition :** préciser ce que signifie « 28 configurations ».

## 4:45–6:30 — Modèles et fusions réellement implémentés

« Nous utilisons quatre branches compactes : CNN1D caractères URL, CNN1D texte HTML, CNN2D image et MLP technique. Chaque branche produit un embedding de 32 valeurs. Les checkpoints sont choisis sur l'AP de validation, avec un budget de dix époques et arrêt anticipé.

M1 est une moyenne des probabilités disponibles ; aucun poids de fusion supplémentaire n'est appris. M2 reçoit 128 coordonnées d'embeddings et quatre masques, donc 132 entrées, puis apprend une tête dense sur train_fusion. Les encodeurs sont gelés. Ce n'est pas une mixture of experts ni un entraînement conjoint profond.

Nous ajoutons six paires, quatre triplets et le quadruplet, chacun avec moyenne tardive et régression logistique sur embeddings. Cela donne 22 variantes supplémentaires. Les encodeurs restent partagés et la moyenne complète reprend fonctionnellement M1. Le nombre de lignes n'est donc pas le nombre de réseaux indépendamment entraînés. »

**Support :** architectures et dimensions ; expliquer CNN/MLP avec une phrase avant tout vocabulaire spécialisé.

## 6:30–9:00 — Résultats centraux et compromis d'erreurs

« Sur les mêmes scans, le meilleur unimodal en AP est le HTML à environ 0,934. M1 atteint environ 0,972 et M2 environ 0,979. La fusion apporte donc un gain interne, mais ce n'est pas la fin de l'analyse.

Regardons les matrices. M1 génère 807 fausses alertes et manque 390 phishing. M2 génère 141 fausses alertes mais manque 1 006 phishing. M2 évite donc 666 faux positifs, au prix de 616 phishing supplémentaires manqués. Son F1 est aussi inférieur à celui de M1 au seuil primary. La meilleure AP ne signifie pas automatiquement le meilleur système de blocage.

AP mesure un classement ; une matrice mesure une décision à un seuil fixé sur une autre population. Les seuils n'ont pas été réajustés après lecture du test. Selon le coût des erreurs et la prévalence du flux, la préférence entre systèmes pourrait changer. Nous ne choisissons pas un gagnant final sur ce test déjà exploré.

L'incertitude doit également être dite. La différence d'AP M2−M1 est environ 0,0068, avec un intervalle apparié incluant zéro. Le classement ponctuel ne constitue pas une supériorité établie. Les intervalles utilisent des groupes et ne couvrent pas les nouvelles graines ou campagnes. »

**Support :** tableau central, figure des comptages M1/M2. **Phrase à retenir :** « moins de fausses alertes peut signifier davantage de menaces manquées ».

## 9:00–10:30 — Ablations et modalité image

« Le CNN image réalise une AP d'environ 0,593 pour une prévalence de 0,495. Son signal est faible dans cette exécution. L'ajout d'image ne produit pas un gain systématique, et URL+HTML+technique est une combinaison informative.

Nous ne disons pas que l'image est inutile dans tous les systèmes. Notre réseau est petit, sans préentraînement et reçoit une image réduite. Le corpus contient des captures uniformes et expirées. Ce sont des explications plausibles, sans expérience qui isole leur responsabilité totale. Les modèles de logos ou d'intention de la littérature ne sont pas les nôtres.

De même, trois et quatre modalités ayant des AP proches ne sont pas prouvées équivalentes. Une marge et un test adaptés seraient nécessaires. Nous comparons les familles de fusion à méthode fixée pour ne pas attribuer à une modalité un effet qui vient de la tête de classification. »

**Support :** heatmap des sous-ensembles, un cas anonymisé si le temps le permet.

## 10:30–12:30 — Temporalité, ressources et réponses incomplètes

« Le test groupé ne démontre pas l'efficacité sur des campagnes ultérieures. Le protocole chronologique actuellement défini devient non faisable après purge : sa calibration contient 1 511 phishing et aucun bénin. Nous ne fabriquons pas un score pour RQ2. Cela montre la nécessité de collecter les deux classes de façon comparable dans le temps.

Pour le coût, l'extraction locale a demandé environ 128,49 minutes selon le journal. Nous avons 24 mesures tabulaires pandas/PyArrow sur deux scénarios, quatre fractions et trois répétitions. Ces mesures ne sont ni des temps de collecte réseau ni une latence multimodale complète.

Spark est resté bloqué par les ressources avant démarrage de la JVM. Nous ne pouvons pas dire qu'il est plus rapide ou plus lent. RQ3 est partiellement traitée sur les coûts locaux et sa comparaison distribuée reste à compléter avec des opérations et vérifications équivalentes. »

**Support :** tableau chronologique et courbes pandas. **À éviter :** une barre de temps Spark à zéro ou un ratio sans mesure.

## 12:30–14:30 — Démonstration et conclusion

« Le prototype teste une URL seule avec U1 ou une archive locale avec les modalités disponibles et les fusions. Il recharge les poids gelés et n'effectue aucune visite de site. Un exemple historique est une démonstration de parité, pas un nouveau test indépendant.

Notre résultat principal est une amélioration interne par fusion accompagnée d'une description précise des compromis. Les limites majeures sont les biais de collecte, la temporalité non démontrée et la comparaison Spark manquante. Les données, poids, seuils et notebook ont été préservés ; les métriques ont été recalculées depuis les prédictions.

La prochaine étape prioritaire est une collecte équilibrée par période, source et plateforme, une revue de qualité des labels, puis une évaluation indépendante dont les modèles et seuils seront figés avant ouverture. Un meilleur encodeur visuel ou une fusion plus profonde pourra ensuite être évalué dans ce cadre. Le projet apporte une chaîne locale reproductible et un bilan honnête de ce qui reste à démontrer. »

**Réserve :** garder 30 secondes pour une interruption ou une démonstration brève. Les réponses détaillées sont dans `QUESTIONS_JURY.md` ; les CSV et annexes servent de preuves.
