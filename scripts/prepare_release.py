"""Create a compact reproducible release, without publishing raw scans or private ledgers."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'artifacts/runs/full_experiment/grouped/77162f55317be0844ec3'


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(2**20),b''):h.update(block)
    return h.hexdigest()


def write(path,value):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2),encoding='utf-8')


def main():
    model_dir=ROOT/'models';model_dir.mkdir(exist_ok=True)
    frozen=read(RUN/'frozen.json');combo=read(RUN/'combinations/frozen.json');prep=read(RUN/'preparation.json')
    names=list(frozen['artifacts'])+['frozen.json']
    names+=['combinations/frozen.json']
    names += ['combinations/'+p for p in combo['artifacts'] if p.endswith('.joblib')]
    names += [model+'/complete.json' for model in ('U1','U2','U3','U4','M2')]
    for name in names:
        target=model_dir/name;target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(RUN/name,target)
    write(model_dir/'preparation.json',dict(code=prep['code'],settings=prep['settings'],version=prep['version']))
    model_files=names+['preparation.json']
    write(model_dir/'manifest.json',dict(schema=1,trained_code=prep['code'],training_run=prep['version'],
        purpose='Frozen inference bundle; no optimizer, raw data, prediction ledgers or embedding datasets',
        files={name:sha(model_dir/name) for name in model_files}))
    public=ROOT/'artifacts/published';public.mkdir(parents=True,exist_ok=True)
    files=['table_28_common.csv','table_28_common.json','six_models_full_test.csv','table_22_available.csv',
        'paired_modality_contributions.csv','operating_points_frozen.csv','benchmark_summary.csv','error_strata.csv',
        'analysis_summary.json','bootstrap_scope.json','temporal_feasibility.json']
    for name in files:shutil.copy2(ROOT/'artifacts/finalization'/name,public/name)
    # Demonstration scores are real; replace only the input identifier, never scores or labels.
    import csv
    with (ROOT/'artifacts/finalization/demo_predictions.csv').open(encoding='utf-8',newline='') as f:
        reader=csv.DictReader(f);columns=reader.fieldnames;rows=list(reader)
    for row in rows:row['scan_id']='historical_demo_001'
    with (public/'demo_predictions.csv').open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=columns);writer.writeheader();writer.writerows(rows)
    files.append('demo_predictions.csv')
    spark=read(ROOT/'artifacts/finalization/bd3/status.json')
    resources={k:v for k,v in spark['resources'].items() if k in ('total_ram_gb','available_ram_gb','free_disk_gb','cpu_count')}
    write(public/'spark_status.json',dict(status=spark['status'],reason=spark.get('reason'),resources=resources,
        planned=spark['planned'],measured_spark_times=spark['measured_spark_times']))
    files.append('spark_status.json')
    write(public/'manifest.json',dict(schema=1,trained_code=prep['code'],training_run=prep['version'],
        scope='Verified aggregate results and anonymized demonstration scores; no raw captures or per-scan URLs',
        files={name:sha(public/name) for name in files}))
    # Keep the exact computational source behind existing weights, without another executable notebook.
    original=read(ROOT/'artifacts/provenance/executed_full_code.json')
    cells=[dict(cell_type=c['cell_type'],source=c['source']) for c in original['cells']]
    write(ROOT/'artifacts/provenance/executed_full_code.json',dict(cells=cells,code_sha256=prep['code'],
        scope='Read-only source provenance of trained weights; not a second notebook to execute'))
    print('Release prepared:',len(model_files),'model files,',len(files),'published evidence files')


if __name__=='__main__':main()
