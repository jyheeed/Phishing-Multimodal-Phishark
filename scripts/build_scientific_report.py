"""Assemble the scientific manuscript from authored prose and verified local tables."""
from pathlib import Path
import ast,csv,hashlib,json,re,shutil
import pandas as pd

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reports/FIGURES_ET_RESULTATS'
P=ROOT/'artifacts/scientific_writing'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def csvread(name):return pd.read_csv(OUT/name,float_precision='round_trip')
def fmt(v):
    if pd.isna(v):return 'NON DÉFINI'
    if isinstance(v,(float,)):
        return f'{v:.6f}' if abs(v)<10 else f'{v:.3f}'
    return str(v).replace('|','/').replace('\n',' ')
def table(frame,columns=None,labels=None):
    if columns is not None:frame=frame[columns]
    labels=labels or {}
    lines=['| '+' | '.join(labels.get(c,c) for c in frame.columns)+' |','| '+' | '.join(['---']*len(frame.columns))+' |']
    lines+=['| '+' | '.join(fmt(v) for v in row)+' |' for row in frame.itertuples(index=False,name=None)]
    return '\n'.join(lines)

FEATURE_PURPOSES={
'dns_records_count':('Nombre de résultats DNS','Réponses observables ; dépend de disponibilité et collecte'),
'whois_creation_date_present':('Présence d’une date de création','Ne mesure pas un âge de domaine'),
'whois_expiration_date_present':('Présence d’une date d’expiration','Dépend du format et des restrictions WHOIS'),
'whois_registrar_present':('Présence du registrar','N’identifie pas directement une réputation'),
'whois_name_servers_count':('Nombre de serveurs de noms','Architecture DNS et représentation du JSON'),
'ip_geo_ip_present':('Présence d’une IP','Disponibilité de la résolution ou du service'),
'ip_geo_country_code_present':('Présence d’un code pays','Ne code pas la valeur du pays ni une dangerosité géographique'),
'ports_open_ports_count':('Nombre de ports ouverts','Périmètre et conditions du scan'),
'tls_certificate_success_boolean':('Succès TLS déclaré','HTTPS valide ne signifie pas bénin'),
'tls_certificate_issuer_present':('Présence d’un émetteur TLS','N’utilise pas son nom'),
'tls_certificate_subject_present':('Présence d’un sujet TLS','Disponibilité du certificat'),
'tls_certificate_subject_alternative_names_count':('Nombre de SAN TLS','Configuration du certificat, pas identité frauduleuse'),
'web_page_title_length':('Longueur du titre de page','Présence ou richesse textuelle, peut refléter une page d’erreur'),
'web_page_description_length':('Longueur de description','Métadonnées et pratiques de publication'),
'web_page_detected_technologies_count':('Nombre de technologies détectées','Dépend du détecteur et du contenu capturé'),
'web_page_outgoing_links_count':('Nombre de liens sortants','Complexité de page et extraction'),
'web_page_total_url_count_number':('Total numérique des URL déclaré','Ne reconstitue pas le contenu des URL'),
'redirection_redirect_count_number':('Nombre de redirections déclaré','Parcours technique, pas intention de fraude'),
'redirection_chain_count':('Taille de la chaîne de redirection','Périmètre et format de capture'),
'compliance_files_checked_files_count':('Nombre de fichiers de conformité vérifiés','Activité du collecteur et disponibilité'),
'compliance_files_found_files_count':('Nombre de fichiers de conformité trouvés','Pratique de publication et conditions de collecte'),
}

