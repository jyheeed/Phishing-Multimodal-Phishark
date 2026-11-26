"""Finalize current FULL evidence without fitting any model or changing thresholds."""
import ast
import csv
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'.runtime'))
import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import pyarrow.compute as pc
from sklearn.metrics import average_precision_score, roc_auc_score, confusion_matrix, precision_recall_curve
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

RUN = ROOT/'artifacts/runs/full_experiment/grouped/77162f55317be0844ec3'
OUT = ROOT/'artifacts/finalization'
FIG = ROOT/'reports/figures'
CENTRAL = ('U1','U2','U3','U4','M1','M2')
MODALITIES = ('URL','HTML','IMAGE','TECH')
LABELS = dict(U1='CNN URL', U2='CNN HTML', U3='CNN image', U4='MLP technique', M1='M1 · moyenne', M2='M2 · embeddings')
COLORS = ['#4677a8','#24a79b','#d69552','#8078bb','#14a09a','#17375e']


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def write(path, value):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(json.dumps(value, ensure_ascii=False, indent=2, default=str), encoding='utf-8')


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for b in iter(lambda:stream.read(2**20),b''): h.update(b)
    return h.hexdigest()


def frame(path):
    return pd.read_csv(path, float_precision='round_trip', dtype={'scan_id':str})


def markdown(data):
    def fmt(v):
        if v is None or (isinstance(v,(float,np.floating)) and not np.isfinite(v)): return '—'
        return (f'{v:.4f}' if isinstance(v,(float,np.floating)) else str(v)).replace('|','/')
    return '\n'.join(['| '+' | '.join(data.columns)+' |','| '+' | '.join(['---']*len(data.columns))+' |']+
                     ['| '+' | '.join(fmt(v) for v in row)+' |' for row in data.itertuples(index=False,name=None)])


def metrics(y,p,t):
    tn,fp,fn,tp=map(int,confusion_matrix(y,p>=t,labels=[0,1]).ravel())
    return dict(n=len(y),prevalence=float(np.mean(y)),AP=float(average_precision_score(y,p)),
                ROC_AUC=float(roc_auc_score(y,p)),precision=tp/(tp+fp) if tp+fp else 0.,
                recall=tp/(tp+fn),F1=2*tp/(2*tp+fp+fn),FPR=fp/(tn+fp),FNR=fn/(tp+fn),
                TN=tn,FP=fp,FN=fn,TP=tp,threshold=t)


def savefig(fig,name):
    fig.savefig(FIG/(name+'.png'),dpi=220,bbox_inches='tight',facecolor='white')
    fig.savefig(FIG/(name+'.pdf'),bbox_inches='tight')
    plt.close(fig)


