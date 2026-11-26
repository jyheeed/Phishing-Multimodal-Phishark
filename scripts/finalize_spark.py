"""Independent lightweight Spark/pandas benchmark; imports no torch or model code."""
import ast
import hashlib
import json
import os
from pathlib import Path
import shutil
import sys
import threading
import time
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.runtime'))
import psutil
OUT=ROOT/'artifacts/finalization/bd3'
OUT.mkdir(parents=True,exist_ok=True)
RUN=ROOT/'artifacts/runs/full_experiment/grouped/77162f55317be0844ec3'


def save(path,data):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    Path(path).write_text(json.dumps(data,indent=2,ensure_ascii=False,default=str),encoding='utf-8')


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda:stream.read(2**20),b''):h.update(block)
    return h.hexdigest()


def main():
    processes=[]
    for process in psutil.process_iter(['pid','name','cmdline','memory_info']):
        try:
            if (process.info['name'] or '').lower() in ('python.exe','pythonw.exe','java.exe'):
                processes.append(dict(pid=process.pid,rss_bytes=process.info['memory_info'].rss,command=process.info['cmdline']))
        except psutil.Error:pass
    resources=dict(total_ram_gb=psutil.virtual_memory().total/1e9,available_ram_gb=psutil.virtual_memory().available/1e9,
        free_disk_gb=shutil.disk_usage(ROOT).free/1e9,java=shutil.which('java'),cpu_count=psutil.cpu_count(),processes=processes)
    # 512 MiB heap is not the whole JVM footprint. Reserve room for Python, metadata and OS.
    planned=dict(master='local[1]',driver_memory='512m',executor_memory='512m',shuffle_partitions=2,
        spark_ui=False,minimum_available_ram_gb=2,compression='snappy',repetitions=3,
        fractions=[.10,.25,.50,1.0],scenarios=['A_unpartitioned','B_partitioned'],torch_imported='torch' in sys.modules)
    if resources['available_ram_gb']<2 or resources['free_disk_gb']<1:
        result=dict(status='BLOCKED_RESOURCE',reason='Separate-process resource check failed; JVM was not started',
            resources=resources,planned=planned,measured_spark_times=False,
            remedy='Close unused applications/kernels and obtain >=2 GB genuinely available RAM plus >=1 GB disk. Existing pandas measurements preserved.')
        save(OUT/'status.json',result);print(json.dumps(result,ensure_ascii=False,indent=2));return
    import numpy as np
    import pandas as pd
    import pyarrow as pa
    from pyspark.sql import SparkSession
    prep=read(RUN/'preparation.json');p=ROOT/'data/processed'/prep['extraction']['version'][:20]/'canonical.parquet'
    features=read(RUN/'preprocess.json')['features']
    raw=pd.read_parquet(p,columns=['scan_id','label_id',*features])
    manifest=pd.read_parquet(ROOT/prep['split_relpath'])
    frame=raw.merge(manifest,on=['scan_id','label_id'],validate='one_to_one')
    frozen_path=ROOT/'artifacts/provenance/executed_full_code.json'
    notebook=read(frozen_path if frozen_path.exists() else ROOT/'notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb')
    names={'spark_schema','canonical_benchmark_table','validate_benchmark_table','write_pandas_dataset','BenchmarkMemory','measure_parquet_case'}
    env=dict(np=np,pd=pd,pa=pa,psutil=psutil,Path=Path,threading=threading,time=time,os=os,
        FEATURES=features,source_signature=lambda:sha(Path(__file__)),save_json=save,load_json=read,file_hash=sha,
        digest=lambda value:hashlib.sha256(json.dumps(value,sort_keys=True,default=str).encode()).hexdigest())
    for cell in notebook['cells']:
        if cell['cell_type']!='code':continue
        tree=ast.parse(''.join(cell['source']))
        for node in tree.body:
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in names:
                exec(compile(ast.Module(body=[node],type_ignores=[]),'frozen_benchmark','exec'),env)
    context=dict(run=OUT,settings=SimpleNamespace(threads=1,benchmark_repeats=3,mode='FULL_EXPERIMENT'),provenance={'version':prep['version']})
    records=[];spark=None;startup=None
    try:
        start=time.perf_counter()
        spark=(SparkSession.builder.master('local[1]').appName('PhiSharkFinalBenchmark')
            .config('spark.ui.enabled','false').config('spark.driver.memory','512m')
            .config('spark.executor.memory','512m').config('spark.sql.shuffle.partitions','2')
            .config('spark.default.parallelism','1').getOrCreate())
        startup=time.perf_counter()-start
        for fraction in planned['fractions']:
            subset=frame.iloc[:max(1,int(len(frame)*fraction))]
            for rep in range(3):
                for scenario in planned['scenarios']:
                    for engine in ('pandas_pyarrow','spark_local'):
                        result=env['measure_parquet_case'](context,subset,scenario,engine,rep,fraction,spark)
                        records.append(result);pd.DataFrame(records).to_csv(OUT/'measurements.csv',index=False)
                        print(engine,scenario,len(subset),rep,result['seconds'],flush=True)
        status='PASS'
    except Exception as error:
        status='FAIL';records.append(dict(engine='spark_local',status='FAIL',reason=type(error).__name__+':'+str(error)[:1000]))
        pd.DataFrame(records).to_csv(OUT/'measurements.csv',index=False)
    finally:
        if spark is not None:spark.stop()
    save(OUT/'status.json',dict(status=status,resources=resources,planned=planned,spark_startup_seconds=startup,
        startup_included_in_measurements=False,measured_spark_times=any(r.get('engine')=='spark_local' and r.get('status')=='MEASURED' for r in records),
        multinode=False,logical_equivalence='Same canonical schema, rows, casts, validation, Snappy and exact readback in both engines'))


if __name__=='__main__':main()
