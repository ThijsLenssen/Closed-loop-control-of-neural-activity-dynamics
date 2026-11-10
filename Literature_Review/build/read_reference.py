import argparse
import re
import unicodedata
from pathlib import Path

parser=argparse.ArgumentParser()
parser.add_argument('ids', nargs='+',type=int)
parser.add_argument('--pages',default='')
parser.add_argument('--scan',default='')
parser.add_argument('--limit',type=int,default=5000)
args=parser.parse_args()
root=Path(__file__).resolve().parent/'paper_texts'
for idx in args.ids:
    pages=(root/f'{idx:02d}.txt').read_text(encoding='utf-8').split('\f')
    if args.pages:
        selected=[]
        for part in args.pages.split(','):
            if '-' in part:
                lo,hi=map(int,part.split('-')); selected.extend(range(lo,hi+1))
            else: selected.append(int(part))
    else:
        selected=range(1,len(pages)+1)
    for p in selected:
        if p>len(pages): continue
        txt=pages[p-1]
        if args.scan:
            matches=list(re.finditer(args.scan,txt,re.I))
            if not matches: continue
            chunks=[]
            last=-1
            for m in matches:
                start=max(0,m.start()-200); end=min(len(txt),m.end()+450)
                if start<=last: continue
                chunks.append(txt[start:end]); last=end
            txt='\n[...]\n'.join(chunks)
        print(f'\n=== PAPER {idx:02d}, PDF PAGE {p} ===')
        print(unicodedata.normalize('NFKD',txt[:args.limit]).encode('ascii','replace').decode())
