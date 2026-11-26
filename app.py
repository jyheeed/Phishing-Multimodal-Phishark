"""PhiShark2026 local research demo. Start with python -m streamlit run app.py."""
from pathlib import Path
import json
import sys
import zipfile

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'.runtime'))
sys.path.insert(0,str(ROOT))
import pandas as pd
import streamlit as st
from src.app_inference import InferenceEngine,example_scans,project_results

st.set_page_config(page_title='PhiShark2026 — test local',page_icon='🛡️',layout='wide')
st.markdown('''<style>
.block-container {max-width:1160px;padding-top:2rem;}
h1,h2,h3 {color:#10243c;}
[data-testid="stMetric"] {background:#fff;border:1px solid #dfe7ef;border-radius:14px;padding:18px;}
.eyebrow {color:#149a91;font-size:.78rem;font-weight:700;letter-spacing:.14em;}
</style>''',unsafe_allow_html=True)
st.markdown('<div class="eyebrow">PROJET ACADÉMIQUE · DÉMONSTRATION LOCALE</div>',unsafe_allow_html=True)
st.title('PhiShark2026')
st.write('Teste les modèles entraînés sur une adresse ou sur les preuves capturées d’une page.')
st.caption('Aucun entraînement et aucune visite du site saisi. Les scores estiment la réputation phishing ; ils ne certifient pas l’état actuel d’un site.')

MODEL_NAMES={'U1':'CNN URL','U2':'CNN HTML','U3':'CNN screenshot','U4':'MLP technique',
             'M1':'Moyenne des probabilités','M2':'Fusion des embeddings'}


@st.cache_resource(show_spinner=False)
def engine():return InferenceEngine()


@st.cache_data(show_spinner=False)
def examples():return example_scans()


@st.cache_data(show_spinner=False)
def historical_results():return project_results()


def render_result(result,key):
    st.subheader('Résultat de l’analyse')
    st.caption('Modalités exploitées : '+', '.join(result['modalities_present']))
    highlights=['M1','M2'] if result['input_kind']=='capture' else ['U1']
    columns=st.columns(len(highlights))
    for column,name in zip(columns,highlights):
        item=result['models'][name]
        with column:
            st.metric(MODEL_NAMES[name],item['decision'])
            st.progress(item['score'])
            st.caption(f"Score : {item['score']:.4f} · seuil : {item['threshold']:.4f}")
    rows=[dict(Modèle=name+' · '+MODEL_NAMES[name],Score=value['score'],Seuil=value['threshold'],Décision=value['decision'])
          for name,value in result['models'].items()]
    st.dataframe(pd.DataFrame(rows),hide_index=True,use_container_width=True)
    st.caption('Score entre 0 et 1, sans calibration probabiliste certifiée. Chaque décision utilise son seuil déjà fixé sur calibration.')
    if result.get('uniform_image'):st.warning('Le screenshot est presque uniforme : son contenu visuel peut être peu informatif.')
    if result.get('warnings'):st.warning('Certaines preuves sont incomplètes ou illisibles : '+', '.join(result['warnings']))
    if result['combinations']:
        with st.expander('Les 22 combinaisons multimodales',expanded=True):
            extra=[dict(Configuration=name,Score=value['score'],Seuil=value['threshold'],Décision=value['decision'])
                   for name,value in result['combinations'].items()]
            st.dataframe(pd.DataFrame(extra),hide_index=True,use_container_width=True)
            st.caption('Les modalités demandées disponibles sont utilisées. Aucune modalité demandée présente : abstention.')
    st.download_button('Télécharger le résultat JSON',json.dumps(result,ensure_ascii=False,indent=2),
                       file_name='phishark_resultat.json',mime='application/json',key=key+'_download')


def run_analysis(call,result_key):
    try:
        with st.spinner('Chargement des poids vérifiés et calcul des scores…'):
            result=call(engine())
        st.session_state[result_key]=result
    except (ValueError,RuntimeError,OSError,zipfile.BadZipFile,EOFError) as error:
        st.session_state.pop(result_key,None)
        st.error(str(error))


