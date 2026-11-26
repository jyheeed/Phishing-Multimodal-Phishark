# Questions du jury — réponses scientifiques défendables

Les chiffres concernent le run courant et la cohorte commune de 13 212 scans, sauf mention contraire. Les tableaux du mémoire et leurs CSV font foi. Ne pas transformer ces réponses en affirmation de validation externe.

## 1. Quelle est exactement votre contribution ?

Nous proposons une étude reproductible de quatre modalités, deux fusions centrales et 22 variantes sur le même corpus, avec rôles de données séparés, contrôle des identités et analyse appariée. La contribution est expérimentale et méthodologique. Nous ne revendiquons ni l'invention de la fusion multimodale ni une architecture équivalente à CrossPhire. Le résultat inclut les limites, notamment l'absence de démonstration temporelle et le compromis d'erreurs.

## 2. Pourquoi quatre modalités plutôt que l'URL seule ?

Elles portent des indices différents : adresse, message extrait, apparence et propriétés techniques. La complémentarité est une hypothèse testée, pas une certitude. Les fusions centrales améliorent le classement interne, mais l'image n'apporte pas un gain systématique. Les données manquantes et le coût d'obtention des preuves font aussi partie de la comparaison.

## 3. Que signifie le label phishing ? Une page 404 est-elle mal étiquetée ?

Le label représente une réputation annotée. La capture représente un contenu à un moment donné. Une campagne peut être expirée ou déplacée lorsqu'on la capture. Un 404 ne suffit donc pas à invalider le label, pas plus qu'un HTTP 200 ne prouve la bénignité. Une correction individuelle exige une revue indépendante du contexte d'annotation ; nous ne relabellisons pas automatiquement.

## 4. À quoi servent CSV et ZIP ?

Le CSV associe identifiant, label et archive. Le ZIP contient des preuves JSON, HTML et screenshot. Le pipeline vérifie les identités et empreintes, extrait des représentations et conserve les états d'indisponibilité. La source, les dates et le label du CSV ne deviennent pas librement des features. Aucune visite de site ni exécution de HTML n'est nécessaire à cette expérience.

## 5. Pourquoi CRISP-DM ?

Le modèle dépend d'un contrat de cible, de la collecte, des transformations et de l'évaluation. Les six phases donnent un produit contrôlable à chaque étape. L'infaisabilité temporelle renvoie à la composition et à la collecte, plutôt qu'à une recherche d'un score de remplacement. CRISP-DM sert ici à relier les décisions et les preuves, pas seulement à nommer les chapitres.

## 6. Qu'apprennent les CNN URL et HTML ?

Les convolutions détectent des motifs locaux dans des séquences de caractères ou tokens après un embedding appris. Elles produisent chacune 32 valeurs. U1 lit au plus 256 caractères et U2 1 024 tokens de texte extrait. Notre HTML n'est pas représenté comme un graphe DOM ; aucun GCN ni rendu JavaScript n'est utilisé. Le texte extrait n'est pas une simulation exacte de visibilité CSS.

## 7. Combien d'entrées possèdent U4 et M2 ?

U4 reçoit 42 valeurs : 21 mesures et 21 indicateurs de manque. M2 reçoit 132 valeurs : quatre embeddings de 32 dimensions et quatre masques. Confondre les mesures brutes avec toutes les entrées ferait perdre le rôle de la disponibilité. Les architectures denses sont respectivement 42→64→32→1 et 132→64→32→1.

## 8. Pourquoi cinq partitions ?

train_encoder ajuste branches et prétraitements ; train_fusion ajuste les têtes sur d'autres observations ; validation choisit les checkpoints ; calibration choisit les seuils ; test décrit la performance. Les groupes restent indivisibles selon les clés contrôlées. Cela réduit des fuites connues et le surapprentissage du méta-modèle sur des prédictions d'entraînement, sans garantir une indépendance parfaite des campagnes.

## 9. Pouvez-vous garantir l'absence de fuite ?

Nous pouvons montrer les contrôles de disjonction des sites, URL, empreintes et entrées encodées effectivement utilisés. Huit clés ont été revérifiées sans recouvrement entre rôles. Nous ne garantissons pas l'absence de tout quasi-doublon sémantique ou proxy de collecte. Une preuve technique de disjonction est nécessaire mais insuffisante pour certifier la validité externe.

## 10. Les 28 configurations correspondent-elles à 28 CNN entraînés ?

Non. Quatre encodeurs sont partagés. M1 moyenne des scores sans apprentissage ; M2 apprend une tête MLP sur embeddings gelés. Les 22 variantes représentent onze ensembles par deux méthodes : LATE et une tête logistique LINEAR_EMBED. La règle LATE complète reprend fonctionnellement M1. Les lignes ne sont donc pas des réseaux ni des essais statistiquement indépendants.

## 11. M1 est-il du stacking et M2 une mixture of experts ?

M1 n'est pas du stacking appris : c'est une moyenne renormalisée des probabilités disponibles. M2 concatène des embeddings et apprend une tête dense ; il ne possède pas de routeur d'experts. Les noms de méthode correspondent au code, sans reprendre des termes de la littérature pour suggérer une architecture non implémentée.

## 12. Quel modèle est le meilleur ?

