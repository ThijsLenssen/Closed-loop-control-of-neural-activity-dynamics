"""Insert a model-and-schematic slide without altering existing slide contents."""
from pathlib import Path
from zipfile import ZipFile
from copy import deepcopy
from xml.dom import minidom
import xml.etree.ElementTree as ET
import re
import os
import pymupdf

ROOT = Path(__file__).resolve().parent.parent
DECK = ROOT / 'Presentation/Closed-loop Control of neural activity dynamics.pptx'
ASSETS = ROOT / 'Presentation/assets'
BUILD = ROOT / 'build/hh_neuron_slide'
NS = {'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
REL = 'http://schemas.openxmlformats.org/package/2006/relationships'
for prefix, uri in NS.items():
    ET.register_namespace(prefix, uri)

def node(parent, tag, **attributes):
    prefix, local = tag.split(':')
    return ET.SubElement(parent, '{'+NS[prefix]+'}'+local,
                         {key: str(value) for key, value in attributes.items()})

def pt(value):
    return str(round(value*12700))

def xml(element):
    return ET.tostring(element, encoding='utf-8', xml_declaration=True)

with ZipFile(DECK) as source:
    entries = {item.filename: (item, source.read(item.filename))
               for item in source.infolist()}
original_slides = {name: data for name, (_, data) in entries.items()
                   if re.fullmatch(r'ppt/slides/slide\d+\.xml', name)}
assert not any(b'Distributed_HH_model_and_schematic' in data
               for data in original_slides.values()), 'The model slide is already present.'
backup = BUILD / 'presentation_before_model_and_schematic.pptx'
if not backup.exists():
    backup.write_bytes(DECK.read_bytes())

slide_index = max(int(re.search(r'slide(\d+)', name).group(1))
                  for name in original_slides) + 1
notes_index = max([int(re.search(r'notesSlide(\d+)', name).group(1))
                   for name in entries if re.fullmatch(r'ppt/notesSlides/notesSlide\d+\.xml', name)]
                  + [0]) + 1
slide_part = f'ppt/slides/slide{slide_index}.xml'
notes_part = f'ppt/notesSlides/notesSlide{notes_index}.xml'

slide = ET.Element('{'+NS['p']+'}sld')
cs = node(slide, 'p:cSld', name='Distributed_HH_model_and_schematic')
tree = node(cs, 'p:spTree')
template = ET.fromstring(entries['ppt/slides/slide2.xml'][1])
template_tree = template.find('p:cSld/p:spTree', NS)
for child in list(template_tree)[:2]:
    tree.append(deepcopy(child))

shape_id = 1
operations = []
INK = '252529'
MUTED = '646C74'
BLUE = '0092B5'
RED = 'C81919'

def shape_base(kind, name, x, y, w, h):
    global shape_id
    shape_id += 1
    shape = node(tree, 'p:'+kind)
    nv = node(shape, 'p:nvPicPr' if kind == 'pic' else 'p:nvSpPr')
    node(nv, 'p:cNvPr', id=shape_id, name=name)
    node(nv, 'p:cNvPicPr' if kind == 'pic' else 'p:cNvSpPr')
    node(nv, 'p:nvPr')
    sp = node(shape, 'p:spPr')
    transform = node(sp, 'a:xfrm')
    node(transform, 'a:off', x=pt(x), y=pt(y))
    node(transform, 'a:ext', cx=pt(w), cy=pt(h))
    geometry = node(sp, 'a:prstGeom', prst='rect')
    node(geometry, 'a:avLst')
    return shape, sp

def text(name, content, x, y, w, h, size=13, color=INK, bold=False, font='Aptos', title=False):
    shape, sp = shape_base('sp', name, x, y, w, h)
    shape.find('p:nvSpPr/p:cNvSpPr', NS).set('txBox', '1')
    if title:
        node(shape.find('p:nvSpPr/p:nvPr', NS), 'p:ph', type='title')
    node(sp, 'a:noFill')
    node(node(sp, 'a:ln'), 'a:noFill')
    body = node(shape, 'p:txBody')
    node(body, 'a:bodyPr', wrap='square', lIns=0, tIns=0, rIns=0, bIns=0, anchor='t')
    node(body, 'a:lstStyle')
    paragraph = node(body, 'a:p')
    node(paragraph, 'a:pPr', algn='l')
    run = node(paragraph, 'a:r')
    props = node(run, 'a:rPr', lang='en-US', sz=round(size*100), b=int(bold))
    node(node(props, 'a:solidFill'), 'a:srgbClr', val=color)
    node(props, 'a:latin', typeface=font)
    node(run, 'a:t').text = content
    operations.append(('text', content, x, y, w, h, size, color, bold))

def line(name, x1, y1, x2, y2, color=INK, width=1.5, arrow=False):
    shape, sp = shape_base('sp', name, min(x1,x2), min(y1,y2), abs(x2-x1), abs(y2-y1))
    transform = sp.find('a:xfrm', NS)
    if x2 < x1:
        transform.set('flipH', '1')
    if y2 < y1:
        transform.set('flipV', '1')
    sp.find('a:prstGeom', NS).set('prst', 'line')
    stroke = node(sp, 'a:ln', w=pt(width), cap='rnd')
    node(node(stroke, 'a:solidFill'), 'a:srgbClr', val=color)
    if arrow:
        node(stroke, 'a:tailEnd', type='triangle', w='sm', len='sm')
    operations.append(('line', x1,y1,x2,y2,color,width,arrow))

def picture(name, filename, relationship, x,y,w,h, description):
    shape, sp = shape_base('pic', name, x,y,w,h)
    shape.find('p:nvPicPr/p:cNvPr', NS).set('descr', description)
    fill = ET.Element('{'+NS['p']+'}blipFill')
    blip = node(fill, 'a:blip')
    blip.set('{'+NS['r']+'}embed', relationship)
    node(node(fill, 'a:stretch'), 'a:fillRect')
    shape.insert(1, fill)
    operations.append(('picture', filename,x,y,w,h))

def cover(name,x,y,w,h):
    shape, sp = shape_base('sp', name,x,y,w,h)
    node(node(sp, 'a:solidFill'), 'a:srgbClr', val='FFFFFF')
    node(node(sp, 'a:ln'), 'a:noFill')
    operations.append(('cover',x,y,w,h))

text('HH model slide title', 'Distributed Hodgkin-Huxley model',36,30,648,40,25,bold=True,title=True)
text('HH model subtitle', 'An excitable membrane at each position along the axon',36,76,648,21,13,color=MUTED)

branches = [(128,207,99,191),(99,191,80,160),(80,160,56,147),
            (80,160,82,136),(99,191,106,151),(106,151,120,133),
            (127,207,87,199),(87,199,57,194),(57,194,40,178),
            (57,194,40,209),(127,209,97,227),(97,227,75,254),
            (75,254,50,260),(75,254,75,276),(97,227,103,261),(103,261,122,277)]
for index, points in enumerate(branches):
    line('Dendrite branch '+str(index), *points)
picture('Soma and axon adapted from Brette Figure 5C', 'brette2015_fig5c_soma_axon.png',
        'rId2',124.2,175.5,206.5,46.2,
        'Soma and axon from Brette (2015), Figure 5C. Dendritic branches and model annotations added schematically.')
cover('Remove original current direction marker',147,185,42,17)
cover('Remove original 20 micrometer scale label',196,211,57,13)
text('Dendrite label','Dendrites',40,110,130,22,16,bold=True)
text('Soma label','Soma',110,233,75,22,16,bold=True)
text('Axon label','Axon',257,175,80,22,16,color=BLUE,bold=True)
text('Applied current','I_app(x,t)',176,146,112,23,14,color=RED,font='Cambria Math')
text('Voltage field','V(x,t)',262,217,85,23,15,font='Cambria Math')
line('Axon spatial coordinate',153,258,329,258,color=BLUE,width=1.25,arrow=True)
text('Proximal axon coordinate','x = 0',147,266,63,18,12,color=BLUE,font='Cambria Math')
text('Distal axon coordinate','x = L',298,266,58,18,12,color=BLUE,font='Cambria Math')
text('Axon distance caption','distance along the axon',169,292,180,17,10.5,color=MUTED)
line('Column divider',350,104,350,342,color='DFE3E7',width=1)
text('Equation heading','Voltage and local channel dynamics',368,102,316,20,13,bold=True)
picture('Full distributed HH voltage and gating equations','hh_distributed_model_full.png','rId3',
        358,125,330,222.5,
        'C_M partial_t V = (r/(2R)) partial_xx V + I_app - I_ion; '
        'I_ion = g_K n^4(V-V_K) + g_Na m^3 h(V-V_Na) + g_l(V-V_l); '
        'partial_t q = (q_infinity(V)-q)/tau_q(V), q in {n,m,h}. All states depend on x and t.')
text('Model scope','The cable equation models the axon; dendrites and soma are shown for context.',36,356,648,17,10.5,color=MUTED)
text('Model and schematic sources','Schematic: Brette (2015), Fig. 5C, adapted (CC BY). Model: Martinez et al. (2023), Eqs. (8)-(9).',36,374,648,11,7.5,color=MUTED)
text('Presentation footer','Msc Defence T.M. Lenssen',36,384,400,13,8,color='747B82')
mapping = node(slide, 'p:clrMapOvr')
node(mapping,'a:masterClrMapping')

def relationships(items):
    doc = ET.Element('Relationships', xmlns=REL)
    for rid, kind, target in items:
        ET.SubElement(doc,'Relationship',Id=rid,Type=NS['r']+'/'+kind,Target=target)
    return xml(doc)

new_parts = {
    slide_part: xml(slide),
    f'ppt/slides/_rels/slide{slide_index}.xml.rels': relationships([
        ('rId1','slideLayout','../slideLayouts/slideLayout12.xml'),
        ('rId2','image','../media/hh_schematic_brette5c.png'),
        ('rId3','image','../media/hh_equations_full.png'),
        ('rId4','notesSlide',f'../notesSlides/notesSlide{notes_index}.xml')]),
    'ppt/media/hh_schematic_brette5c.png': (ASSETS/'brette2015_fig5c_soma_axon.png').read_bytes(),
    'ppt/media/hh_equations_full.png': (ASSETS/'hh_distributed_model_full.png').read_bytes(),
}

notes = ET.Element('{'+NS['p']+'}notes')
notes_tree = node(node(notes,'p:cSld'),'p:spTree')
for child in list(template_tree)[:2]:
    notes_tree.append(deepcopy(child))
note_shape = node(notes_tree,'p:sp')
nv = node(note_shape,'p:nvSpPr')
node(nv,'p:cNvPr',id=2,name='Model and schematic speaker notes')
node(nv,'p:cNvSpPr')
node(node(nv,'p:nvPr'),'p:ph',type='body',idx=1)
node(note_shape,'p:spPr')
body = node(note_shape,'p:txBody')
node(body,'a:bodyPr')
node(body,'a:lstStyle')
note_text = '''The left schematic adds dendritic branches to the soma-axon portion of Brette (2015), Figure 5C. The original current direction marker and distance label are covered; the red current injection arrow is retained. These labels illustrate the distributed HH model rather than the quantitative experiment of that original panel.
Schematic source: Romain Brette (2015), What Is the Most Realistic Single-Compartment Model of Spike Initiation?, PLoS Computational Biology 11:e1004114, Figure 5C; CC BY. https://doi.org/10.1371/journal.pcbi.1004114. That figure adapts Brette (2013), https://doi.org/10.1371/journal.pcbi.1003338.
Model source: Martinez et al. (2023), Dynamical Models in Neuroscience From a Closed-Loop Control Perspective, p. 708, Eqs. (8)-(9). https://doi.org/10.1109/RBME.2022.3180559.
The voltage PDE is for a uniform unmyelinated axon. V, n, m and h are functions of x and t. q is shorthand for each of n, m, h; therefore the displayed q equation denotes three local gating equations. n is K activation; m is Na activation; h is Na inactivation. The sodium, potassium and leak currents are explicitly expanded.
Dendrites and soma provide anatomical context. They require a branched cable/compartment extension and appropriate interface conditions to model explicitly. This is an individual-neuron model, not a population-rate model. Initial/boundary conditions, kinetics and parameters must be supplied for simulation.'''
for paragraph_text in note_text.splitlines():
    node(node(node(body,'a:p'),'a:r'),'a:t').text = paragraph_text
node(node(notes,'p:clrMapOvr'),'a:masterClrMapping')
new_parts[notes_part] = xml(notes)
new_parts[f'ppt/notesSlides/_rels/notesSlide{notes_index}.xml.rels'] = relationships([
    ('rId1','notesMaster','../notesMasters/notesMaster1.xml'),
    ('rId2','slide',f'../slides/slide{slide_index}.xml')])

pres = minidom.parseString(entries['ppt/presentation.xml'][1])
pres_rels = minidom.parseString(entries['ppt/_rels/presentation.xml.rels'][1])
rid = 'rId'+str(max(int(el.getAttribute('Id')[3:])
                     for el in pres_rels.getElementsByTagName('Relationship'))+1)
relation = pres_rels.createElementNS(REL,'Relationship')
for key,value in [('Id',rid),('Type',NS['r']+'/slide'),('Target',f'slides/slide{slide_index}.xml')]:
    relation.setAttribute(key,value)
pres_rels.documentElement.appendChild(relation)
ids = pres.getElementsByTagName('p:sldIdLst')[0]
old_ids = list(ids.getElementsByTagName('p:sldId'))
new_id = str(max(int(el.getAttribute('id')) for el in old_ids)+1)
element = pres.createElementNS(NS['p'],'p:sldId')
element.setAttribute('id',new_id)
element.setAttributeNS(NS['r'],'r:id',rid)
ids.insertBefore(element,old_ids[2])
for section in pres.getElementsByTagName('p14:sldIdLst'):
    matching = [el for el in section.getElementsByTagName('p14:sldId')
                if el.getAttribute('id') == old_ids[2].getAttribute('id')]
    if matching:
        entry = pres.createElement('p14:sldId')
        entry.setAttribute('id',new_id)
        section.insertBefore(entry,matching[0])
new_parts['ppt/presentation.xml'] = pres.toxml(encoding='utf-8')
new_parts['ppt/_rels/presentation.xml.rels'] = pres_rels.toxml(encoding='utf-8')

types = minidom.parseString(entries['[Content_Types].xml'][1])
for part,content_type in [(slide_part,'application/vnd.openxmlformats-officedocument.presentationml.slide+xml'),
                          (notes_part,'application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml')]:
    entry = types.createElement('Override')
    entry.setAttribute('PartName','/'+part)
    entry.setAttribute('ContentType',content_type)
    types.documentElement.appendChild(entry)
new_parts['[Content_Types].xml'] = types.toxml(encoding='utf-8')
app = minidom.parseString(entries['docProps/app.xml'][1])
for tag in ['Slides','Notes']:
    values = app.getElementsByTagName(tag)
    if values and values[0].firstChild:
        values[0].firstChild.data = str(int(values[0].firstChild.data)+1)
headings = app.getElementsByTagName('HeadingPairs')
if headings:
    variants = headings[0].getElementsByTagName('vt:variant')
    for i, item in enumerate(variants[:-1]):
        if 'Slide Titles' in item.toxml():
            count = variants[i+1].getElementsByTagName('vt:i4')[0]
            count.firstChild.data = str(int(count.firstChild.data)+1)
titles = app.getElementsByTagName('TitlesOfParts')
if titles:
    vector = titles[0].getElementsByTagName('vt:vector')[0]
    vector.setAttribute('size',str(int(vector.getAttribute('size'))+1))
    entry = app.createElement('vt:lpstr')
    entry.appendChild(app.createTextNode('Distributed Hodgkin-Huxley model'))
    existing = vector.getElementsByTagName('vt:lpstr')
    vector.insertBefore(entry,existing[-1])
new_parts['docProps/app.xml'] = app.toxml(encoding='utf-8')

temporary = DECK.with_suffix('.model-update.pptx')
with ZipFile(temporary,'w') as result:
    for name,(info,data) in entries.items():
        result.writestr(info,new_parts.pop(name,data))
    for name,data in new_parts.items():
        result.writestr(name,data)
with ZipFile(temporary) as result:
    assert result.testzip() is None
    for name,data in original_slides.items():
        assert result.read(name) == data, 'An existing slide changed: '+name
    for name in result.namelist():
        if name.endswith(('.xml','.rels')):
            minidom.parseString(result.read(name))
os.replace(temporary,DECK)

# Render the authored slide geometry for layout inspection.
review = pymupdf.open()
page = review.new_page(width=720,height=405)
def rgb(hex_color):
    return tuple(int(hex_color[i:i+2],16)/255 for i in (0,2,4))
for operation in operations:
    kind,*args = operation
    if kind == 'text':
        content,x,y,w,h,size,color,bold = args
        font = 'hebo' if bold else 'helv'
        page.insert_text((x,y+size),content,fontsize=size,fontname=font,color=rgb(color))
    elif kind == 'line':
        x1,y1,x2,y2,color,width,arrow = args
        page.draw_line((x1,y1),(x2,y2),color=rgb(color),width=width)
        if arrow:
            page.draw_polyline([(x2-5,y2-3),(x2,y2),(x2-5,y2+3)],color=rgb(color),width=width)
    elif kind == 'cover':
        x,y,w,h = args
        page.draw_rect(pymupdf.Rect(x,y,x+w,y+h),color=None,fill=(1,1,1))
    elif kind == 'picture':
        filename,x,y,w,h = args
        page.insert_image(pymupdf.Rect(x,y,x+w,y+h),filename=str(ASSETS/filename))
page.insert_text((664,394),'TU/e',fontsize=16,fontname='hebo',color=rgb(RED))
review.save(BUILD/'hh_model_and_schematic_slide.pdf')
page.get_pixmap(matrix=pymupdf.Matrix(1920/720,1920/720)).save(BUILD/'hh_model_and_schematic_slide.png')
print('Inserted the HH equations and schematic as slide 3. Existing comparison is slide 4.')
print('All existing slide XML parts are unchanged. Presentation:',DECK)
