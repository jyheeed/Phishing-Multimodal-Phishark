# PhiShark2026 — Détection multimodale du phishing

Mémoire scientifique et expérimental selon CRISP-DM

Version du 26 novembre 2026 — expérience FULL conservée : `77162f55317be0844ec3`.

**Périmètre de preuve.** Ce mémoire développe l'expérience effectivement exécutée dans le projet courant. Les résultats historiques sont préservés ; leurs métriques sont recalculées depuis les prédictions sauvegardées. Aucun entraînement, ajustement de seuil, relabel ou modification du notebook n'est effectué pour la rédaction. L'auteur, l'établissement, l'encadrement et le jury ne sont pas renseignés faute d'informations validées. Ils devront être ajoutés par l'étudiant avant dépôt institutionnel.

## Résumé

La détection du phishing à partir d'une seule URL ignore une partie des preuves disponibles, tandis que l'apparence d'une page ne suffit pas à établir son intention frauduleuse. Ce travail étudie la complémentarité de quatre modalités sur PhiShark2026 : URL, texte HTML, screenshot et caractéristiques techniques. La démarche CRISP-DM relie compréhension de la cible, analyse du corpus, préparation contrôlée, modélisation, évaluation et démonstration locale. L'unité étudiée est un scan associé à une réputation historique, distincte du contenu actuellement visible sur Internet.

Le corpus local contient 67 502 scans. Une observation est mise en quarantaine logique pour une incohérence d'intégrité, sans changement de label. La séparation par identités et contenus distingue entraînement des encodeurs, apprentissage des fusions, validation, calibration des seuils et test. Quatre réseaux compacts produisent des représentations unimodales. Une moyenne de scores disponibles constitue M1 ; un MLP sur embeddings gelés constitue M2. Onze sous-ensembles de modalités sont également évalués par deux méthodes, soit 28 configurations comparées sur les mêmes 13 212 scans complets.

L'AP interne atteint 0,972201 pour M1 et 0,978963 pour M2, contre 0,933933 pour le meilleur unimodal en AP. Ces gains de classement ne suffisent pas à choisir une politique de déploiement : M2 évite 666 faux positifs mais manque 616 phishing supplémentaires aux seuils respectifs déterminés hors test. L'intervalle apparié de différence d'AP entre M2 et M1 contient zéro. Le CNN image est faible dans cette exécution et son ajout ne procure pas un gain systématique.

Les associations entre sources, périodes et classes limitent la portée de ces résultats exploratoires. Le protocole chronologique défini reste non faisable, sa calibration ne contenant aucun bénin après purge. Vingt-quatre mesures pandas/PyArrow sont disponibles ; Spark reste bloqué par les ressources. La contribution consiste en une comparaison traçable et une interprétation des compromis, sans preuve de robustesse externe. Une nouvelle collecte équilibrée et un test indépendant sont nécessaires avant toute revendication opérationnelle.

Mots-clés : phishing ; multimodalité ; CNN ; fusion ; CRISP-DM ; average precision ; biais de collecte ; Parquet ; évaluation groupée.

## Abstract

Detecting phishing from a URL alone ignores potentially useful evidence, whereas visual similarity does not establish fraudulent intent. This study investigates URL, HTML text, screenshots and technical evidence in the local PhiShark2026 corpus. The CRISP-DM framework connects the target definition, exploratory analysis, controlled preparation, modeling, evaluation and an offline demonstration. Labels represent historical URL reputation rather than proof that every captured page displays an active attack.

The corpus contains 67,502 scans, including one integrity-related quarantined observation. Site and content identities are used to separate encoder training, fusion training, checkpoint validation, threshold calibration and testing. Four compact neural branches support a late score average, M1, and an intermediate MLP over frozen embeddings, M2. Eleven modality subsets and two fusion methods extend the study to 28 configurations evaluated on the same 13,212 complete test scans.

Internal average precision is 0.972201 for M1 and 0.978963 for M2, compared with 0.933933 for the strongest unimodal AP. At their frozen thresholds, M2 avoids 666 false positives but misses 616 additional phishing observations. Its paired AP difference against M1 has an interval crossing zero. The compact image branch performs weakly, and adding screenshots does not consistently improve ranking.

These findings remain exploratory. Strong source–label and period–label associations limit the interpretation of historical performance. The defined chronological protocol is not feasible because its post-purge calibration subset contains no benign observations. Twenty-four pandas/PyArrow measurements are available, while the recorded Spark experiment is resource-blocked. The contribution is a reproducible comparison and an explicit account of decision trade-offs, rather than a deployment guarantee. A balanced future collection and an untouched independent evaluation are required.

## Sommaire

{{TOC}}

## Sigles et conventions

