"""Validate scientific deliverables and preserve all protected experimental artifacts."""
from pathlib import Path
import ast,csv,hashlib,json,re
from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'artifacts/scientific_writing'
OUT=ROOT/'reports/FIGURES_ET_RESULTATS'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def rows(p):
    with Path(p).open(encoding='utf8',newline='') as f:return list(csv.DictReader(f))
def sha(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for block in iter(lambda:f.read(2**20),b''):h.update(block)
    return h.hexdigest()

def main():
    before=read(P/'protected_before.json')
    for rel,expected in before.items():assert sha(ROOT/rel)==expected,rel
    original_preserved=read(ROOT/'artifacts/finalization/preserved_run_hashes.json')
    for rel,expected in original_preserved.items():assert sha(ROOT/rel)==expected,rel
    report=(ROOT/'reports/PHISHARK2026_RAPPORT_FINAL.md').read_text(encoding='utf8')
    assert len(re.findall(r'^## Chapitre [1-8] ',report,re.M))==8
    assert '{{' not in report
    metrics=rows(OUT/'table_28_common.csv');checked=rows(OUT/'verification_28.csv')
    assert len(metrics)==len(checked)==28 and len({r['model'] for r in metrics})==28
    checks={r['model']:r for r in checked}
    for r in metrics:
        assert r['model'] in report and r['n']=='13212'
        for key in ['AP','ROC_AUC','precision','recall','F1','FPR','FNR','TN','FP','FN','TP']:
            assert abs(float(r[key])-float(checks[r['model']][key]))<1e-10
    by_model={r['model']:r for r in metrics};a=by_model['M1'];b=by_model['M2']
    assert int(a['FP'])-int(b['FP'])==666 and int(b['FN'])-int(a['FN'])==616
    assert abs(float(a['AP'])-.9722010990399745)<1e-12 and abs(float(b['AP'])-.9789633291034159)<1e-12
    assert len(rows(OUT/'dictionnaire_21_features.csv'))==21
    assert all(r['cross_partition_identities']=='0' for r in rows(OUT/'split_identity_audit.csv'))
    assert len(rows(OUT/'cas_erreurs_anonymises.csv'))==20
    assert not any('target_url' in r or 'scan_id' in r for r in rows(OUT/'cas_erreurs_anonymises.csv'))
    definitions=read(P/'implemented_definitions.json')
    assert 'DenseClassifier(132)' in definitions['architecture']
    assert 'DenseClassifier(2 * len(FEATURES))' in definitions['architecture']
    prep=read(ROOT/'artifacts/runs/full_experiment/grouped/77162f55317be0844ec3/preparation.json')
    assert sha(ROOT/'data/processed/aea0809c7521684e3b49/canonical.parquet')==prep['extraction']['canonical_sha256']
    assert sha(ROOT/prep['split_relpath'])==prep['split_sha256']
    assert sha(ROOT/'data/raw/phishark2026_public_metadata.csv')==prep['extraction']['binding']['metadata_sha256']
    images=re.findall(r'!\[([^\]]+)\]\(([^)]+)\)',report)
    assert len(images)==9
    assert [int(re.match(r'Figure (\d+)',caption)[1]) for caption,_ in images]==list(range(1,10))
    for _,path in images:assert (ROOT/'reports'/path).is_file(),path
    assert len(re.findall(r'^\*\*Tableau \d+',report,re.M))==31
    bib=(ROOT/'reports/BIBLIOGRAPHIE.bib').read_text(encoding='utf8')
    assert len(re.findall(r'^@',bib,re.M))==10
    inventory=read(P/'sources/pdf_inventory.json');assert len(inventory)==4
    for item in inventory:
        assert 'sha256' in item and sha(ROOT/item['file'])==item['sha256']
    pdf=PdfReader(ROOT/'reports/PHISHARK2026_RAPPORT_FINAL.pdf')
    text=[page.extract_text() or '' for page in pdf.pages]
    layout=read(P/'layout_check.json')
    assert layout['pages']==len(pdf.pages) and layout['rendered_pages']==len(pdf.pages)
    assert not layout['pages_under_70_characters'] and not layout['contains_missing_glyph']
    assert not layout['unresolved_template']
    annex=max(i+1 for i,t in enumerate(text) if 'Annexes — Preuves, paramètres et résultats complets' in t and 'Annexe A.' in t)
    assert 30<annex<len(pdf.pages),'The annex boundary must be the actual chapter, not its TOC entry'
    # A numerical table in the source and corresponding PDF must include the central counts.
    joined='\n'.join(text)
    for fragment in ['0,972201','0,978963','666','616','132','42','NOT_FEASIBLE','BLOCKED_RESOURCE']:assert fragment in joined,fragment
    questions=(ROOT/'presentation/QUESTIONS_JURY.md').read_text(encoding='utf8')
    assert len(re.findall(r'^## \d+\.',questions,re.M))==24
    assert (ROOT/'presentation/ARGUMENTAIRE_SOUTENANCE.md').is_file()
    for name in ['01_REVUE_CRITIQUE_LITTERATURE.md','02_HYPOTHESES_ET_PREUVES.md','03_JUSTIFICATION_METHODOLOGIQUE.md','04_PLAN_DETAILLE_RAPPORT.md']:
        assert (ROOT/'reports/scientific'/name).stat().st_size>2500
    catalog=[dict(file=x['file'],pages=x['pages'],sha256=x['sha256']) for x in inventory]
    output_manifest={f.name:sha(f) for f in OUT.iterdir() if f.is_file() and f.name!='manifest.json'}
    (OUT/'manifest.json').write_text(json.dumps(dict(run=prep['version'],code=prep['code'],scope='Verified aggregates and pseudonymous decisions; no raw captures or private scan mapping',files=output_manifest),indent=2),encoding='utf8')
    status=dict(status='PASS',pages=len(pdf.pages),pages_before_annexes=annex-1,annex_pages=len(pdf.pages)-annex+1,configurations=28,common_scans=13212,figures=9,tables=31,pseudonymous_error_rows=20,jury_questions=24,protected_hashes_verified=len(before),raw_metadata_and_cache_hashes_verified=True,networks_trained=False,threshold_changes=False,label_changes=False,notebook_changed=False,visual_review='All pages rendered; contact sheets and detailed pages inspected',source_pdfs=catalog)
    (ROOT/'reports/VERIFICATION_SCIENTIFIQUE.json').write_text(json.dumps(status,indent=2,ensure_ascii=False),encoding='utf8')
    report_text=f'''# Vérification scientifique — 26 novembre 2026

## Périmètre et réalisation

Le mémoire courant comporte **{len(pdf.pages)} pages**, dont **{len(pdf.pages)-annex+1} pages d'annexes**. Il comprend huit chapitres, 31 tableaux et neuf figures ; son corps principal est distinct des résumés, sommaire et bibliographie. La cible de volume reste indicative : aucun contenu artificiel n'a été ajouté pour atteindre un quota de pages. Les quatre documents de cadrage, la bibliographie, les données des illustrations et les supports oraux demandés sont présents.

Le rapport précédent, son PDF et les anciennes questions du jury sont conservés localement dans `artifacts/scientific_writing/before_scientific_revision/`. Les résultats historiques ne sont pas écrasés. Le notebook, les poids, les seuils, le cache et les partitions n'ont pas été modifiés pour la rédaction. Aucun réseau n'a été entraîné.

## Contrôles exécutés

| Élément | Statut | Preuve et portée |
|---|---|---|
| Bibliographie | PASS | Dix entrées, dont le sujet local ; trois PDF scientifiques complets lus par sections ciblées, notices officielles et DOI vérifiés pour les références complémentaires. Pas de reproduction prétendue des articles. |
| Source des métriques | PASS | 28 configurations recomputées depuis les registres individuels sur exactement 13 212 IDs ; AP, ROC-AUC, précision, rappel, F1, FPR/FNR et matrices concordent à 1e-10. |
| Architectures | PASS | Définitions du notebook inspectées : 21 features, 42 entrées U4, 132 entrées M2 ; HTML textuel, sans GCN ; couches décrites et paramètres du run. |
| Figures et tableaux | PASS | Neuf figures intégrées avec sources explicites ; 31 tableaux numérotés ; tables de toutes les métriques et matrices des 28 en annexe ; manifeste des fichiers. |
| CRISP-DM | PASS | Les six phases sont reliées aux huit chapitres, aux artefacts et aux questions de recherche. |
| M1/M2 | PASS | 807/390 contre 141/1 006 FP/FN ; 666 FP évités et 616 FN supplémentaires ; intervalle apparié M2−M1 contenant zéro correctement discuté. |
| RQ1 | PARTIAL | Gain interne et exploratoire des fusions centrales ; pas de validation indépendante d'une supériorité générale ni d'équivalence trimodale. |
| RQ2 | BLOCKED | NOT_FEASIBLE pour le protocole chronologique défini : calibration 1 511 phishing/0 bénin après purge. Aucun score futur inventé. |
| RQ3 | PARTIAL | 24 mesures pandas/PyArrow et coûts partiels sauvegardés ; Spark BLOCKED_RESOURCE avant JVM, comparaison distribuée non démontrée. |
| Erreurs et confidentialité | PASS | Vingt décisions pseudonymisées, sans URL ni ID privé ; échantillon illustratif déterministe, pas une revue humaine de labels. Mapping conservé uniquement localement. |
| Préservation | PASS | {len(before)} empreintes protégées identiques ; empreintes supplémentaires du CSV original, cache canonique et manifeste de partitions conformes à la préparation. Aucun changement de label ou de seuil. |
| Export et mise en page | PASS | Texte PDF extractible, sommaire paginé, signets, police Unicode ; toutes les pages rendues, planches et pages détaillées inspectées. Aucune page vide ni caractère manquant détecté. |
| Soutenance | PASS | Argumentaire de 12–15 minutes proposé et 24 questions/réponses ; chiffres rattachés à la cohorte commune. Aucun PPTX historique modifié. |

## Sources effectivement consultées

- Sujet de l'enseignante : copie locale de deux pages, lue intégralement ; RQ1–RQ3.
- Yoon, Buu et Kim 2024 : PDF officiel de 21 pages, méthodes et résultats, §§3–4 et tableaux identifiés.
- Thèse Almakhamreh 2024 : PDF complet de 130 pages physiques obtenu par l'API officielle Hacettepe ; lecture ciblée des méthodes, datasets et chapitre d'évaluation. La première copie tronquée a été remplacée et n'est pas citée comme preuve.
- CrossPhire 2026 : PDF officiel de 45 pages, notamment §§5–7 et tables de protocoles internes/inter-corpus.
- Phishpedia et PhishIntention : notices, résumés et métadonnées USENIX officiels ; aucune affirmation de relecture intégrale des deux articles.
- CRISP-DM : document officiel du consortium hébergé par IBM ; notice arXiv PhiShark vérifiée ; source PLOS des métriques PR et documentation Spark versionnée vérifiées.

Les copies de lecture et leurs empreintes sont locales dans `artifacts/scientific_writing/sources/`. La bibliographie publique conserve DOI/URL et statut des publications ; aucune donnée brute n'est redistribuée avec les figures.

## Limites non levées par la rédaction

Les sources sont parfaitement associées aux labels dans cette copie, et les périodes sont déséquilibrées. Le retrait de colonnes de provenance n'établit pas l'absence de proxys indirects. La fraction causale de l'AP due aux artefacts n'est pas mesurée. Les durées brutes fin−début sont toutes négatives et ne sont pas utilisées comme temps physiques ; la sémantique des horodatages reste à clarifier.

Le bootstrap apparié est conditionnel aux poids et au corpus, avec 200 tirages de groupes ; il ne remplace pas plusieurs graines et ses nombreuses comparaisons ne sont pas corrigées. Les contrôles exacts de contenu ne garantissent pas l'absence de quasi-doublons sémantiques. Les cas FP/FN ne sont pas des labels corrigés ni une expertise humaine. Une nouvelle collecte équilibrée et un test scellé restent nécessaires.

Le PDF comporte {annex-1} pages avant les annexes et {len(pdf.pages)-annex+1} pages d'annexes ; le nombre total ne doit pas être présenté comme un nombre de pages de résultats nouveaux. Le projet est un prototype local reproductible ; certaines exigences expérimentales de généralisation et distribution demeurent partielles ou bloquées.
'''
    (ROOT/'reports/VERIFICATION_SCIENTIFIQUE.md').write_text(report_text,encoding='utf8')
    print(json.dumps(status,ensure_ascii=False))

if __name__=='__main__':main()
