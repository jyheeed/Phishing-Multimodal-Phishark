"""The public release is sufficient and retains its scientific provenance."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]


def test_published_and_model_bundles_match_their_manifests():
    for directory in ('models','artifacts/published'):
        folder=ROOT/directory
        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
        assert manifest['files']
        for name,expected in manifest['files'].items():
            assert hashlib.sha256((folder/name).read_bytes()).hexdigest()==expected, name


def test_one_clean_notebook_and_no_machine_specific_bootstrap_path():
    notebooks=list((ROOT/'notebooks').glob('*.ipynb'))
    assert len(notebooks)==1
    document=json.loads(notebooks[0].read_text(encoding='utf8'))
    bootstrap=''.join(document['cells'][1]['source'])
    assert '__vsc_ipynb_file__' in bootstrap
    assert 'C:\\Users\\pc' not in bootstrap
    assert all(c.get('execution_count') is None and not c.get('outputs')
               for c in document['cells'] if c['cell_type']=='code')
