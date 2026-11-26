## Chapitre 6 — Résultats expérimentaux et discussion

### 6.1. Population comparée et contrat de lecture

L'objectif prioritaire est de déterminer ce que les fusions changent sur les mêmes individus. Chaque configuration est évaluée sur 13 212 identifiants communs, dont 6 544 phishing et 6 668 bénins. La prévalence vaut 0,495307. Les 5 230 groupes de la cohorte définissent l'unité du bootstrap. Les résultats des 13 439 scans du test complet sont présentés séparément : ils ne constituent pas le dénominateur des matrices de ce chapitre.

La nouvelle vérification relit les scores non arrondis, aligne les identifiants, applique les seuils gelés et recalcule AP, ROC-AUC et matrices. Les 28 lignes concordent à la tolérance numérique fixée avec les CSV publiés. Ce contrôle montre la cohérence des artefacts ; il ne démontre pas une vérité universelle des labels ni une bonne généralisation. Les prédictions et le test ont déjà été consultés, de sorte que cette comparaison doit rester exploratoire.

Les configurations n'ont pas toutes le même nombre de paramètres ni le même mécanisme de fusion, mais la population reste fixe. Cela évite de confondre une AP plus haute et une cohorte plus facile. La restriction aux cas complets peut toutefois exclure des pages difficiles à capturer. Son coût de couverture est documenté, et les tableaux secondaires conservent les observations disponibles pour chaque combinaison.

### 6.2. Définir les métriques avant de les interpréter

La précision mesure la fraction de phishing étiquetés parmi les alertes. Le rappel mesure la fraction de phishing retrouvés. Le FPR rapporte les fausses alertes au nombre de bénins ; le FNR rapporte les phishing manqués au nombre de phishing. Le F1 est la moyenne harmonique de précision et rappel. Ces définitions ne donnent pas le même poids aux erreurs et leurs dénominateurs doivent rester visibles.

L'exemple M1 fournit un calcul contrôlable : précision=6 154/(6 154+807)=0,884068 ; rappel=6 154/(6 154+390)=0,940403 ; FPR=807/(807+5 861)=0,121026. Une précision élevée et un FPR non négligeable peuvent coexister, parce qu'ils ne divisent pas par la même population. Une précision de test proche de 0,88 ne sera pas nécessairement celle d'un flux opérationnel beaucoup moins riche en phishing.

AP résume le classement aux changements de rappel, suivant la définition d'average precision utilisée dans le code. Elle ne dépend pas du choix final primary ou recall85 lorsque les scores restent identiques. La courbe PR porte une référence de prévalence. ROC-AUC décrit un autre aspect du classement et ne remplace pas le contrôle des fausses alertes. Saito et Rehmsmeier [8] motivent l'attention aux courbes PR ; notre corpus quasi équilibré et un futur flux opérationnel déséquilibré restent des populations différentes.

La sigmoid borne un logit entre 0 et 1, mais ne garantit pas que 0,8 signifie 80 % de risque en déploiement. Le sous-ensemble nommé calibration a servi à choisir des seuils, sans calibrateur probabiliste supplémentaire. AP, seuil et calibration probabiliste sont trois notions séparées. Les amalgamer rendrait l'interprétation du score de l'interface trompeuse.

### 6.3. Vue d'ensemble des six modèles centraux

{{CENTRAL_RANKING}}

{{CENTRAL_DECISION}}

Les deux fusions centrales ont une AP supérieure à celle de chaque unimodal sur cette cohorte. Le meilleur unimodal en AP est le CNN HTML, U2. L'URL et la technique contiennent également un signal important, tandis qu'U3 reste nettement plus faible. Ces constats répondent au cœur de RQ1 sur une population et une exécution définies. Ils ne justifient pas l'affirmation que toute fusion ou toute modalité additionnelle améliore les résultats.

