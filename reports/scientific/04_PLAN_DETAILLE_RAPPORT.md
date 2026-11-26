# Plan détaillé du mémoire et traçabilité

Le volume est déterminé par les preuves et la lisibilité. La cible indicative 45–65 pages n'autorise ni répétition artificielle ni résultats imaginés. Les pages liminaires, bibliographie et annexes sont distinguées du corps scientifique.

| Partie | Question argumentative | Éléments et illustrations | Sources de preuve |
|---|---|---|---|
| Résumés et glossaire | Quel problème, quelle méthode, quelles limites ? | Résumé FR, abstract EN, sigles, sommaire, listes de figures et tableaux | Synthèse des chapitres, aucune nouvelle métrique |
| 1. Introduction | Pourquoi associer des preuves plutôt qu'une seule heuristique ? | Réputation vs contenu capturé ; FP/FN ; RQ1–RQ3 ; contribution sans revendication architecturale nouvelle | Sujet enseignant ; cadre de littérature |
| 2. État de l'art | Quels enseignements sont transférables ? | URL/HTML/image/technique ; Yoon ; thèse 2024 ; article 2026 ; logos/intention ; matrice de positionnement | Revue critique, DOI et sections précises |
| 3. Problème et données | Qu'est-ce que les labels et les captures mesurent ? | Classes, périodes, sources, disponibilité, erreurs de capture ; risques et hypothèses | Métadonnées originales et canonical.parquet ; agrégats EDA recalculés |
| 4. Préparation | Comment construire une expérience sans fuite connue ? | CSV→ZIP→JSON/HTML/image→Parquet ; 21 features/42 entrées ; groupes ; cinq rôles ; fit train-only | Notebook courant, préparation du run, dictionnaire de features |
| 5. Modélisation | Que compare-t-on effectivement ? | Couches et tenseurs ; loss/optimiseur ; M1 ; M2=132 ; 11 sous-ensembles×2 ; hyperparamètres et coût | Définitions AST, settings, complete.json et frozen.json |
| 6. Résultats et discussion | La fusion apporte-t-elle un bénéfice et à quel prix ? | 28 configurations ; AP/ROC et décision ; paires/triplets ; matrices ; erreurs ; M1/M2 ; coût relatif des erreurs ; incertitude ; limites de l'image | Prédictions test, cohortes, seuils gelés, tables appariées et cas anonymisés |
| 7. Échelle et généralisation | Qu'a-t-on réellement mesuré au-delà du classement ? | 24 mesures pandas ; Spark bloqué ; chronologie non faisable ; collecte et test futur indépendant | benchmark_summary, spark_status, temporal_feasibility |
| 8. Démonstration et conclusion | Que peut montrer le prototype et que reste-t-il à démontrer ? | URL seule/capture ; abstention ; exemple sauvegardé ; réponses RQ ; perspectives hiérarchisées | Interface, manifestes et résultats d'exemple |
| Annexes | Un lecteur peut-il contrôler les affirmations ? | Liste des 28, dictionnaire de 21 variables, tableaux complets, couches, empreintes et index des figures | reports/FIGURES_ET_RESULTATS et scripts de rédaction/vérification |

## Priorités de rédaction

Le chapitre 6 porte l'argument principal : comparer les mêmes individus, distinguer classement et décision, documenter le coût des erreurs et qualifier l'incertitude. Les chapitres 3–5 apportent les conditions nécessaires à sa lecture. Les chapitres 7–8 délimitent la généralisation, sans transformer RQ2 et Spark en succès non observés.

Chaque section majeure présente objectif, justification, méthode, exemple, résultat, interprétation et limite dans une progression rédigée. Les exemples sont des cas locaux pseudonymisés ; aucun lien malveillant actif, token ou contenu sensible n'est publié.

## Critères de sortie

1. Toutes les lignes des 28 sont recalculées depuis leurs prédictions sur mêmes IDs et labels.
2. Les 21/42/132 dimensions et couches concordent avec le code.
3. Les sources bibliographiques ont un titre, un auteur, un statut et un accès identifiables.
4. Les figures possèdent un fichier de données source et une population explicite.
5. RQ1 est interne/exploratoire, RQ2 non démontrée dans le protocole défini, RQ3 partielle.
6. Aucun entraînement, relabel, changement de seuil, modification de checkpoint ou du notebook n'est réalisé pour la rédaction.
