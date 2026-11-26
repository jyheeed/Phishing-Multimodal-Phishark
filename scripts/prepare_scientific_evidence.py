"""Recompute report facts from stored predictions; never fit or change a model."""
from pathlib import Path
import ast,json,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.runtime'))
import numpy as np
import pandas as pd
from sklearn.metrics import average_precision_score,roc_auc_score,confusion_matrix

RUN=ROOT/'artifacts/runs/full_experiment/grouped/77162f55317be0844ec3'
OUT=ROOT/'reports/FIGURES_ET_RESULTATS'
PRIVATE=ROOT/'artifacts/scientific_writing'

def read(p):return json.loads(Path(p).read_text(encoding='utf8'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def write(p,v):p.write_text(json.dumps(v,indent=2,ensure_ascii=False,default=str),encoding='utf8')

def main():
    PRIVATE.mkdir(parents=True,exist_ok=True);OUT.mkdir(parents=True,exist_ok=True)
    backup=PRIVATE/'before_scientific_revision';backup.mkdir(exist_ok=True)
    for rel in ('reports/PHISHARK2026_RAPPORT_FINAL.md','reports/PHISHARK2026_RAPPORT_FINAL.pdf','presentation/QUESTIONS_JURY.md'):
        source=ROOT/rel;target=backup/source.name
        if source.exists() and not target.exists():shutil.copy2(source,target)
    protected={name:sha(ROOT/name) for name in read(ROOT/'artifacts/finalization/preserved_run_hashes.json')}
    protected['notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb']=sha(ROOT/'notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb')
    write(PRIVATE/'protected_before.json',protected)
    table=pd.read_csv(ROOT/'artifacts/published/table_28_common.csv',float_precision='round_trip')
    # Each configuration is checked against its own unrounded probabilities and common IDs.
    common=pd.read_csv(ROOT/'artifacts/finalization/common_cohort_ids.csv',dtype=str)
    ids=set(common.scan_id)
    central=pd.read_csv(RUN/'predictions.csv',dtype={'scan_id':str},float_precision='round_trip')
    extra=pd.read_csv(RUN/'combinations/predictions.csv',dtype={'scan_id':str},float_precision='round_trip')
    extra['split']='test'  # This ledger contains only the frozen test predictions.
    ledger=pd.concat([central,extra],ignore_index=True)
    rows=[]
    for row in table.to_dict('records'):
        q=ledger.loc[ledger.split.eq('test') & ledger.model.eq(row['model']) & ledger.scan_id.isin(ids)].copy()
        assert q.scan_id.is_unique and set(q.scan_id)==ids,(row['model'],len(q),len(ids),q.scan_id.nunique())
        y=q.label_id.to_numpy();p=q.probability.to_numpy();decision=p>=row['threshold']
        tn,fp,fn,tp=confusion_matrix(y,decision,labels=[0,1]).ravel()
        metrics=dict(AP=average_precision_score(y,p),ROC_AUC=roc_auc_score(y,p),precision=tp/(tp+fp),recall=tp/(tp+fn),F1=2*tp/(2*tp+fp+fn),FPR=fp/(fp+tn),FNR=fn/(fn+tp),TN=int(tn),FP=int(fp),FN=int(fn),TP=int(tp))
        for key,value in metrics.items():assert np.isclose(value,row[key],rtol=0,atol=1e-10),(row['model'],key)
        rows.append(dict(model=row['model'],verified=True,n=len(q),**metrics))
    pd.DataFrame(rows).to_csv(OUT/'verification_28.csv',index=False)
    for name in ('table_28_common.csv','six_models_full_test.csv','table_22_available.csv','paired_modality_contributions.csv','operating_points_frozen.csv','benchmark_summary.csv','error_strata.csv'):
        shutil.copy2(ROOT/'artifacts/published'/name,OUT/name)
    prep=read(RUN/'preparation.json')
    # The current canonical cache and saved split are the private sources for aggregate EDA.
    cache=ROOT/'data/processed/aea0809c7521684e3b49/canonical.parquet'
    import pyarrow.parquet as pq
    frame=pd.read_parquet(cache,columns=[name for name in pq.ParquetFile(cache).schema_arrow.names if name!='html_text'])
    manifest=pd.read_parquet(ROOT/prep['split_relpath'])
    write(PRIVATE/'column_names.json',dict(canonical=list(frame.columns),split=list(manifest.columns)))
    # Derive all publication metadata from real code rather than an older model mirror.
    notebook=read(ROOT/'notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb')
    nodes=[n for c in notebook['cells'] if c['cell_type']=='code' for n in ast.walk(ast.parse(''.join(c['source'])))]
    definitions=next(ast.literal_eval(n.value) for n in nodes if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='DEFINITIONS' for t in n.targets))
    pd.DataFrame(definitions,columns=['json_file','field','operation']).to_csv(OUT/'dictionnaire_21_features.csv',index=False)
    selected=('Settings','SequenceCNN','ScreenshotCNN','DenseClassifier','architecture','fit_model','fit_fusion','fit_preprocessing','connected_groups','construct_partitions','calibrate','VisibleText','url_model_text','fit_combo_head')
    code={n.name:ast.unparse(n) for n in nodes if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in selected}
    write(PRIVATE/'implemented_definitions.json',code)
    write(PRIVATE/'metrics_check.json',dict(status='PASS',models=28,n=len(ids),protected_files=len(protected),fit_called=False))
    print('Verified all 28 configurations on',len(ids),'common IDs. Columns:',','.join(frame.columns))

if __name__=='__main__':main()