Le critère choisi change aussi l'ordre. M2 a une AP plus élevée que M1, alors que son F1 primary est inférieur et son rappel plus faible. U1 atteint un rappel élevé au prix de nombreuses fausses alertes. Les tableaux de classement et de décision sont séparés pour rendre ces différences lisibles. Le seuil est une partie du système évalué ; il n'est pas choisi pour embellir la matrice présentée.

![Figure 1 — AP des six modèles centraux sur les mêmes 13 212 scans ; figure historique vérifiée, aucun nouveau réseau entraîné.](FIGURES_ET_RESULTATS/01_modeles_AP.png)

### 6.4. URL, HTML et technique : informations et erreurs résiduelles

U1 réalise un rappel de 0,968062 au seuil primary, avec 2 743 faux positifs. La normalisation retire HTTP/HTTPS et le fragment, mais l'hôte, le chemin et la query demeurent observables. Le score peut exploiter des régularités de sources ou de plateformes. L'absence de source explicite dans l'entrée n'est donc pas la preuve que le modèle a appris uniquement des signes sémantiques du phishing.

U2 atteint une AP de 0,933933, mais sa représentation est limitée au texte extrait et tronqué. Les pages riches en scripts ou les indices structurels non textuels ne sont pas modélisés comme tels. Une bonne performance textuelle peut refléter des messages de formulaire, des pages d'erreur ou des signatures de collecte ; l'AP seule ne permet pas de distribuer la contribution entre ces mécanismes. Les cas doivent être examinés sans réécrire les labels à partir des prédictions.

U4 atteint une AP de 0,905998 et utilise explicitement les indicateurs manquants. Ses 42 entrées décrivent des propriétés de preuves plutôt qu'une liste universelle de critères malveillants. Les comptes de liens, redirections et preuves techniques peuvent compléter une URL ambiguë. Mais les proxys de collecte restent possibles, puisque source et classe sont associées dans le corpus. La part exacte du score historique due à ces proxys n'est pas causalement mesurée dans l'exécution finale.

Un écart de validation à test ne doit pas être attribué à une seule cause. Les sites, contenus et cas disponibles changent ; le checkpoint a été choisi sur validation ; et l'échantillonnage des groupes peut modifier la difficulté. Le recul d'AP d'U1 ou U3 indique une sensibilité de généralisation interne, sans identifier à lui seul un bug ou une fuite résiduelle.

### 6.5. CNN image : résultat faible et explications non confondues

U3 obtient une AP de 0,592764 pour une prévalence commune de 0,495307, une ROC-AUC de 0,564554 et 3 654 faux positifs à son seuil primary. Il serait excessif d'affirmer qu'il n'existe aucun signal visuel ; il serait tout aussi excessif de présenter cette branche comme une contribution forte. Le constat est celui d'une discrimination modeste dans le système exécuté.

Quatre mécanismes sont plausibles : perte de détails à 96×96, capacité d'un petit CNN entraîné depuis zéro, captures d'erreur ou uniformes et distribution propre aux sites séparés en groupes. Les données EDA confirment l'existence de captures uniformes et de statuts 404, mais elles ne démontrent pas que ces éléments causent toute la faiblesse d'U3. Nous n'avons pas isolé l'effet de la résolution, du préentraînement ou de la langue par une expérience contrôlée dédiée.

Les architectures de marque des références ne peuvent pas servir à attribuer rétrospectivement au CNN des capacités qu'il ne possède pas. Une étude future pourrait comparer une représentation préentraînée et une autre résolution, avec mêmes groupes et budget de sélection, puis évaluation indépendante. Elle ne sera pertinente qu'après contrôle des sources et des cibles. Relancer un réseau plus grand pour obtenir une valeur attendue ne répondrait pas à cette exigence.

Les ablations renforcent la lecture prudente : ajouter IMAGE à certaines combinaisons détériore leur AP. Ce résultat concerne une branche donnée et une famille de fusion donnée. Il ne signifie pas qu'un screenshot est inutile à l'analyste humain ni qu'une autre représentation ne pourrait pas compléter le texte.

### 6.6. Combinaisons bimodales : comparer à méthode fixée

{{PAIRS_TABLE}}