url_tab,capture_tab,results_tab=st.tabs(['URL seule','Capture multimodale','Exemples et résultats'])
with url_tab:
    st.subheader('Tester une adresse')
    st.write('Le CNN URL analyse l’hôte, le chemin et la query. Il ne télécharge ni HTML ni screenshot.')
    with st.form('url_form'):
        url=st.text_input('Adresse à analyser',placeholder='https://exemple.org/connexion',key='url_value')
        submitted=st.form_submit_button('Analyser l’URL',type='primary')
    if submitted:
        run_analysis(lambda predictor:predictor.predict_url(url),'url_result')
    if 'url_result' in st.session_state:render_result(st.session_state['url_result'],'url')

with capture_tab:
    st.subheader('Tester une capture complète')
    st.write('Charge une archive ZIP PhiShark contenant metadata.json, les JSON techniques et, si disponibles, le HTML et le screenshot.')
    with st.form('capture_form'):
        uploaded=st.file_uploader('Archive ZIP · 32 Mio maximum',type=['zip'],key='capture_zip')
        missing_url=st.text_input('URL de la page, uniquement si elle est absente de l’archive',key='capture_url')
        all_combos=st.checkbox('Calculer aussi les 22 combinaisons',value=False,key='capture_combos')
        submitted=st.form_submit_button('Analyser la capture',type='primary')
    if submitted:
        if uploaded is None:st.error('Choisis une archive ZIP avant de lancer l’analyse.')
        else:run_analysis(lambda predictor:predictor.predict_bytes(uploaded.getvalue(),missing_url,all_combos),'capture_result')
    if 'capture_result' in st.session_state:render_result(st.session_state['capture_result'],'capture')

with results_tab:
    st.subheader('Essayer les captures déjà disponibles')
    st.caption('Ces exemples appartiennent au test historique du projet. Les réanalyser est une démonstration, pas une nouvelle validation indépendante.')
    try:
        available=examples()
        selected=st.selectbox('Exemple à réanalyser',available,
            format_func=lambda item:('Bénin' if item['label_id']==0 else 'Phishing')+' annoté · '+item['scan_id'][:12])
        example_combos=st.checkbox('Inclure les 22 combinaisons pour cet exemple',key='example_combos')
        if not available:st.info('Installer les données originales pour ces exemples. URL et import ZIP restent disponibles.')
        if st.button('Analyser cet exemple',key='analyze_example',type='primary',disabled=not available):
            run_analysis(lambda predictor:predictor.predict_archive(selected['archive'],include_combinations=example_combos),'example_result')
        if 'example_result' in st.session_state:render_result(st.session_state['example_result'],'example')
    except (ValueError,RuntimeError,OSError) as error:st.error(str(error))
    st.divider()
    st.subheader('Les résultats du projet')
    try:
        table=historical_results()
        a,b,c=st.columns(3);a.metric('Configurations',len(table));b.metric('Scans communs',f"{int(table.n.iloc[0]):,}".replace(',',' '));c.metric('Couverture',f"{table.coverage.iloc[0]*100:.2f} %")
        st.dataframe(table[['model','modalities','AP','precision','recall','F1','FPR','FP','FN']],hide_index=True,use_container_width=True)
        st.caption('Cohorte commune de quatre modalités disponibles. Les comparaisons sont internes et exploratoires ; elles ne choisissent pas un gagnant final indépendant.')
    except (ValueError,OSError) as error:st.error(str(error))

with st.expander('Ce que ce prototype permet de vérifier'):
    st.write('Comparer les scores de réseaux déjà entraînés, tester leur seuil de décision et observer les désaccords entre modalités. Aucun label, checkpoint ou seuil n’est modifié.')
    st.write('L’URL seule teste uniquement U1. Les fusions nécessitent une capture. La généralisation temporelle et externe n’est pas démontrée ; les erreurs possibles restent celles d’un prototype de recherche.')