| Terme | Définition et convention dans ce mémoire |
|---|---|
| AP | Average precision, calculée à partir des scores, distincte d'une intégration trapézoïdale arbitraire de la courbe PR. |
| PR / ROC | Précision–rappel / taux de vrais positifs en fonction du taux de faux positifs. |
| FP / FN | Bénin prédit phishing / phishing prédit bénin, selon le label historique du scan. |
| FPR / FNR | FP/(FP+TN) / FN/(FN+TP). Le dénominateur est propre à la classe concernée. |
| CNN / MLP | Réseau convolutif / réseau dense multicouche. |
| DOM | Arbre des éléments HTML ; il n'est pas encodé par GCN dans notre système. |
| TLS / DNS / WHOIS | Transport sécurisé / résolution des noms / enregistrement des domaines. |
| PSL | Public Suffix List, incluant les suffixes privés pour traiter certains locataires. |
| Calibration | Ici, partition de sélection des seuils ; ce terme ne signifie pas calibration probabiliste des scores. |
| Cohorte commune | Sous-ensemble test disposant des quatre modalités exploitables selon les règles du pipeline. |
| Groupe | Composante reliée par les identités effectivement vérifiées, pas une famille sémantique parfaite de campagnes. |
| Résultat interne | Mesure sur le test groupé courant ; aucune assimilation à une validation temporelle ou externe. |

## Liste des figures et tableaux

{{INDEX}}

## Chapitre 1 — Introduction générale

### 1.1. Problème de détection et décision de sécurité

Une page de phishing vise à obtenir une action trompeuse, par exemple la saisie d'identifiants, en se faisant passer pour un service attendu. Un filtre automatique doit décider à partir d'indices imparfaits. Une URL peut contenir une longue chaîne légitime de paramètres ; une page malveillante peut posséder un certificat TLS valide. Déduire le label d'un seul indice revient à confondre une corrélation du corpus et une règle de sécurité.

Le coût des erreurs donne son sens à l'évaluation. Un faux positif peut interrompre l'accès à un service autorisé et mobiliser un analyste. Un faux négatif laisse passer une observation annotée phishing. Une même accuracy peut résulter de compromis opposés entre ces coûts. Le mémoire examine donc le classement des scores et la décision à seuil fixé, en conservant séparément leurs interprétations.

Le cas réel M1_FP_01 illustre le problème : l'URL annotée bénigne compte 184 caractères, le statut est 200 et le screenshot est lisible selon le parseur ; M1 produit pourtant un score supérieur à son seuil. Ces métadonnées montrent une erreur de décision, sans démontrer que la longueur de l'URL en est la cause. Ce distinguo entre observation et explication causale gouverne toute l'analyse.

### 1.2. Pourquoi associer quatre modalités ?

Les modalités interrogent des aspects différents d'une capture. L'URL décrit une adresse et une organisation lexicale. Le texte HTML décrit un message extrait. Le screenshot représente une apparence à résolution donnée. Les JSON techniques décrivent des propriétés ou disponibilités de preuves. L'hypothèse multimodale est qu'une observation ambiguë dans un espace puisse être mieux classée lorsqu'un autre fournit une information complémentaire.

Cette hypothèse n'implique ni indépendance des modalités ni amélioration automatique. Une page d'erreur peut produire simultanément un HTML pauvre et une image uniforme. La disponibilité de plusieurs JSON peut dépendre du collecteur ou de l'hébergement. L'ajout d'un score faible dans une moyenne peut dégrader un bon score. La multimodalité crée donc une question expérimentale, pas un argument de performance suffisant.

Notre protocole confronte cette question à une cohorte commune, puis étudie les cas incomplets séparément. Cela permet d'attribuer un écart de métrique à une configuration sur les mêmes observations, tout en reconnaissant la sélection introduite par les cas complets. Les modèles ne seront pas comparés sur des populations silencieusement différentes.

### 1.3. Questions imposées par le sujet

Le document de l'enseignante, lu dans sa copie locale de deux pages, définit trois questions. RQ1 demande si la fusion surpasse chaque modalité isolée. RQ2 demande si cet avantage se maintient sur des campagnes postérieures à l'entraînement. RQ3 demande le coût de calcul selon le volume pour une approche distribuée. Les trois questions ne sont pas interchangeables : un gain interne répond partiellement à RQ1, sans répondre à RQ2 ou démontrer un bénéfice distribué.

La contribution marginale de chaque modalité sert à discuter RQ1. Elle ne remplace pas les obligations de généralisation et de coût. Le statut de chaque question est exposé même lorsqu'un protocole ne peut aboutir. Le résultat « non faisable » est une information sur les conditions de preuve ; il ne constitue ni un score de zéro ni une expérience réussie.

### 1.4. Contributions et limites annoncées

Le projet apporte une chaîne inspectable d'extraction, de regroupement, d'entraînement et d'évaluation ; une comparaison de quatre branches, deux fusions et 22 variantes ; une analyse appariée des contributions ; et une démonstration hors ligne utilisant des poids réels. La rédaction ajoute une lecture critique des résultats et leur rattachement aux hypothèses. Elle ne revendique pas une nouvelle architecture générale de fusion.

