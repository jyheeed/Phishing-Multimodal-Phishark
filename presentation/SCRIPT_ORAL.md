# Script oral — 15 diapositives, environ10–15minutes


Les chiffres des modèles proviennent de la cohorte commune13212, sauf indication explicite. Les questions de coût portent sur leur périmètre réellement mesuré.


## 1. PhiShark2026

Je présente PhiShark 2026, un projet de détection multimodale du phishing. Mon objectif n'est pas d'afficher le score le plus élevé, mais de vérifier ce que la combinaison des preuves apporte et à quel coût en erreurs. Le travail suit CRISP-DM. Je présenterai les réseaux, les fusions et leurs limites. Les résultats proviennent d'un FULL exécuté et vérifié ; aucun entraînement n'est lancé pendant cette soutenance.



## 2. Une URL ne raconte pas toute la page

Le phishing peut être visible dans une adresse, dans le texte d'une page ou dans son apparence. Une seule preuve peut manquer ou être trompeuse. Il faut aussi distinguer le label d'une URL et ce que la capture a effectivement enregistré. Une erreur 404 ne rend pas automatiquement la réputation bénigne. Les faux positifs bloquent des sites légitimes ; les faux négatifs laissent passer des phishing. C'est ce compromis que je mesure.



## 3. Trois questions, trois niveaux de preuve

Le sujet pose trois questions. La première concerne la complémentarité des modalités et sera étudiée par des comparaisons appariées. La deuxième concerne le temps : un test groupé ne suffit pas à démontrer une robustesse à de nouvelles campagnes. La troisième porte sur le coût Big Data. Je distinguerai les mesures réellement exécutées des expériences bloquées. Une réponse non démontrée est une limite du protocole, pas une invitation à fabriquer une métrique.



## 4. 67 502 scans, des sources très structurées

Le corpus compte 67502 scans. Une archive diverge du manifeste d'origine et reste en quarantaine, avec son label intact. Les captures sont riches, mais la composition du dataset crée une limite forte : source et classe sont parfaitement associées dans le CSV. Même si ces colonnes ne sont pas utilisées directement comme features, leurs effets peuvent se refléter dans les captures ou les URL. Cela empêche de confondre un bon score interne et une certification externe.



## 5. CRISP-DM organise le raisonnement

CRISP-DM structure le projet en six phases. Je définis d'abord la cible et les coûts d'erreur, puis j'audite le corpus. La préparation ne consiste pas seulement à nettoyer : elle empêche qu'un site ou un contenu identique soit partagé entre les rôles. Les modèles sont ensuite entraînés, puis évalués avec des seuils gelés. Enfin, le déploiement reste un prototype local accompagné de limites et d'un plan de validation future.



## 6. Un pipeline traçable, pas seulement un modèle

L'extraction lit les archives originales sans visiter les sites. Elle produit les entrées techniques, le texte visible et les images. Parquet conserve une représentation typée et réutilisable. Les groupes réunissent les entités et les contenus contrôlés. Cinq rôles distincts évitent d'apprendre les encodeurs et la fusion sur les mêmes observations. Les vocabulaires et normalisations voient uniquement leur train autorisé. Les labels et les dates ne sont pas modifiés pour obtenir de meilleurs résultats.



## 7. Quatre branches, une représentation commune

Les convolutions 1 D apprennent des motifs locaux dans les caractères d'URL ou les tokens du HTML. Le CNN 2 D traite l'image globale, sans reconnaissance de logo spécialisée. Le MLP technique traite des mesures numériques normalisées et leurs indicateurs manquants. Les quatre branches fournissent chacune 32 valeurs. Les checkpoints sont choisis sur validation avec early stopping. Le schéma HTTP/HTTPS a été retiré des entrées d'U 1 pour éviter ce raccourci particulier, mais les biais d'hébergement peuvent subsister.



## 8. Deux fusions centrales, 22 études complémentaires

M 1 combine les probabilités à poids égaux, en tenant compte des modalités disponibles. M 2 concatène les quatre embeddings et les masques, puis apprend un MLP sur un train de fusion indépendant. Les 22 études supplémentaires testent six paires, quatre triplets et le quadruplet, par moyenne et par régression logistique sur embeddings. Ce ne sont donc pas 22 nouveaux CNN. Toutes les politiques sont définies avant leur évaluation ; le test ne choisit pas rétroactivement un gagnant final.



