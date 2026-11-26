"""Offline-only interface inference from the verified trained FULL checkpoints.

Uses an allowlisted set of inference definitions from the single final notebook.
Never executes a notebook cell, optimizer, fitting function or network request.
"""
import ast
from dataclasses import dataclass
import gzip
import hashlib
from html.parser import HTMLParser
import io
import json
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
import threading
import time
import types
from urllib.parse import urlsplit
import warnings
import zipfile

ROOT=Path(__file__).resolve().parents[1]
RUN=ROOT/'artifacts/runs/full_experiment/grouped/77162f55317be0844ec3'
MANIFEST=ROOT/'artifacts/interface/inference_source_manifest.json'
NOTEBOOK=ROOT/'notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb'
MODEL_IDS=('U1','U2','U3','U4','M1','M2')
NAMES={
    'Settings','VisibleText','visible_text','validate_members','read_archive','finite_nonnegative',
    'normalized_status','extract_numeric','word_tokens','url_model_text','encode','availability',
    'ModalDataset','SequenceCNN','ScreenshotCNN','DenseClassifier','architecture','inference',
    'late_fusion','combo_selected',
}
CONSTANTS={'FEATURE_VERSION','DEFINITIONS','FEATURES','JSON_LIMIT','HTML_LIMIT'}
MAX_UPLOAD_BYTES=32*2**20


def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))


def sha(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(2**20),b''):h.update(b)
    return h.hexdigest()


def definition_nodes(path):
    definitions={};constants=[]
    for cell in read(path)['cells']:
        if cell['cell_type']!='code':continue
        tree=ast.parse(''.join(cell['source']))
        # Only inspect module-level statements or the delivered FULL mode guard.
        statements=tree.body
        if len(statements)==1 and isinstance(statements[0],ast.If) and ast.unparse(statements[0].test)=="MODE == 'FULL_EXPERIMENT'":
            statements=statements[0].body
        for node in statements:
            if isinstance(node,(ast.FunctionDef,ast.ClassDef)) and node.name in NAMES:
                if node.name in definitions:raise ValueError('Duplicate inference definition: '+node.name)
                definitions[node.name]=node
            if isinstance(node,ast.Assign) and all(isinstance(t,ast.Name) and t.id in CONSTANTS for t in node.targets):
                constants.append(node)
    if set(definitions)!=NAMES:raise ValueError('Missing inference definitions in the final notebook')
    return definitions,constants


def fingerprints(definitions,constants):
    result={name:hashlib.sha256(ast.dump(node,include_attributes=False).encode()).hexdigest() for name,node in definitions.items()}
    result['constants']=hashlib.sha256('\n'.join(ast.dump(n,include_attributes=False) for n in constants).encode()).hexdigest()
    return result


def validate_url(value):
    text=str(value or '').strip()
    if not text or len(text)>8192 or any(c.isspace() for c in text):
        raise ValueError('Saisis une URL valide, sans espace, de moins de 8 192 caractères.')
    parsed=urlsplit(text if '://' in text else 'https://'+text)
    if parsed.scheme not in ('http','https') or not parsed.hostname:
        raise ValueError('Seules les adresses HTTP ou HTTPS sont acceptées.')
    try:_=parsed.port
    except ValueError:raise ValueError('Le port indiqué dans l’URL est invalide.') from None
    return text


def project_results():
    import pandas as pd
    return pd.read_csv(ROOT/'artifacts/published/table_28_common.csv')


def example_scans():
    """A few explicitly identified held-out examples, never a new evaluation set."""
    import pandas as pd
    if not (RUN/'preparation.json').is_file() or not (ROOT/'data/raw').is_dir():return []
    prep=read(RUN/'preparation.json');manifest=pd.read_parquet(ROOT/prep['split_relpath'])
    selected=manifest.loc[manifest.split.eq('test')].sort_values('scan_id').groupby('label_id').head(3)
    return [dict(scan_id=r.scan_id,label_id=int(r.label_id),archive=str((ROOT/'data/raw'/f'{r.scan_id}.zip').resolve()))
            for r in selected.itertuples()]