URL+HTML, URL+TECH et HTML+TECH illustrent une complémentarité interne de modalités déjà informatives. Les ensembles comportant l'image ne sont pas systématiquement supérieurs aux modèles non visuels. La méthode de fusion joue également un rôle : LINEAR_EMBED et LATE n'ordonnent pas toujours les mêmes ensembles de la même manière. L'une apprend une tête et une normalisation ; l'autre moyenne des scores disponibles.

La comparaison d'une paire au meilleur de ses composants renseigne sur un bénéfice interne, mais ne suffit pas à expliquer la cause du bénéfice. Par exemple, un texte peut aider à réordonner des URL mal classées ; il peut aussi porter des indices de source partagés. Les différences appariées d'AP et les cas d'erreur permettent de mieux décrire le comportement, sans transformer une association en mécanisme causal confirmé.

Il faut aussi éviter d'affirmer que le meilleur chiffre bimodal constituerait le meilleur système à déployer. Les variantes ont été examinées sur le même test et leur comparaison n'est pas un concours indépendant. Un choix opérationnel doit fixer les objectifs de rappel, couverture et coût sur validation, puis être évalué sur une population restée hors sélection.

### 6.7. Triplets et quadruplet : proximité n'est pas équivalence

{{TRIPLETS_TABLE}}

URL+HTML+TECH est particulièrement informatif dans cette exécution. Son AP LATE est légèrement supérieure à celle de la moyenne complète ; sa tête LINEAR_EMBED possède également une AP supérieure au quadruplet de la même famille. Ces résultats suggèrent que la quatrième modalité n'ajoute pas systématiquement un signal utile sous ces représentations.

La proximité des AP ne prouve pas l'équivalence entre trois et quatre modalités. Une étude d'équivalence définirait une marge acceptable avant l'évaluation et analyserait l'incertitude de la différence dans ce cadre. Un intervalle recouvrant zéro ne prouve pas que les systèmes sont égaux. Inversement, un écart ponctuel ne suffit pas à déclarer une supériorité générale après de nombreuses comparaisons.

Comparer M2 à LINEAR_EMBED sur un triplet change à la fois les modalités et la tête. Pour attribuer un effet à IMAGE, il faut utiliser les deux configurations LINEAR_EMBED ou les deux règles LATE à ensembles emboîtés. Le tableau des contrastes conserve cette règle. Le choix d'une architecture et le choix d'un sous-ensemble sont deux décisions de modélisation différentes.

![Figure 2 — AP des onze sous-ensembles et des deux méthodes de fusion ; cohorte commune, comparaison exploratoire.](FIGURES_ET_RESULTATS/02_combinaisons_heatmap.png)

### 6.8. Contribution marginale et bootstrap apparié

{{CONTRIBUTION_TABLE}}

Les contrastes ajoutent une modalité à un ensemble de référence, en conservant la famille de fusion. Le signe de la différence indique une amélioration ou une dégradation d'AP dans cette exécution. Les intervalles sauvegardés reposent sur 200 tirages appariés des 5 230 groupes, avec graine 42. Les mêmes groupes rééchantillonnés sont utilisés pour les modèles comparés afin de préserver la dépendance des observations.

Le rééchantillonnage porte sur les groupes sites/contenus effectivement constitués, pas sur une campagne parfaitement annotée. Les groupes sont tirés avec remise et les différences recalculées sur leurs observations. Cette méthode évite de traiter chaque scan comme indépendant lorsque plusieurs appartiennent à une même entité. Elle reste conditionnelle aux poids appris et au corpus de test observé.

Les intervalles ne couvrent ni les variations d'une nouvelle graine d'entraînement ni une autre distribution de sources. Les 65 contrastes sauvegardés ne sont pas corrigés pour multiplicité. Une borne excluant zéro est une indication exploratoire conditionnelle, pas une découverte définitive. Aucun nouveau seuil ni modèle n'est choisi à partir de ces intervalles.

