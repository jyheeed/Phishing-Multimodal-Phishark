# Tester PhiShark2026 avec l'interface locale

L'interface utilise les poids et seuils du FULL déjà exécuté. Aucun entraînement, aucune modification des labels et aucune visite des URL saisies. Elle reste accessible uniquement depuis la machine locale.

## Ouvrir ou lancer

Adresse : **http://127.0.0.1:8502**. Si le serveur est déjà lancé, ouvrir directement ce lien.

Pour un lancement manuel dans le terminal PowerShell de VS Code, depuis la racine du dépôt :

```powershell
& 'C:\Users\pc\anaconda3\envs\my_env\python.exe' -m streamlit run app.py --server.address 127.0.0.1 --server.port 8502 --server.headless true --browser.gatherUsageStats false
```

Le lanceur LANCER_INTERFACE.ps1 contient la même commande. Garder le terminal ouvert pendant les tests. Arrêter un serveur lancé manuellement par Ctrl+C. Ne pas lancer deux serveurs sur le même port. Aucun changement du notebook ni du mode FULL n'est nécessaire.

## 1. URL seule

Saisir une URL HTTP/HTTPS et cliquer sur Analyser l'URL. Seul U1 est utilisé : le CNN analyse hôte, chemin et query, sans schéma ni fragment. Il n'invente pas un HTML, un screenshot ou des JSON techniques. Le résultat n'est donc pas un test de la fusion multimodale.

Le score est affiché avec son seuil gelé, et une décision Bénin/Phishing. Il s'agit d'un indice du modèle, pas d'une probabilité de danger certifiée. Même une URL connue peut produire une erreur ; cela ne doit pas conduire à modifier le seuil après consultation.

## 2. Capture multimodale

Charger une archive ZIP PhiShark de moins de 32 Mio. Structure attendue :

```text
metadata.json                 # cible dans le champ target
data/*.json                   # preuves techniques réellement disponibles
artifacts/page.html.gz        # texte HTML capturé, si présent
artifacts/screenshot.png      # capture d'écran, si présente
```

Le champ URL facultatif sert seulement si la capture ne contient pas déjà de cible. Une URL contradictoire n'est pas substituée silencieusement. Les membres ZIP, tailles et empreintes déclarées sont contrôlés. Les fichiers ne sont pas extraits librement sur le disque et le HTML n'est jamais exécuté.

Cliquer sur Analyser la capture. Les branches disponibles, M1 et M2 sont évaluées. Cocher Calculer aussi les 22 combinaisons pour comparer les paires, triplets et quadruplet LATE/LINEAR_EMBED. Les modalités manquantes restent absentes ; si aucune preuve n'est exploitable, aucun score n'est produit. Une combinaison sans modalité demandée présente s'abstient.

Les premières inférences peuvent être plus lentes : les bibliothèques et poids sont chargés à la demande, puis gardés en cache. Il n'y a aucun appel d'entraînement.

## 3. Exemples et résultats

Pour une démonstration immédiate, choisir un exemple déjà disponible parmi trois scans bénins et trois phishing du test historique. Cliquer sur Analyser cet exemple pour réellement recalculer ses scores avec les modèles, et éventuellement les 22 combinaisons.

La classe affichée dans le sélecteur provient de l'annotation connue de cet exemple. Un désaccord du modèle constitue une erreur de prédiction, pas automatiquement une erreur du label. Ces exemples font déjà partie du test du projet : les réanalyser ne crée pas une nouvelle validation indépendante.

La table des résultats présente les 28 configurations sur leur cohorte commune de 13 212 scans. Elle ne réentraîne ni ne reconstitue le benchmark à chaque ouverture de page.

## Vérifications exécutées

- Huit tests automatisés réussis.
- Un vrai ZIP du test réanalysé : scores des six modèles et 22 combinaisons concordants avec les prédictions enregistrées, tolérance absolue 1e-5.
- U1 seul pour une URL ; invariance HTTP/HTTPS et absence de téléchargement.
- Gestion des modalités manquantes, capture vide, archive invalide et cible contradictoire.
- Démarrage de l'interface et soumission URL vérifiés avec AppTest.
- Checkpoints, labels, seuils et résultats historiques inchangés.

Preuves : artifacts/interface/tests.xml et status.json. Le manifeste d'inférence atteste que les définitions reprises du notebook unique correspondent à celles du FULL réellement exécuté. Les anciens modules CNN64 ne sont pas utilisés pour charger le CNN96. Aucun autre notebook n'est exécuté par l'interface.

## Limites à expliquer au jury

Tester quelques entrées démontre que le logiciel calcule une décision ; cela ne mesure pas son accuracy sur de nouveaux sites. Il faut un ensemble indépendant et annoté pour mesurer la généralisation. RQ2 reste non démontrée ; les biais de collecte et les faux positifs/faux négatifs restent documentés. Une capture peut représenter une page inactive ou une404 alors que le label décrit la réputation de l'URL.

Cette interface est un prototype local de recherche. Elle ne fournit pas un verdict de sécurité garanti et ne remplace pas l'analyse des preuves. Après une modification des modèles ou du code d'inférence, redémarrer l'interface et revérifier leur compatibilité.
