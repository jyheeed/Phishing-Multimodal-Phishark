"""Render the scientific PDF and record structural pagination checks."""
from pathlib import Path
import sys,json,re
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'artifacts/scientific_writing/pdf_tools'))
import pypdfium2 as pdfium
from pypdf import PdfReader
from PIL import Image,ImageDraw

def main():
    folder=ROOT/'artifacts/scientific_writing/render';folder.mkdir(parents=True,exist_ok=True)
    path=ROOT/'reports/PHISHARK2026_RAPPORT_FINAL.pdf';reader=PdfReader(path)
    text=[p.extract_text() or '' for p in reader.pages]
    entries=[]
    for i,t in enumerate(text):
        for line in t.splitlines()[:8]:
            if line.startswith('Chapitre ') or line.startswith('Annexe') or line=='Bibliographie':entries.append(dict(page=i+1,title=line))
    pdf=pdfium.PdfDocument(str(path));thumbs=[]
    for i in range(len(pdf)):
        page=pdf[i];bitmap=page.render(scale=.34);im=bitmap.to_pil().convert('RGB')
        tile=Image.new('RGB',(220,315),'#DDE3EA');im.thumbnail((208,286));tile.paste(im,((220-im.width)//2,18));ImageDraw.Draw(tile).text((8,3),f'Page {i+1}',fill='black');thumbs.append(tile)
        if i in [0,2,6,11,17,24,30,35,40,45,49,53,55]:
            full=page.render(scale=1.15).to_pil();full.save(folder/f'page_{i+1:02d}.png')
        bitmap.close();page.close()
    for start in range(0,len(thumbs),28):
        group=thumbs[start:start+28];sheet=Image.new('RGB',(7*220,4*315),'white')
        for j,tile in enumerate(group):sheet.paste(tile,((j%7)*220,(j//7)*315))
        sheet.save(folder/f'contact_{start//28+1}.png')
    status=dict(pages=len(reader.pages),extractable_characters=sum(map(len,text)),pages_under_70_characters=[i+1 for i,t in enumerate(text) if len(t.strip())<70],chapter_positions=entries,contains_missing_glyph=any('\ufffd' in t or '\u25a0' in t for t in text),unresolved_template=any('{{' in t for t in text),rendered_pages=len(thumbs))
    (ROOT/'artifacts/scientific_writing/layout_check.json').write_text(json.dumps(status,indent=2,ensure_ascii=False),encoding='utf8')
    print(json.dumps(status,ensure_ascii=False))

if __name__=='__main__':main()