Pour M2 moins M1, la différence d'AP est 0,006762, avec un intervalle descriptif à 95 % de −0,004944 à 0,020995. Le gain ponctuel ne fournit donc pas une preuve nette de supériorité d'AP de M2 sur M1 dans ce cadre. En revanche, leurs matrices aux seuils fixés montrent un échange d'erreurs concret que l'on peut discuter indépendamment de cette incertitude de classement.

### 6.9. M1 contre M2 : lire les matrices avant de choisir

{{M1_M2_MATRICES}}

M1 détecte 6 154 phishing et en manque 390, au prix de 807 fausses alertes. M2 en détecte 5 538 et en manque 1 006, avec 141 fausses alertes. M2 évite donc 666 FP, mais ajoute 616 FN. Il privilégie un point plus conservateur sur les alertes au seuil retenu. Il ne domine pas M1 simultanément en rappel et FPR.

Le nombre total d'erreurs est de 1 197 pour M1 et 1 147 pour M2. Même cette légère réduction totale ne résout pas la question métier : une omission de phishing peut coûter davantage qu'une fausse alerte, ou inversement dans un système d'analyse manuelle. Compter toutes les erreurs avec le même coût impose une hypothèse qui doit être annoncée, pas dissimulée derrière une accuracy.

Le F1 de M1 est supérieur au F1 de M2 sur ce test commun, bien que l'AP de M2 soit plus élevée. Les deux métriques répondent à des questions différentes. L'AP mesure le classement sur une gamme de seuils ; le F1 primary est le résultat d'un seuil choisi ailleurs, sur calibration. Un bon classement ne garantit pas que ce seuil conserve le même compromis lorsque la population change.

![Figure 10 — Faux positifs et phishing manqués pour M1 et M2 ; mêmes 13 212 scans, seuils primary déterminés sur calibration.](FIGURES_ET_RESULTATS/10_compromis_comptages.png)

### 6.10. Un calcul pédagogique de coût, sans sélection sur le test

Posons, uniquement pour interprétation, un coût cFP par faux positif et cFN par faux négatif. Sur cette cohorte, la différence de coût M2−M1 vaut −666×cFP+616×cFN. Si cFN/cFP est inférieur à 666/616, soit environ 1,0812, M2 a le coût le plus faible sous ce modèle simplifié. Au-delà, M1 a le coût le plus faible. Ce calcul illustre comment une préférence peut s'inverser sans modifier les AP.

Ces coûts ne sont pas des coûts d'entreprise mesurés. Le calcul ne sert pas à choisir un système final sur le test courant. Il ignore la gravité variable des incidents, les abstentions, la charge d'analystes et le changement de prévalence. En déploiement, les effectifs dépendent du flux de bénins et de phishing, pas de la taille artificiellement équilibrée d'un benchmark.

La bonne pratique future serait de définir les coûts ou une contrainte de rappel avant l'évaluation finale, de choisir la politique sur un historique approprié, puis de tester sans réajustement sur un lot indépendant. Le mémoire contribue à formuler cette décision ; il ne transforme pas des scénarios pédagogiques en rendement économique démontré.

### 6.11. Politiques primary et recall85

{{OPERATING_TABLE}}

La politique recall85 conserve les seuils déjà fixés sur calibration. Elle ne représente pas un nouveau réglage sur test. Pour M1 et M2, le rappel de test sous cette politique peut être inférieur à 85 %. Ce résultat n'est pas une anomalie de formule : le niveau cible était atteint sur une autre population. L'effet peut provenir des différences de composition et des scores, sans qu'un ajustement postérieur soit autorisé pour le masquer.

Une contrainte de rappel est plus directement interprétable qu'un F1 maximal pour certaines opérations, mais elle doit être évaluée sur une validation représentative. Il faut aussi rapporter le FPR et le nombre d'alertes induits, pas seulement vérifier la contrainte sur l'échantillon de choix. La figure de compromis est donc présentée avec son origine de seuil.

![Figure 3 — Compromis rappel/FPR aux politiques figées ; les points sont des diagnostics, pas une optimisation a posteriori.](FIGURES_ET_RESULTATS/03_compromis_FPR_rappel.png)

