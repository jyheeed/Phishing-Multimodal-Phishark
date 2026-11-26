"""Detailed defense rationale; update only report files, never a running notebook."""
import ast
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
MARKER='\n\n## Annexe pédagogique — expliquer chaque étape et sa justification\n'


def execution_snapshot():
    document=json.loads((ROOT/'notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb').read_text(encoding='utf-8'))
    code=[c for c in document['cells'] if c['cell_type']=='code']
    mode='UNKNOWN'
    for node in ast.parse(''.join(code[0]['source'])).body:
        if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='MODE' for t in node.targets):
            mode=ast.literal_eval(node.value)
    errors=[dict(cell=i+1,name=o.get('ename'),message=o.get('evalue')) for i,c in enumerate(document['cells'])
            for o in c.get('outputs',[]) if o.get('output_type')=='error']
    executed=sum(c.get('execution_count') is not None for c in code)
    text=''.join(''.join(o.get('text',[])) for o in code[-1].get('outputs',[]) if o.get('output_type')=='stream')
    complete=executed==len(code) and not errors and 'PRESENTATION_VALIDATION_OK' in text and code[-1].get('execution_count') is not None
    return dict(mode=mode,code_cells=len(code),executed_cells=executed,errors=errors,
                saved_presentation_execution_complete=complete,notebook_modified=False,new_training_performed=False)