def main():
    start=time.perf_counter(); OUT.mkdir(parents=True,exist_ok=True); FIG.mkdir(parents=True,exist_ok=True)
    (ROOT/'reports').mkdir(exist_ok=True)
    inventory=[]; preserved={}
    required=['comparison.csv','predictions.csv','combinations/metrics.csv','combinations/all_28_comparable_models.csv',
              'combinations/predictions.csv','combinations/calibration_policies.csv','AP_intervals.csv',
              'bd2/measurements.csv','bd2/scope.json','PROJECT_FINAL_CRISP_DM.md','preparation.json','preprocess.json',
              'frozen.json','combinations/frozen.json','evaluation.json','combinations/study.json',
              'figures/precision_recall.png','figures/confusion.png','figures/learning.png']
    required += [f'{model}/{name}' for model in ('U1','U2','U3','U4','M2') for name in ('best.pt','complete.json','history.csv')]
    required += [p.relative_to(RUN).as_posix() for p in (RUN/'feature_audit').glob('*.csv')]
    for name in required:
        p=RUN/name
        row=dict(path=str(p.relative_to(ROOT)),status='PASS' if p.is_file() else 'NOT_AVAILABLE')
        if p.is_file():
            row.update(bytes=p.stat().st_size,sha256=sha(p));preserved[row['path']]=row['sha256']
            if p.suffix=='.csv':
                with p.open(encoding='utf-8-sig',newline='') as stream:
                    reader=csv.reader(stream);row['columns']=','.join(next(reader))
        inventory.append(row)
    pd.DataFrame(inventory).to_csv(OUT/'artifact_inventory.csv',index=False)
    assert all(r['status']=='PASS' for r in inventory),'Required artifacts missing'
    for manifest,base,key in [('frozen.json',RUN,'artifacts'),('evaluation.json',RUN,'files'),
            ('combinations/frozen.json',RUN/'combinations','artifacts'),('combinations/study.json',RUN/'combinations','files')]:
        for name,expected in read(RUN/manifest)[key].items(): assert sha(base/name)==expected,(manifest,name)
    prep=read(RUN/'preparation.json'); frozen=read(RUN/'frozen.json'); combo=read(RUN/'combinations/frozen.json')
    assert prep['code']==frozen['code'] and prep['split_sha256']==sha(ROOT/prep['split_relpath'])
    for model in ('U1','U2','U3','U4','M2'):
        assert read(RUN/model/'complete.json')['sha256']==sha(RUN/model/'best.pt')
    canonical=ROOT/'data/processed'/prep['extraction']['version'][:20]/'canonical.parquet'
    assert sha(canonical)==prep['extraction']['canonical_sha256']
    split=pd.read_parquet(ROOT/prep['split_relpath']);assert split.scan_id.is_unique
    metadata_cols=['scan_id','label_id','source_name','provider','http_status','scan_created_at','site_id','normalized_url',
        'url_input_hash','html_input_hash','raw_html_hash','image_input_hash','html_state','image_state','uniform',
        'quality_state','primary_eligible','target_url','capture_errors','negative_duration']
    available=pq.ParquetFile(canonical).schema_arrow.names
    metadata_cols=[name for name in metadata_cols if name in available]
    raw=pd.read_parquet(canonical,columns=metadata_cols)
    eligible=raw.loc[raw.primary_eligible].merge(split,on=['scan_id','label_id'],validate='one_to_one')
    for name in ['group_id','site_id','normalized_url','url_input_hash','html_input_hash','raw_html_hash','image_input_hash','encoding_component']:
        if name not in eligible:continue
        selected=eligible.loc[eligible[name].notna() & eligible[name].ne('')]
        assert not selected.groupby(name).split.nunique().gt(1).any(),name
    source_csv=ROOT/'data/raw/phishark2026_public_metadata.csv'
    public=pd.read_csv(source_csv,low_memory=False)
    assert sha(source_csv)==prep['extraction']['binding']['metadata_sha256']
    labels=public.set_index('scan_id').label_id
    assert raw.set_index('scan_id').label_id.eq(labels.loc[raw.scan_id].set_axis(raw.scan_id)).all()
    # Derive complete-case cohort independently from captured inputs, without loading all HTML into Python.
    feature_names=read(RUN/'preprocess.json')['features'];mask_rows=[]
    cols=['scan_id','target_url','html_text','html_state','image_state',*feature_names]
    for batch in pq.ParquetFile(canonical).iter_batches(batch_size=2048,columns=cols):
        table=batch.to_pydict()
        tech=np.column_stack([np.asarray(table[name],float) for name in feature_names])
        mask=np.column_stack(([len(v or '')>0 for v in table['target_url']],
            [state in ('ok','truncated') and len(v or '')>0 for state,v in zip(table['html_state'],table['html_text'])],
            [state=='ok' for state in table['image_state']],np.isfinite(tech).any(axis=1)))
        mask_rows.extend(zip(table['scan_id'],mask.all(axis=1)))
    complete_map=dict(mask_rows)
    test=split.loc[split.split.eq('test')].sort_values('scan_id').reset_index(drop=True)
    common=test.loc[test.scan_id.map(complete_map)].copy().reset_index(drop=True)
    y=common.label_id.to_numpy();ids=common.scan_id.tolist();full_ids=test.scan_id.tolist()
    common[['scan_id','label_id','group_id']].to_csv(OUT/'common_cohort_ids.csv',index=False)
    central=frame(RUN/'predictions.csv');central_test=central.loc[central.split.eq('test')].copy()
    additional=frame(RUN/'combinations/predictions.csv');policies={r['model']:r for r in combo['policies']}
    scores={};thresholds={};rows=[];full_rows=[]
    stored=frame(RUN/'combinations/all_28_comparable_models.csv').set_index('model')
    for name in [*CENTRAL,*policies]:
        selected=(central_test if name in CENTRAL else additional).loc[lambda d:d.model.eq(name)].set_index('scan_id')
        assert selected.index.is_unique and set(selected.index)==set(full_ids),name
        selected=selected.loc[full_ids]
        assert np.array_equal(selected.label_id,test.label_id),name
        if name not in CENTRAL:
            observed=set(selected.loc[selected.complete_case,'scan_id']) if 'scan_id' in selected else set(selected.index[selected.complete_case])
            assert observed==set(ids)
            assert selected.loc[~selected.eligible,'probability'].isna().all()
        t=frozen['policies'][name]['primary'] if name in CENTRAL else policies[name]['threshold']
        assert t is not None
        thresholds[name]=t;scores[name]=selected.loc[ids,'probability'].to_numpy()
        assert np.isfinite(scores[name]).all()
        if name in CENTRAL:
            modality=MODALITIES[CENTRAL.index(name)] if name.startswith('U') else '+'.join(MODALITIES)
            method='UNIMODAL' if name.startswith('U') else 'LATE' if name=='M1' else 'MLP_EMBED'
        else:modality=policies[name]['modalities'];method=policies[name]['method']
        values=metrics(y,scores[name],t)
        for key in ['n','AP','ROC_AUC','precision','recall','F1','FPR','FNR','FP','FN','TN','TP']:
            assert np.isclose(values[key],stored.loc[name,key],rtol=0,atol=1e-8),(name,key,values[key],stored.loc[name,key])
        rows.append(dict(model=name,modalities=modality,fusion=method,modality_count=len(modality.split('+')),
                         coverage=len(common)/len(test),**values))
        if name in CENTRAL:
            values=metrics(test.label_id.to_numpy(),selected.probability.to_numpy(),t)
            full_rows.append(dict(model=name,coverage=1.,**values))
    main_table=pd.DataFrame(rows);main_table.to_csv(OUT/'table_28_common.csv',index=False)
    main_table.to_json(OUT/'table_28_common.json',orient='records',force_ascii=False,indent=2)
    pd.DataFrame(full_rows).to_csv(OUT/'six_models_full_test.csv',index=False)
    own=frame(RUN/'combinations/metrics.csv');own.loc[own.cohort.eq('available')].to_csv(OUT/'table_22_available.csv',index=False)
    # Independently recompute own-cohort metrics, including abstentions and calibration thresholds.
    for name,item in policies.items():
        selected=additional.loc[additional.model.eq(name)].set_index('scan_id').loc[full_ids]
        keep=selected.eligible.to_numpy(bool)&selected.probability.notna().to_numpy()
        values=metrics(selected.label_id.to_numpy()[keep],selected.probability.to_numpy()[keep],item['threshold'])
        old=own.loc[own.model.eq(name)&own.cohort.eq('available')].iloc[0]
        for key in ['n','AP','F1','FPR','FNR','FP','FN']:assert np.isclose(values[key],old[key],rtol=0,atol=1e-8),(name,key)
    print('All 28 common-cohort and 22 available-cohort metrics verified',flush=True)
    # Efficient paired site/content-group bootstrap. Ranking is fixed; multiplicities are sampled by group.
    names=list(scores);group_ids,inverse=np.unique(common.group_id,return_inverse=True);rng=np.random.default_rng(42)
    ranking={}
    for name,p in scores.items():
        order=np.argsort(-p,kind='stable');ends=np.r_[np.flatnonzero(np.diff(p[order])),len(p)-1]
        ranking[name]=(order,ends)
    boot=np.full((200,len(names)),np.nan)
    for repetition in range(200):
        weight=np.bincount(rng.integers(0,len(group_ids),len(group_ids)),minlength=len(group_ids))[inverse]
        positives=float(np.dot(weight,y))
        if positives==0 or np.dot(weight,1-y)==0:continue
        for j,name in enumerate(names):
            order,ends=ranking[name];tp=np.cumsum(weight[order]*y[order])[ends];total=np.cumsum(weight[order])[ends]
            precision=np.divide(tp,total,out=np.zeros_like(tp,dtype=float),where=total>0)
            boot[repetition,j]=np.dot(np.diff(np.r_[0.,tp])/positives,precision)
    index=main_table.set_index('model');pairs=[]
    requests=[(fusion,u,None) for fusion in ('M1','M2') for u in CENTRAL[:4]]+[('M2','M1',None)]
    from itertools import combinations
    for method in ('LATE','LINEAR_EMBED'):
        for count in (2,3,4):
            for choice in combinations(MODALITIES,count):
                target=method+'__'+'+'.join(choice)
                for added in choice:
                    reduced=tuple(v for v in choice if v!=added)
                    baseline='U'+str(MODALITIES.index(reduced[0])+1) if len(reduced)==1 else method+'__'+'+'.join(reduced)
                    requests.append((target,baseline,added))
    for a,b,added in requests:
        difference=boot[:,names.index(a)]-boot[:,names.index(b)];valid=difference[np.isfinite(difference)]
        lo,hi=np.quantile(valid,[.025,.975])
        pairs.append(dict(model=a,reference=b,added_modality=added,AP_difference=index.loc[a,'AP']-index.loc[b,'AP'],
            lower95=lo,upper95=hi,valid_replicates=len(valid),unit='connected_site_content_group',cohort_n=len(common),
            multiple_comparisons_corrected=False,interpretation='exploratory_internal'))
    paired=pd.DataFrame(pairs);paired.to_csv(OUT/'paired_modality_contributions.csv',index=False)
    write(OUT/'bootstrap_scope.json',dict(repetitions=200,seed=42,groups=len(group_ids),cohort_n=len(common),paired=True,
        unit='original_connected_site_content_group',selection_on_test=False,multiplicity_adjusted=False))
    # Frozen operating points only; no new threshold is selected from the test.
    operating=[]
    for name in names:
        policies_for_name=frozen['policies'][name] if name in CENTRAL else dict(primary=policies[name]['threshold'],recall85=policies[name]['threshold_recall85'])
        for policy,t in policies_for_name.items():
            if t is not None:operating.append(dict(model=name,policy=policy,threshold_origin='calibration',cohort='common',**metrics(y,scores[name],t)))
    pd.DataFrame(operating).to_csv(OUT/'operating_points_frozen.csv',index=False)
    # Errors on full test for central models: denominators by class retained for every stratum.
    context=raw.set_index('scan_id').loc[full_ids].reset_index();context['month']=pd.to_datetime(context.scan_created_at,utc=True,format='mixed').dt.strftime('%Y-%m')
    error_rows=[];examples=[]
    for model in CENTRAL:
        part=central_test.loc[central_test.model.eq(model)].set_index('scan_id').loc[full_ids].reset_index()
        part=part.merge(context.drop(columns='label_id'),on='scan_id',validate='one_to_one')
        part['prediction']=part.probability.ge(thresholds[model]).astype(int)
        part['error']=np.where(part.label_id.eq(0)&part.prediction.eq(1),'FP',np.where(part.label_id.eq(1)&part.prediction.eq(0),'FN','correct'))
        for dim in ('provider','http_status','source_name','month','html_state','image_state','uniform','quality_state'):
            for value,sub in part.groupby(dim,dropna=False):
                negatives=int(sub.label_id.eq(0).sum());positives=int(sub.label_id.eq(1).sum())
                fp=int(sub.error.eq('FP').sum());fn=int(sub.error.eq('FN').sum())
                error_rows.append(dict(model=model,dimension=dim,value=str(value),n=len(sub),benign=negatives,phishing=positives,
                    FP=fp,FN=fn,FPR=fp/negatives if negatives else None,FNR=fn/positives if positives else None))
        for error in ('FP','FN'):
            chosen=part.loc[part.error.eq(error)].sort_values(['probability','scan_id'],ascending=[error=='FN',True]).head(4)
            for row in chosen.to_dict('records'):
                examples.append({k:row.get(k) for k in ['scan_id','label_id','model','probability','error','provider','http_status','scan_created_at','source_name','html_state','image_state','uniform','quality_state','target_url']})
    pd.DataFrame(error_rows).to_csv(OUT/'error_strata.csv',index=False)
    queue=pd.DataFrame(examples);queue['review_status']='PENDING_HUMAN';queue['label_changed']=False;queue.to_csv(OUT/'manual_error_review_queue.csv',index=False)
    # Temporal feasibility replay: same raw-date quantiles and same raw identity components, no model fitting.
    original_path=ROOT/'artifacts/provenance/executed_full_code.json'
    if not original_path.exists():original_path=ROOT/'notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb'
    original=json.loads(original_path.read_text(encoding='utf-8'))
    env={'np':np,'pd':pd}
    for cell in original['cells']:
        s=''.join(cell.get('source',[]))
        if s.startswith('IDENTITY_KEYS =') or s.startswith('def connected_groups('):exec(s,env)
    source=raw.loc[raw.primary_eligible].copy();source['group_id']=env['connected_groups'](source)
    dates=pd.to_datetime(source.scan_created_at,format='mixed',utc=True);edges=[dates.quantile(float(q)) for q in np.cumsum(prep['settings']['split_fractions'])[:-1]]
    roles=('train_encoder','train_fusion','validation','calibration','test')
    source['role']=[roles[int(np.searchsorted(edges,date,side='right'))] for date in dates]
    crossing=source.groupby('group_id').role.nunique().gt(1);source['purged']=source.group_id.isin(crossing.index[crossing])
    source.groupby(['role','purged','label_id']).size().reset_index(name='n').to_csv(OUT/'temporal_class_counts_before_after_purge.csv',index=False)
    for period in ('D','M'):
        public.assign(period=pd.to_datetime(public.scan_created_at,format='mixed',utc=True).dt.strftime('%Y-%m-%d' if period=='D' else '%Y-%m')).groupby(['period','label_id','source_name']).size().reset_index(name='n').to_csv(OUT/f'temporal_distribution_{period}.csv',index=False)
    kept=source.loc[~source.purged];feasibility={role:kept.loc[kept.role.eq(role)].label_id.value_counts().to_dict() for role in roles}
    write(OUT/'temporal_feasibility.json',dict(status='NOT_FEASIBLE' if any(len(v)!=2 for v in feasibility.values()) else 'FEASIBLE',
        boundaries_utc=list(map(str,edges)),counts=feasibility,purged=int(source.purged.sum()),original_status=read(ROOT/'artifacts/temporal_full_experiment.json'),
        date_modified=False,labels_modified=False,networks_fitted=False))
    # Five publication-ready main figures; every model figure uses the verified same cohort.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':11,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(9.5,4.8));values=index.loc[list(CENTRAL),'AP'];ax.bar([LABELS[n] for n in CENTRAL],values,color=COLORS)
    ax.set(ylim=(0,1.06),ylabel='Average precision (AP)',title=f'Comparaison centrale · mêmes {len(common):,} scans complets'.replace(',',' '))
    ax.axhline(y.mean(),ls='--',color='#9ca3af',label=f'Prévalence phishing : {y.mean():.3f}');ax.legend(fontsize=9)
    for i,v in enumerate(values):ax.text(i,v+.015,f'{v:.3f}',ha='center')
    savefig(fig,'01_modeles_AP')
    heat=main_table.loc[main_table.model.str.contains('__')].pivot(index='modalities',columns='fusion',values='AP').reindex(columns=['LATE','LINEAR_EMBED'])
    fig,ax=plt.subplots(figsize=(8.5,8));im=ax.imshow(heat.values,cmap='YlGnBu',vmin=.5,vmax=1,aspect='auto');ax.set_xticks([0,1],['Moyenne des probabilités','Embeddings + logistique']);ax.set_yticks(range(len(heat)),heat.index)
    for i in range(len(heat)):
        for j in range(2):ax.text(j,i,f'{heat.iloc[i,j]:.4f}',ha='center',va='center',color='white' if heat.iloc[i,j]>.86 else '#10243c')
    fig.colorbar(im,ax=ax,label='AP');ax.set_title('11 sous-ensembles × 2 fusions · cohorte commune');savefig(fig,'02_combinaisons_heatmap')
    fig,ax=plt.subplots(figsize=(10,6));markers={'UNIMODAL':'s','LATE':'o','MLP_EMBED':'*','LINEAR_EMBED':'^'}
    for method,part in main_table.groupby('fusion'):
        ax.scatter(part.FPR*100,part.recall*100,s=35+part.modality_count*23,marker=markers[method],label=method,alpha=.8,edgecolors='white')
    for name in ['U1','U2','U3','U4','M1','M2','LINEAR_EMBED__URL+HTML+TECH']:
        row=index.loc[name];ax.annotate(name.replace('LINEAR_EMBED__','Linéaire '),(row.FPR*100,row.recall*100),xytext=(6,5),textcoords='offset points',fontsize=8)
    ax.set(xlabel='Faux positifs parmi les bénins — FPR (%)',ylabel='Rappel phishing (%)',title='Détection et fausses alertes · seuils figés sur calibration');ax.grid(alpha=.15);ax.legend(fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.16),ncol=4);savefig(fig,'03_compromis_FPR_rappel')
    fig,ax=plt.subplots(figsize=(10,6));chosen=[*CENTRAL,'LINEAR_EMBED__URL+HTML+TECH','LATE__URL+HTML']
    pr_payload=[]
    for name in chosen:
        precision,recall,_=precision_recall_curve(y,scores[name]);ax.step(recall,precision,where='post',label=f'{name} · AP={index.loc[name,"AP"]:.3f}',lw=1.6)
        positions=np.unique(np.linspace(0,len(recall)-1,150,dtype=int));pr_payload.append(dict(model=name,recall=recall[positions].tolist(),precision=precision[positions].tolist()))
    ax.axhline(y.mean(),ls='--',color='#9ca3af',label=f'Prévalence : {y.mean():.3f}');ax.set(xlabel='Rappel phishing',ylabel='Précision phishing',xlim=(0,1),ylim=(0,1.02),title='Courbes précision–rappel · comparaison interne exploratoire');ax.legend(fontsize=8,ncol=2);savefig(fig,'04_precision_recall')
    fig,axes=plt.subplots(2,3,figsize=(11,7))
    for ax,name in zip(axes.flat,CENTRAL):
        row=index.loc[name];matrix=np.array([[row.TN,row.FP],[row.FN,row.TP]],int);ax.imshow(matrix,cmap='Blues',vmin=0,vmax=max(matrix.ravel()))
        for (i,j),v in np.ndenumerate(matrix):ax.text(j,i,f'{["TN","FP","FN","TP"][2*i+j]}\n{v:,}'.replace(',',' '),ha='center',va='center',color='white' if v>matrix.max()*.6 else '#10243c',fontsize=12)
        ax.set_xticks([0,1],['Prédit bénin','Prédit phishing']);ax.set_yticks([0,1],['Réel bénin','Réel phishing']);ax.set_title(LABELS[name])
    fig.suptitle(f'Matrices de confusion · {len(common):,} scans communs'.replace(',',' '));fig.tight_layout();savefig(fig,'05_confusion_matrices')
    # Measured pandas results and explicit Spark resource status are kept separate.
    pandas=frame(RUN/'bd2/measurements.csv');pandas=pandas.loc[pandas.status.eq('MEASURED')]
    summary=pandas.groupby(['engine','scenario','n'],dropna=False).agg(repetitions=('seconds','size'),seconds_median=('seconds','median'),seconds_min=('seconds','min'),seconds_max=('seconds','max'),
        throughput_median=('scans_per_second','median'),peak_rss_bytes=('peak_process_tree_rss_bytes','max'),input_bytes=('input_bytes','median'),output_bytes=('output_bytes','median'),data_files=('data_files','median')).reset_index()
    summary.to_csv(OUT/'benchmark_summary.csv',index=False)
    benchmark_records=summary.to_dict('records')
    for field,ylabel,name in [('seconds_median','Temps médian mesuré (s)','06_bigdata_temps'),('throughput_median','Débit médian (scans/s)','07_bigdata_debit')]:
        fig,ax=plt.subplots(figsize=(8,4.5))
        for scenario,part in summary.groupby('scenario'):ax.plot(part.n,part[field],marker='o',label='pandas/PyArrow · '+scenario)
        ax.set(xlabel='Nombre de scans',ylabel=ylabel,title='Lecture → validation → cast → Parquet → relecture vérifiée');ax.legend(fontsize=8);ax.grid(alpha=.15);savefig(fig,name)
    # Bind all derived tables and visuals to current-run immutable inputs.
    write(OUT/'preserved_run_hashes.json',preserved)
    model_training=[read(RUN/name/'complete.json') for name in ('U1','U2','U3','U4','M2')]
    summary=dict(run=str(RUN.relative_to(ROOT)),code=prep['code'],raw_rows=prep['raw_rows'],eligible_rows=prep['eligible_rows'],
        quarantined_rows=prep['quarantined_rows'],test_n=len(test),common_n=len(common),coverage=len(common)/len(test),
        common_prevalence=float(y.mean()),test_prevalence=float(test.label_id.mean()),group_count=len(group_ids),
        metrics_verified=28,available_metrics_verified=22,bootstrap_repetitions=200,networks_trained=False,
        label_changes=False,threshold_changes=False,selection_on_test=False,seconds=time.perf_counter()-start,
        training=model_training,class_counts=prep['class_counts'],extraction_seconds=prep['extraction']['seconds'])
    write(OUT/'analysis_summary.json',summary)
    write(OUT/'deck_data.json',dict(summary=summary,models=main_table.to_dict('records'),six_full=full_rows,
        heatmap=dict(rows=heat.index.tolist(),columns=heat.columns.tolist(),values=heat.values.tolist()),
        pr_curves=pr_payload,benchmark=benchmark_records))
    # Report comparisons most useful for oral interpretation, with no winner selected.
    text='# Analyse appariée des modalités\n\nMême cohorte : '+str(len(common))+' scans. 200 bootstraps par groupes ; comparaisons exploratoires, sans correction de multiplicité.\n\n'
    text+=markdown(paired.loc[paired.added_modality.eq('IMAGE')|paired.model.isin(['M1','M2']),['model','reference','AP_difference','lower95','upper95']])
    (ROOT/'reports/ANALYSE_MODALITES.md').write_text(text+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)


if __name__=='__main__':main()
