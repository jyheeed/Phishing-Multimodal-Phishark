"""Aggregate actual captured metadata and publish pseudonymous error descriptions only."""
from pathlib import Path
import ast,json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.runtime'))
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RUN=ROOT/'artifacts/runs/full_experiment/grouped/77162f55317be0844ec3'
OUT=ROOT/'reports/FIGURES_ET_RESULTATS'
P=ROOT/'artifacts/scientific_writing'
def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def write(p,x):p.write_text(json.dumps(x,ensure_ascii=False,indent=2,default=str),encoding='utf8')

def main():
    prep=read(RUN/'preparation.json');cache=ROOT/'data/processed/aea0809c7521684e3b49/canonical.parquet'
    cols=[c for c in pq.ParquetFile(cache).schema_arrow.names if c!='html_text']
    raw=pd.read_parquet(cache,columns=cols);split=pd.read_parquet(ROOT/prep['split_relpath'])
    tech=read(RUN/'preprocess.json')['features']
    # Read the text-presence flag in bounded batches, never expose the text itself.
    nonempty={}
    for batch in pq.ParquetFile(cache).iter_batches(batch_size=2048,columns=['scan_id','html_text']):
        values=batch.to_pydict();nonempty.update(zip(values['scan_id'],[bool(t) for t in values['html_text']]))
    raw['URL']=raw.target_url.fillna('').str.len().gt(0)
    raw['HTML']=raw.html_state.isin(['ok','truncated']) & raw.scan_id.map(nonempty)
    raw['IMAGE']=raw.image_state.eq('ok')
    raw['TECH']=np.isfinite(raw[tech].to_numpy(float)).any(axis=1)
    raw['availability_pattern']=raw[['URL','HTML','IMAGE','TECH']].astype(int).astype(str).agg(''.join,axis=1)
    raw['period']=pd.to_datetime(raw.scan_created_at,utc=True).dt.strftime('%Y-%m')
    raw['url_characters']=raw.target_url.fillna('').str.len()
    for key in ['source_name','period','availability_pattern','html_state','image_state','http_status','uses_https','uniform','quality_state','negative_duration']:
        counts=raw.groupby([key,'label_id'],dropna=False).size().rename('n').reset_index()
        counts.to_csv(OUT/('EDA_'+key+'.csv'),index=False)
    missing=raw[tech].isna().groupby(raw.label_id).mean().T.rename(columns={0:'benign_missing_fraction',1:'phishing_missing_fraction'})
    missing.index.name='feature';missing.to_csv(OUT/'EDA_missing_features.csv')
    aggregate=raw.groupby('label_id').agg(n=('scan_id','size'),min_utc=('scan_created_at','min'),max_utc=('scan_created_at','max'),http_404=('http_status',lambda x:x.eq(404).sum()),image_ok=('IMAGE','sum'),html_ok=('HTML','sum'),image_uniform=('uniform','sum'),url_length_median=('url_characters','median')).reset_index()
    aggregate.to_csv(OUT/'EDA_classes.csv',index=False)
    merged=raw.merge(split,on=['scan_id','label_id'],validate='one_to_one')
    split_counts=merged.groupby(['split','label_id']).size().unstack(fill_value=0).reset_index()
    split_counts.columns=['split','benign','phishing'];split_counts['n']=split_counts.benign+split_counts.phishing
    split_counts.to_csv(OUT/'partition_counts.csv',index=False)
    checks=[]
    for key in ['group_id','site_id','normalized_url','raw_html_hash','url_input_hash','html_input_hash','image_input_hash','encoding_component']:
        if key not in merged:continue
        subset=merged.loc[merged[key].notna() & merged[key].astype(str).ne('')]
        overlap=int(subset.groupby(key).split.nunique().gt(1).sum())
        assert overlap==0,(key,overlap)
        checks.append(dict(identity=key,identities=int(subset[key].nunique()),cross_partition_identities=overlap))
    pd.DataFrame(checks).to_csv(OUT/'split_identity_audit.csv',index=False)
    table=pd.read_csv(OUT/'table_28_common.csv',float_precision='round_trip').set_index('model')
    ledger=pd.read_csv(RUN/'predictions.csv',dtype={'scan_id':str},float_precision='round_trip')
    common=set(pd.read_csv(ROOT/'artifacts/finalization/common_cohort_ids.csv',dtype=str).scan_id)
    cases=[];private_map={}
    for model in ['M1','M2']:
        q=ledger.loc[ledger.model.eq(model)&ledger.split.eq('test')&ledger.scan_id.isin(common)].copy()
        q['prediction']=q.probability.ge(table.loc[model,'threshold']).astype(int)
        q=q.merge(raw,on=['scan_id','label_id'],validate='one_to_one')
        for kind,label in [('FP',0),('FN',1)]:
            selected=q.loc[q.label_id.eq(label)&q.prediction.ne(q.label_id)].sort_values('scan_id').head(5)
            for row in selected.itertuples():
                code=f'{model}_{kind}_{len(cases)+1:02d}';private_map[code]=row.scan_id
                cases.append(dict(case=code,model=model,error=kind,label_id=int(row.label_id),probability=row.probability,threshold=table.loc[model,'threshold'],period=row.period,http_status=row.http_status,html_state=row.html_state,image_state=row.image_state,uniform=bool(row.uniform),url_characters=int(row.url_characters),technical_missing=int(pd.isna(pd.Series(row._asdict())[tech]).sum()),interpretation='Prediction disagrees with historical label; cause and relabeling require independent review'))
    pd.DataFrame(cases).to_csv(OUT/'cas_erreurs_anonymises.csv',index=False)
    write(P/'private_case_mapping.json',private_map)
    demo=pd.read_csv(ROOT/'artifacts/published/demo_predictions.csv')
    demo.to_csv(OUT/'demonstration_enregistree.csv',index=False)
    # New illustrations use aggregates only. No screenshots, domains or live URLs are exposed.
    plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False})
    fig,axes=plt.subplots(1,2,figsize=(11,4))
    pd.crosstab(raw.period,raw.label_id).rename(columns={0:'Bénin',1:'Phishing'}).plot.bar(ax=axes[0],color=['#4677a8','#d69552'])
    axes[0].set(xlabel='Mois UTC de capture',ylabel='Scans',title='Composition temporelle — corpus brut')
    pd.crosstab(raw.source_name,raw.label_id).rename(columns={0:'Bénin',1:'Phishing'}).plot.bar(ax=axes[1],color=['#4677a8','#d69552'])
    axes[1].set(xlabel='Source enregistrée',ylabel='Scans',title='Source et classe — association, pas causalité')
    fig.tight_layout();fig.savefig(OUT/'08_EDA_sources_periodes.png',dpi=160);fig.savefig(OUT/'08_EDA_sources_periodes.pdf');plt.close(fig)
    fig,ax=plt.subplots(figsize=(10,4))
    raw.groupby('label_id')[['URL','HTML','IMAGE','TECH']].mean().T.rename(columns={0:'Bénin',1:'Phishing'}).plot.bar(ax=ax,color=['#4677a8','#d69552'])
    ax.set(ylabel='Fraction exploitable',ylim=(0,1.08),title='Disponibilité réelle des modalités — corpus brut');fig.tight_layout();fig.savefig(OUT/'09_disponibilite_modalites.png',dpi=160);fig.savefig(OUT/'09_disponibilite_modalites.pdf');plt.close(fig)
    m=table.loc[['M1','M2']];fig,ax=plt.subplots(figsize=(8,4));x=np.arange(2)
    ax.bar(x-.17,m.FP,width=.34,label='Faux positifs',color='#4677a8');ax.bar(x+.17,m.FN,width=.34,label='Phishing manqués',color='#d69552')
    ax.set(xticks=x,xticklabels=['M1 tardive','M2 embeddings'],ylabel='Scans',title='Même cohorte, seuils primary figés sur calibration');ax.legend();fig.tight_layout();fig.savefig(OUT/'10_compromis_comptages.png',dpi=160);fig.savefig(OUT/'10_compromis_comptages.pdf');plt.close(fig)
    source_table=pd.crosstab(raw.source_name,raw.label_id).to_numpy(float)
    expected=source_table.sum(1)[:,None]*source_table.sum(0)[None,:]/source_table.sum()
    cramerv=float(np.sqrt((((source_table-expected)**2/expected).sum()/source_table.sum())/min(source_table.shape[0]-1,source_table.shape[1]-1)))
    summary=dict(raw_n=len(raw),class_counts=raw.label_id.value_counts().sort_index().to_dict(),source_cramer_v=cramerv,complete_all=int(raw[['URL','HTML','IMAGE','TECH']].all(axis=1).sum()),negative_duration_n=int(raw.negative_duration.sum()),date_min=str(raw.scan_created_at.min()),date_max=str(raw.scan_created_at.max()),splits_checked=len(checks),cases=len(cases),case_sampling='First five sorted IDs per central fusion and error type; illustrative, not random or representative',modalities_by_class=raw.groupby('label_id')[['URL','HTML','IMAGE','TECH']].sum().to_dict(),url_length_by_class=raw.groupby('label_id').url_characters.describe().to_dict())
    write(OUT/'EDA_summary.json',summary)
    for source in (ROOT/'reports/figures').glob('*'):
        if source.is_file():
            import shutil;shutil.copy2(source,OUT/source.name)
    print(json.dumps(summary,ensure_ascii=False))

if __name__=='__main__':main()