Les limites principales sont annoncées avant les résultats : composition de collecte fortement liée aux labels, test déjà examiné, absence de répétitions d'entraînement multi-graines, contrôles exacts ne couvrant pas tous les quasi-doublons et temporalité non démontrée. Ces limites servent à définir ce qu'un lecteur peut conclure. Elles ne sont pas compensées par le nombre de décimales d'une AP.

## Chapitre 2 — État de l'art et hypothèses

### 2.1. Représentations URL : motifs et contexte

Une représentation de caractères conserve la ponctuation, la longueur locale et les segments de l'adresse. Un CNN1D peut apprendre des motifs répétés sans que leur position absolue soit fixe. Une représentation de mots ou de sous-unités associe d'autres régularités, mais dépend d'une segmentation et d'un vocabulaire. Dans les deux cas, les symboles inconnus et la troncature modifient l'information observable.

Notre choix d'un CNN compact permet une branche spécialisée et un embedding fixe. Il reste sensible aux hôtes et chemins propres aux sources du corpus. Retirer le schéma HTTP/HTTPS élimine un raccourci lexical particulier, sans neutraliser l'hébergement, la profondeur des URL ou les locataires. L'état de l'art motive des contrôles de représentation ; il n'autorise pas à déclarer ces biais résolus par une seule normalisation.

### 2.2. Texte HTML et structure DOM

Le HTML offre à la fois des chaînes visibles et une organisation d'éléments. Les méthodes textuelles peuvent reconnaître des vocabulaires ou des séquences, tandis qu'un graphe DOM expose des relations structurelles. Ces choix impliquent des pertes différentes : supprimer les balises simplifie le texte mais abandonne leurs relations ; conserver un graphe exige un parseur et une architecture adaptés.

Yoon et al. [1] associent URL caractères, URL mots et DOM dans une fusion apprise. La revue critique détaille leur validation et leurs ablations, avec repères de section et de tableau. L'enseignement retenu ici est de comparer des représentations complémentaires. Notre U2 traite du texte extrait par HTMLParser : il ne conserve pas les arêtes DOM, n'emploie pas de GCN et n'exécute pas JavaScript. Ses résultats ne sont pas une réimplémentation du modèle de Yoon.

### 2.3. Capture visuelle, marque et intention

Un screenshot peut contenir des indices de mise en page, d'interface et d'identité. Cependant, un classement global d'image n'identifie pas nécessairement la marque ni l'action trompeuse. Réduire une image peut effacer un logo, un champ ou une mention de domaine. Inversement, une apparence de page de connexion existe aussi sur les sites légitimes.

Phishpedia [4] et PhishIntention [5] décrivent des tâches de marque et d'intention plus spécifiques que notre CNN global. La revue les situe à partir des notices officielles, sans prétendre reproduire leurs systèmes. Leurs enseignements servent à éviter une conclusion abusive : une faible AP d'U3 renseigne sur notre représentation et notre population, pas sur l'inutilité universelle de l'image.

### 2.4. Signaux techniques et disponibilité

Les propriétés DNS, TLS, d'enregistrement et de contenu de page peuvent contribuer à une classification. Mais elles sont aussi affectées par la méthode de capture, les permissions, l'expiration d'un service ou les plateformes partagées. L'absence d'une propriété n'est pas nécessairement une propriété négative du site. La distinction entre faux, zéro et inconnu doit être explicitée au niveau des données.

Notre allowlist ne contient pas de source de collecte ni de statut HTTP comme feature directe. Elle contient toutefois des mesures de présence et de compte, accompagnées de masques. Ces informations peuvent devenir des proxys. Les retirer toutes sans expérience supprimerait également une partie du signal. Le mémoire décrit donc précisément leur sémantique et borne les conclusions : leur contribution est mesurée ; leur part causale de biais ne l'est pas.

### 2.5. CrossPhire : apport et différence de protocole

La thèse d'Almakhamreh [2] et l'article de 2026 [3] étudient trois modalités sur plusieurs corpus avec des encodeurs textuels et visuels plus riches. Ils examinent le transfert entre datasets, ce qui constitue un changement réel de population. Ils sont distingués dans la bibliographie et la revue ; leurs configurations et résultats ne sont pas fusionnés en une performance unique.

Le transfert est un enseignement méthodologique pour RQ2, et non une justification de notre AP. Deux datasets peuvent partager des types de sources, des captures ou des périodes ; même un test externe doit donc être décrit. Notre résultat groupé n'est pas placé sur le même axe qu'une accuracy bibliographique. Le choix d'un encodeur plus puissant reste une perspective à évaluer avec le même soin porté aux populations.

### 2.6. Synthèse critique et hypothèses

{{LITERATURE_TABLE}}

Le cadre bibliographique distingue trois niveaux : ce que chaque publication mesure sur son corpus ; l'hypothèse que ce résultat suggère ; et ce que notre expérience permet réellement de constater. Par exemple, la complémentarité justifie H1, mais l'image ne doit pas être déclarée informative avant d'examiner U3 et les contrastes à méthode fixée. L'écart entre M1 et M2 justifie une question de décision différente de la question de classement.