def main():
    metrics=csvread('table_28_common.csv');m=metrics.set_index('model');summary=read(ROOT/'artifacts/published/analysis_summary.json')
    verification=read(P/'metrics_check.json');assert verification['models']==28 and verification['status']=='PASS'
    draft=(ROOT/'scripts/report_scientific_template.md').read_text(encoding='utf8')
    for marker,file in [('CHAPTER_RESULTS','scientific_results.md'),('CHAPTER_GENERALIZATION','scientific_generalization.md'),('CHAPTER_CONCLUSION','scientific_conclusion.md')]:
        draft=draft.replace('{{'+marker+'}}',(ROOT/'scripts'/file).read_text(encoding='utf8'))
    training=pd.DataFrame(summary['training'])
    central=metrics.loc[metrics.model.isin(['U1','U2','U3','U4','M1','M2'])]
    extra=metrics.loc[metrics.fusion.ne('UNIMODAL')&~metrics.model.isin(['M1','M2'])]
    eda=csvread('EDA_classes.csv');availability=[]
    for column in ('min_utc','max_utc'):eda[column]=eda[column].str[:10]
    for row in eda.itertuples():
        availability.append(dict(classe='Bénin' if row.label_id==0 else 'Phishing',n=int(row.n),URL=int(row.n),HTML=int(row.html_ok),IMAGE=int(row.image_ok),TECH=int(row.n),images_uniformes=int(row.image_uniform)))
    declarations=[]
    for n in ast.walk(ast.parse(read(P/'implemented_definitions.json')['Settings'])):
        if isinstance(n,ast.AnnAssign) and isinstance(n.target,ast.Name):declarations.append((n.target.id,ast.unparse(n.value) if n.value else ''))
    sub=csvread('paired_modality_contributions.csv')
    chosen=sub.loc[(sub.reference.eq('U2')&sub.model.isin(['M1','M2']))|(sub.model.eq('M2')&sub.reference.eq('M1'))|(sub.model.eq('LINEAR_EMBED__URL+HTML+IMAGE+TECH'))]
    chosen=chosen[['model','reference','added_modality','AP_difference','lower95','upper95']].fillna('—')
    types=[]
    for _,row in csvread('dictionnaire_21_features.csv').iterrows():
        key='_'.join(row.tolist());purpose,risk=FEATURE_PURPOSES[key]
        types.append(dict(feature=key,champ=row.json_file+'.json / '+row.field,opération=row.operation,interprétation=purpose,limite=risk))
    normal_splits=csvread('partition_counts.csv')
    temporal=read(ROOT/'artifacts/published/temporal_feasibility.json');tcounts=[]
    for role,counts in temporal['counts'].items():tcounts.append(dict(partition=role,bénins=counts.get('0',0),phishing=counts.get('1',0)))
    matrices=[]
    for name in ['M1','M2']:
        r=m.loc[name];matrices.append(dict(modèle=name,vrais_bénins_prédits_bénins=int(r.TN),bénins_prédits_phishing=int(r.FP),phishing_prédits_bénins=int(r.FN),vrais_phishing_détectés=int(r.TP)))
    strata=csvread('error_strata.csv')
    strata=strata.loc[strata.model.isin(['M1','M2'])&((strata.dimension.eq('http_status')&strata.value.astype(str).isin(['200','200.0','404','404.0']))|strata.dimension.eq('uniform'))]
    if len(strata)==0:strata=csvread('error_strata.csv').query("model in ['M1','M2'] and dimension == 'uniform'")
    literature=pd.DataFrame([
        ['Yoon 2024 [1]','URL caractères/mots + DOM','CNN + Transformer + GCN, fusion apprise','Validation croisée ; externe phishing seuls','Complémentarité ; pas notre représentation HTML'],
        ['Thèse 2024 [2]','URL + texte + image','Encodeurs spécialisés, fusion multimodale','Intra/inter-corpus, configurations distinctes','Ne pas assimiler une accuracy à notre AP'],
        ['CrossPhire 2026 [3]','URL + texte + image','Concaténation et mixture of experts','Cinq corpus, transfert','Notre M2 n’est pas une MoE'],
        ['Phishpedia [4]','Visuel + références de marque','Reconnaissance de logos','Comparaison et terrain','Notre CNN ne reconnaît pas explicitement une marque'],
        ['PhishIntention [5]','Apparence + interaction','Analyse d’intention','Comparaison et terrain','Notre système ne navigue pas activement'],
    ],columns=['Étude','Preuves','Conception','Protocole','Limite de transfert'])
    seq=pd.DataFrame([
        ['Indices','B×256','B×1024','Caractères URL / tokens HTML'],
        ['Embedding 24','B×256×24','B×1024×24','PAD=0 ; vocabulaire train seul'],
        ['Conv1d 24→48, k5/s2/p2','B×48×128','B×48×512','ReLU'],
        ['Conv1d 48→32, k3/s2/p1','B×32×64','B×32×256','ReLU'],
        ['AdaptiveMaxPool1d(1)','B×32','B×32','Embedding exporté'],
        ['Dropout 0,25 + Linear32→1','B','B','Logit puis sigmoid en inférence'],
    ],columns=['Étape','U1','U2','Précision'])
    image=pd.DataFrame([
        ['RGB normalisé','B×3×96×96','Division par 255'],['Conv k5/s2/p2 + BN/ReLU','B×24×48×48','3→24 canaux'],
        ['Conv k3/s2/p1 + BN/ReLU','B×48×24×24','24→48'],['Conv k3/s2/p1 + BN/ReLU','B×64×12×12','48→64'],
        ['AdaptiveAvgPool2d(2,2)','B×64×2×2','256 valeurs aplaties'],['Linear256→64/ReLU/Dropout0,2','B×64','Projection'],
        ['Linear64→32/ReLU','B×32','Embedding'],['Linear32→1','B','Logit'],
    ],columns=['Étape U3','Tenseur','Précision'])
    combination_defs=pd.DataFrame([dict(sous_ensemble=x,méthodes='LATE ; LINEAR_EMBED',modalités=len(x.split('+'))) for x in extra.modalities.drop_duplicates()])
    benchmark=csvread('benchmark_summary.csv');benchmark['pic_RSS_Mio']=benchmark.peak_rss_bytes/2**20
    operating=csvread('operating_points_frozen.csv');operating=operating.loc[operating.model.isin(['M1','M2'])]
    hypotheses=(ROOT/'reports/scientific/02_HYPOTHESES_ET_PREUVES.md').read_text(encoding='utf8')
    hlines=[line for line in hypotheses.splitlines() if line.startswith('|')]
    demo=csvread('demonstration_enregistree.csv')
    bibliography='''[1] J.-H. Yoon, S.-J. Buu et H.-J. Kim, « Phishing Webpage Detection via Multi-Modal Integration of HTML DOM Graphs and URL Features Based on Graph Convolutional and Transformer Networks », Electronics, 13(16), 3344, 2024. [DOI et texte](https://doi.org/10.3390/electronics13163344). Lecture : §§3–4, tableaux 3, 5, 7 et 8.

[2] A. H. A. Almakhamreh, Detection of Phishing Web Pages by Combining Semantical and Visual Information, mémoire de master, Hacettepe University, avril 2024. [Notice et PDF officiels](https://openaccess.hacettepe.edu.tr/items/52a1fd1b-60a5-482e-8235-a51a32f10e01). Lecture ciblée : chapitres 4–6 ; tableaux 6.5–6.9, en particulier p. 82 imprimée.

[3] A. H. A. Almakhamreh et A. S. Bozkir, « CrossPhire: Benefiting Multimodality for Robust Phishing Web Page Identification », Applied Sciences, 16(2), 751, 2026. [DOI et texte](https://doi.org/10.3390/app16020751). Lecture : §§5–7, tableaux 10–12 ; distinct de la thèse 2024.

[4] Y. Lin et al., « Phishpedia: A Hybrid Deep Learning Based Approach to Visually Identify Phishing Webpages », USENIX Security 21, p. 3793–3810, 2021. [Notice et BibTeX officiels](https://www.usenix.org/conference/usenixsecurity21/presentation/lin). Consultation de la notice/résumé ; pas de reproduction des expériences.

[5] R. Liu et al., « Inferring Phishing Intention via Webpage Appearance and Dynamics: A Deep Vision Based Approach », USENIX Security 22, p. 1633–1650, 2022. [Notice et BibTeX officiels](https://www.usenix.org/conference/usenixsecurity22/presentation/liu-ruofan). Consultation de la notice/résumé.

[6] P. Chapman, J. Clinton, R. Kerber, T. Khabaza, T. Reinartz, C. Shearer et R. Wirth, CRISP-DM 1.0: Step-by-step Data Mining Guide, 2000. [Guide du consortium hébergé par IBM](https://public.dhe.ibm.com/software/analytics/spss/documentation/modeler/14.2/fr/CRISP-DM.pdf). Les six phases organisent la démarche, sans garantir la performance.

[7] F. Çolhak, F. Demirkıran, H. Dağ et A. Iliev, « PhiShark2026: A Multi-Layer Active-Web Raw-Evidence Dataset for Phishing Website Research », préprint arXiv:2608.23199, août 2026. [Notice officielle](https://arxiv.org/abs/2608.23199). Le statut de préprint est conservé ; les effectifs de notre copie sont vérifiés localement.

[8] T. Saito et M. Rehmsmeier, « The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets », PLOS ONE, 10(3), e0118432, 2015. [Article officiel](https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0118432). Motivation des métriques PR, sans transfert de scores.

[9] Apache Spark, Performance Tuning, documentation versionnée 4.0.1. [Documentation officielle](https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html). Source technique sur partitionnement et ressources ; aucun temps de benchmark attribué à cette page.

[10] Sujet local de l'enseignante, Phishing multimodal, 2 pages, sans date ou auteur inventé. Fichier : docs/specification/Projet_phishing_multimodal.pdf. Questions RQ1–RQ3 et périmètre du projet. Sources consultées le 25 novembre 2026.
'''
    protected=read(P/'protected_before.json')
    provenance='''Le run expérimental courant est `77162f55317be0844ec3`. Son code producteur est `75d3c99cede2b5723ea44c3710ffb991a3434d0c9f0ca6846458ad2d406633d6`. Le notebook unifié courant reste distinct de cette provenance et n'est pas réattribué aux poids historiques. Les anciennes versions du rapport et des questions du jury sont conservées dans les artefacts locaux avant révision.

Les 28 lignes sont recomputées dans `verification_28.csv`. Les tables sources et figures sont réunies dans `reports/FIGURES_ET_RESULTATS/`. Un manifeste relie les fichiers produits à leurs empreintes. Les registres privés de prédictions, les identifiants complets de cas et les captures brutes ne sont pas copiés dans ces illustrations.

Scripts : `prepare_scientific_evidence.py` contrôle les métriques ; `describe_scientific_data.py` construit l'EDA et les cas anonymisés ; `build_scientific_report.py` assemble ce mémoire ; `export_scientific_pdf.py` produit le PDF ; `validate_scientific_report.py` contrôle les livrables et la préservation. Aucun de ces scripts n'ajuste un modèle.
'''
    mapping={
        'LITERATURE_TABLE':table(literature),'EDA_CLASS_TABLE':table(eda),
        'SOURCE_TABLE':table(csvread('EDA_source_name.csv')),'PERIOD_TABLE':table(csvread('EDA_period.csv')),
        'AVAILABILITY_TABLE':table(pd.DataFrame(availability)),
        'SPLIT_AUDIT_TABLE':table(csvread('split_identity_audit.csv')),'PARTITION_TABLE':table(normal_splits),
        'SEQUENCE_LAYERS':table(seq),'IMAGE_LAYERS':table(image),'TRAINING_TABLE':table(training,['model','best_epoch','validation_AP','train_seconds','parameters','device']),
        'COMBINATIONS_TABLE':table(combination_defs),
        'CENTRAL_RANKING':table(central,['model','modalities','AP','ROC_AUC','threshold']),
        'CENTRAL_DECISION':table(central,['model','precision','recall','F1','FPR','FNR','FP','FN']),
        'PAIRS_TABLE':table(extra.loc[extra.modality_count.eq(2)],['model','AP','ROC_AUC','F1','FPR','FNR']),
        'TRIPLETS_TABLE':table(extra.loc[extra.modality_count.ge(3)],['model','AP','F1','recall','FPR','FP','FN']),
        'CONTRIBUTION_TABLE':table(chosen),'M1_M2_MATRICES':table(pd.DataFrame(matrices)),
        'OPERATING_TABLE':table(operating,['model','policy','threshold','AP','precision','recall','FPR','FN','FP']),
        'ERROR_STRATA_TABLE':table(strata,['model','dimension','value','n','benign','phishing','FP','FN','FPR','FNR']),
        'FULL_TEST_TABLE':table(csvread('six_models_full_test.csv'),['model','n','AP','precision','recall','F1','FPR','FP','FN']),
        'BENCHMARK_TABLE':table(benchmark,['scenario','n','repetitions','seconds_median','seconds_min','seconds_max','throughput_median','pic_RSS_Mio']),
        'TEMPORAL_TABLE':table(pd.DataFrame(tcounts)),'DEMO_TABLE':table(demo,['model','label_id','probability','threshold','prediction']),
        'FEATURE_TABLE':table(pd.DataFrame(types)),
        'CONFUSION_ALL':table(metrics,['model','TN','FP','FN','TP','threshold']),
        'METRICS_ALL':table(metrics,['model','AP','ROC_AUC','precision','recall','F1','FPR','FNR']),
        'ERROR_CASES':table(csvread('cas_erreurs_anonymises.csv'),['case','error','probability','threshold','http_status','uniform','technical_missing','url_characters']),
        'HYPOTHESES_TABLE':'\n'.join(hlines),'PROVENANCE':provenance,'BIBLIOGRAPHY':bibliography,
    }
    for key,value in mapping.items():draft=draft.replace('{{'+key+'}}',value)
    figure_count=0
    def renumber(match):
        nonlocal figure_count
        figure_count+=1
        caption=re.sub(r'^Figure \d+ — ',f'Figure {figure_count} — ',match.group(1))
        return '!['+caption+']('+match.group(2)+')'
    draft=re.sub(r'!\[([^\]]+)\]\(([^)]+)\)',renumber,draft)
    figures=re.findall(r'!\[([^\]]+)\]\(([^)]+)\)',draft)
    figure_table=pd.DataFrame([dict(figure=caption.split(' — ')[0],fichier=file,message=caption,source='CSV et code vérifiés ; voir index détaillé',split='corpus brut' if 'corpus brut' in caption else ('benchmark local' if 'benchmark' in caption else 'test commun')) for caption,file in figures])
    figure_table.to_csv(OUT/'index_figures.csv',index=False)
    index='Les tableaux portent leur population dans le texte et sont fournis en CSV pour réutilisation.\n\n'+table(figure_table,['figure','fichier','split'])
    draft=draft.replace('{{INDEX}}',index)
    headings=re.findall(r'^## (.+)$',draft,re.M)
    toc='\n'.join('- '+h for h in headings if h not in ['Sommaire','Liste des figures et tableaux'])
    draft=draft.replace('{{TOC}}',toc)
    numbered=[];table_number=0;heading='Données du mémoire';in_table=False
    for line in draft.splitlines():
        if line.startswith('#'):heading=line.lstrip('# ').strip()
        if line.startswith('|') and not in_table:
            table_number+=1
            numbered.extend([f'**Tableau {table_number} — {heading}.**',''])
        in_table=line.startswith('|')
        numbered.append(line)
    draft='\n'.join(numbered)+'\n'
    assert not re.search(r'\{\{[A-Z_]+\}\}',draft),'Unresolved report placeholder'
    report=ROOT/'reports/PHISHARK2026_RAPPORT_FINAL.md';report.write_text(draft,encoding='utf8')
    # Use the supplied BibTeX identities and append the independently checked methodology sources.
    bib=(ROOT/'scripts/references_base.bib').read_text(encoding='utf8')
    bib+='''\n% Additional verified references
@techreport{chapman2000crispdm,
 author={Chapman, Pete and Clinton, Julian and Kerber, Randy and Khabaza, Thomas and Reinartz, Thomas and Shearer, Colin and Wirth, Ruediger},
 title={CRISP-DM 1.0: Step-by-step Data Mining Guide},year={2000},
 institution={CRISP-DM Consortium},url={https://public.dhe.ibm.com/software/analytics/spss/documentation/modeler/14.2/fr/CRISP-DM.pdf}}
@misc{colhak2026phishark,
 author={Çolhak, Furkan and Demirkıran, Ferhat and Dağ, Hasan and Iliev, Alexander},
 title={PhiShark2026: A Multi-Layer Active-Web Raw-Evidence Dataset for Phishing Website Research},
 year={2026},eprint={2608.23199},archivePrefix={arXiv},doi={10.48550/arXiv.2608.23199},url={https://arxiv.org/abs/2608.23199},note={Preprint}}
@article{saito2015precisionrecall,
 author={Saito, Takaya and Rehmsmeier, Marc},title={The Precision-Recall Plot Is More Informative than the ROC Plot When Evaluating Binary Classifiers on Imbalanced Datasets},
 journal={PLOS ONE},year={2015},volume={10},number={3},pages={e0118432},doi={10.1371/journal.pone.0118432}}
@manual{spark401performance,
 title={Performance Tuning},author={{Apache Spark}},organization={Apache Software Foundation},
 url={https://spark.apache.org/docs/4.0.1/sql-performance-tuning.html},note={Version 4.0.1; consulted 2026-11-25}}
@misc{enseignante_phishing_subject,
 title={Phishing multimodal},howpublished={Sujet local de l'enseignante},
 note={2 pages; questions RQ1, RQ2 et RQ3; copie locale docs/specification/Projet_phishing_multimodal.pdf}}
'''
    (ROOT/'reports/BIBLIOGRAPHIE.bib').write_text(bib,encoding='utf8')
    writeup=dict(words=len(re.findall(r"\b[\wÀ-ÿ'-]+\b",draft)),characters=len(draft),chapters=8,figures=len(figures),tables=table_number,original_results_preserved=True,protected_files=len(protected))
    (P/'manuscript_build.json').write_text(json.dumps(writeup,indent=2),encoding='utf8')
    shutil.copy2(ROOT/'scripts/jury_questions.md',ROOT/'presentation/QUESTIONS_JURY.md')
    print(json.dumps(writeup))

if __name__=='__main__':main()
