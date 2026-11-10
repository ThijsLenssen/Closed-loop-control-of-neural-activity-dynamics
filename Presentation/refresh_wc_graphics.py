"""Refresh the already inserted WC slide graphics and vector review artifacts."""
from pathlib import Path
from zipfile import ZipFile
import xml.etree.ElementTree as E
import os,re
import pymupdf

root=Path(__file__).resolve().parent.parent
deck=root/'Presentation/Closed-loop Control of neural activity dynamics.pptx'
assets=root/'Presentation/assets'
build=root/'build/hh_neuron_slide'
ns={'p':'http://schemas.openxmlformats.org/presentationml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main'}
names=['wc_coarse_graining_content','wc_transport_content']
with ZipFile(deck) as source:
    items={item.filename:(item,source.read(item.filename)) for item in source.infolist()}
original_slides={name:data for name,(_,data) in items.items() if re.fullmatch(r'ppt/slides/slide\d+.xml',name)}
graphics={}
for name in names:
    doc=pymupdf.open(build/(name+'.pdf'))
    doc[0].get_pixmap(matrix=pymupdf.Matrix(2,2)).save(assets/(name+'.png'))
    (assets/(name+'.svg')).write_text(doc[0].get_svg_image(),encoding='utf-8')
    for extension in ['png','svg']:
        graphics['ppt/media/'+name+'.'+extension]=(assets/(name+'.'+extension)).read_bytes()
temporary=deck.with_suffix('.graphics-update.pptx')
with ZipFile(temporary,'w') as target:
    for name,(info,data) in items.items():
        if re.fullmatch(r'ppt/notesSlides/notesSlide\d+.xml',name) and b'wc1972_fig3_history.csv' in data:
            data=data.replace(b'A monotone isotonic fit removes raster noise from the coarse curve.',
                b'A seven-column median filter rejects isolated scan artifacts in the history curve (about 0.3 ms). A monotone isotonic fit removes raster noise from the coarse curve.')
        target.writestr(info,graphics.get(name,data))
with ZipFile(temporary) as check:
    assert check.testzip() is None
    for name,data in original_slides.items():assert check.read(name)==data
os.replace(temporary,deck)

specs=[('Wilson_Cowan_coarse_graining',names[0]),('Wilson_Cowan_transport_memory',names[1])]
review=pymupdf.open()
for index,(identifier,asset) in enumerate(specs):
    selected=[E.fromstring(data) for data in original_slides.values() if identifier.encode() in data]
    assert len(selected)==1
    text=[node.text for node in selected[0].findall('.//a:t',ns)]
    title,footer,subtitle,credit=text[:4]
    page=review.new_page(width=720,height=405)
    page.insert_text((36,55),title,fontsize=25,fontname='hebo',color=(.145,.145,.16))
    page.insert_text((36,89),subtitle,fontsize=13,color=(.39,.42,.45))
    content=pymupdf.open(build/(asset+'.pdf'))
    page.show_pdf_page(pymupdf.Rect(36,99,684,374),content,0)
    page.insert_text((36,382),credit,fontsize=7.2,color=(.39,.42,.45))
    page.insert_text((36,395),footer,fontsize=8,color=(.45,.48,.51))
    page.insert_text((664,394),'TU/e',fontsize=16,fontname='hebo',color=(.784,.098,.098))
    page.get_pixmap(matrix=pymupdf.Matrix(1920/720,1920/720)).save(build/('wc_slide_'+str(index+1)+'.png'))
review.save(build/'wilson_cowan_slides.pdf')
figure=pymupdf.open();page=figure.new_page(width=283,height=274)
content=pymupdf.open(build/(names[0]+'.pdf'))
page.show_pdf_page(page.rect,content,0,clip=pymupdf.Rect(0,0,283,274))
figure.save(assets/'wilson_cowan_figure3_redrawn.pdf')
(assets/'wilson_cowan_figure3_redrawn.svg').write_text(page.get_svg_image(),encoding='utf-8')
print('Refreshed digitized curves in the presentation and previews; all slide XML preserved.')