![Figure 4 — Courbes précision–rappel des modèles centraux et prévalence de référence ; test commun.](FIGURES_ET_RESULTATS/04_precision_recall.png)

### 6.12. Analyse des faux positifs et faux négatifs

{{ERROR_STRATA_TABLE}}

Les taux par statut, qualité d'image, source ou période permettent de localiser des difficultés. Chaque strate doit préciser le nombre de bénins et de phishing, car un taux sans dénominateur est trompeur et une strate ne contenant qu'une classe ne définit pas tous les taux. Les petites strates ne constituent pas des preuves stables de comportement général.

Les vingt cas anonymisés de l'annexe illustrent les erreurs des fusions. M1_FP_01 possède un statut 200 et trois champs manquants ; sa probabilité enregistrée est environ 0,57735 pour un seuil d'environ 0,380406. M2_FN_16 est un phishing historique avec HTTP 404 et image uniforme, dont le score d'environ 0,256577 est inférieur au seuil d'environ 0,753241. Ces descriptions montrent comment une décision est obtenue et quels éléments examiner ensuite.

Les descriptions ne sont pas une revue humaine de labels. Aucun examen indépendant ne permet ici d'affirmer que ces scans sont mal annotés. Un HTTP 200 n'établit pas la bénignité et un 404 n'invalide pas une réputation antérieure. La prochaine revue doit confronter le moment d'annotation, les redirections et les preuves archivées, avec accès contrôlé et protection des informations sensibles.

L'échantillon est déterministe : cinq premiers IDs triés par modèle et type d'erreur, et non les exemples les plus convaincants choisis après lecture du contenu. Cette règle rend la sélection reproductible mais non représentative. Les causes proposées restent des hypothèses ; l'évaluation globale repose sur tous les individus, pas sur les seuls exemples.

### 6.13. Cohorte commune, cas disponibles et couverture

{{FULL_TEST_TABLE}}

Le test complet réintroduit 227 observations absentes de la cohorte commune. Les performances centrales et la couverture doivent alors être lues avec les règles de modalité propre à chaque modèle. Pour les variantes, `table_22_available.csv` décrit les populations disponibles. Une AP sur une cohorte élargie n'est pas directement une variation de qualité à modèle et population fixes.

Le bilan principal conserve les cas complets pour les contrastes appariés. Le bilan secondaire renseigne ce que le système ferait lorsque certaines preuves manquent. Aucun des deux n'annule l'autre : l'un privilégie la comparabilité, l'autre la proximité avec l'indisponibilité réelle. Une évaluation indépendante future doit définir à l'avance quelle couverture et quelle politique d'abstention correspondent à l'usage.

### 6.14. Réponse à RQ1 et portée de l'explication

Sur la cohorte interne, M1 et M2 dépassent les quatre unimodaux en AP et en F1 primary. Les contrastes et leur incertitude soutiennent l'intérêt de combiner des modalités informatives. Ils réfutent en revanche l'idée d'un gain automatique à chaque ajout et ne démontrent pas une équivalence entre trois et quatre modalités. M2 n'est pas déclaré gagnant universel : son point de décision manque davantage de phishing et sa différence d'AP avec M1 demeure incertaine au regard de l'intervalle apparié.

La facilité apparente de certains scores ne justifie ni une baisse artificielle des performances ni une satisfaction sans examen. Les sources et périodes expliquent une partie plausible de la séparabilité, sans quantification causale de cette part. Les contrôles de disjonction et de recalcul retirent des erreurs connues d'évaluation ; ils ne transforment pas un corpus de collecte biaisé en population opérationnelle représentative.

La conclusion défendable est une amélioration de classification interne sous conditions explicites. Les limites de l'image, les cas expirés, les inconnus techniques et l'effet du seuil sont des résultats de recherche utiles. L'étape suivante n'est pas de sélectionner la ligne la plus haute du tableau, mais de concevoir l'évaluation indépendante décrite au chapitre 7.
