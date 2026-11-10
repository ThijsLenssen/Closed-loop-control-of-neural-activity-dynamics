"""Append the digitized coarse-graining comparison and its transport realization."""
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
from xml.dom import minidom
import xml.etree.ElementTree as E
import hashlib
import os
import re
import pymupdf

ROOT=Path(__file__).resolve().parent.parent
DECK=ROOT/'Presentation/Closed-loop Control of neural activity dynamics.pptx'
ASSETS=ROOT/'Presentation/assets'
BUILD=ROOT/'build/hh_neuron_slide'
P='http://schemas.openxmlformats.org/presentationml/2006/main'
A='http://schemas.openxmlformats.org/drawingml/2006/main'
R='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
REL='http://schemas.openxmlformats.org/package/2006/relationships'
SVG='http://schemas.microsoft.com/office/drawing/2016/SVG/main'
NS={'p':P,'a':A,'r':R}
for prefix,namespace in NS.items(): E.register_namespace(prefix,namespace)
E.register_namespace('asvg',SVG)
def child(parent,tag,**attrs):
    prefix,local=tag.split(':');return E.SubElement(parent,'{'+NS[prefix]+'}'+local,{k:str(v) for k,v in attrs.items()})
def serialize(root): return E.tostring(root,encoding='utf-8',xml_declaration=True)
def emu(value): return str(round(value*12700))
def rels(items):
    root=E.Element('Relationships',xmlns=REL)
    for rid,kind,target in items:
        E.SubElement(root,'Relationship',Id=rid,Type=R+'/'+kind,Target=target)
    return serialize(root)

initial_bytes=DECK.read_bytes()
with ZipFile(DECK) as archive:
    entries={item.filename:(item,archive.read(item.filename)) for item in archive.infolist()}
