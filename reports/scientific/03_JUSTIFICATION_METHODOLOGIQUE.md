# Justification méthodologique et réponses aux objections

## 1. Pourquoi CRISP-DM ?

L'objectif est de produire une décision à partir de preuves hétérogènes, pas seulement d'entraîner un réseau. CRISP-DM rend visibles les dépendances : la cible définit le coût des erreurs ; l'EDA révèle la disponibilité et les biais ; la préparation matérialise les règles ; la modélisation teste des conceptions ; l'évaluation délimite leur validité ; le prototype restitue le résultat. Une mauvaise calibration temporelle renvoie à la collecte et au partitionnement. Ce retour n'est pas un échec à masquer par un autre chiffre.

**Objection du jury :** les six phases seraient seulement des titres. **Réponse :** chaque phase possède des produits vérifiables, du contrat de label au manifeste de partitions, puis aux prédictions et à l'interface. Le rapport relie explicitement ces produits aux questions RQ1–RQ3.

## 2. Pourquoi ce corpus et quatre modalités ?

Le corpus conserve les preuves brutes nécessaires à des représentations différentes du même scan. Cela permet de comparer les indices lexicaux, textuels, visuels et techniques sans juxtaposer des datasets distincts. La complémentarité est une hypothèse testée ; la simple présence de quatre modalités n'est pas un argument de supériorité. Une capture uniforme ou expirée peut être peu informative, et une métadonnée disponible seulement pour une classe peut devenir un raccourci.

**Limite :** les labels expriment une réputation annotée, pas nécessairement une fraude visible dans chaque capture. Les sources et périodes peuvent être associées à la classe. Le retrait des colonnes de source n'élimine pas leurs traces indirectes dans les preuves.

## 3. Pourquoi des CNN compacts et un MLP ?

Les CNN1D partagent des filtres locaux et produisent des embeddings de taille fixe, malgré des séquences d'entrée de longueurs différentes. Le CNN2D fournit une baseline visuelle réalisable sur CPU. Le MLP traite un vecteur déjà numérique. Cette spécialisation simplifie les ablations et la gestion des modalités manquantes. Les choix 256 caractères, 1 024 tokens et 96×96 pixels sont les configurations effectivement exécutées ; ils ne sont pas déclarés optimaux par recherche exhaustive.

**Limite :** petites images, troncature, pooling et absence de préentraînement peuvent perdre des indices. Leur contribution exacte à la performance n'a pas été isolée. Un Transformer ou ResNet serait une expérience future contrôlée, pas une architecture implicitement présente.

## 4. Pourquoi deux fusions et 22 combinaisons ?

M1 teste une règle simple de moyenne des scores disponibles. M2 teste une interaction apprise sur quatre embeddings gelés : 128 dimensions et quatre masques. Les 11 sous-ensembles à deux, trois ou quatre modalités sont évalués par LATE et LINEAR_EMBED. Cette seconde tête est logistique, différente du MLP M2. La règle LATE complète duplique fonctionnellement M1 : 28 lignes ne sont donc ni 28 réseaux indépendants ni 28 découvertes distinctes.

Le gel des encodeurs limite le coût et évite de modifier les branches à chaque comparaison. Il réduit aussi la capacité d'adaptation conjointe : nous ne revendiquons pas un entraînement de bout en bout.

## 5. Pourquoi cinq partitions ?

train_encoder ajuste les branches et prétraitements ; train_fusion ajuste les têtes sur des représentations d'observations disjointes ; validation choisit les checkpoints ; calibration fixe les seuils ; test décrit le résultat hors ajustement direct. Les groupes restent indivisibles pour les clés contrôlées. Apprendre la fusion sur les scores d'entraînement des encodeurs favoriserait des scores excessivement confiants.

**Nuance :** la validation est réutilisée par plusieurs choix de checkpoints ; les modèles partagent aussi des observations et des encodeurs. Leur dépendance et la consultation répétée du test imposent une interprétation exploratoire. Une disjonction technique ne certifie pas l'indépendance sémantique de toutes les campagnes.

## 6. Pourquoi AP, FPR et rappel ensemble ?

AP apprécie le classement de scores sur plusieurs seuils. FPR et rappel décrivent un point de décision. La précision dépend de la prévalence et du nombre de fausses alertes. Deux systèmes peuvent s'ordonner différemment selon ces critères. M2 classe mieux en AP que M1 mais manque davantage de phishing à son seuil primary ; cela ne constitue pas une contradiction mathématique.

Le F1 privilégie un compromis implicite qui ne représente pas tous les coûts de déploiement. Une politique rappel85 est fixée sur calibration et comparée comme diagnostic ; elle n'est pas réajustée sur le test. Sans calibration probabiliste dédiée, un score sigmoid n'est pas présenté comme une probabilité de risque certifiée.

## 7. Pourquoi une cohorte commune et un bootstrap groupé ?

Comparer des sous-populations distinctes confondrait le modèle et la facilité des observations. La cohorte complète de 13 212 scans permet une comparaison appariée, puis le tableau des observations disponibles décrit la couverture réelle. La restriction aux cas complets introduit elle-même une sélection : les cas indisponibles ne disparaissent pas de la discussion.

Les sites ou familles exactes ne sont pas des scans indépendants. Le bootstrap rééchantillonne les groupes avec remise, ensemble pour les modèles comparés. Il estime une incertitude conditionnelle au corpus et aux poids. Il ne prouve ni robustesse future, ni équivalence, ni significativité après 65 comparaisons non corrigées.

## 8. Pourquoi pandas/PyArrow et Spark ?

Le stockage typé facilite les vérifications et répétitions. Le benchmark doit conserver données, opérations et validation de sortie identiques. Une lecture/écriture Parquet locale ne mesure pas la collecte réseau, le décodage des images ou l'entraînement distribué. Les 24 mesures pandas sont exploitables pour leur périmètre ; le contrôle Spark a empêché le démarrage de la JVM. RQ3 reste partielle et la comparaison distribuée bloquée.

## 9. Pourquoi ne pas réentraîner pour le rapport ?

Le besoin est de comprendre une expérience exécutée et vérifiée. Recalculer des métriques est léger et pertinent ; refaire des réseaux ne corrigerait pas l'absence de bénins dans une partition temporelle ni un biais de source. Les données, checkpoints, seuils et notebook sont protégés par empreintes. Les anciennes analyses restent des archives, et les faits du mémoire sont rattachés uniquement au run courant.
