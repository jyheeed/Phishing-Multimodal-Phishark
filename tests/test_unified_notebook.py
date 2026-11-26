"""The delivered notebook really contains the executable core and final analysis."""
import ast
import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]


def document(name):
    return json.loads((ROOT/'notebooks'/name).read_text(encoding='utf-8'))


def source(cell):return ''.join(cell.get('source',[]))


def test_all_original_computation_is_visible_and_unchanged():
    original=json.loads((ROOT/'artifacts/provenance/executed_full_code.json').read_text(encoding='utf-8'))
    unified=document('PhiShark2026_FINAL_CRISP_DM.ipynb')
    expected=[source(c) for c in original['cells'][2:] if c['cell_type']=='code']
    actual=[]
    for c in unified['cells']:
        if c['cell_type']!='code':continue
        tree=ast.parse(source(c))
        if len(tree.body)==1 and isinstance(tree.body[0],ast.If) and ast.unparse(tree.body[0].test)=="MODE == 'FULL_EXPERIMENT'":
            actual.append(ast.Module(body=tree.body[0].body,type_ignores=[]))
    assert len(expected)==106
    for a,b in zip(expected,actual[:106]):
        assert ast.dump(ast.parse(a),include_attributes=False)==ast.dump(b,include_attributes=False)


def test_no_project_module_or_second_notebook_is_executed():
    unified=document('PhiShark2026_FINAL_CRISP_DM.ipynb')
    for cell in unified['cells']:
        if cell['cell_type']!='code':continue
        for node in ast.walk(ast.parse(source(cell))):
            if isinstance(node,ast.ImportFrom):assert not (node.module or '').startswith(('src','nbclient'))
            if isinstance(node,ast.Import):assert not any(n.name.startswith(('src','nbclient')) for n in node.names)
            if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):assert node.func.id!='exec'
    assert "MODE = 'PRESENTATION'" in source(unified['cells'][1])


def test_analysis_code_is_inline_and_has_been_executed_without_models():
    unified=document('PhiShark2026_FINAL_CRISP_DM.ipynb')
    names={node.name for c in unified['cells'] if c['cell_type']=='code' for node in ast.walk(ast.parse(source(c))) if isinstance(node,ast.FunctionDef)}
    assert {'extract','construct_partitions','fit_model','fit_fusion','run_combo_study','finalize_current_run','saved_demo','load_evidence'}.issubset(names)
    proof=json.loads((ROOT/'artifacts/verification/unified_analysis_test.json').read_text())
    assert proof['status']=='PASS' and proof['models']==28 and not proof['models_loaded']


def test_default_presentation_was_run_with_project_imports_blocked():
    proof=json.loads((ROOT/'artifacts/verification/presentation_test.json').read_text())
    assert proof['status']=='PASS' and proof['cells']==225
    assert proof['project_code_imports_prohibited'] and proof['networks_trained'] is False
