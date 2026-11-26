"""Read-only Git publication checks: manifests, excluded data, paths and file sizes."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT=Path(__file__).resolve().parents[1]


def main():
    for relative in ('models','artifacts/published'):
        folder=ROOT/relative
        manifest=json.loads((folder/'manifest.json').read_text(encoding='utf8'))
        for name,expected in manifest['files'].items():
            target=(folder/name).resolve()
            if not target.is_relative_to(folder.resolve()):raise RuntimeError('Manifest path outside its bundle')
            if hashlib.sha256(target.read_bytes()).hexdigest()!=expected:raise RuntimeError('Hash mismatch: '+str(target))
    candidates=subprocess.check_output(['git','ls-files','--cached','--others','--exclude-standard','-z'],cwd=ROOT).decode('utf8').split('\0')
    files=[ROOT/p for p in candidates if p and (ROOT/p).is_file()]
    forbidden=('.local_archive/','.runtime/','.maintenance/','data/raw/','data/processed/','data/splits/','phisharkl2026dataset-v1.1/','artifacts/runs/')
    for p in files:
        relative=p.relative_to(ROOT).as_posix()
        if relative.startswith(forbidden):raise RuntimeError('Private/generated file exposed: '+relative)
        if p.is_symlink():raise RuntimeError('Unexpected publication symlink: '+relative)
        if p.stat().st_size>=50*2**20:raise RuntimeError('Large Git file: '+relative)
        if p.name in ('.env','credentials','id_rsa','id_ed25519'):raise RuntimeError('Credential filename: '+relative)
    print(json.dumps(dict(status='PASS',files=len(files),total_mib=round(sum(p.stat().st_size for p in files)/2**20,2),largest_mib=round(max(p.stat().st_size for p in files)/2**20,2),git_index_modified=False)))


if __name__=='__main__':main()