Le registre H1–H15 figure en annexe et dans `scientific/02_HYPOTHESES_ET_PREUVES.md`. H1, H2, H4, H6, H7, H9, H10, H12 et H14 structurent la discussion. Les hypothèses d'équivalence et de causalité disposent d'exigences supplémentaires que les différences ponctuelles de métrique ne satisfont pas. La conclusion reprendra explicitement leurs statuts.

## Chapitre 3 — Compréhension du problème et des données

### 3.1. Définir correctement l'observation et le label

L'unité est un scan identifié par `scan_id`, relié au CSV et à une archive ZIP. Le label binaire est celui de la réputation annotée. Le contenu capturé peut être une page active, une erreur ou une ressource expirée. Il serait incorrect de déduire automatiquement un nouveau label du seul screenshot ou statut HTTP. Le mémoire ne modifie aucun label pour rapprocher les prédictions d'une attente.

Cette définition explique pourquoi certaines erreurs nécessitent une revue plutôt qu'une correction immédiate. Un phishing historiquement signalé peut ne plus afficher son formulaire lors de la capture. Un site bénin peut héberger une page qui ressemble à une connexion frauduleuse. L'annotation et le contenu ne sont pas des mesures identiques d'un même instant. La pertinence opérationnelle d'un classifieur dépend de la cible choisie et de la disponibilité des preuves au moment de la décision.

### 3.2. Composition et périmètres du corpus

{{EDA_CLASS_TABLE}}

Les bornes du tableau sont affichées au jour UTC ; les CSV conservent les horodatages complets.

L'effectif brut n'est pas l'effectif d'entraînement ni celui de la comparaison centrale. Une observation en désaccord avec le manifeste d'intégrité est mise en quarantaine logique : elle demeure dans le corpus brut et son label reste inchangé, mais elle ne participe pas à l'expérience principale. Les 67 501 admissibles sont ensuite répartis en cinq rôles. Le test complet contient 13 439 scans ; la comparaison des 28 utilise 13 212 cas complets, soit 98,31 % de ce test.

Cette cascade empêche une confusion fréquente : annoncer 67 502 observations comme si elles avaient toutes été utilisées pour tester chaque modèle. La population et le dénominateur accompagnent chaque figure. Les statistiques d'EDA décrivent le brut ; les tableaux de performance décrivent explicitement le test commun ou le test complet. Les observations exclues ne sont pas assimilées à des erreurs ou succès de classification.

### 3.3. Sources, dates et biais de composition

{{SOURCE_TABLE}}

Les noms de source observés sont entièrement associés à une classe dans cette copie : le V de Cramér recalculé vaut 1. Cette association descriptive ne signifie pas que le modèle lit directement la colonne source, qui est exclue de ses entrées. Elle signifie que des caractéristiques indirectes de la capture ou de l'hébergement peuvent également séparer les sources et donc les labels. Le retrait des colonnes évidentes ne suffit pas à éliminer cette possibilité.

{{PERIOD_TABLE}}

Les distributions temporelles sont également différentes. Les phishing commencent avant les bénins et certains mois ne contiennent qu'une classe. Une coupe chronologique peut donc changer simultanément période, prévalence et source. Ce constat fournit une explication de l'infaisabilité observée du protocole, mais ne démontre pas à lui seul la cause de chaque erreur future. Une collecte plus équilibrée doit être conçue avant le prochain entraînement.

![Figure 8 — Composition par source et mois UTC ; corpus brut, 67 502 scans. Une association ne mesure pas un effet causal sur les prédictions.](FIGURES_ET_RESULTATS/08_EDA_sources_periodes.png)

### 3.4. Disponibilité et qualité des captures

{{AVAILABILITY_TABLE}}

Une image décodable est disponible pour tous les scans de ce cache, ce qui n'implique pas une image informative. Les captures quasi uniformes sont comptées séparément. Le texte HTML exploitable manque pour une partie des observations, même si un fichier HTML ou une image existe. La disponibilité technique signifie qu'au moins une des mesures autorisées est finie ; elle ne garantit pas l'exhaustivité des JSON.

Le corpus brut contient 66 253 scans complets selon les règles de disponibilité. Ce nombre diffère de la cohorte test commune, qui applique aussi le rôle test et l'admissibilité. Le masque reflète cette définition opérationnelle. Une absence de contenu ne doit pas être remplacée par un exemple fictif ; lorsqu'aucune modalité demandée n'est disponible, les combinaisons s'abstiennent.

![Figure 9 — Disponibilité exploitable par classe dans le corpus brut ; les quatre modalités suivent la définition exacte du pipeline.](FIGURES_ET_RESULTATS/09_disponibilite_modalites.png)

### 3.5. HTTP, durée enregistrée et sens des valeurs

