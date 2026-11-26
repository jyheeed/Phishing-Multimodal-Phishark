"""Attest inference definitions against this project's already executed FULL."""
import sys
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from src.app_inference import definition_nodes,fingerprints,NOTEBOOK,RUN,MANIFEST


def main():
    current=definition_nodes(NOTEBOOK)
    original=definition_nodes(ROOT/'artifacts/provenance/executed_full_code.json')
    assert fingerprints(*current)==fingerprints(*original),'Inference changed since the executed FULL; do not silently attest new definitions'
    MANIFEST.parent.mkdir(parents=True,exist_ok=True)
    data=dict(definitions=fingerprints(*current),trained_code=json.loads((ROOT/'models/frozen.json').read_text())['code'],
              runtime_code_source='single_final_notebook',inference_only=True,training_functions_loaded=False)
    MANIFEST.write_text(json.dumps(data,indent=2),encoding='utf-8');print('Inference source manifest verified and saved.')


if __name__=='__main__':main()
