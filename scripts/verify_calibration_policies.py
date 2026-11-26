"""Recompute frozen policies from saved calibration representations, never refit."""
import ast
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.runtime'))
import numpy as np
import pandas as pd
import joblib
from sklearn.metrics import precision_recall_curve


def main():
    run=ROOT/'artifacts/runs/full_experiment/grouped/77162f55317be0844ec3'
    read=lambda p:json.loads(Path(p).read_text(encoding='utf-8'))
    frozen=read(run/'frozen.json');additional=read(run/'combinations/frozen.json');prep=read(run/'preparation.json')
    manifest=pd.read_parquet(ROOT/prep['split_relpath']).set_index('scan_id')
    env=dict(np=np,precision_recall_curve=precision_recall_curve)
    original=read(ROOT/'artifacts/provenance/executed_full_code.json')
    for cell in original['cells']:
        if cell['cell_type']!='code':continue
        for node in ast.parse(''.join(cell['source'])).body:
            if isinstance(node,ast.FunctionDef) and node.name in ('calibrate','late_fusion','combo_selected'):
                exec(compile(ast.Module(body=[node],type_ignores=[]),'frozen_policy','exec'),env)
    with np.load(run/'combinations/calibration.npz',allow_pickle=False) as a:
        ids=a['ids'].tolist();z=a['z'].copy();p=a['probability'].copy();mask=a['mask'].copy()
    selected=manifest.loc[ids];assert selected.split.eq('calibration').all() and len(ids)==3371
    y=selected.label_id.to_numpy();scores={name:p[:,i] for i,name in enumerate(('U1','U2','U3','U4'))}
    scores['M1']=env['late_fusion'](p,mask)
    # Only deserialize and evaluate the small frozen M2 head, on calibration, with no optimization.
    import torch
    from torch import nn
    env['nn']=nn
    for cell in original['cells']:
        if cell['cell_type']=='code' and ''.join(cell['source']).startswith('class DenseClassifier'):
            exec(''.join(cell['source']),env)
    model=env['DenseClassifier'](132)
    state=torch.load(run/'M2/best.pt',map_location='cpu',weights_only=True)
    assert state['signature']==read(run/'M2/complete.json')['signature']
    model.load_state_dict(state['weights']);model.eval();torch.set_num_threads(2)
    scaling=read(run/'fusion_scaling.json');x=((z-np.asarray(scaling['mean'],np.float32))/np.asarray(scaling['scale'],np.float32)).astype(np.float32)
    with torch.inference_mode():
        scores['M2']=np.concatenate([torch.sigmoid(model(torch.from_numpy(x[i:i+32]))).numpy() for i in range(0,len(x),32)])
    expected={name:policy for name,policy in frozen['policies'].items()}
    for item in additional['policies']:
        values,late,valid=env['combo_selected'](z,p,mask,item['choice'])
        probability=late
        if item['method']=='LINEAR_EMBED':
            head=joblib.load(run/'combinations'/item['checkpoint']);probability=np.full(len(z),np.nan)
            probability[valid]=head.predict_proba(values[valid])[:,1]
        scores[item['model']]=probability
        expected[item['model']]=dict(primary=item['threshold'],recall85=item['threshold_recall85'])
    rows=[]
    for name,probability in scores.items():
        valid=np.isfinite(probability);recomputed=env['calibrate'](y[valid],probability[valid])
        for policy,value in recomputed.items():
            target=expected[name][policy]
            matches=(value is None and target is None) or (value is not None and target is not None and abs(value-target)<=1e-6)
            rows.append(dict(model=name,policy=policy,expected=target,recomputed=value,calibration_n=int(valid.sum()),
                status='PASS' if matches else 'FAIL',tolerance=1e-6,threshold_changed=False,fit_performed=False))
    pd.DataFrame(rows).to_csv(ROOT/'artifacts/finalization/calibration_verification.csv',index=False)
    assert all(r['status']=='PASS' for r in rows)
    print('All 56 frozen thresholds verified from calibration; no fitting, no changes.')


if __name__=='__main__':main()
