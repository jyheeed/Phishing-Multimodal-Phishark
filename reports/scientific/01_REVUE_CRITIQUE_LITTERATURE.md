# Revue critique de littérature — PhiShark2026

## Périmètre de lecture et statut des sources

Revue arrêtée au 25 novembre 2026. Le sujet de l'enseignante, conservé dans `docs/specification/Projet_phishing_multimodal.pdf`, a été lu sur ses deux pages. Il impose RQ1, RQ2 et RQ3. La question de contribution marginale des modalités est une analyse auxiliaire, pas une quatrième exigence ajoutée au sujet.

Les PDF officiels des trois travaux sont récupérés et leur texte extrait : Yoon, 21 pages ; CrossPhire 2026, 45 pages ; thèse 2024, 130 pages physiques. La lecture porte notamment sur les méthodes, tableaux expérimentaux et limites ; il ne s'agit pas d'une reproduction de leurs expériences. Pour la thèse, les chapitres 5 et 6 et tableaux 6.5, 6.6, 6.8 et 6.9 sont les repères principaux. Une première copie tronquée a été remplacée par le fichier complet obtenu via l'API officielle du dépôt universitaire. Les références complémentaires USENIX sont vérifiées sur les notices et résumés officiels ; leurs architectures complètes ne sont pas prétendues reproduites.

Les numéros de page imprimés peuvent différer du rang physique dans un PDF. Pour la thèse, le tableau 6.6 se trouve p. 82 imprimée, autour de la 99e page physique. Les sections et numéros de tableau sont les repères prioritaires.

## 1. Yoon, Buu et Kim — Electronics, 2024

**Objectif et données.** Détecter le phishing en associant des indices URL et DOM. Les bénins proviennent de Common Crawl et les phishing de PhishTank ; la section 4.1 décrit une sélection à 60 000 bénins et 14 912 HTML phishing exploitables. **Architecture/fusion.** CNN de caractères URL, Transformer de mots URL et GCN du DOM ; représentations concaténées puis combinaison apprise. **Évaluation.** Validation croisée à dix plis (§4.3), ablations (§4.5, tableau 7), accuracy, précision, rappel et F1. Le tableau 7 indique une accuracy de 0,8952 pour l'URL caractères, 0,8739 pour le DOM seul et 0,9884 pour l'ensemble. L'expérience externe (§4.7) n'inclut que des phishing : elle ne mesure donc pas un FPR externe.

**Lecture critique et transfert.** L'intérêt pour notre projet est la question de complémentarité, et non l'adoption automatique de son score. Deux branches différentes sur la même URL ne sont pas deux sources de collecte indépendantes. Un graphe DOM représente les liens entre éléments ; notre texte visible ne conserve pas cette topologie. Affirmer que notre CNN HTML « reproduit Yoon » serait donc incorrect. La validation croisée n'est pas interchangeable avec notre séparation par groupes, et aucune des deux ne remplace une évaluation chronologique. Les valeurs publiées doivent rester dans le tableau bibliographique, jamais dans le benchmark PhiShark.