## 9. RQ1 · Les fusions améliorent le classement interne

Les six modèles sont comparés sur exactement 13212 scans. M 1 et M 2 améliorent l'AP par rapport aux unimodaux, dont le meilleur est le HTML. Les différences avec HTML ont des intervalles bootstrap groupés positifs dans cette analyse exploratoire. En revanche, l'intervalle de la différence entre M 2 et M 1 recouvre zéro : je ne peux pas affirmer leur supériorité générale l'un sur l'autre. Le CNN image est faible ; je conserve ce résultat au lieu de le masquer.



## 10. Trois modalités peuvent rivaliser avec quatre

La comparaison commune montre que trois modalités peuvent rivaliser avec quatre. La tête linéaire URL, HTML et technique obtient une AP légèrement supérieure à sa version avec image. Le bootstrap de cet ajout d'image suggère une baisse locale, mais les multiples comparaisons ne sont pas corrigées. Dans la moyenne tardive, le petit écart avec ou sans image reste compatible avec zéro. Je n'en conclus pas que les images sont inutiles en général : mon petit CNN n'analyse ni logo ni intention de saisie.



## 11. Une meilleure AP ne décide pas du bon seuil

Sur la cohorte commune, M 1 produit 807 faux positifs et 390 faux négatifs. M 2 produit 141 faux positifs et 1006 faux négatifs. La forte réduction des fausses alertes s'accompagne donc de phishing supplémentaires manqués. L'AP décrit le classement des scores, pas ce point d'exploitation. Le choix métier doit fixer à l'avance le coût acceptable de ces erreurs, puis être confirmé sur une collecte indépendante.



## 12. RQ3 · pandas mesuré, Spark bloqué par la mémoire

Le benchmark stocke les mêmes colonnes et réalise la même chaîne logique. Les médianes pandas au volume maximal sont d'environ 0,31 seconde et 0,40 seconde selon le scénario. Ces valeurs portent sur un Parquet tabulaire de quelques mégaoctets, pas sur l'extraction des 28 Go d'archives. L'extraction complète a duré environ 128 minutes. Un processus séparé sans réseaux a contrôlé Spark, mais moins d'un gigaoctet restait disponible. Je ne présente donc aucune comparaison de vitesse Spark, ni une exécution locale comme un cluster.



## 13. RQ2 · La généralisation temporelle reste non démontrée

Le protocole temporel applique des frontières fixes et purge les groupes partagés entre périodes. Après cette opération, la calibration contient 1511 phishing et aucun bénin. Il est impossible d'y fixer un compromis binaire représentatif. Je n'ai pas déplacé les dates ni changé les labels. La généralisation temporelle n'a donc pas pu être démontrée avec le corpus actuel. Cela constitue une limite méthodologique documentée, qui motive une collecte où chaque période contient les deux classes dans des conditions comparables.



## 14. Démonstration : comprendre une décision sauvegardée

La démonstration charge une décision déjà calculée, plutôt que de dépendre d'un site vivant pendant la soutenance. On voit les six scores, leurs seuils et leurs décisions, qui peuvent différer. Cette démonstration ne crée pas un nouvel exemple indépendant et ne prouve pas que le phishing est actif aujourd'hui. Pour un nouveau site, il faudrait produire une capture contrôlée, puis appeler les fonctions d'inférence du notebook FULL avec les checkpoints figés. L'acquisition et la validation prospective restent nécessaires.



## 15. Ce que le projet démontre — et ce qu’il reste à valider

Le projet est terminé pour ses entraînements et son analyse multimodale. La fusion améliore le classement interne, mais aucune architecture n'est universellement meilleure au seuil opérationnel. Les limites importantes sont les sources, les périodes, les captures et l'absence de nouveau lot indépendant. Je propose donc une suite ciblée : finir Spark sur une machine suffisante, revoir les erreurs humaines prioritaires et collecter un lot équilibré puis scellé. Il ne s'agit pas de recommencer les réseaux pour augmenter artificiellement leurs scores.