Cela dépend du critère et d'une validation indépendante. M2 a une AP ponctuellement plus haute, mais M1 a un meilleur rappel et F1 primary dans le test commun. Le test a été exploré, donc nous ne proclamons pas un gagnant final à partir de ce tableau. Un choix opérationnel doit être spécifié sur validation avec coûts, rappel et couverture, puis confirmé sur un nouveau lot.

## 13. Pourquoi une AP élevée peut-elle coexister avec des erreurs importantes ?

AP mesure le classement sur plusieurs seuils. La matrice utilise un seul seuil fixé sur calibration, dont le compromis peut changer sur test. La prévalence et la distribution influencent les décisions observées. Le score sigmoid n'est pas automatiquement calibré comme probabilité de risque. Il faut lire ensemble AP, rappel, précision, FPR, FNR et comptages.

## 14. Quel est le compromis exact M1/M2 ?

M1 produit 807 faux positifs et 390 faux négatifs ; M2 en produit 141 et 1 006 sur les mêmes scans. M2 évite 666 fausses alertes mais manque 616 phishing supplémentaires. Son AP est 0,978963 contre 0,972201. Cette meilleure AP ne justifie pas d'ignorer le rappel ; le coût relatif des erreurs peut inverser la préférence.

## 15. L'écart d'AP M2/M1 est-il statistiquement établi ?

La différence est 0,006762. L'intervalle apparié descriptif à 95 %, calculé sur 200 rééchantillonnages des 5 230 groupes, va de −0,004944 à 0,020995. Il contient zéro : nous ne prétendons pas à une supériorité nette de classement. Les comparaisons multiples ne sont pas corrigées et plusieurs graines d'entraînement n'ont pas été testées.

## 16. Trois modalités sont-elles équivalentes à quatre ?

Les scores de certaines configurations trimodales sont proches ou supérieurs dans cette exécution. Une équivalence demanderait une marge définie avant le test et un protocole adapté. Nous n'en avons pas établi une. Il faut aussi comparer la même famille de fusion : M2/MLP contre LINEAR_EMBED/logistique change simultanément la tête et les modalités.

## 17. Pourquoi votre CNN image est-il faible ?

Nous constatons une AP de 0,592764, pour une référence de prévalence de 0,495307. Résolution 96×96, petit réseau sans préentraînement, qualité des captures et changement de sites sont des explications plausibles. Les captures uniformes existent, mais aucune expérience n'isole à elle seule leur responsabilité totale. Nous ne concluons ni que toute image est inutile, ni qu'un ResNet résoudra nécessairement le problème.

## 18. Les hauts scores historiques proviennent-ils des biais ?

La source est entièrement associée à la classe dans cette copie, et les périodes diffèrent fortement. Ces constats rendent plausibles des raccourcis indirects. Retirer source et dates de X ne supprime pas forcément leurs traces dans le contenu. La fraction causale de l'AP attribuable à ces artefacts n'est pas mesurée ; nous ne donnons pas un pourcentage arbitraire.

## 19. Que signifie « calibration » ici ?

C'est la partition où les seuils primary et recall85 sont déterminés. Il n'y a pas de calibrateur probabiliste supplémentaire de type Platt ou isotone. Le rappel cible de 85 % sur calibration peut ne pas être atteint sur test. Aucun seuil n'est réajusté après lecture des erreurs test pour rendre le résultat plus favorable.

## 20. Pourquoi RQ2 n'est-elle pas démontrée ?

Le protocole chronologique défini purge les groupes traversant les frontières. Sa calibration finale contient 1 511 phishing et aucun bénin après retrait de 22 064 scans. Il ne fournit pas les conditions nécessaires à la comparaison envisagée. Nous ne déclarons pas toute évaluation temporelle impossible, mais ce protocole est NOT_FEASIBLE. La prochaine collecte doit représenter les deux classes au cours du temps.

## 21. Qu'avez-vous vraiment mesuré pour Big Data ?

L'extraction locale est chronométrée et les temps d'entraînement sont enregistrés. Le benchmark tabulaire pandas/PyArrow comporte quatre fractions, deux scénarios et trois répétitions, soit 24 mesures. Il inclut vérification des sorties mais pas capture réseau ni toute la chaîne multimodale. Ces mesures ne démontrent pas un débit de nouveaux sites sur Internet.

## 22. Spark est-il plus rapide ?

Nous ne pouvons pas le conclure. Le contrôle séparé a enregistré BLOCKED_RESOURCE avant la JVM. Aucun temps Spark comparable n'est disponible. Il faut des ressources suffisantes et un périmètre équivalent, en distinguant démarrage, lecture/écriture et validation. Spark local n'est pas une preuve de scalabilité multi-nœuds.

## 23. Que montrent les durées négatives ?

Le calcul fin−début est négatif pour tous les scans du cache. Ce champ ne peut pas être utilisé comme durée physique sans clarification du producteur. Nous ne changeons pas le signe pour le rendre acceptable et ne l'utilisons pas dans les features. Les temps d'extraction et d'entraînement proviennent d'autres chronométrages.

## 24. Comment tester le projet et que reste-t-il à faire ?

L'interface accepte une URL seule ou un ZIP local et recharge les poids gelés. PRESENTATION réaffiche les résultats sans réentraîner. Un exemple historique n'est pas un nouveau test indépendant. Il reste à équilibrer la collecte, clarifier les dates, revoir les labels de cas litigieux, compléter Spark et évaluer plusieurs fenêtres/graines puis un lot scellé. Le prototype est reproductible ; ses limites de généralisation demeurent.