Le brut contient 4 629 statuts 404 chez les bénins et 990 chez les phishing. Un statut 404 est un résultat de capture, pas une classe. Sa fréquence dépend notamment de la composition des URL et de l'instant d'observation. Les valeurs de statut hors intervalle valide, dont zéro, sont traitées comme inconnues dans le pipeline ; elles ne constituent pas un nouveau code HTTP.

Les 67 502 durées calculées comme `scan_finished_at - scan_created_at` sont négatives dans le cache actuel. Cette anomalie systématique interdit d'interpréter ce champ comme un temps physique de capture. Les dates ne sont pas inversées pour obtenir des valeurs positives ; leur sémantique doit être clarifiée auprès du producteur. Les chronométrages d'extraction et d'entraînement rapportés plus loin proviennent d'autres mesures et ne reposent pas sur ces durées.

Ce résultat est une limite de métadonnées à documenter, pas une raison de supprimer silencieusement les observations. Les champs concernés restent hors des entrées des modèles. La généralisation chronologique utilise l'horodatage déclaré et doit être lue avec cette réserve sur la sémantique des dates.

### 3.6. Exemples locaux anonymisés et risques de validité

Les cas M1_FP_01 et M2_FN_16 sont issus des prédictions réellement enregistrées. Le premier est une observation bénigne avec HTTP 200 et trois features techniques manquantes ; le second est un phishing historique avec HTTP 404, image uniforme et huit features manquantes. Dans les deux cas, le résultat du modèle contredit le label. Aucun de ces éléments ne suffit à conclure que le label est faux ou à attribuer causalement l'erreur à une seule modalité.

Les exemples sont pseudonymisés ; le registre de correspondance reste dans les artefacts privés. Aucun domaine, lien actif, cookie ou texte de formulaire n'est publié. Les descriptions sont structurées à partir des métadonnées, pas présentées comme une inspection humaine des captures. Le chapitre 6 distingue ces cas illustratifs des taux calculés sur l'ensemble du test.

Les risques sont de quatre types : validité de construit entre réputation et capture ; validité interne face aux proxys et répétitions ; validité externe face aux périodes et sources nouvelles ; validité statistique face aux dépendances et comparaisons multiples. Le protocole réduit certains risques contrôlables, sans supprimer les autres par déclaration.

## Chapitre 4 — Préparation et pipeline Big Data

### 4.1. De l'index CSV aux preuves brutes

Le CSV sert à associer identité, label et fichier d'archive ; il n'est pas un ensemble de features librement utilisables. Les ZIP contiennent des JSON, du HTML et des screenshots. Le pipeline contrôle les membres, tailles et empreintes avant extraction. La lecture n'exécute ni HTML ni JavaScript et ne visite pas de site. Cette séparation évite de mêler les variations du Web actuel à une expérience sur captures figées.

Les erreurs de lecture, indisponibilités et désaccords d'intégrité deviennent des états explicites. L'observation incohérente est mise en quarantaine logique, tandis que les captures incomplètes peuvent rester utilisables par certaines branches. Cette distinction évite d'assimiler une modalité absente à une corruption globale de tous les indices. Les règles d'admissibilité et de disponibilité sont donc des objets différents.

### 4.2. URL et texte HTML : transformations cohérentes

L'URL est convertie en hôte, chemin et query, en minuscules, sans schéma ni fragment. Cette transformation est identique pour vocabulaire, audit d'entrée, entraînement et inférence. U1 observe au plus 256 caractères. Par exemple, une URL de 184 caractères dans le cas réel M1_FP_01 entre dans une séquence de longueur fixe, complétée par PAD si nécessaire. Le rapport ne publie pas l'adresse d'origine.

Le HTML est décodé en tolérant les caractères invalides ; HTMLParser accumule les données textuelles hors script, style et noscript. Les espaces et la casse sont normalisés avant tokenisation. U2 observe au plus 1 024 tokens et utilise un vocabulaire ajusté sur train_encoder. Il s'agit d'un texte extrait sans calcul de visibilité CSS : ce n'est ni un DOM conservé ni un rendu de navigateur. Une page dynamique dont le texte n'existe qu'après JavaScript reste une limite du procédé.

La cohérence des transformations protège contre une divergence entraînement–inférence, mais elle crée aussi des collisions : des observations différentes peuvent devenir la même séquence après normalisation ou encodage UNK. Le partitionnement vérifie donc les entrées réellement encodées, au-delà des seules URL brutes.

### 4.3. Image et mesures techniques

Les captures sont converties en RGB et redimensionnées en 96×96. Les valeurs utilisées par U3 sont ramenées dans l'intervalle 0–1 par division par 255. Il n'y a ni normalisation ImageNet déclarée ni poids visuels préentraînés. Cette transformation rend le calcul peu coûteux, tout en perdant potentiellement du texte fin et des petits logos. Cette perte est une propriété du système, pas une explication causale déjà isolée de son AP.