class InferenceEngine:
    def __init__(self):
        self.lock=threading.RLock();self.models={};self.heads={}
        self.model_root=ROOT/'models'
        if not MANIFEST.is_file():raise RuntimeError('Le manifeste d’inférence de l’interface est absent.')
        self.source_manifest=read(MANIFEST);self.frozen=read(self.model_root/'frozen.json')
        self.combo_frozen=read(self.model_root/'combinations/frozen.json')
        self.preparation=read(self.model_root/'preparation.json');self.verify_artifacts()
        definitions,constants=definition_nodes(NOTEBOOK)
        if fingerprints(definitions,constants)!=self.source_manifest['definitions']:
            raise RuntimeError('Le code d’inférence du notebook a changé ; vérifier sa compatibilité avant de charger les poids.')
        import numpy as np
        import pandas as pd
        import torch
        from torch import nn
        from torch.utils.data import Dataset,DataLoader
        from PIL import Image
        torch.set_num_threads(2)
        module=types.ModuleType('_phishark_interface_bundle');sys.modules[module.__name__]=module
        namespace=module.__dict__
        namespace.update(ROOT=ROOT,np=np,pd=pd,torch=torch,nn=nn,Dataset=Dataset,DataLoader=DataLoader,
            Image=Image,dataclass=dataclass,gzip=gzip,hashlib=hashlib,HTMLParser=HTMLParser,io=io,json=json,
            Path=Path,PurePosixPath=PurePosixPath,re=re,urlsplit=urlsplit,warnings=warnings,zipfile=zipfile,time=time)
        # Constants are exactly attested against the executed FULL, then definitions only are compiled.
        for node in constants:exec(compile(ast.Module(body=[node],type_ignores=[]),str(NOTEBOOK),'exec'),namespace)
        for name in NAMES:
            node=definitions[name]
            exec(compile(ast.Module(body=[node],type_ignores=[]),str(NOTEBOOK),'exec'),namespace)
        Image.MAX_IMAGE_PIXELS=20_000_000
        self.namespace=namespace;self.np=np;self.pd=pd;self.torch=torch
        self.settings=namespace['Settings'](**self.preparation['settings'])
        self.preprocessing=read(self.model_root/'preprocess.json')
        for name in ('median','mean','scale'):self.preprocessing[name]=np.asarray(self.preprocessing[name],np.float32)
        if tuple(self.preprocessing['features'])!=tuple(namespace['FEATURES']):raise RuntimeError('Définitions des features incompatibles.')

    def verify_artifacts(self):
        if self.frozen['code']!=self.source_manifest['trained_code'] or self.preparation['code']!=self.frozen['code']:
            raise RuntimeError('Provenance du modèle incompatible.')
        deployment=read(self.model_root/'manifest.json')
        if deployment['trained_code']!=self.frozen['code']:raise RuntimeError('Model provenance mismatch')
        for name,expected in deployment['files'].items():
            if sha(self.model_root/name)!=expected:raise RuntimeError('Modified model artifact: '+name)

    def _model(self,name):
        if name not in self.models:
            complete=read(self.model_root/name/'complete.json')
            if sha(self.model_root/name/'best.pt')!=complete['sha256']:raise RuntimeError('Checkpoint modifié : '+name)
            state=self.torch.load(self.model_root/name/'best.pt',map_location='cpu',weights_only=True)
            if state['signature']!=complete['signature']:raise RuntimeError('Signature du checkpoint incorrecte : '+name)
            model=self.namespace['architecture'](name,self.preprocessing)
            model.load_state_dict(state['weights']);model.eval()
            self.models[name]=model
        return self.models[name]

    def _decision(self,score,threshold):
        if not self.np.isfinite(score) or not 0<=score<=1:
            raise ValueError('Le modèle n’a pas produit de score numérique valide pour cette entrée.')
        return dict(score=float(score),threshold=float(threshold),predicted_class=int(score>=threshold),
                    decision='Phishing' if score>=threshold else 'Bénin')

    def predict_url(self,url):
        url=validate_url(url)
        with self.lock:
            frame=self.pd.DataFrame([dict(scan_id='input-url',label_id=0,target_url=url)])
            dataset=self.namespace['ModalDataset'](frame,self.preprocessing,self.settings,'U1')
            probability,_=self.namespace['inference'](self._model('U1'),dataset,1)
            return dict(input_kind='url_only',url=url,modalities_present=['URL'],network_access=False,
                models={'U1':self._decision(float(probability[0]),self.frozen['policies']['U1']['primary'])},
                combinations={},warnings=[],trained_code=self.frozen['code'],ground_truth=None)

    def predict_archive(self,path,url_if_missing='',include_combinations=False):
        path=Path(path)
        if not path.is_file() or path.stat().st_size>MAX_UPLOAD_BYTES:
            raise ValueError('Archive absente ou supérieure à 32 Mio.')
        with self.lock:
            scan=self.namespace['read_archive'](path,self.settings.image_size)
            if any(v is False for v in scan.get('declared_hash_checks',[])):
                raise ValueError('L’intégrité déclarée de la capture ne concorde pas avec ses fichiers.')
            target=scan['data'].get('metadata.json',{}).get('target') or scan['data'].get('data/redirection.json',{}).get('original_url','')
            if target and url_if_missing and str(target).strip()!=str(url_if_missing).strip():
                raise ValueError('L’URL saisie diffère de celle de la capture. Le champ facultatif ne remplace pas une cible existante.')
            target=target or url_if_missing
            if target:target=validate_url(target)
            tmp_root=ROOT/'artifacts/interface/tmp';tmp_root.mkdir(parents=True,exist_ok=True)
            with tempfile.TemporaryDirectory(dir=tmp_root) as directory:
                image=Path(directory)/'image.npy';self.np.save(image,scan['image'])
                row=dict(scan_id='uploaded-capture',label_id=0,target_url=target,html_text=scan['text'],
                         html_state=scan['html_state'],image_state=scan['image_state'],image_relpath=image.relative_to(ROOT).as_posix())
                row.update(zip(self.namespace['FEATURES'],self.namespace['extract_numeric'](scan['data'])))
                frame=self.pd.DataFrame([row]);mask=self.namespace['availability'](frame)
                if not mask.any():raise ValueError('La capture ne contient aucune modalité exploitable. Aucun score ne peut être produit.')
                embeddings=[];probabilities=[];result={}
                for i,name in enumerate(('U1','U2','U3','U4')):
                    if not mask[0,i]:
                        embeddings.append(self.np.zeros((1,32),self.np.float32));probabilities.append(0.);continue
                    dataset=self.namespace['ModalDataset'](frame,self.preprocessing,self.settings,name)
                    model=self._model(name)
                    z,_=self.namespace['inference'](model,dataset,1,True)
                    p,_=self.namespace['inference'](model,dataset,1)
                    embeddings.append(z);probabilities.append(float(p[0]))
                    result[name]=self._decision(float(p[0]),self.frozen['policies'][name]['primary'])
                z=self.np.concatenate(embeddings+[mask],axis=1).astype(self.np.float32)
                p=self.np.asarray([probabilities],self.np.float32)
                mean=self.namespace['late_fusion'](p,mask)[0]
                result['M1']=self._decision(mean,self.frozen['policies']['M1']['primary'])
                scaling=read(self.model_root/'fusion_scaling.json')
                normalized=((z-self.np.asarray(scaling['mean'],self.np.float32))/self.np.asarray(scaling['scale'],self.np.float32)).astype(self.np.float32)
                dataset=self.namespace['ModalDataset'](frame,self.preprocessing,self.settings,'M2',normalized)
                middle,_=self.namespace['inference'](self._model('M2'),dataset,1)
                result['M2']=self._decision(float(middle[0]),self.frozen['policies']['M2']['primary'])
                combinations={}
                if include_combinations:
                    import joblib
                    for policy in self.combo_frozen['policies']:
                        x,late,eligible=self.namespace['combo_selected'](z,p,mask,policy['choice'])
                        if policy['status']!='FROZEN' or not eligible[0]:
                            combinations[policy['model']]=dict(decision='Abstention',score=None,threshold=policy['threshold']);continue
                        score=float(late[0])
                        if policy['method']=='LINEAR_EMBED':
                            key=policy['checkpoint']
                            if key not in self.heads:self.heads[key]=joblib.load(self.model_root/'combinations'/key)
                            score=float(self.heads[key].predict_proba(x)[0,1])
                        combinations[policy['model']]=self._decision(score,policy['threshold'])
            return dict(input_kind='capture',url=str(target),models=result,combinations=combinations,
                modalities_present=[name for name,ok in zip(('URL','HTML','IMAGE','TECH'),mask[0]) if ok],
                network_access=False,html_state=scan['html_state'],image_state=scan['image_state'],
                uniform_image=scan['uniform'],warnings=scan['errors'],trained_code=self.frozen['code'],ground_truth=None)

    def predict_bytes(self,payload,url_if_missing='',include_combinations=False):
        if not payload or len(payload)>MAX_UPLOAD_BYTES:raise ValueError('Charge une archive ZIP de moins de 32 Mio.')
        folder=ROOT/'artifacts/interface/tmp';folder.mkdir(parents=True,exist_ok=True)
        with tempfile.TemporaryDirectory(dir=folder) as directory:
            path=Path(directory)/'capture.zip';path.write_bytes(payload)
            return self.predict_archive(path,url_if_missing,include_combinations)