Source : [article et DOI officiels](https://doi.org/10.3390/electronics13163344), §§3–4, tableaux 3, 5, 7 et 8. Une différence entre tableaux ou conventions de moyennage ne doit pas être corrigée silencieusement par le rédacteur : nous utilisons le tableau identifié pour chaque valeur.

## 2. Almakhamreh — thèse de master Hacettepe, 2024

**Objectif/données.** CrossPhire étudie URL, texte et screenshots sur Phish360 et quatre corpus : PILWD-134K, VanNL126K, PhishIntention et PWD2016. **Architecture/fusion.** GramBeddings URL, représentations textuelles de Transformers et ResNet50/DenseNet121 pour l'image, réunis dans un modèle multimodal. **Protocole/résultats.** Comparaisons intra-corpus et inter-corpus ; le tableau 6.6 rapporte 99,21 % d'accuracy sur Phish360 pour CP-EX-2/ResNet50. Le chapitre 6 examine également la dégradation en transfert. Les configurations de texte et d'image diffèrent entre expériences : leurs résultats ne doivent pas être amalgamés.

**Lecture critique et transfert.** Cette thèse fournit un contrepoint utile à l'idée qu'une très bonne validation interne suffit. Le choix du parseur, la langue du texte et la représentation visuelle font partie du système mesuré. Notre petite image 96×96 et notre CNN appris depuis zéro ne possèdent pas les mêmes acquis qu'un encodeur visuel préentraîné. L'écart n'autorise ni à déclarer notre image universellement inutile, ni à annoncer qu'un ResNet résoudra nécessairement notre problème. La bonne expérience future modifierait l'encodeur à données, groupes et budget de sélection contrôlés. Elle ne sera pas inventée pour compléter ce rapport.

Source : [notice universitaire et PDF](https://openaccess.hacettepe.edu.tr/items/52a1fd1b-60a5-482e-8235-a51a32f10e01), chapitres 4–6, tableaux 6.5–6.9. Il s'agit d'un mémoire de master, distinct de l'article de 2026. Nous ne fusionnons pas leurs résultats dans une moyenne bibliographique.

## 3. Almakhamreh et Bozkir — CrossPhire, Applied Sciences, 2026

**Objectif/architecture.** Approfondissement de la détection URL–texte–image avec comparaison concaténation et mixture of experts. **Données/protocole.** Cinq datasets, expériences internes et transfert 80/20 entre corpus (§6.3, tableau 11). **Métriques/résultats.** Accuracy, précision, rappel et F1 ; le transfert Phish360 vers PhishIntention atteint 94,66 % d'accuracy dans le protocole décrit. Les résultats dépendent du couple entraînement–test : ce chiffre n'est pas une performance générale ni une AP.

**Lecture critique et transfert.** L'article motive une évaluation dont la population change réellement. Une fusion intermédiaire sur embeddings gelés, comme notre M2, n'est pas une mixture of experts : elle n'utilise pas un routeur de spécialistes. La comparaison pertinente porte sur la capacité de chaque conception à gérer complémentarité et indisponibilité, pas sur un rapprochement de chiffres produits avec des corpus différents. Le travail fournit aussi un exemple de protocole à préparer pour une collecte indépendante ; il ne valide pas rétrospectivement notre test exploré.

Source : [DOI et texte officiels](https://doi.org/10.3390/app16020751), §§5, 6.2–6.3 et 7, tableaux 10–12. Les paramètres et résultats de cette publication ne sont pas attribués à la thèse 2024.

## 4. Phishpedia et PhishIntention

| Travail | Objectif, méthode et évaluation officiellement décrits | Enseignement et limite de transfert |
|---|---|---|
| Lin et al., Phishpedia, USENIX Security 2021 | Reconnaissance et rapprochement de logos avec des références de marques ; évaluation comparative et étude sur le terrain. La notice rapporte 1 704 nouveaux sites en 30 jours. | Détecter une marque usurpée apporte une explication spécifique. Notre classifieur d'image globale n'accomplit pas cette identification ; aucune équivalence d'architecture ou de protocole n'est revendiquée. |
| Liu et al., PhishIntention, USENIX Security 2022 | Analyse visuelle de marque, collecte d'identifiants et interaction avec la page ; évaluation comparative et terrain. La notice décrit 139 contre 1 033 faux positifs pour un nombre de détections similaire à la baseline comparée. | La ressemblance visuelle seule ne prouve pas l'intention de phishing. Notre système ne navigue pas activement et ne vérifie pas l'intention par interaction. Les comptages du papier ne sont pas des FP de PhiShark. |

Sources : [Phishpedia, notice et BibTeX](https://www.usenix.org/conference/usenixsecurity21/presentation/lin), [PhishIntention, notice et BibTeX](https://www.usenix.org/conference/usenixsecurity22/presentation/liu-ruofan). Les valeurs ci-dessus sont des résultats publiés, sans confrontation numérique directe avec notre AP.

## 5. Sources de méthode et de données

Le document de Chapman et al., *CRISP-DM 1.0* (2000), structure les responsabilités entre compréhension, préparation, modélisation et évaluation. Il ne constitue pas une garantie de qualité d'un modèle particulier. Source : [guide officiel hébergé par IBM](https://public.dhe.ibm.com/software/analytics/spss/documentation/modeler/14.2/fr/CRISP-DM.pdf).

Le préprint de Çolhak et al. (2026), [arXiv:2608.23199](https://arxiv.org/abs/2608.23199), décrit PhiShark comme un corpus de preuves brutes et de disponibilité explicite. Son statut est celui d'un préprint, sans le présenter comme une validation de notre copie. Nos effectifs, quarantaines et métriques sont déterminés par les fichiers locaux.

## 6. Positionnement de notre contribution

Notre contribution est une étude contrôlée de quatre modalités, deux fusions centrales et onze sous-ensembles par deux méthodes, avec contrôles d'alignement, séparation des rôles et analyse du coût des erreurs. Elle n'est ni l'invention de la fusion multimodale, ni une réimplémentation de CrossPhire, ni une validation externe de Phishpedia. Une modalité est jugée dans le système effectivement construit. Le compte rendu doit séparer l'amélioration du classement interne, la décision à seuil fixé et la généralisation sur de nouvelles populations.

Les hypothèses deviennent réfutables en désignant un indicateur et une population : gain d'AP sur mêmes observations, modification du rappel/FPR, effet marginal à méthode de fusion fixée. Une causalité de collecte, une équivalence entre modèles ou une robustesse temporelle nécessitent des expériences supplémentaires. Les déclarer ouvertes fait partie de la contribution scientifique.
