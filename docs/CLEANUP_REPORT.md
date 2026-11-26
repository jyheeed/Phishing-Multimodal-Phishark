# Nettoyage et préparation du dépôt Git

## Organisation retenue

La version finale auparavant dans `PhiShark2026-Final/` a été promue à la racine du dépôt. Un seul notebook actif subsiste : `notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb`. Il contient le pipeline complet et conserve le mode `PRESENTATION` par défaut. Ses sorties sont retirées pour permettre des différences Git lisibles ; une copie exécutée reste dans les artefacts locaux.

Les anciens modules d'entraînement, anciennes générations de rapports, notebooks, constructeurs et scripts de correction ont été déplacés dans `.local_archive/cleanup_20261125/`. Cette archive reste locale et n'est pas une dépendance de la version finale. Le code exact producteur des checkpoints existants est conservé séparément dans `artifacts/provenance/executed_full_code.json`.

Les copies UAT, essais synthétiques, caches pytest/Python, caches d'extraction obsolètes et fichiers temporaires de rendu ont été supprimés. Le lien vers le runtime externe de fabrication des diapositives a été détaché sans supprimer sa cible. Le PPTX final, les rapports et les figures sont conservés. Le code de construction historique des diapositives est archivé localement.

Le dossier vide `PhiShark2026-Final/notebooks` peut rester visible tant que l'éditeur garde un handle sur l'ancien emplacement. Il est ignoré par Git et ne contient aucun notebook actif. Fermer les anciens onglets et rouvrir le notebook à son nouvel emplacement.

## Préservation scientifique

Le corpus original n'a pas été supprimé ou dupliqué. La jonction `data/raw` pointe toujours vers ce corpus. Le cache actif `aea0809c7521684e3b49`, les partitions et les expériences FULL ont été conservés localement. Aucun réseau n'a été réentraîné et aucun label, seuil ou score n'a été modifié.

Les 41 empreintes de préservation existantes ont été revérifiées après déplacement. Les modèles publiables et résultats agrégés possèdent leurs propres manifestes SHA-256. Le bundle d'inférence contient les poids réels, les prétraitements, les seuils et les têtes nécessaires à l'interface. Il ne publie ni captures brutes, ni embeddings par scan, ni registre privé d'URL/prédictions.

## Vérifications

- Tests locaux : parité des six modèles et 22 combinaisons avec les prédictions FULL enregistrées, contrôles des ZIP et modalités manquantes, interface et invariants du notebook.
- Notebook de présentation : noyau neuf, imports des modèles et du code projet interdits ; 225 cellules exécutées, 28 configurations et 13 212 observations communes retrouvées.
- Copie publique de contrôle : uniquement les fichiers autorisés par Git, sans corpus, cache, run privé, environnement ni archive. Tests et présentation vérifiés dans cette copie. Le test de parité dépendant du corpus est explicitement facultatif.
- `scripts/check_repository.py` vérifie les manifestes, les chemins exclus et les tailles des fichiers. Les fichiers publics sont inférieurs à 2 Mio chacun ; le dépôt utile représente environ 8 Mio avant l'historique Git.

Les résultats scientifiques et leurs limites restent ceux du rapport : RQ2 temporelle non démontrée, Spark bloqué par les ressources de l'expérience enregistrée, et besoin d'un nouveau lot indépendant pour confirmer la généralisation.

## Périmètre Git

`.gitignore` exclut corpus, caches, partitions, résultats privés, environnements, archives et secrets usuels. Les modèles compacts, résultats agrégés, preuves de provenance, notebook, code de l'interface, tests et livrables sont inclus.

Le nettoyage n'a ni créé de commit, ni modifié l'index, ni envoyé de données au dépôt distant. Les anciens fichiers déjà suivis apparaissent comme supprimés et les livrables organisés comme nouveaux fichiers : c'est attendu avant la revue et le prochain commit. Ce contrôle concerne l'arbre de travail, pas une réécriture ou un audit exhaustif de l'historique distant.
