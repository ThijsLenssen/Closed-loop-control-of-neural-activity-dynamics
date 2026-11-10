import hashlib
import json
import subprocess
import shutil
from pathlib import Path

workspace = Path(__file__).resolve().parents[2]
root = workspace/'Literature_Review'/'build'/'paper_texts'
root.mkdir(exist_ok=True)
papers=[]
previews=[]
for idx, source in enumerate(sorted((workspace/'References').rglob('*.pdf'), key=lambda x: (x.parent.name, x.name.casefold())),1):
    target=root/f'{idx:02d}.txt'
    if not target.exists() or target.stat().st_size<100:
        short_source=root/f'source_{idx:02d}.pdf'
        shutil.copyfile(source,short_source)
        result=subprocess.run(['pdftotext','-layout',str(short_source),str(target)],capture_output=True)
        if result.returncode:
            (root/f'error_{idx:02d}.txt').write_bytes(result.stderr)
            print(f'FAILED reference {idx:02d}; see error file.')
            continue
    txt=target.read_text(encoding='utf-8',errors='replace')
    pages=txt.split('\f')
    if not pages[-1].strip():
        pages.pop()
    record={'id':idx,'source':str(source.relative_to(workspace)),'text':str(target.relative_to(workspace)),
            'pages':len(pages),'sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
    papers.append(record)
    previews.append(f"\n=== {idx:02d} | {len(pages)} PDF pages | {source.parent.name} | {source.name} ===\n"+pages[0][:2600])
(root/'inventory.json').write_text(json.dumps(papers,indent=2),encoding='utf-8')
(root.parent/'reference_inventory.txt').write_text('\n'.join(previews),encoding='utf-8')
print(f'Extracted {len(papers)} PDFs ({sum(p["pages"] for p in papers)} pages).')
