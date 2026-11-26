"""Extract official PDF text for a traceable, targeted literature review."""
from pathlib import Path
import json,hashlib
from pypdf import PdfReader
ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/scientific_writing/sources'

def main():
    records=[]
    for path in [ROOT/'docs/specification/Projet_phishing_multimodal.pdf',*FOLDER.glob('*.pdf')]:
        try:
            pdf=PdfReader(path);pages=[page.extract_text() or '' for page in pdf.pages]
        except Exception as error:
            records.append(dict(file=path.name,status='INVALID_LOCAL_COPY',reason=str(error)))
            continue
        target=FOLDER/(path.stem+'.pages.json')
        target.write_text(json.dumps(pages,ensure_ascii=False),encoding='utf8')
        records.append(dict(file=path.relative_to(ROOT).as_posix(),pages=len(pages),characters=sum(map(len,pages)),sha256=hashlib.sha256(path.read_bytes()).hexdigest()))
    (FOLDER/'pdf_inventory.json').write_text(json.dumps(records,indent=2),encoding='utf8')
    print(json.dumps(records))

if __name__=='__main__':main()