original_slides={name:data for name,(_,data) in entries.items() if re.fullmatch(r'ppt/slides/slide\d+\.xml',name)}
assert not any(b'Wilson_Cowan_coarse_graining' in data for data in original_slides.values()), 'Comparison slides already present.'
backup=BUILD/'presentation_before_wilson_cowan_slides.pptx'
if not backup.exists(): backup.write_bytes(initial_bytes)
next_slide=max(int(re.search(r'slide(\d+)',name).group(1)) for name in original_slides)+1
next_note=max([int(re.search(r'notesSlide(\d+)',name).group(1)) for name in entries if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml',name)]+[0])+1
template=E.fromstring(entries['ppt/slides/slide2.xml'][1])
template_tree=template.find('p:cSld/p:spTree',NS)
new_parts={}

def textbox(tree,name,text,x,y,w,h,size=13,color='646C74'):
    shape=child(tree,'p:sp');nv=child(shape,'p:nvSpPr')
    child(nv,'p:cNvPr',id=80+len(list(tree)),name=name)
    child(nv,'p:cNvSpPr',txBox=1);child(nv,'p:nvPr')
    props=child(shape,'p:spPr');xf=child(props,'a:xfrm')
    child(xf,'a:off',x=emu(x),y=emu(y));child(xf,'a:ext',cx=emu(w),cy=emu(h))
    child(child(props,'a:prstGeom',prst='rect'),'a:avLst');child(props,'a:noFill')
    child(child(props,'a:ln'),'a:noFill')
    body=child(shape,'p:txBody');child(body,'a:bodyPr',wrap='square',lIns=0,tIns=0,rIns=0,bIns=0)
    child(body,'a:lstStyle');para=child(body,'a:p');run=child(para,'a:r')
    fmt=child(run,'a:rPr',lang='en-US',sz=round(size*100));child(child(fmt,'a:solidFill'),'a:srgbClr',val=color)
    child(fmt,'a:latin',typeface='Aptos');child(run,'a:t').text=text

specifications=[
    dict(name='Wilson_Cowan_coarse_graining',title='Population activity: temporal coarse graining',
         subtitle='Excitatory population only: explicit memory versus temporal averaging',
         asset='wc_coarse_graining_content',
         credit='Wilson and Cowan (1972), Fig. 3 and Eqs. (9)-(10). Curves digitized from the published scan.',
         description='Digitized Figure 3 comparison, r=3 ms: Equation 9 retains temporal memory and exhibits damped oscillations; Equation 10 is coarse grained and approaches the same plateau monotonically. Both equations are displayed explicitly.',
         notes='''Wilson and Cowan (1972), Excitatory and Inhibitory Interactions in Localized Populations of Model Neurons, Biophysical Journal 12:1-24. Figure 3 on p. 10 and Eqs. (9)-(10) on p. 8. https://doi.org/10.1016/S0006-3495(72)86068-5
This is a digitized graphical redrawing of the published curves, not an independently reproduced simulation. The caption specifies r=3 ms but does not give a complete parameter set, response function, input waveform and initial history for Figure 3. The parameters listed for Figure 4 are not assumed to be those of Figure 3.
The blue curve is sampled from pixels of the thin oscillatory curve; the red curve is sampled from the thick coarse-grained curve. A monotone isotonic fit removes raster noise from the coarse curve. Spatial calibration in the rendered crop: t=0 at x=155, t=25 ms at x=745; E=0 at y=647 and E=0.5 at y=63. The source page is rendered at 6x with clip (170,475,305,615). Data are stored in wc1972_fig3_history.csv and wc1972_fig3_coarse.csv; the digitization script and PGFPlots source are included in Presentation/.
Equation (9) already uses a first-order expansion of the original response delay and omits inhibition for this comparison. It retains the refractory moving integral and exponentially weighted synaptic input. Its exponential is reproduced as printed, exp[-alpha(t-s)]; alpha is therefore a decay-rate coefficient in the displayed equations. Equation (10) replaces the histories by coarse-grained values and gain k.'''),
    dict(name='Wilson_Cowan_transport_memory',title='Retaining population memory with transport',
         subtitle='An equivalent realization of Equation (9), with compatible initial history',
         asset='wc_transport_content',
         credit='Transport formulation derived from Wilson and Cowan (1972), Eq. (9). The extra coordinate is memory age.',
         description='History transport PDE z_t+z_a=0 for age a in [0,r], boundary z(t,0)=E(t), refractory fraction R=integral z da. Coupled ODEs U_dot=-alpha U+c1 E+P and tau E_dot=-E+(1-R)S_e(U).',
         notes='''Derived here from Eq. (9) in Wilson and Cowan (1972), rather than an equation quoted from the paper. https://doi.org/10.1016/S0006-3495(72)86068-5
Define z(t,a)=E(t-a), a in [0,r]. Then z_t+z_a=0, z(t,0)=E(t), and R(t)=integral_0^r z(t,a) da is exactly the refractory integral in Eq. (9). The coordinate a is history age, not physical tissue position.
Define U(t)=integral_{-infinity}^t exp[-alpha(t-s)] [c1 E(s)+P(s)] ds. Then U_dot=-alpha U+c1 E+P. The population ODE tau E_dot=-E+(1-R)S_e(U) is exactly Eq. (9). Thus this PDE-ODE system retains the two histories in Eq. (9), without the extra temporal coarse-graining that yields Eq. (10).
Consistent initialization is essential: z(0,a)=E_history(-a), and U(0) equals the convolution of the past excitation and input. Boundary compatibility also requires z(0,0)=E(0). If histories vanish before zero, use z(0,a)=0 and U(0)=0, with compatible E(0).
The transport formulation is equivalent to Eq. (9), which itself already approximates the original delayed response in Eqs. (3)-(4). It does not undo that earlier response-delay approximation. No extra PDE simulation curve is claimed in the digitized Figure 3.
For constant signals and this unnormalized exponential, the convolution DC gain is 1/alpha; k in Eq. (10) denotes the coarse-graining gain. Polynomial/constant coefficients appear in the transport and filter realization. The remaining sigmoid and refractory-factor product are nonlinear.''')]

for offset,spec in enumerate(specifications):
    sidx=next_slide+offset;nidx=next_note+offset
    slide=E.Element('{'+P+'}sld');cs=child(slide,'p:cSld',name=spec['name']);tree=child(cs,'p:spTree')
    for shape in template_tree:
        name_node=shape.find('.//p:cNvPr',NS)
        name=name_node.attrib.get('name','') if name_node is not None else ''
        if shape.tag in ['{'+P+'}nvGrpSpPr','{'+P+'}grpSpPr'] or name in ['Title 1','Footer Placeholder 2']:
            copy=deepcopy(shape)
            if name=='Title 1':
                texts=copy.findall('.//a:t',NS)
                texts[0].text=spec['title']
                for item in texts[1:]:item.text=''
            tree.append(copy)
    textbox(tree,'Population model subtitle',spec['subtitle'],36,76,648,20,13)
    picture=child(tree,'p:pic');nv=child(picture,'p:nvPicPr')
    child(nv,'p:cNvPr',id=100,name=spec['name']+'_graphic',descr=spec['description'])
    child(child(nv,'p:cNvPicPr'),'a:picLocks',noChangeAspect=1);child(nv,'p:nvPr')
    fill=child(picture,'p:blipFill');blip=child(fill,'a:blip');blip.set('{'+R+'}embed','rId2')
    ext=child(child(blip,'a:extLst'),'a:ext',uri='{96DAC541-7B7A-43D3-8B79-37D633B846F1}')
    svg=E.SubElement(ext,'{'+SVG+'}svgBlip');svg.set('{'+R+'}embed','rId3')
    child(child(fill,'a:stretch'),'a:fillRect')
    props=child(picture,'p:spPr');xf=child(props,'a:xfrm')
    child(xf,'a:off',x=emu(36),y=emu(99));child(xf,'a:ext',cx=emu(648),cy=emu(275))
    child(child(props,'a:prstGeom',prst='rect'),'a:avLst')
    textbox(tree,'Source and provenance',spec['credit'],36,375,648,10,7.2)
    child(child(slide,'p:clrMapOvr'),'a:masterClrMapping')
    new_parts[f'ppt/slides/slide{sidx}.xml']=serialize(slide)
    new_parts[f'ppt/slides/_rels/slide{sidx}.xml.rels']=rels([
        ('rId1','slideLayout','../slideLayouts/slideLayout12.xml'),
        ('rId2','image','../media/'+spec['asset']+'.png'),
        ('rId3','image','../media/'+spec['asset']+'.svg'),
        ('rId4','notesSlide',f'../notesSlides/notesSlide{nidx}.xml')])
    for extension in ['png','svg']:
        new_parts['ppt/media/'+spec['asset']+'.'+extension]=(ASSETS/(spec['asset']+'.'+extension)).read_bytes()
    note=E.Element('{'+P+'}notes');note_tree=child(child(note,'p:cSld'),'p:spTree')
    for base in list(template_tree)[:2]:note_tree.append(deepcopy(base))
    shape=child(note_tree,'p:sp');nv=child(shape,'p:nvSpPr');child(nv,'p:cNvPr',id=2,name='Speaker notes')
    child(nv,'p:cNvSpPr');child(child(nv,'p:nvPr'),'p:ph',type='body',idx=1)
    child(shape,'p:spPr');body=child(shape,'p:txBody');child(body,'a:bodyPr');child(body,'a:lstStyle')
    for paragraph in spec['notes'].splitlines():child(child(child(body,'a:p'),'a:r'),'a:t').text=paragraph
    child(child(note,'p:clrMapOvr'),'a:masterClrMapping')
    new_parts[f'ppt/notesSlides/notesSlide{nidx}.xml']=serialize(note)
    new_parts[f'ppt/notesSlides/_rels/notesSlide{nidx}.xml.rels']=rels([
        ('rId1','notesMaster','../notesMasters/notesMaster1.xml'),('rId2','slide',f'../slides/slide{sidx}.xml')])

pres=minidom.parseString(entries['ppt/presentation.xml'][1])
pres_rels=minidom.parseString(entries['ppt/_rels/presentation.xml.rels'][1])
types=minidom.parseString(entries['[Content_Types].xml'][1])
ids=pres.getElementsByTagName('p:sldIdLst')[0]
next_id=max(int(el.getAttribute('id')) for el in ids.getElementsByTagName('p:sldId'))+1
next_rid=max(int(el.getAttribute('Id')[3:]) for el in pres_rels.getElementsByTagName('Relationship'))+1
section_lists=pres.getElementsByTagName('p14:sldIdLst')
for offset in range(2):
    sidx=next_slide+offset;nidx=next_note+offset;rid='rId'+str(next_rid+offset)
    relation=pres_rels.createElementNS(REL,'Relationship')
    for key,value in [('Id',rid),('Type',R+'/slide'),('Target',f'slides/slide{sidx}.xml')]:relation.setAttribute(key,value)
    pres_rels.documentElement.appendChild(relation)
    identifier=pres.createElementNS(P,'p:sldId');identifier.setAttribute('id',str(next_id+offset));identifier.setAttributeNS(R,'r:id',rid);ids.appendChild(identifier)
    if section_lists:
        entry=pres.createElement('p14:sldId');entry.setAttribute('id',str(next_id+offset));section_lists[-1].appendChild(entry)
    for part,ctype in [(f'ppt/slides/slide{sidx}.xml','application/vnd.openxmlformats-officedocument.presentationml.slide+xml'),(f'ppt/notesSlides/notesSlide{nidx}.xml','application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml')]:
        entry=types.createElement('Override');entry.setAttribute('PartName','/'+part);entry.setAttribute('ContentType',ctype);types.documentElement.appendChild(entry)
new_parts['ppt/presentation.xml']=pres.toxml(encoding='utf-8')
new_parts['ppt/_rels/presentation.xml.rels']=pres_rels.toxml(encoding='utf-8')
new_parts['[Content_Types].xml']=types.toxml(encoding='utf-8')
app=minidom.parseString(entries['docProps/app.xml'][1])
for tag in ['Slides','Notes']:
    nodes=app.getElementsByTagName(tag)
    if nodes and nodes[0].firstChild:nodes[0].firstChild.data=str(int(nodes[0].firstChild.data)+2)
for headings in app.getElementsByTagName('HeadingPairs'):
    variants=headings.getElementsByTagName('vt:variant')
    for i,item in enumerate(variants[:-1]):
        if 'Slide Titles' in item.toxml():
            value=variants[i+1].getElementsByTagName('vt:i4')[0];value.firstChild.data=str(int(value.firstChild.data)+2)
for titles in app.getElementsByTagName('TitlesOfParts'):
    vector=titles.getElementsByTagName('vt:vector')[0];vector.setAttribute('size',str(int(vector.getAttribute('size'))+2))
    for spec in specifications:
        item=app.createElement('vt:lpstr');item.appendChild(app.createTextNode(spec['title']));vector.appendChild(item)
new_parts['docProps/app.xml']=app.toxml(encoding='utf-8')
staged=BUILD/'presentation_with_wilson_cowan_slides.pptx'
with ZipFile(staged,'w') as archive:
    for name,(info,data) in entries.items():archive.writestr(info,new_parts.pop(name,data))
    for name,data in new_parts.items():archive.writestr(name,data)
with ZipFile(staged) as archive:
    assert archive.testzip() is None
    for name,data in original_slides.items():assert archive.read(name)==data
    for name in archive.namelist():
        if name.endswith(('.xml','.rels')):minidom.parseString(archive.read(name))
assert hashlib.sha256(DECK.read_bytes()).digest()==hashlib.sha256(initial_bytes).digest(),'Presentation changed while preparing slides; staged copy retained.'
try:
    os.replace(staged,DECK);saved=DECK
except PermissionError:
    saved=ROOT/'Presentation/Closed-loop Control of neural activity dynamics - with population models.pptx'
    saved.write_bytes(staged.read_bytes())
    print('Original presentation is open/locked. Updated presentation saved separately.')

# Vector PDF review of the two new slides, plus a standalone redrawn figure.
review=pymupdf.open()
for index,spec in enumerate(specifications):
    page=review.new_page(width=720,height=405)
    page.insert_text((36,55),spec['title'],fontsize=25,fontname='hebo',color=(.145,.145,.16))
    page.insert_text((36,89),spec['subtitle'],fontsize=13,color=(.39,.42,.45))
    body=pymupdf.open(BUILD/(spec['asset']+'.pdf'))
    page.show_pdf_page(pymupdf.Rect(36,99,684,374),body,0)
    page.insert_text((36,382),spec['credit'],fontsize=7.2,color=(.39,.42,.45))
    page.insert_text((36,395),'Msc Defence T.M. Lenssen',fontsize=8,color=(.45,.48,.51))
    page.insert_text((664,394),'TU/e',fontsize=16,fontname='hebo',color=(.784,.098,.098))
    page.get_pixmap(matrix=pymupdf.Matrix(1920/720,1920/720)).save(BUILD/('wc_slide_'+str(index+1)+'.png'))
review.save(BUILD/'wilson_cowan_slides.pdf')
figure=pymupdf.open();page=figure.new_page(width=283,height=274)
body=pymupdf.open(BUILD/'wc_coarse_graining_content.pdf')
page.show_pdf_page(page.rect,body,0,clip=pymupdf.Rect(0,0,283,274))
figure.save(ASSETS/'wilson_cowan_figure3_redrawn.pdf')
(ASSETS/'wilson_cowan_figure3_redrawn.svg').write_text(page.get_svg_image(),encoding='utf-8')
print('Added two slides after',len(original_slides),'existing slides. Existing slide XML is unchanged.')
print('Saved presentation:',saved)
