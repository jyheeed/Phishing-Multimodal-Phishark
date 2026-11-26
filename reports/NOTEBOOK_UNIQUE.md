# Notebook final unique — consignes

Le seul fichier de travail à utiliser est `notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb`.

Il contient 225 cellules, dont 122 de code, en trois parties :

1. **Pipeline FULL CRISP-DM** : extraction, contrôle, partitions, quatre réseaux unimodaux, deux fusions, 22 combinaisons, calibration, test, inférence, diagnostics et benchmark.
2. **Analyse finale intégrée** : recalcul des métriques, cohortes, bootstrap par groupes, contribution des modalités, erreurs, figures et rapport d'analyse.
3. **Restitution** : rechargement des résultats déjà exécutés, tableaux, graphiques et démonstration enregistrée.

En `PRESENTATION`, les cellules de calcul FULL sont ignorées automatiquement. Tout exécuter affiche les résultats sans charger les réseaux. Les fonctions de lecture sont intégrées : aucun import de `src/` et aucun appel à un autre notebook.

En `FULL_EXPERIMENT`, le code du pipeline et de l'analyse s'exécute directement dans les cellules. La signature est celle de cette nouvelle version. Les anciens résultats ne sont pas rebaptisés ni réattribués à un nouveau code ; ce mode peut créer une nouvelle extraction et de nouveaux entraînements. Il n'est pas nécessaire pour consulter ou défendre l'expérience déjà terminée.

Les anciens notebooks restent des sauvegardes. Les données, checkpoints, figures et CSV sont naturellement des fichiers d'entrée/sortie du projet, pas des dépendances à un autre code de notebook.

Validation : présentation exécutée avec tous les imports de code projet et de modèles interdits ; analyse du notebook exécutée sur une copie des résultats, sans réseaux ; équivalence structurelle des 106 cellules de calcul d'origine vérifiée ; 12 tests légers réussis. Aucun FULL relancé lors de cette préparation.

Recharger le fichier depuis le disque, sélectionner `my_env`, redémarrer le noyau puis Tout exécuter. Éviter d'enregistrer une ancienne copie ouverte par-dessus la version unifiée.
