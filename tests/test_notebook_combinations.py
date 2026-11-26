"""Exercise definitions from the actual standalone notebook, never a model mirror."""
import ast
import json
from pathlib import Path
import sys
import types

import numpy as np
import pandas as pd
import pytest


@pytest.fixture
def nb():
    path = Path(__file__).resolve().parents[1]/'artifacts/provenance/executed_full_code.json'
    if not path.exists():
        path = Path(__file__).resolve().parents[1]/'notebooks/PhiShark2026_FINAL_CRISP_DM.ipynb'
    document = json.loads(path.read_text(encoding='utf-8'))
    module = types.ModuleType('phishark_notebook_definitions')
    sys.modules[module.__name__] = module
    namespace = module.__dict__
    for index, cell in enumerate(document['cells']):
        if cell['cell_type'] != 'code' or index == 1:
            continue
        tree = ast.parse(''.join(cell['source']))
        keep = []
        for node in tree.body:
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.FunctionDef, ast.ClassDef)):
                keep.append(node)
            elif isinstance(node, ast.Assign) and all(isinstance(t, ast.Name) and t.id.isupper() for t in node.targets):
                keep.append(node)
        if keep:
            exec(compile(ast.Module(body=keep, type_ignores=[]), str(path), 'exec'), namespace)
    return namespace


def test_full_configuration_and_url_pipeline(nb):
    settings = nb['Settings'].full()
    assert settings.mode == 'FULL_EXPERIMENT' and settings.samples_per_class == 0
    assert settings.image_size == 96 and settings.epochs == 10
    url = nb['url_model_text']
    assert url('http://Example.org/Login?q=1#first') == url('https://Example.org/Login?q=1#second')
    assert url('example.org/Login?q=1') == 'example.org/login?q=1'
    assert url('') == '' and isinstance(url('http://[bad'), str)
    part = pd.DataFrame(dict(scan_id=['a', 'b'], label_id=[0, 1], split=['train_encoder']*2,
        target_url=['http://example.org/a', 'https://example.org/a'], html_text=['hello', 'world']))
    for feature in nb['FEATURES']:
        part[feature] = 1.0
    preprocessing = nb['fit_preprocessing'](part, settings)
    dataset = nb['ModalDataset'](part, preprocessing, settings, 'U1')
    np.testing.assert_array_equal(dataset[0][0].numpy(), dataset[1][0].numpy())
    assert preprocessing['fitted_ids'] == ['a', 'b']


@pytest.mark.parametrize('size', [32, 96])
def test_image_embedding_has_32_values(nb, size):
    torch = nb['torch']
    torch.set_num_threads(1)
    model = nb['ScreenshotCNN']().eval()
    with torch.inference_mode():
        values = torch.zeros(2, 3, size, size)
        assert model.encode(values).shape == (2, 32)
        assert model(values).shape == (2,)


def synthetic_study(nb, tmp_path, monkeypatch, complete=True):
    rng = np.random.default_rng(42)
    frame = pd.concat([pd.DataFrame(dict(scan_id=[role+str(i) for i in range(20)],
        split=role, label_id=np.arange(20) % 2)) for role in ('train_fusion', 'calibration', 'test')], ignore_index=True)
    context = dict(frame=frame, run=tmp_path, settings=nb['Settings'](), provenance={'version': 'synthetic-v1'})
    central = dict(policies={name: {'primary': 0.5} for name in nb['MODEL_IDS']})
    monkeypatch.setitem(nb, 'verify_frozen', lambda context: central)
    monkeypatch.setitem(nb, 'source_signature', lambda: 'notebook-code-signature')
    calls = []

    def representations(context, models, part):
        role = part.split.iloc[0]
        if role == 'test':
            assert (tmp_path/'combinations/frozen.json').exists()
        calls.append(role)
        mask = np.ones((len(part), 4), np.float32)
        mask[0] = 0
        if not complete:
            mask[:, 0] = 0
        probability = np.tile((0.2 + part.label_id.to_numpy()*0.6)[:, None], (1, 4))
        z = np.concatenate([rng.normal(size=(len(part), 32)).astype(np.float32)*mask[:, i:i+1]
                            for i in range(4)] + [mask], axis=1)
        return z, probability, []

    monkeypatch.setitem(nb, 'representations', representations)
    # The array helper independently checks availability and its cache alignment.
    def availability(part):
        mask = np.ones((len(part), 4), np.float32)
        mask[0] = 0
        if not complete:
            mask[:, 0] = 0
        return mask
    monkeypatch.setitem(nb, 'availability', availability)
    test = frame.loc[frame.split.eq('test')]
    ledger = pd.concat([test.assign(model=name, probability=0.2+test.label_id*0.6) for name in nb['MODEL_IDS']])
    ledger.to_csv(tmp_path/'predictions.csv', index=False)
    return context, calls


