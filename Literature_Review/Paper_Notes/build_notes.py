"""Compile each standalone paper note; outputs stay in Paper_Notes/build."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import json
import subprocess
import sys

ROOT = Path(__file__).resolve().parent


def compile_note(record):
    result = subprocess.run(
        ['latexmk', '-pdf', '-interaction=nonstopmode', '-halt-on-error',
         '-file-line-error', '-outdir=build', record['notes']],
        cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    transcript = ROOT/'build'/(Path(record['notes']).stem+'.compile.txt')
    transcript.write_text(result.stdout+'\n'+result.stderr, encoding='utf-8')
    return record, result.returncode, transcript


if __name__ == '__main__':
    (ROOT/'build').mkdir(exist_ok=True)
    records = json.loads((ROOT/'sources.json').read_text(encoding='utf-8'))
    failures = []
    with ThreadPoolExecutor(max_workers=3) as pool:
        for record, code, transcript in pool.map(compile_note, records):
            print(f"{record['id']:02d}: {'OK' if code == 0 else 'FAILED'} {record['notes']}", flush=True)
            if code:
                failures.append(str(transcript))
    if failures:
        print('\nFailed builds; see:\n'+'\n'.join(failures))
        sys.exit(1)
    print(f'Compiled all {len(records)} notes.')
