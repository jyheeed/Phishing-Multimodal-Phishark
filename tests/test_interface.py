"""Local inference parity with the executed FULL, uploads and UI behavior."""
import io
import json
from pathlib import Path
import zipfile

import numpy as np
import pandas as pd
import pytest

from src.app_inference import InferenceEngine,ROOT,RUN,validate_url,sha,read


@pytest.fixture(scope='module')
def engine():return InferenceEngine()


def payload(metadata,extra=None):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as archive:
        archive.writestr('metadata.json',json.dumps(metadata))
        for name,value in (extra or {}).items():archive.writestr(name,value)
    return stream.getvalue()


def test_inference_only_namespace_has_no_fitting_functions(engine):
    assert 'fit_model' not in engine.namespace and 'fit_fusion' not in engine.namespace
    assert engine.settings.image_size==96
    assert engine.models=={}


def test_url_scheme_invariance_and_no_network(engine,monkeypatch):
    import socket
    monkeypatch.setattr(socket,'create_connection',lambda *a,**k:pytest.fail('Inference must not connect to a site'))
    a=engine.predict_url('http://example.org/login?q=1');b=engine.predict_url('https://example.org/login?q=1')
    assert a['models']['U1']['score']==b['models']['U1']['score']
    assert set(a['models'])=={'U1'} and a['network_access'] is False and a['ground_truth'] is None
    assert set(engine.models)=={'U1'}


def test_real_capture_and_22_combinations_match_saved_full(engine):
    if not (RUN/'predictions.csv').is_file() or not (ROOT/'data/raw').is_dir():pytest.skip('Optional original dataset integration test')
    ledger=pd.read_csv(RUN/'predictions.csv',dtype={'scan_id':str},float_precision='round_trip')
    test=ledger.loc[ledger.split.eq('test')];scan=sorted(test.scan_id.unique())[0]
    result=engine.predict_archive(ROOT/'data/raw'/f'{scan}.zip',include_combinations=True)
    expected=test.loc[test.scan_id.eq(scan)].set_index('model')
    assert len(result['models'])==6 and len(result['combinations'])==22
    for name,value in result['models'].items():
        assert value['score']==pytest.approx(expected.loc[name,'probability'],abs=1e-5)
    combinations=pd.read_csv(RUN/'combinations/predictions.csv',dtype={'scan_id':str},float_precision='round_trip')
    expected=combinations.loc[combinations.scan_id.eq(scan)].set_index('model')
    for name,value in result['combinations'].items():
        assert value['score']==pytest.approx(expected.loc[name,'probability'],abs=1e-5)


def test_missing_modalities_are_not_invented(engine):
    result=engine.predict_bytes(payload({'target':'https://example.org/login'}))
    assert result['modalities_present']==['URL']
    assert set(result['models'])=={'U1','M1','M2'}
    assert result['models']['M1']['score']==pytest.approx(result['models']['U1']['score'])
    with pytest.raises(ValueError,match='aucune modalité'):
        engine.predict_bytes(payload({}))


def test_invalid_capture_and_target_override_are_rejected(engine):
    with pytest.raises(ValueError):engine.predict_bytes(payload({'target':'https://a.org'},{'../escape.json':'{}'}))
    with pytest.raises(ValueError,match='diffère'):
        engine.predict_bytes(payload({'target':'https://a.org'}),url_if_missing='https://b.org')
    with pytest.raises(ValueError):validate_url('file:///C:/private')
    with pytest.raises(ValueError):validate_url('')


def test_inference_did_not_modify_frozen_models_or_results(engine):
    engine.verify_artifacts()
    preserved=ROOT/'artifacts/finalization/preserved_run_hashes.json'
    if preserved.is_file():
        for name,expected in read(preserved).items():
            assert sha(ROOT/name)==expected


def test_nonfinite_or_out_of_range_score_cannot_be_reported_as_benign(engine):
    for score in (float('nan'),float('inf'),-.1,1.1):
        with pytest.raises(ValueError,match='score numérique valide'):engine._decision(score,.5)


def test_ui_starts_without_loading_weights_and_url_submission_works(monkeypatch):
    import src.app_inference as module
    calls=[]
    class Stub:
        def predict_url(self,value):
            calls.append(value)
            return dict(input_kind='url_only',url=value,modalities_present=['URL'],warnings=[],network_access=False,
                combinations={},models={'U1':dict(score=.7,threshold=.5,decision='Phishing',predicted_class=1)})
    def factory():calls.append('load');return Stub()
    monkeypatch.setattr(module,'InferenceEngine',factory)
    from streamlit.testing.v1 import AppTest
    app=AppTest.from_file(str(ROOT/'app.py'),default_timeout=30).run()
    assert not app.exception and calls==[]
    app.text_input(key='url_value').set_value('https://example.org/login')
    app.button[0].click().run()
    assert not app.exception and calls==['load','https://example.org/login']
    assert any(metric.value=='Phishing' for metric in app.metric)
    app.button[1].click().run()
    assert not app.exception and any('Choisis une archive' in error.value for error in app.error)