def enrich():
    path=ROOT/'reports/PHISHARK2026_RAPPORT_FINAL.md'
    original=path.read_text(encoding='utf-8').split(MARKER)[0].rstrip()
    snapshot=execution_snapshot()
    status=('L’exécution PRESENTATION enregistrée est complète, sans erreur enregistrée.' if snapshot['saved_presentation_execution_complete']
            else 'La fin du relancement en cours ne peut pas encore être confirmée à partir du fichier enregistré. Une sortie ancienne ne suffit pas si son compteur d’exécution actuel est vide.')
    steps=[
      ('0. Choisir le mode et vérifier la provenance',
       'Distinguer la consultation des preuves d’une nouvelle expérience de calcul.',
       'Sans cette distinction, des sorties conservées peuvent être prises à tort pour de nouveaux entraînements. Une modification de code ne rend pas automatiquement les anciens checkpoints compatibles avec une nouvelle version.',
       'La première cellule définit PRESENTATION ou FULL_EXPERIMENT, le chemin du fichier réellement ouvert et sa signature. La garde refuse un code exécuté qui diffère du fichier enregistré. En présentation, les cellules FULL sont visibles mais ignorées ; les résultats affichent leur code producteur d’origine.',
       'Vérifier le mode, le chemin et les empreintes des artefacts. Enregistrer puis redémarrer après toute modification de code. Une exécution de présentation ne démontre pas de nouvelles performances.',
       '« Je montre des résultats FULL déjà exécutés et vérifiés. Le mode présentation permet de les consulter sans réentraîner et sans leur attribuer une nouvelle provenance. »'),
      ('1. Définir précisément la cible',
       'Classer la réputation annotée de l’URL, avec phishing comme classe positive1 et bénin comme classe0.',
       'Le contenu d’une capture peut avoir changé depuis le signalement. Un modèle qui prédit la réputation n’est pas automatiquement un détecteur de collecte active d’identifiants au moment de la démonstration.',
       'Les labels du CSV sont conservés. Les états HTTP, les preuves manquantes et les anomalies de capture sont décrits séparément. La décision du modèle est comparée au label, puis les cas litigieux sont proposés à la revue humaine.',
       'Ne pas changer une étiquette parce que la capture est une404. Distinguer erreur de prédiction, erreur d’acquisition et éventuelle erreur d’annotation.',
       '« La vérité terrain décrit ici la réputation de l’URL ; une capture indisponible ne prouve pas que cette réputation est bénigne. »'),
      ('2. Inventorier le corpus avant le calcul',
       'Confirmer les observations, classes, archives disponibles et périodes réellement présentes.',
       'Un pipeline peut fonctionner tout en ayant ignoré des fichiers ou en utilisant une sous-population involontaire. L’inventaire empêche de présenter un échantillon comme une expérience complète.',
       'Le CSV original contient67502identifiants uniques,34115bénins et33387phishing. Les noms d’archives sont rapprochés des fichiers présents. Les dates sont lues en UTC avec prise en charge des formats ISO mixtes.',
       'Comparer effectifs du CSV, identifiants uniques, archives présentes et compte rendu d’extraction. Conserver une trace des absences plutôt que les effacer silencieusement.',
       '« Avant de comparer les réseaux, je vérifie que le corpus annoncé correspond aux preuves réellement disponibles. »'),
      ('3. Contrôler les archives et la qualité des captures',
       'Empêcher qu’une incohérence technique soit confondue avec une observation valide.',
       'Une archive illisible, une cible différente ou une empreinte divergente peuvent casser l’alignement entre l’entrée et son label. À l’inverse, une modalité simplement absente ne justifie pas nécessairement de supprimer le scan.',
       'Les membres ZIP et tailles sont contrôlés, les JSON et captures sont lus avec des bornes, les empreintes sont vérifiées et les identifiants/cibles rapprochés du CSV. Une archive divergente du manifeste reste en quarantaine ;67501observations sont admissibles avant partition.',
       'Conserver les motifs de quarantaine et les effectifs par classe/source. La catégorie review signale une revue nécessaire ; elle n’est pas automatiquement une erreur de label.',
       '« Je sépare une preuve absente, un cas à revoir et une incohérence critique, afin de ne pas fabriquer des données propres artificiellement. »'),
      ('4. Construire les21features techniques et les masques',
       'Transformer les preuves JSON en entrées numériques définies et reproductibles.',
       'Zéro peut signifier une valeur observée nulle, alors que NaN signifie une information inconnue. Les confondre créerait un signal artificiel. Une allowlist réduit le risque d’injecter directement la source ou la classe dans le modèle.',
       'Les21variables décrivent la présence ou la quantité de preuves DNS, WHOIS, IP, ports, TLS, page, redirections et conformité. U4reçoit les21mesures et21indicateurs de valeurs manquantes. Les champs de dates WHOIS sont ici de simples indicateurs de présence, sans calcul d’âge.',
       'Contrôler l’ordre exact des colonnes et leurs définitions. Source, label, scan_id, dates de collecte, hébergeur et statut HTTP ne sont pas des entrées techniques autorisées. Des proxies indirects peuvent néanmoins rester.',
       '« Le masque indique au réseau qu’une information manque ; il ne transforme pas une absence de preuve en preuve négative. »'),
      ('5. Transformer les URL et limiter un raccourci identifié',
       'Créer une séquence de caractères cohérente pour U1.',
       'Si HTTP/HTTPS est très associé à la collecte des classes, le réseau pourrait l’exploiter sans apprendre des motifs d’URL robustes. Retirer le schéma isole ce raccourci particulier, sans prétendre résoudre tous les biais.',
       'L’entrée conserve hôte, chemin et query, sans schéma ni fragment. La transformation est identique pour les vocabulaires, les empreintes, l’entraînement et l’inférence. La longueur FULL est256caractères.',
       'Le diagnostic de perturbation HTTP/HTTPS doit produire des entrées identiques et une variation de score nulle. Cette invariance est attendue par construction ; elle ne prouve pas une indépendance à l’hébergeur.',
       '« Je retire un indice de collecte précis, puis je vérifie que toutes les étapes du pipeline utilisent bien la même transformation. »'),
      ('6. Préparer le HTML et les screenshots',
       'Fournir aux réseaux des représentations bornées et alignées du contenu capturé.',
       'Exécuter la page n’est pas nécessaire pour analyser des archives. Des séquences et images de taille fixe rendent les lots calculables, avec une perte d’information qu’il faut assumer.',
       'U2utilise le texte visible du HTML, sans contenu de script/style/noscript, puis au plus1024tokens. U3reçoit une image RGB96×96. Les troncatures, images uniformes, captures absentes ou illisibles sont documentées.',
       'Vérifier les états de capture, dimensions et identifiants. Ne pas attribuer causalement une faible AP à la résolution ou aux pages uniformes sans expérience dédiée.',
       '« Je standardise les entrées pour entraîner des réseaux compacts, mais je conserve les indicateurs de ce qui a été perdu ou indisponible. »'),
      ('7. Stocker les représentations avec Parquet',
       'Découpler le décodage coûteux des archives des étapes répétées d’apprentissage et d’analyse.',
       'Relire et décoder toutes les preuves à chaque étape gaspillerait le temps de calcul. Un cache non signé pourrait toutefois réintroduire des entrées obsolètes ou incompatibles.',
       'Le pipeline conserve une table canonique Parquet et des caches d’images, avec empreintes, configuration et provenance. Le cache n’est réutilisé que lorsque les contrôles correspondent. L’extraction FULL exécutée a duré environ128,49minutes.',
       'Distinguer le coût d’extraction des ZIP de la lecture d’une table dérivée compressée. Les quelques mégaoctets de Parquet du benchmark ne représentent pas le volume brut des archives.',
       '« Le cache économise du calcul, mais sa compatibilité doit être prouvée : je ne réutilise pas une image64×64 comme si elle était96×96. »'),
      ('8. Construire les groupes avant les partitions',
       'Éviter qu’un site, un locataire ou une entrée identique soit partagé entre apprentissage et évaluation.',
       'Une séparation aléatoire des lignes peut laisser des versions presque identiques d’un même site des deux côtés. Le score mesure alors en partie la reconnaissance d’éléments déjà vus.',
       'Des composantes relient les identités de sites et locataires, URL normalisées, contenus et encodages exacts. Quand un encodage traverse des rôles, tous ses membres concernés sont réunis. Le raffinement doit fusionner effectivement des groupes et ne s’arrête pas arbitrairement à huit passages.',
       'Contrôler l’absence de chevauchement sur toutes les clés prévues. Ne pas assimiler les séquences PAD réellement vides à une identité de contenu. Les contrôles exacts ne démontrent pas l’absence de tous les quasi-doublons.',
       '« Je sépare des entités et des contenus contrôlés, pas seulement des numéros de lignes. »'),
      ('9. Donner un rôle distinct à cinq partitions',
       'Réserver des données différentes à chaque décision d’apprentissage et d’évaluation.',
       'Entraîner la fusion sur les mêmes observations que les encodeurs peut lui donner des représentations trop favorables. Choisir les seuils sur le test rendrait ensuite la performance optimiste.',
       'train_encoder ajuste les quatre branches ; train_fusion ajuste les têtes ; validation choisit les checkpoints ; calibration fixe les seuils ; test mesure les résultats. Les fractions cibles sont50/15/10/5/20%, ajustées par les groupes indivisibles.',
       'Lire les effectifs réels par classe, vérifier les intersections d’identifiants et conserver les manifests. Les proportions cibles ne sont pas une garantie d’effectifs exactement proportionnels.',
       '« Chaque partition répond à une décision précise : apprendre les preuves, apprendre leur combinaison, sélectionner, fixer le seuil puis évaluer. »'),
      ('10. Ajuster les vocabulaires et normalisations sur le train',
       'Transformer les entrées sans apprendre indirectement la distribution du test.',
       'Un vocabulaire ou une médiane calculés sur toutes les données introduiraient des informations de validation ou de test dans la préparation du modèle.',
       'Les vocabulaires URL/HTML, médianes, moyennes et écarts-types sont ajustés sur train_encoder. Les mots inconnus deviennent UNK et les séquences sont complétées par PAD. Le scaler de fusion est ajusté sur train_fusion, avec traitement explicite des masques.',
       'Vérifier la liste fitted_ids et les rôles. Une transformation ajustée n’est pas recalculée sur les observations futures. Les nouvelles collisions d’encodage sont contrôlées après ajustement.',
       '« Le test peut contenir des mots inconnus : c’est une situation à évaluer, pas une raison pour apprendre son vocabulaire à l’avance. »'),
      ('11. Entraîner les quatre modèles unimodaux',
       'Mesurer ce que chaque modalité peut apporter seule avant de discuter une fusion.',
       'Sans baselines unimodales, une bonne fusion pourrait simplement reproduire une seule modalité forte. Les architectures sont adaptées à la structure des entrées, pas sélectionnées pour obtenir un score souhaité.',
       'CNN1Dpour motifs locaux d’URL et tokens HTML, CNN2Dpour l’image et MLPpour les variables tabulaires. Chaque branche produit32valeurs. AdamW, BCEWithLogits pondérée selon son train, batch32, au plus10époques et patience2sont conservés.',
       'Lire les courbes de loss et d’AP validation, restaurer le meilleur checkpoint de validation et vérifier signatures et alignement. Une loss qui baisse n’est pas une garantie d’amélioration sur test.',
       '« Les unimodaux sont les témoins de l’expérience : ils permettent d’identifier les modalités fortes et faibles avant la fusion. »'),
      ('12. Geler les encodeurs et apprendre M1/M2',
       'Combiner des décisions ou des représentations sans confondre ces deux stratégies.',
       'La moyenne des probabilités est simple et transparente. Une tête apprise peut exploiter des interactions entre représentations, mais demande des données indépendantes pour son ajustement.',
       'M1moyenne les probabilités disponibles, sans poids appris. M2reçoit128valeurs d’embeddings et4masques, soit132entrées, et apprend un MLP sur train_fusion. Les encodeurs restent gelés ; ce n’est pas un entraînement profond conjoint.',
       'Vérifier les identifiants et dimensions avant concaténation. Contrôler que le train de fusion est disjoint du train des encodeurs. Ne pas comparer une fusion dont les scans sont désalignés.',
       '« M1combine ce que les réseaux décident ; M2apprend à combiner ce qu’ils représentent. »'),
      ('13. Évaluer les11sous-ensembles par deux méthodes',
       'Identifier les contributions et redondances entre modalités.',
       'Ajouter une modalité peut améliorer, ne rien changer ou dégrader un classement. Tester les paires, triplets et quadruplet permet de distinguer complémentarité réelle et intuition.',
       'Les six paires, quatre triplets et quadruplet utilisent LATE ou LINEAR_EMBED, soit22configurations supplémentaires. Les têtes linéaires utilisent StandardScaler et régression logistique sur train_fusion. Aucun nouveau CNN n’est entraîné pour chacune.',
       'La liste est fixée dans le code. Les politiques sont gelées avant les scores de test. Si aucune modalité demandée n’est présente, le système s’abstient et la couverture baisse ; cette baisse doit être rapportée.',
       '« Je teste aussi si deux ou trois modalités suffisent ; quatre n’est pas automatiquement mieux que trois. »'),
      ('14. Fixer les seuils sur calibration',
       'Convertir les scores en décisions selon une règle explicite et indépendante du test.',
       'AP ne choisit pas le seuil opérationnel. Employer0,5sans justification ou régler le seuil après lecture des erreurs de test pourrait donner une conclusion trompeuse.',
       'primary maximise le F1sur calibration, avec seuil le plus élevé en cas d’égalité. recall85est le plus haut seuil conservant au moins85%de rappel de calibration. Les56politiques des28configurations ont été recalculées et vérifiées, sans changement.',
       'Le rappel de test peut être inférieur à85%au point recall85. Les scores sigmoid ne sont pas garantis comme probabilités calibrées. Ne pas réoptimiser sur les FP/FN du test.',
       '« La calibration fixe les décisions avant le test ; le test révèle si ce compromis se transfère réellement. »'),
      ('15. Comparer les mêmes scans et plusieurs métriques',
       'Éviter qu’une différence de population soit interprétée comme une différence de modèle.',
       'Une modalité peut manquer sur les cas les plus difficiles. Comparer deux AP sans contrôler les identifiants peut favoriser une configuration qui s’abstient davantage.',
       'La comparaison principale utilise13212scans avec les quatre modalités disponibles, soit98,31%du test complet de13439scans. Les observations disponibles propres aux22combinaisons sont présentées séparément. AP, ROC-AUC, précision, rappel, F1, FPR, FNR et matrices de confusion sont recalculés.',
       'Vérifier identifiants, labels, seuils, nombre de lignes, prévalence et couverture. Les valeurs sur13439ne doivent pas être mélangées avec celles sur13212dans une même comparaison.',
       '« Je compare les modèles sur les mêmes exemples, puis je montre séparément leur capacité à couvrir les données incomplètes. »'),
      ('16. Quantifier l’incertitude et la contribution des modalités',
       'Distinguer un écart numérique d’un résultat suffisamment stable sur les groupes observés.',
       'Les scans d’un même site ou contenu ne sont pas indépendants. Un bootstrap ligne par ligne pourrait sous-estimer l’incertitude.',
       'Les différences sont appariées sur les mêmes5230groupes et200rééchantillonnages. Les65comparaisons incluent les fusions centrales et les ajouts de modalités. Les rangs sont conservés et les multiplicateurs de groupes changent à chaque tirage.',
       'Les intervalles ne sont pas corrigés pour toutes les comparaisons et n’intègrent pas plusieurs graines d’entraînement. M2−M1a un intervalle qui recouvre zéro : ne pas annoncer sa supériorité générale.',
       '« Un écart d’AP doit être accompagné de son incertitude et de son périmètre ; je ne transforme pas un classement exploratoire en preuve indépendante. »'),
      ('17. Examiner les erreurs et le rôle des captures',
       'Comprendre les conséquences des décisions et préparer une revue humaine.',
       'Un faux positif bloque un site légitime ; un faux négatif laisse passer du phishing. Les deux coûts ne sont pas équivalents et doivent être discutés avant un choix de déploiement.',
       'Les erreurs sont regroupées par hébergeur, statut HTTP, source, mois, état HTML/image et qualité. Les dénominateurs de chaque classe sont conservés. Une file de48exemples est proposée à la revue humaine, sans modification de label.',
       'Sur le test complet, M1produit842FP/401FN et M2produit148FP/1023FN. Ces comptes montrent un compromis, pas un meilleur modèle universel. La faiblesse de l’image est observée ; ses causes restent des hypothèses à tester.',
       '« Réduire les alertes n’est pas nécessairement améliorer la sécurité si davantage de phishing sont manqués. »'),
      ('18. Tester la faisabilité chronologique',
       'Vérifier si les données permettent réellement d’évaluer des périodes postérieures.',
       'Un test groupé protège des identités, mais ne simule pas nécessairement une nouvelle campagne ou un changement d’hébergement dans le temps.',
       'Les dates fixent les rôles par quantiles et les groupes traversant les périodes sont purgés. Après cette purge, calibration ne conserve que1511phishing et aucun bénin. Le protocole est donc NOT_FEASIBLE.',
       'Ne pas déplacer les dates, rechercher une fenêtre favorable ou changer les labels après observation. Collecter à l’avenir les deux classes par période et des conditions de capture comparables.',
       '« La généralisation temporelle n’a pas pu être démontrée avec ce corpus ; cette limite est documentée, pas masquée par un score artificiel. »'),
      ('19. Mesurer le coût Big Data à périmètre égal',
       'Comparer les moteurs sur la même opération logique et comprendre ce qui coûte réellement du temps.',
       'Le décodage de ZIP bruts n’est pas comparable à une lecture Parquet. Les temps de démarrage et le nombre de fichiers produits peuvent dominer un petit benchmark local.',
       'Le benchmark pandas lit, valide, cast, écrit en Snappy, relit et vérifie l’égalité. Quatre fractions, trois répétitions et deux scénarios donnent24mesures. À67501lignes, les médianes sont0,3075spour Aet0,4048spour B. L’extraction ZIP est mesurée séparément.',
       'Spark a été contrôlé dans un processus sans PyTorch mais reste BLOCKED_RESOURCE, sans démarrage JVM ni temps annoncé. Conserver médianes, étendues, tailles, fichiers et RSS estimée ; local[1]n’est pas un cluster multi-nœuds.',
       '« Je démontre un coût pandas mesuré. Je ne prétends pas que Spark est plus rapide ou plus lent sans l’avoir exécuté. »'),
      ('20. Restituer, démontrer et préparer la suite',
       'Faire une démonstration reproductible et formuler une conclusion proportionnée aux preuves.',
       'Une capture de site vivant peut changer pendant une soutenance. Une démonstration enregistrée rend le déroulé fiable, à condition de ne pas la présenter comme un nouveau test.',
       'Le notebook présente une inférence réellement enregistrée, ses six scores et leurs seuils. Le code d’inférence de nouveaux inputs est intégré dans la partie FULL. Rapport, figures et soutenance reprennent les mêmes populations et métriques.',
       'Annoncer RQ1comme gain interne de classement avec compromis FP/FN, RQ2comme non démontrée, et RQ3comme partiellement mesurée. Conserver modèles et seuils avant une collecte équilibrée et un nouveau lot indépendant scellé.',
       '« Le résultat final est une comparaison défendable, avec ses limites et un protocole de validation future, pas une promesse de détection parfaite. »')]
    intro=f'''
Cette annexe sert de guide de compréhension et de préparation orale. Elle ne remplace pas les tableaux de résultats du rapport et ne décrit pas des expériences supplémentaires.

**État du notebook enregistré lors de cette mise à jour :** mode `{snapshot['mode']}`, {snapshot['executed_cells']}/{snapshot['code_cells']} cellules de code avec compteur d’exécution, {len(snapshot['errors'])} erreur enregistrée. {status}

Les scores du rapport proviennent du FULL déjà vérifié du projet actuel. Une exécution PRESENTATION recharge ces scores ; elle ne constitue pas un nouvel entraînement ou un nouveau test indépendant. Le notebook n’a pas été modifié par la mise à jour du rapport.
'''
    paragraphs=[intro]
    for title,objective,reason,method,control,oral in steps:
        paragraphs.append(f'''### {title}

**Objectif.** {objective}

**Pourquoi cette étape ?** {reason}

**Ce qui est réalisé dans le projet.** {method}

**Vérification et limite à annoncer.** {control}

**Formulation possible à l’oral.** {oral}
''')
    conclusion='''
### Fil conducteur pour la soutenance

Présenter d’abord le problème et la cible, puis le corpus et ses biais. Expliquer ensuite comment les partitions empêchent les fuites, ce que chaque branche apprend et ce que les fusions combinent. Montrer les résultats sur une même cohorte, puis le compromis entre fausses alertes et phishing manqués. Terminer par les limites temporelles, matérielles et de validation externe, avec les améliorations de collecte prévues.

L’objectif n’est pas de lire chaque fonction du notebook. Il est de pouvoir relier chaque choix technique à un risque méthodologique, à une preuve enregistrée et à une limite clairement assumée. Les hypothèses d’explication ne doivent pas être présentées comme des causes confirmées.
'''
    # Improve ordinary prose spacing while preserving URLs, code and identifiers such as U1/M2.
    import re
    appendix='\n\n'.join(paragraphs)+conclusion
    parts=re.split(r'(`[^`]+`|https?://\S+)',appendix)
    appendix=''.join(p if i%2 else re.sub(r'(?<=[a-zà-ÿ])(?=\d)|(?<=\d)(?=[a-zà-ÿ])',' ',p) for i,p in enumerate(parts))
    path.write_text(original+MARKER+appendix+'\n',encoding='utf-8')
    proof=dict(snapshot,steps_explained=len(steps),report=str(path.relative_to(ROOT)),report_updated=True,
               metrics_source='verified existing FULL only',thresholds_changed=False,labels_changed=False)
    (ROOT/'artifacts/finalization/defense_report_update.json').write_text(json.dumps(proof,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(proof,ensure_ascii=False))


if __name__=='__main__':enrich()
