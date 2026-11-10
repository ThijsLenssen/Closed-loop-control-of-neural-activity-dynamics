import hashlib
import json
from pathlib import Path
import re
import subprocess

root=Path(__file__).resolve().parents[2]
notes=root/'Literature_Review/Paper_Notes'
records=json.loads((notes/'sources.json').read_text(encoding='utf-8'))
actual={p.resolve() for p in (root/'References').rglob('*.pdf')}
listed={(root/r['source']).resolve() for r in records}
assert actual==listed, 'Source coverage mismatch'
assert len(records)==len({r['notes'] for r in records}), 'Duplicate note paths'
issues=[]
for rec in records:
    source=root/rec['source']
    assert hashlib.sha256(source.read_bytes()).hexdigest()==rec['sha256'], f"Changed source: {source}"
    pdf=notes/rec['compiled']
    assert pdf.exists(), f'Missing PDF: {pdf}'
    info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,text=True,encoding='utf-8',errors='replace')
    assert info.returncode==0, info.stderr
    pages=int(re.search(r'^Pages:\s+(\d+)',info.stdout,re.M).group(1))
    log=(notes/'build'/(Path(rec['notes']).stem+'.log')).read_text(encoding='utf-8',errors='replace')
    warnings=[line for line in log.splitlines() if re.search(r'Overfull|Undefined|^!|LaTeX Warning',line)]
    text=subprocess.run(['pdftotext',str(pdf),'-'],capture_output=True,text=True,encoding='utf-8',errors='replace').stdout
    for marker in ['To which general question','How does it answer','What papers does it cite']:
        assert marker in text, f"Missing heading {marker}: {rec['notes']}"
    print(f"{rec['id']:02d}: {pages} page(s); {len(warnings)} warning(s)")
    if pages!=1 or warnings:
        issues.append({'id':rec['id'],'pages':pages,'warnings':warnings})
print(f'Coverage: {len(actual)}/{len(actual)} source PDFs, hashes verified.')
print(json.dumps(issues,indent=2))