Les JSON sont lus suivant une allowlist de 21 mesures. Les opérations sont des comptes, présences, longueurs, booléens ou nombres non négatifs. Une date WHOIS présente n'est pas un âge de domaine : aucune soustraction d'années n'est inventée. La présence d'une chaîne et son absence ne sont pas nécessairement synonymes de succès et d'échec d'un protocole. Le dictionnaire exhaustif des champs est donné en annexe.

Les inconnus numériques restent des NaN. Pour U4, la médiane d'entraînement remplace les absences, puis les valeurs sont centrées et réduites avec les statistiques d'entraînement. Vingt et un indicateurs manquants sont concaténés aux 21 valeurs, soit 42 entrées. L'exemple d'une mesure absente illustre l'intérêt : une valeur imputée peut être identique à une mesure réelle médiane, mais le masque permet de les distinguer. Cette information peut être utile ou refléter la collecte ; son rôle doit être analysé avec prudence.

### 4.4. Stockage, provenance et reproductibilité

Le stockage Parquet/PyArrow conserve un schéma et permet de relire un sous-ensemble de colonnes. Les images transformées sont mises en cache séparément. Le calcul est versionné à partir du code, de la configuration et des empreintes d'entrée. Une modification du notebook ne réattribue pas les anciens poids à une nouvelle signature ; elle constitue une nouvelle expérience possible.

Le notebook actif contient tout le code scientifique et distingue PRESENTATION et FULL_EXPERIMENT. Le premier lit les résultats publiés sans charger les réseaux. Le second pourrait reconstruire la chaîne et produire de nouveaux artefacts ; il n'a pas été lancé pour ce mémoire. La provenance des poids existants est conservée comme source immuable séparée, sans second notebook actif. Les manifestes lient les fichiers aux résultats, mais n'affirment pas l'absence de biais scientifiques.

### 4.5. Identités, contenus et construction des groupes

Une séparation aléatoire de scans peut placer le même site, une URL normalisée ou un contenu identique de part et d'autre. Le pipeline relie les identités de site ou de locataire et les empreintes contrôlées en composantes. Les suffixes privés de la PSL contribuent à distinguer certains locataires de plateformes partagées. Une plateforme entière ne doit pas être confondue automatiquement avec une seule entité autonome.

Le contrôle des entrées encodées fusionne également des groupes lorsque l'encodage courant crée des collisions. La stabilisation est monotone : les composantes ne se divisent pas arbitrairement d'une itération à l'autre. Cette précaution évite qu'un même tenseur connu soit vu comme une entrée indépendante de test. Elle ne démontre pas l'absence de templates proches mais non identiques ou de campagnes partageant une marque.

{{SPLIT_AUDIT_TABLE}}

Les contrôles recalculés portent sur huit clés présentes et ne détectent aucun recouvrement entre rôles pour ces clés. La formulation est volontairement limitée aux identités observables. Nous ne transformons pas cette absence de recouvrement exact en certification d'indépendance sémantique.

### 4.6. Cinq rôles et ajustements train-only

{{PARTITION_TABLE}}

train_encoder ajuste vocabulaires, imputation, normalisation et poids des branches. train_fusion apprend la combinaison de représentations sur d'autres observations. validation choisit le meilleur checkpoint par AP. calibration fixe les seuils. test mesure les performances sans ajuster les poids ni les décisions. Les fractions cibles peuvent différer des effectifs exacts parce que les groupes sont indivisibles.

Cette séparation évite d'entraîner le méta-modèle sur des représentations de scans que les encodeurs viennent d'apprendre par cœur. Elle coûte une partie du volume disponible à chaque étape, mais clarifie les rôles. La normalisation des embeddings est ajustée sur train_fusion, pas sur la cohorte de test. Les encodeurs restent gelés pendant l'apprentissage des têtes supplémentaires.

La distinction validation/calibration est méthodologique : choisir un checkpoint et choisir une règle de décision ne sont pas la même opération. Elle ne supprime pas les dépendances induites par plusieurs modèles utilisant le même jeu de validation. La répétition des analyses du test rend ensuite les comparaisons exploratoires, même lorsque chaque étape informatique respecte son rôle initial.

## Chapitre 5 — Modélisation unimodale et multimodale

### 5.1. Contrat commun des branches

Les quatre branches associent une entrée spécialisée à un embedding de 32 valeurs et un logit. Pendant l'apprentissage, la perte utilise le logit directement ; pour les métriques, une sigmoid produit un score entre 0 et 1. Ce score n'est pas une probabilité de risque externe calibrée. Les masques de disponibilité sont déterminés avant la fusion et les identifiants restent alignés aux lignes de prédiction.

Un embedding est une représentation apprise qui n'attribue pas nécessairement un sens humain à chaque coordonnée. Son intérêt est d'exposer à la tête de fusion davantage d'information qu'une seule probabilité. Ce choix accroît aussi le nombre de paramètres et le risque d'apprentissage de corrélations propres au corpus. La comparaison M1/M2 mesure un système complet avec son protocole de seuil ; elle ne isole pas tous ces mécanismes séparément.

### 5.2. CNN1D URL et HTML

{{SEQUENCE_LAYERS}}

