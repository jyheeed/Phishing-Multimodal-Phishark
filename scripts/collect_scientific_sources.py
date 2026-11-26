"""Fetch official research PDFs into ignored local evidence storage, never execute them."""
from pathlib import Path
import hashlib,json,urllib.request

ROOT=Path(__file__).resolve().parents[1]
FOLDER=ROOT/'artifacts/scientific_writing/sources'
URLS={
    'yoon2024.pdf':'https://mdpi-res.com/d_attachment/electronics/electronics-13-03344/article_deploy/electronics-13-03344.pdf',
    'crossphire2026.pdf':'https://mdpi-res.com/d_attachment/applsci/applsci-16-00751/article_deploy/applsci-16-00751.pdf',
    'almakhamreh2024.pdf':'https://openaccess.hacettepe.edu.tr/server/api/core/bitstreams/9d379f54-8b90-4e38-8265-b4f95322476c/content',
}

def main():
    FOLDER.mkdir(parents=True,exist_ok=True);manifest={}
    for name,url in URLS.items():
        path=FOLDER/name
        if not path.exists():
            request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 (academic source verification)'})
            try:
                with urllib.request.urlopen(request,timeout=50) as response:payload=response.read(40*2**20)
            except Exception as error:
                manifest[name]=dict(url=url,status='DOWNLOAD_FAILED',reason=str(error));print(name,str(error));continue
            if not payload.startswith(b'%PDF-'):raise ValueError('Not a PDF: '+name)
            path.write_bytes(payload)
        manifest[name]=dict(url=url,sha256=hashlib.sha256(path.read_bytes()).hexdigest(),bytes=path.stat().st_size)
        print(name,path.stat().st_size)
    (FOLDER/'manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')

if __name__=='__main__':main()
