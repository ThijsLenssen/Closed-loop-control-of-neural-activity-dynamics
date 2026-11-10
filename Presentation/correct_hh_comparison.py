"""Apply the Figure 3A correction without requiring Office automation."""
from pathlib import Path
from zipfile import ZipFile
from xml.dom import minidom
import os
import pymupdf

root = Path(__file__).resolve().parent.parent
deck = root / 'Presentation/Closed-loop Control of neural activity dynamics.pptx'
asset = root / 'Presentation/assets/brette2015_fig3a_recording_hh.png'
build = root / 'build/hh_neuron_slide'
title = 'Spike initiation: recording vs. HH'
subtitle = 'Recorded cortical spikes and single-compartment Hodgkin-Huxley examples'
caption = 'Spike-onset comparison across different preparations; not a fit to the same cell.'
credit = 'Brette (2015), Fig. 3A; adapted from Testa-Silva et al. (2014) and Sengupta et al. (2010). CC BY.'

with ZipFile(deck) as archive:
    entries = {item.filename: (item, archive.read(item.filename)) for item in archive.infolist()}

doc = minidom.parseString(entries['ppt/slides/slide3.xml'][1])
tree = doc.getElementsByTagName('p:spTree')[0]

def name_of(shape):
    names = shape.getElementsByTagName('p:cNvPr')
    return names[0].getAttribute('name') if names else ''

def set_text(shape, text):
    nodes = shape.getElementsByTagName('a:t')
    assert nodes
    for node in nodes:
        while node.firstChild:
            node.removeChild(node.firstChild)
    nodes[0].appendChild(doc.createTextNode(text))

def position(shape, x, y, w, h):
    transform = shape.getElementsByTagName('a:xfrm')[0]
    off = transform.getElementsByTagName('a:off')[0]
    ext = transform.getElementsByTagName('a:ext')[0]
    for key, value in [('x', x), ('y', y)]:
        off.setAttribute(key, str(round(value * 12700)))
    for key, value in [('cx', w), ('cy', h)]:
        ext.setAttribute(key, str(round(value * 12700)))

remove = {'Measured signal legend', 'Predicted signal legend'}
for shape in list(tree.childNodes):
    if shape.nodeType != shape.ELEMENT_NODE:
        continue
    name = name_of(shape)
    if name in remove or shape.tagName == 'p:cxnSp':
        tree.removeChild(shape)
    elif name == 'Title 1':
        set_text(shape, title)
    elif name == 'Comparison subtitle':
        set_text(shape, subtitle)
    elif name == 'Meaning of reported percentages':
        set_text(shape, caption)
        position(shape, 60, 358, 620, 16)
        shape.getElementsByTagName('p:cNvPr')[0].setAttribute('name', 'Comparison interpretation')
    elif name == 'Figure attribution':
        set_text(shape, credit)
    elif shape.tagName == 'p:pic':
        position(shape, 60, 111, 600, 243.01)
        props = shape.getElementsByTagName('p:cNvPr')[0]
        props.setAttribute('name', 'Brette 2015 Figure 3A experimental and HH spike waveforms')
        props.setAttribute('descr', 'Left: recorded human pyramidal-cell spikes. Right: single-compartment HH waveforms for squid giant axon and rat interneuron. Different preparations, not a matched fit.')

replacements = {'ppt/slides/slide3.xml': doc.toxml(encoding='utf-8')}
# The replaced image must be exclusive to slide 3.
references = [name for name, (_, data) in entries.items()
              if name.endswith('.rels') and b'../media/image5.png' in data]
assert references == ['ppt/slides/_rels/slide3.xml.rels'], references
replacements['ppt/media/image5.png'] = asset.read_bytes()

notes = minidom.parseString(entries['ppt/notesSlides/notesSlide2.xml'][1])
for shape in notes.getElementsByTagName('p:sp'):
    placeholders = shape.getElementsByTagName('p:ph')
    if not placeholders or placeholders[0].getAttribute('type') != 'body':
        continue
    body = shape.getElementsByTagName('p:txBody')[0]
    for paragraph in list(body.getElementsByTagName('a:p')):
        body.removeChild(paragraph)
    text = (
        'Brette (2015), What Is the Most Realistic Single-Compartment Model of Spike Initiation?, '
        'PLoS Computational Biology 11:e1004114, Figure 3A (PDF page 6). '
        'https://doi.org/10.1371/journal.pcbi.1004114\n'
        'Left: recorded human pyramidal-cell action potentials in vitro. Right: single-compartment '
        'HH examples for squid giant axon and rat interneuron. These are different preparations, '
        'not a model fitted to the recorded cell. The comparison concerns spike-onset shape, '
        'not a validation of the distributed HH cable model.\n'
        'Brette credits Testa-Silva et al. (2014), https://doi.org/10.1371/journal.pbio.1002007, '
        'and Sengupta et al. (2010), https://doi.org/10.1371/journal.pcbi.1000840. '
        'Figure reproduced under the article Creative Commons Attribution license. '
        'The original plotted data, labels and scale bars are retained.'
    )
    for line in text.splitlines():
        paragraph = notes.createElement('a:p')
        run = notes.createElement('a:r')
        node = notes.createElement('a:t')
        node.appendChild(notes.createTextNode(line))
        run.appendChild(node)
        paragraph.appendChild(run)
        body.appendChild(paragraph)
replacements['ppt/notesSlides/notesSlide2.xml'] = notes.toxml(encoding='utf-8')
app = entries['docProps/app.xml'][1].replace(b'Neural activity: measurement vs. model', title.encode())
replacements['docProps/app.xml'] = app
temporary = deck.with_suffix('.corrected.pptx')
with ZipFile(temporary, 'w') as archive:
    for name, (info, data) in entries.items():
        archive.writestr(info, replacements.get(name, data))
with ZipFile(temporary) as archive:
    assert archive.testzip() is None
    for name in archive.namelist():
        if name.endswith('.xml'):
            minidom.parseString(archive.read(name))
try:
    os.replace(temporary, deck)
except PermissionError:
    # The original may be open in the user's PowerPoint session. Preserve it
    # and its unsaved changes; the fully edited copy is already validated.
    deck = temporary
    print('Original presentation is locked; corrected presentation saved separately.')

# Standalone review rendering using the same image and slide coordinates.
review = pymupdf.open()
page = review.new_page(width=720, height=405)
ink = (37/255, 37/255, 41/255)
muted = (100/255, 108/255, 116/255)
page.insert_text((36, 55), title, fontsize=25, fontname='hebo', color=ink)
page.insert_text((36, 90), subtitle, fontsize=14, color=muted)
page.insert_image(pymupdf.Rect(60, 111, 660, 354.01), filename=str(asset))
page.insert_text((60, 370), caption, fontsize=10.5, color=muted)
page.insert_text((36, 385), credit, fontsize=7.5, color=muted)
page.insert_text((36, 395), 'Msc Defence T.M. Lenssen', fontsize=8, color=muted)
page.insert_text((664, 394), 'TU/e', fontsize=16, fontname='hebo', color=(.784, .098, .098))
review.save(build / 'measurement_model_slide.pdf')
page.get_pixmap(matrix=pymupdf.Matrix(1920/720, 1920/720)).save(build / 'measurement_model_slide.png')
print('Corrected slide 3 to Figure 3A. Original slides 1 and 2 retained:', deck)