Les deux réseaux partagent une architecture, mais ni le vocabulaire ni la granularité de l'entrée. L'embedding de 24 valeurs transforme un identifiant discret en vecteur. Les convolutions 24→48 puis 48→32 utilisent des noyaux de 5 et 3, des strides de 2 et des activations ReLU. Le max-pooling adaptatif réduit la dimension de longueur et conserve un vecteur de 32 valeurs. La tête applique un dropout de 0,25 puis une projection vers un logit.

Pour U1, une longueur fixe de 256 impose un budget de lecture de l'adresse ; une partie finale peut être perdue pour les URL longues. Pour U2, 1 024 tokens représentent un compromis de calcul, sans garantie de contenir tous les indices d'une grande page. Les vocabulaires sont ajustés exclusivement sur l'entraînement des encodeurs. Le pooling facilite une sortie fixe mais perd une partie de l'ordre fin : l'architecture n'est pas un analyseur de structure HTML.

### 5.3. CNN screenshot

{{IMAGE_LAYERS}}

U3 emploie trois convolutions avec BatchNorm et ReLU : 3→24→48→64 canaux. Les trois strides de 2 ramènent une image 96×96 à des cartes 12×12 avant pooling adaptatif 2×2. Les 256 valeurs sont projetées en 64 puis 32 ; le dropout de cette projection vaut 0,2. Une tête linéaire produit le logit. Aucune préconnaissance de marque n'est fournie à ce réseau entraîné depuis zéro.

Cette architecture permet une baseline visuelle compacte mais ne peut être présentée comme un ResNet de l'état de l'art. L'analyse ultérieure examine son signal observé, la qualité des captures et ses contributions marginales. Pour attribuer causalement sa faiblesse à la résolution, il faudrait conserver les partitions et comparer des résolutions selon un budget contrôlé, sans consulter le test pour choisir la meilleure.

### 5.4. MLP technique et choix d'optimisation

U4 reçoit 42 valeurs : mesures standardisées et masques. Le MLP applique 42→64, ReLU, dropout 0,25, puis 64→32, ReLU, et 32→1. La structure dense convient à ce vecteur numérique, sans imposer une notion artificielle de voisinage spatial entre champs DNS et TLS. La présence de masques ne garantit pas la robustesse : une tête peut s'appuyer fortement sur la disponibilité si celle-ci corrèle au label.

Les modèles utilisent AdamW, un learning rate de 0,001, un weight decay de 0,0001 et une BCEWithLogits pondérée selon le rapport de classes du train propre à la branche. Le batch vaut 32 ; le budget maximal est de dix époques avec patience deux. Le meilleur checkpoint maximise l'AP de validation et est restauré avant export. Ces valeurs décrivent l'expérience exécutée, pas des hyperparamètres démontrés optimaux par recherche exhaustive.

{{TRAINING_TABLE}}

Les temps enregistrés ne sont pas comparables à une collecte de nouvelles pages ni à une latence utilisateur. Ils concernent l'apprentissage local sur les caches déjà extraits. Le temps de M2 ne comprend pas toute la préparation des embeddings. Une somme de durées partielles ne constituerait pas un coût complet de production.

### 5.5. M1 : moyenne des scores disponibles

Pour un scan i et des masques m(i,j), M1 calcule la somme des scores p(i,j) des branches disponibles, divisée par la somme de leurs masques. La règle conserve des poids égaux renormalisés. Elle n'apprend pas un modèle supplémentaire et ne doit pas être appelée stacking. Lorsque seule une modalité est disponible, sa moyenne est simplement son score ; lorsque rien n'est disponible, aucun score valide ne peut être produit.

La simplicité de M1 constitue une baseline importante. Elle permet de comparer l'ajout d'une modalité sans modifier un méta-modèle complexe. Mais des scores de branches de qualité ou d'échelle différentes ne sont pas nécessairement comparables comme probabilités calibrées. Une branche faible peut perturber la moyenne. Les sous-ensembles permettent d'examiner cet effet empiriquement.

### 5.6. M2 : fusion intermédiaire sur encodeurs gelés

Les quatre embeddings de 32 valeurs sont concaténés avec quatre masques : 4×32+4=132 entrées. Les embeddings manquants sont représentés par des zéros et le masque précise la disponibilité. Une normalisation ajustée sur train_fusion précède le MLP 132→64→32→1, avec les mêmes types d'activation et dropout que la tête dense. Les poids des encodeurs ne sont pas mis à jour pendant cet apprentissage.

Cette fusion peut apprendre des interactions qu'une moyenne ne représente pas. Elle reste dépendante de la qualité des embeddings et de la composition de train_fusion. Elle n'est ni une mixture of experts ni un entraînement conjoint de bout en bout. Les quatre masques donnent une information de disponibilité à la tête, sans garantir le comportement sur des motifs d'absence peu rencontrés.

### 5.7. Les 22 combinaisons et leurs dépendances

