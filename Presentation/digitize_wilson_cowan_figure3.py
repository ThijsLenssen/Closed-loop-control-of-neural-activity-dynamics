"""Digitize Fig. 3's published curves; this does not reproduce its simulation."""
from pathlib import Path
import csv
import numpy as np
from PIL import Image
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'References/modeling and control/modeling/Excitatory and Inhibitory Interactions in Localized Populations of Model Neurons.pdf'
OUT = ROOT / 'Presentation/assets'
OUT.mkdir(exist_ok=True)
document = pymupdf.open(SOURCE)
pixmap = document[9].get_pixmap(matrix=pymupdf.Matrix(6,6),
                              clip=pymupdf.Rect(170,475,305,615),alpha=False)
gray = np.asarray(Image.frombytes('RGB',(pixmap.width,pixmap.height),pixmap.samples).convert('L'))
dark = gray < 170
# Axis calibration in the rendered crop: t=0,25 ms and E=0,0.5.
x0,x25,y0,y05 = 155.0,745.0,647.0,63.0
# Sparse graphical guides distinguish the thin oscillatory curve from the thick
# monotone curve at crossings. Actual samples are taken from dark source pixels.
guides = np.array([
    (156,647),(159,635),(163,612),(167,599),(171,570),(175,530),
    (179,443),(183,357),(187,309),(191,257),(195,224),
    (201,188),(206,182),(211,215),(219,294),(229,385),(239,434),
    (249,453),(259,458),(269,436),(279,396),(289,351),(299,322),
    (309,313),(319,319),(329,337),(339,361),(349,382),(359,391),
    (369,389),(379,373),(389,358),(399,350),(409,349),(419,353),
    (429,362),(439,367),(449,369),(459,368),(469,363),(479,360),
    (489,359),(499,360),(509,362),(519,365),(529,366),(539,365),
    (549,361),(559,360),(569,360),(579,362),(589,365),(599,366),
    (609,366),(619,364),(629,363),(639,363),(649,365),(659,366),
    (669,365),(679,364),(689,364),(699,365),(709,365),(719,365),
    (729,365),(739,365),(745,366)],float)
coarse_guides=np.array([
    (155,647),(159,605),(163,563),(167,538),(171,513),(175,493),
    (179,478),(183,467),(187,458),(191,447),(195,441),(200,431),
    (210,416),(225,401),(250,384),(275,374),(300,367),(325,363),
    (350,360),(375,360),(400,360),(450,361),(500,362),(600,363),
    (745,365)],float)

curves = [[],[]]
for x in range(159,746):
    rows = np.flatnonzero(dark[75:641,x])+75
    if not len(rows):
        continue
    groups = np.split(rows,np.flatnonzero(np.diff(rows)>2)+1)
    # Remove the E=0.25 axis tick, which projects into the first columns.
    groups=[group for group in groups if not (x<180 and len(group)<8 and abs(np.median(group)-355)<5)]
    if not groups: continue
    centers=np.array([np.median(group) for group in groups])
    coarse_target=np.interp(x,coarse_guides[:,0],coarse_guides[:,1])
    coarse_index=int(np.argmin(np.abs(centers-coarse_target)))
    coarse_group=groups[coarse_index]
    coarse_y=float(np.median(coarse_group)) if len(coarse_group)<=14 else float(coarse_group[np.argmin(np.abs(coarse_group-coarse_target))])
    target=np.interp(x,guides[:,0],guides[:,1])
    other=[i for i in range(len(groups)) if i!=coarse_index and abs(centers[i]-target)<45]
    if other:
        selected=min(other,key=lambda i:abs(centers[i]-target))
        group=groups[selected]
        history_y=float(np.median(group)) if len(group)<=20 else float(group[np.argmin(np.abs(group-target))])
    else:
        group=coarse_group
        history_y=float(np.median(group)) if len(group)<=20 else float(group[np.argmin(np.abs(group-target))])
    for index,y in enumerate([history_y,coarse_y]):
        curves[index].append((25*(x-x0)/(x25-x0),.5*(y0-y)/(y0-y05)))

def isotonic_increasing(values):
    blocks = []
    for value in values:
        blocks.append([float(value),1])
        while len(blocks)>1 and blocks[-2][0]>blocks[-1][0]:
            b=blocks.pop(); a=blocks.pop(); count=a[1]+b[1]
            blocks.append([(a[0]*a[1]+b[0]*b[1])/count,count])
    return np.concatenate([np.full(count,value) for value,count in blocks])

for index,name in enumerate(['wc1972_fig3_history','wc1972_fig3_coarse']):
    data = np.array([(0,0)]+curves[index])
    if index == 0:
        # A seven-column median rejects isolated branch/tick misassignments at
        # crossings in the scanned plot (about 0.3 ms at this calibration).
        padded=np.pad(data[:,1],(3,3),mode='edge')
        data[:,1]=np.median(np.lib.stride_tricks.sliding_window_view(padded,7),axis=1)
    if index == 1:
        # The published coarse-grained response is described as monotone. Apply
        # an isotonic fit to remove raster noise without changing that property.
        data[:,1] = isotonic_increasing(data[:,1])
    with (OUT/(name+'.csv')).open('w',newline='',encoding='utf-8') as stream:
        writer=csv.writer(stream);writer.writerow(['t_ms','E'])
        writer.writerows((f'{t:.7f}',f'{e:.7f}') for t,e in data)
    print(name,len(data),'samples; peak',data[:,1].max())
