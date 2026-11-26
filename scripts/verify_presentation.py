"""Execute PRESENTATION in a fresh kernel with DL imports prohibited."""
import json
from pathlib import Path
import os
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'.runtime'))
import nbformat
from nbclient import NotebookClient
from jupyter_client import KernelManager
from jupyter_client.kernelspec import KernelSpecManager


def main():
    target=ROOT/'notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb';notebook=nbformat.read(target,as_version=4);nbformat.validate(notebook)
    guard=nbformat.v4.new_code_cell('''import importlib.abc,sys
class ForbidTrainingImports(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname in ('torch','src') or fullname.startswith(('torch.','src.')):
            raise AssertionError('Presentation must not import training/inference model code')
sys.meta_path.insert(0,ForbidTrainingImports())
''')
    notebook.cells.insert(0,guard)
    folder=ROOT/'artifacts/finalization/presentation_kernel';folder.mkdir(parents=True,exist_ok=True)
    (folder/'kernel.json').write_text(json.dumps(dict(argv=[sys.executable,'-m','ipykernel_launcher','-f','{connection_file}'],display_name='my_env presentation test',language='python')),encoding='utf-8')
    manager=KernelSpecManager(kernel_dirs=[str(folder.parent)])
    client=NotebookClient(notebook,timeout=180,kernel_name=folder.name,resources={'metadata':{'path':str(ROOT)}})
    client.km=KernelManager(kernel_name=folder.name,kernel_spec_manager=manager)
    try:client.execute(env=dict(os.environ,PYTHONPATH='',PHISHARK_NOTEBOOK_FILE=str(target)))
    except Exception:
        nbformat.write(notebook,ROOT/'artifacts/finalization/failed_presentation.ipynb');raise
    finally:
        if client.km is not None and client.km.has_kernel:client.km.shutdown_kernel(now=True)
        if client.kc is not None:client.kc.stop_channels()
    text=''.join(o.get('text','') for o in notebook.cells[-1].outputs)
    assert 'PRESENTATION_VALIDATION_OK 28 13212' in text
    notebook.cells.pop(0);nbformat.write(notebook,ROOT/'artifacts/finalization/presentation_executed.ipynb')
    status=dict(status='PASS',cells=len(notebook.cells),code_cells=sum(c.cell_type=='code' for c in notebook.cells),
        model_imports_prohibited=True,networks_trained=False,full_replay_executed=False,common_models=28,common_n=13212)
    status['project_code_imports_prohibited']=True
    (ROOT/'artifacts/finalization/presentation_test.json').write_text(json.dumps(status,indent=2),encoding='utf-8');print(json.dumps(status))
    (ROOT/'artifacts/verification/presentation_test.json').write_text(json.dumps(status,indent=2),encoding='utf-8')


if __name__=='__main__':main()