Les onze sous-ensembles comprennent six paires, quatre triplets et le quadruplet. Chaque ensemble est évalué par LATE et LINEAR_EMBED. Dans LINEAR_EMBED, un StandardScaler et une régression logistique sont ajustés sur train_fusion ; les paramètres déclarés sont C=1, max_iter=500 et class_weight=balanced. Cette tête est distincte de M2, qui est un MLP. Les deux ne doivent pas être confondus sous l'étiquette unique « fusion intermédiaire » sans précision.

Les encodeurs sont partagés entre les variantes. La ligne LATE à quatre modalités reprend fonctionnellement M1, avec de très petits écarts possibles d'arrondi numérique dans les scores. Les 28 lignes ne sont donc pas 28 preuves indépendantes. Ce partage limite le coût et rend les contrastes possibles, tout en imposant une analyse appariée et une prudence face aux comparaisons multiples.

{{COMBINATIONS_TABLE}}

### 5.8. Seuils, calibration et préservation du test

La politique primary choisit le seuil maximisant le F1 sur calibration ; en cas d'égalité à la tolérance numérique du code, le seuil le plus élevé est retenu. La politique recall85 choisit le seuil le plus élevé maintenant au moins 85 % de rappel sur calibration. Le code exige les deux classes et des scores finis. Le rôle calibration ne contient pas un apprentissage de Platt ou une régression isotone : les probabilités ne sont pas recalibrées par ces méthodes.

Les seuils sont figés avant l'inférence test. Les modifier après observation des erreurs rendrait le test participant à la sélection. Le présent mémoire compare seulement les politiques déjà enregistrées. Un rappel de calibration de 85 % n'est pas une promesse de rappel test, comme le montrent les résultats du chapitre suivant. Tout protocole futur doit définir son objectif opérationnel sur une validation historique distincte, puis conserver une évaluation scellée.

{{CHAPTER_RESULTS}}

{{CHAPTER_GENERALIZATION}}

{{CHAPTER_CONCLUSION}}

## Bibliographie

{{BIBLIOGRAPHY}}

## Annexes — Preuves, paramètres et résultats complets

### Annexe A. Dictionnaire des 21 caractéristiques techniques

La colonne opération définit la transformation réellement effectuée. Les champs de date sont des présences, les chaînes de titre et description sont mesurées en longueur, et aucun statut HTTP n'apparaît dans l'allowlist. À ces 21 valeurs s'ajoutent les 21 masques dans U4. Les inconnus demeurent distingués de zéro avant imputation.

{{FEATURE_TABLE}}

### Annexe B. Matrices des 28 configurations

Ces comptages concernent exclusivement les 13 212 scans communs aux seuils primary propres à chaque configuration. Ils ne doivent pas être combinés à une prévalence du test complet ou du corpus brut. Toutes les lignes ont été recalculées depuis les scores sauvegardés.

Les métriques complètes ci-dessous explicitent également précision, rappel, F1, FPR et FNR pour les 28 configurations. L'annexe fournit six décimales pour la vérification ; les conclusions ne dépendent pas d'une prétendue précision scientifique à la sixième décimale.

{{METRICS_ALL}}

{{CONFUSION_ALL}}

### Annexe C. Cas d'erreur réels pseudonymisés

Les vingt lignes correspondent aux cinq premiers identifiants triés pour chaque couple M1/M2 et FP/FN. Il s'agit d'un échantillon déterministe illustratif, pas d'une sélection aléatoire représentative. Deux lignes peuvent concerner la même observation sous des modèles différents. Le mapping privé ne figure pas dans les livrables publics. Aucune cause de l'erreur ni correction de label n'est déduite de ces seuls attributs.

{{ERROR_CASES}}

### Annexe D. Hypothèses et force des conclusions

{{HYPOTHESES_TABLE}}

### Annexe E. Reproductibilité et sources des tableaux

{{PROVENANCE}}

### Annexe F. Réponse synthétique au sujet de l'enseignante

| Question | Réponse fondée sur l'expérience | Ce qui reste nécessaire |
|---|---|---|
| RQ1 — bénéfice multimodal | Gains internes de M1/M2 face aux unimodaux sur cohorte commune, avec compromis FP/FN et intervalles appariés ; ajout d'image non systématiquement bénéfique. | Répétitions de graines et nouveau test indépendant pour confirmer le résultat hors analyses exploratoires. |
| RQ2 — campagnes ultérieures | Non démontrée : calibration chronologique définie sans bénins après purge. | Collecte des deux classes par période et source, protocole préenregistré, nouveau lot scellé. |
| RQ3 — coût distribué | Coûts partiels d'extraction/entraînement et 24 mesures pandas/PyArrow documentés ; comparaison Spark bloquée. | Ressources adaptées, opérations et vérifications équivalentes, répétitions JVM froide/chaude, éventuellement vrai cluster. |

Le résultat final n'est pas une garantie de protection en production. C'est une expérience reproductible dont les gains, conditions et limites sont explicités pour permettre une décision d'ingénierie informée.
