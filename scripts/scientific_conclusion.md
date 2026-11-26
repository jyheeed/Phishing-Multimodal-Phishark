## Chapitre 8 — Démonstration, conclusion et perspectives

### 8.1. Ce que le système permet effectivement de tester

L'interface Streamlit utilise les checkpoints gelés et les définitions d'inférence vérifiées du notebook. Une URL seule déclenche U1 et ne provoque pas de visite du site. Une archive ZIP locale fournit les modalités réellement présentes, puis les fusions et, en option, les 22 variantes. L'utilisateur voit le score, le seuil et la décision ; les absences ne sont pas remplacées par des captures inventées.

Cette démonstration vérifie l'intégration du prétraitement et des modèles. Elle n'est pas un crawler de production ni une preuve de phishing actif. Pour une nouvelle page, obtenir HTML et screenshot demanderait un protocole de collecte autorisé distinct, avec protection de l'environnement et des données. Le prototype reste hors ligne sur les preuves qui lui sont soumises.

Les exemples historiques de l'interface appartiennent déjà au test : les réanalyser vérifie la parité d'inférence, pas une généralisation indépendante. Le mode PRESENTATION affiche des résultats sauvegardés et le précise. La distinction entre une prédiction recalculée sur un ZIP et une ligne d'exemple enregistrée est conservée dans le rapport et la soutenance.

### 8.2. Exemple d'entrée/sortie et limites du score

{{DEMO_TABLE}}

La démonstration enregistrée ci-dessus provient réellement du FULL ; seul l'identifiant public est anonymisé. Elle montre comment plusieurs branches peuvent produire des scores différents et comment les fusions appliquent leurs seuils. Elle ne prouve pas que l'exemple est représentatif ni que la capture correspond encore à l'état du site aujourd'hui. Le label est fourni comme vérité d'annotation historique, pas découvert par l'interface.

Un score près du seuil peut changer de décision lors d'une petite variation de représentation. Un score éloigné peut également être faux sur une population nouvelle. L'interface ne convertit pas ces nombres en certification de sûreté. Une politique d'abstention, de revue humaine ou de blocage doit être définie selon l'usage et évaluée indépendamment.

### 8.3. Réponses aux trois questions de recherche

RQ1 reçoit une réponse positive mais circonscrite : les fusions centrales dépassent les unimodaux sur le test commun de cette exécution. Les variantes montrent que l'image n'ajoute pas systématiquement un bénéfice, et que le choix du mécanisme de fusion importe. La différence d'AP M2/M1 est ponctuellement favorable à M2 mais son intervalle apparié contient zéro ; leurs compromis de décision restent différents.

RQ2 ne reçoit pas une démonstration de généralisation temporelle. La partition de calibration définie manque de bénins après purge. La conclusion est une limite documentée du protocole et de la composition du corpus, non un résultat de performance futur. Une nouvelle collecte et une évaluation scellée sont nécessaires pour répondre à la question de campagnes postérieures.

RQ3 est partiellement traitée : les chronométrages d'extraction et d'entraînement sont sauvegardés et le benchmark pandas/PyArrow comprend 24 mesures vérifiées. La comparaison Spark est bloquée avant JVM ; aucun gain distribué n'est démontré. Cette réponse distingue la qualité de la documentation du degré de réalisation expérimentale de chaque exigence.

### 8.4. Retour aux hypothèses et contribution du mémoire

H1 et H6 disposent d'indices internes directs, alors qu'H2 n'est pas une équivalence prouvée et que l'ajout systématique d'image n'est pas soutenu. H7 est illustrée par les politiques de seuil ; H9 est confirmée descriptivement par les agrégats de collecte, sans démontrer la part causale des artefacts dans l'AP. H10 et H12 restent non testables sous les conditions enregistrées. H14 rappelle la portée insuffisante d'un test interne pour garantir le transfert.

La contribution scientifique tient à l'articulation entre représentations, population et décision. Un système qui réduit fortement les fausses alertes peut manquer davantage de menaces ; un meilleur classement peut ne pas compenser un seuil mal transféré ; un contrôle exact de contenu peut coexister avec un biais de source. Les mettre en évidence est plus informatif qu'afficher un seul score élevé.

Le mémoire ne propose pas une preuve causale globale de « pourquoi tout est facile ». Les données montrent des facteurs de séparabilité et les résultats montrent leur compatibilité avec plusieurs explications. Quantifier leur responsabilité demanderait des contrôles de collecte, des ablations dédiées et des populations indépendantes. Les causes confirmées, associations et hypothèses ne sont pas mélangées dans une conclusion unique.

### 8.5. Perspectives hiérarchisées et décision d'ingénierie

La première priorité est la qualité de preuve : clarifier la sémantique des horodatages, diversifier les classes par source et période, compléter les revues de labels sans modification automatique et contrôler les quasi-doublons. La deuxième est l'évaluation : définir les objectifs opérationnels et le budget de sélection, prévoir plusieurs fenêtres et graines, puis conserver un lot indépendant. Ces étapes conditionnent la valeur des améliorations de modèle.

Ensuite seulement, un meilleur encodeur visuel, une représentation HTML structurée, une calibration probabiliste dédiée ou une fusion conjointe peuvent être étudiés. Leur coût et leur couverture doivent être comparés sur les mêmes observations, avec une règle de choix annoncée. Il n'est pas établi que ces architectures résoudront le biais de collecte ; une capacité plus élevée pourrait également mieux l'exploiter.

Le passage à l'échelle demande une infrastructure et des mesures adaptées. Des essais Spark contrôlés doivent distinguer la taille du tableau de la taille des preuves, le démarrage du moteur des opérations répétées et le local du distribué. La démonstration actuelle offre une base reproductible pour ces prolongements, tout en maintenant les limites du prototype.

### 8.6. Conclusion générale

PhiShark2026 permet d'étudier quatre types de preuves dans un protocole inspectable. Les résultats internes soutiennent l'intérêt de la fusion, mais montrent aussi que la multiplication des modalités et l'augmentation d'AP ne suffisent pas à définir un meilleur dispositif de sécurité. La comparaison M1/M2 établit un compromis concret entre fausses alertes et phishing manqués, tandis que les ablations mettent en évidence la contribution limitée du CNN image actuel.

La démarche a une valeur d'ingénierie parce qu'elle relie chaque décision aux données, au code, aux fichiers de résultats et à ses limites. La généralisation temporelle et le bénéfice distribué demeurent à démontrer, et le test courant reste exploratoire. Le projet constitue ainsi un prototype académique complet dans sa chaîne locale, accompagné d'un bilan expérimental partiel sur certaines exigences du sujet ; il ne doit pas être présenté comme un service opérationnel validé.