def test_22_combinations_freeze_coverage_alignment_and_resume(nb, tmp_path, monkeypatch):
    context, calls = synthetic_study(nb, tmp_path, monkeypatch)
    metrics, baselines = nb['run_combo_study'](context, {})
    assert calls == ['train_fusion', 'calibration', 'test']
    assert len(nb['COMBO_SPECS']) == 11
    assert len(metrics) == 44 and metrics.model.nunique() == 22
    assert len(baselines) == 6 and set(baselines.n) == {19}
    predictions = pd.read_csv(tmp_path/'combinations/predictions.csv')
    assert len(predictions) == 22*20
    assert predictions.loc[predictions.abstained, 'probability'].isna().all()
    assert predictions.groupby('model').abstained.sum().eq(1).all()
    assert pd.read_csv(tmp_path/'combinations/all_28_comparable_models.csv').n.eq(19).all()
    first = (tmp_path/'combinations/frozen.json').read_bytes()
    monkeypatch.setitem(nb, 'LogisticRegression', lambda **kw: pytest.fail('A resumed frozen head must not refit'))
    again, _ = nb['run_combo_study'](context, {})
    pd.testing.assert_frame_equal(metrics, again)
    assert (tmp_path/'combinations/frozen.json').read_bytes() == first
    assert calls == ['train_fusion', 'calibration', 'test']
    head = next((tmp_path/'combinations').glob('*.joblib'))
    head.write_bytes(head.read_bytes()+b'changed')
    with pytest.raises(ValueError, match='Modified combination'):
        nb['run_combo_study'](context, {})


def test_no_complete_case_is_reported_without_fabricating_metrics(nb, tmp_path, monkeypatch):
    context, _ = synthetic_study(nb, tmp_path, monkeypatch, complete=False)
    metrics, base = nb['run_combo_study'](context, {})
    common = metrics.loc[metrics.cohort.eq('all_four_available')]
    assert len(common) == 22 and common.n.eq(0).all() and common.AP.isna().all()
    assert base.n.eq(0).all()


def test_full_missing_corpus_preflight_stops_before_extraction(nb, tmp_path, monkeypatch):
    pd.DataFrame(dict(archive_filename=[str(i)+'.zip' for i in range(100)])).to_csv(
        tmp_path/'phishark2026_public_metadata.csv', index=False)
    monkeypatch.setitem(nb, 'RAW_DIRECTORY', tmp_path)
    monkeypatch.setitem(nb, 'ROOT', tmp_path)
    monkeypatch.setitem(nb, 'dependency_report', lambda: dict(missing_core=[], available_ram_gb=0.1,
        free_disk_gb=20, spark_status='AVAILABLE'))
    result = nb['preflight'](nb['Settings'].full())
    assert result['status'] == 'BLOCKED' and result['missing_archive_count'] == 100
    assert result['warnings']  # RAM still warns, as authorized; it is not a blocking reason.
    assert not any('RAM' in reason for reason in result['reasons'])


def test_disk_budget_does_not_charge_completed_cache_twice(nb, tmp_path, monkeypatch):
    pd.DataFrame(dict(archive_filename=['a.zip'])).to_csv(tmp_path/'phishark2026_public_metadata.csv', index=False)
    (tmp_path/'a.zip').touch()
    settings = nb['Settings'].full()
    monkeypatch.setitem(nb, 'ROOT', tmp_path)
    monkeypatch.setitem(nb, 'RAW_DIRECTORY', tmp_path)
    monkeypatch.setitem(nb, 'source_signature', lambda: 'current-code')
    monkeypatch.setitem(nb, 'dependency_report', lambda: dict(missing_core=[], available_ram_gb=0.1,
        free_disk_gb=4, spark_status='AVAILABLE'))
    assert nb['preflight'](settings)['status'] == 'BLOCKED'
    folder = tmp_path/'data/processed/example'
    folder.mkdir(parents=True)
    config = {k: v for k, v in nb['asdict'](settings).items() if k not in ('protocol', 'epochs', 'patience', 'bootstrap_replicates')}
    (folder/'complete.json').write_text(json.dumps(dict(binding=dict(code='current-code', config=config))))
    (folder/'canonical.parquet').touch()
    result = nb['preflight'](settings)
    assert result['status'] == 'PASS' and result['required_free_disk_gb'] == 2
    # This is only a budget hint: actual extract still verifies the cache checksum and raw binding.
