$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$deckPath = Join-Path $PSScriptRoot 'Closed-loop Control of neural activity dynamics.pptx'
$assetDir = Join-Path $PSScriptRoot 'assets'
$checkDir = Join-Path $projectRoot 'build\hh_neuron_slide'
$slideTitle = 'Distributed Hodgkin-Huxley dynamics'

function Color-Rgb([int]$red, [int]$green, [int]$blue) {
    return $red + 256 * $green + 65536 * $blue
}
$ink = Color-Rgb 37 37 41
$muted = Color-Rgb 100 108 116
$blue = Color-Rgb 0 146 181
$red = Color-Rgb 200 25 25
$white = Color-Rgb 255 255 255

function Add-Text([string]$name, [string]$text, [single]$x, [single]$y,
                  [single]$width, [single]$height, [single]$size,
                  [int]$color, [bool]$bold = $false, [string]$font = 'Aptos') {
    $shape = $script:hhSlide.Shapes.AddTextbox(1, $x, $y, $width, $height)
    $shape.Name = $name
    $shape.TextFrame.MarginLeft = 0
    $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0
    $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.AutoSize = 0
    $shape.TextFrame.TextRange.Text = $text
    $shape.TextFrame.TextRange.Font.Name = $font
    $shape.TextFrame.TextRange.Font.Size = $size
    $shape.TextFrame.TextRange.Font.Color.RGB = $color
    $shape.TextFrame.TextRange.Font.Bold = $(if ($bold) { -1 } else { 0 })
    $shape.TextFrame.TextRange.ParagraphFormat.SpaceBefore = 0
    $shape.TextFrame.TextRange.ParagraphFormat.SpaceAfter = 0
}

function Add-Line([string]$name, [single]$x1, [single]$y1,
                  [single]$x2, [single]$y2, [int]$color, [bool]$arrow = $false) {
    $line = $script:hhSlide.Shapes.AddLine($x1, $y1, $x2, $y2)
    $line.Name = $name
    $line.Line.ForeColor.RGB = $color
    $line.Line.Weight = 1.25
    if ($arrow) { $line.Line.EndArrowheadStyle = 2 }
}

function Add-Cover([string]$name, [single]$x, [single]$y, [single]$w, [single]$h) {
    $shape = $script:hhSlide.Shapes.AddShape(1, $x, $y, $w, $h)
    $shape.Name = $name
    $shape.Fill.ForeColor.RGB = $white
    $shape.Line.Visible = 0
}

function Add-Point([string]$name, [single]$x, [single]$y) {
    $shape = $script:hhSlide.Shapes.AddShape(9, $x-2.5, $y-2.5, 5, 5)
    $shape.Name = $name
    $shape.Fill.ForeColor.RGB = $red
    $shape.Line.Visible = 0
}

# Keep a recovery copy before the first edit. Re-running replaces only our slide.
$backup = Join-Path $checkDir 'presentation_before_hh_slide.pptx'
if (-not (Test-Path -LiteralPath $backup)) {
    Copy-Item -LiteralPath $deckPath -Destination $backup
}

$app = $null
$deck = $null
try {
    # Open without a presentation window; do not launch a visible helper window.
    $app = New-Object -ComObject PowerPoint.Application
    $app.DisplayAlerts = 1
    $app.AutomationSecurity = 3
    $deck = $app.Presentations.Open($deckPath, 0, 0, 0)
    for ($index = $deck.Slides.Count; $index -ge 1; $index--) {
        if ($deck.Slides.Item($index).Tags.Item('CODEX_HH_SLIDE') -eq '1') {
            $deck.Slides.Item($index).Delete()
        }
    }
    $layout = $deck.Slides.Item(2).CustomLayout
    $script:hhSlide = $deck.Slides.AddSlide($deck.Slides.Count+1, $layout)
    $hhSlide.Tags.Add('CODEX_HH_SLIDE', '1')
    $hhSlide.Name = 'Distributed_HH_neuron'
    $titleShape = $hhSlide.Shapes.Title
    $titleShape.TextFrame.TextRange.Text = $slideTitle

    Add-Text 'Scope subtitle' 'Voltage propagates along the axon; ion channels act locally.' 36 76 648 20 14 $muted

    # The paper's soma-axon illustration forms the central image. Add a minimal
    # dendritic tree as editable strokes, explicitly credited as an addition.
    $branches = @(
        @(226,216,181,197), @(181,197,143,164), @(143,164,104,145),
        @(143,164,141,134), @(181,197,176,159), @(176,159,191,137),
        @(224,216,172,216), @(172,216,123,202), @(123,202,92,205),
        @(123,202,103,181), @(225,218,177,238), @(177,238,139,266),
        @(139,266,105,273), @(139,266,133,288), @(177,238,175,270),
        @(175,270,192,288)
    )
    $branchIndex = 0
    foreach ($branch in $branches) {
        Add-Line ('Dendritic branch ' + $branchIndex) $branch[0] $branch[1] $branch[2] $branch[3] $ink
        $branchIndex++
    }
    $picture = $hhSlide.Shapes.AddPicture((Join-Path $assetDir 'brette2015_fig5c_soma_axon.png'), 0, -1, 221, 157, 390, 87.25)
    $picture.Name = 'Soma and axon from Brette 2015 Figure 5C'
    $picture.AlternativeText = 'Soma and axon adapted from Brette (2015), Figure 5C, with schematic dendrites added as editable slide shapes.'
    Add-Cover 'Cover source current-direction arrow' 265 181 80 22
    Add-Cover 'Cover source distance scale label' 348 221 100 24

    Add-Text 'Dendrite anatomy label' 'Dendrites' 82 111 120 24 17 $ink $true
    Add-Text 'Soma anatomy label' 'Soma' 218 263 80 24 17 $ink $true
    Add-Text 'Axon anatomy label' 'Axon' 502 178 90 25 17 $blue $true
    Add-Text 'Applied current label' 'Input I(x,t)' 325 123 120 24 16 $red $false 'Cambria Math'
    Add-Text 'Local state label' 'V(x,t), n(x,t), m(x,t), h(x,t)' 414 135 270 24 14 $ink $false 'Cambria Math'

    Add-Line 'Axon spatial coordinate' 268 254 610 254 $blue $true
    Add-Text 'Proximal spatial coordinate' 'x = 0' 264 264 65 19 13 $blue $false 'Cambria Math'
    Add-Text 'Distal spatial coordinate' 'x = L' 583 264 65 19 13 $blue $false 'Cambria Math'
    Add-Text 'Distance along axon' 'distance along the axon' 353 262 211 18 11 $muted

    $equation = $hhSlide.Shapes.AddPicture((Join-Path $assetDir 'distributed_hh_equations.png'), 0, -1, 172, 306, 435, 42.5)
    $equation.Name = 'Distributed Hodgkin-Huxley cable equation'
    $equation.AlternativeText = 'C_M V_t = (r/(2R)) V_xx + I_app - I_ion. Local ionic currents depend on voltage and the gating states n, m and h.'
    Add-Text 'Model scope' 'Eq. (9) describes the axon; dendrites and soma are shown schematically.' 92 356 590 15 10.5 $muted
    Add-Text 'Image and equation credits' 'Adapted from Brette (2015), Fig. 5C (CC BY); dendrites added. Equation: Martinez et al. (2023), Eq. (9).' 36 374 648 11 7.5 $muted

    $notes = @'
This slide illustrates neuronal anatomy and maps the axon to the distributed Hodgkin-Huxley equations.

Equation scope: Eq. (9) in Martinez et al. (2023) is the uniform single-axon cable equation. The local gating equations are the spatial counterparts of Eq. (8). It is not a population model. Dendrites and soma are anatomy context; modeling them requires branch/compartment geometry and interface conditions, with appropriate channel distributions. Synaptic connections require an additional current/coupling model. Spatial coordinate x denotes distance along the modeled axon, not the horizontal image coordinate; endpoints are schematic.

Illustration: Romain Brette (2015), What Is the Most Realistic Single-Compartment Model of Spike Initiation?, PLoS Computational Biology 11(4):e1004114, Figure 5C. Figure 5B-F are adapted in Brette from reference [31], Brette (2013), Sharpness of spike initiation in neurons explained by compartmentalization, PLoS Computational Biology 9:e1003338.
https://doi.org/10.1371/journal.pcbi.1004114
https://doi.org/10.1371/journal.pcbi.1003338
The soma-axon portion is extracted from the supplied PDF page 10. Original scale text and the current-direction arrow are covered by editable slide shapes. The red input arrow is retained. Dendritic branches and model labels are schematic additions. Source figure is provided under the paper's Creative Commons Attribution license.

Model: Sebastian Martinez et al., Dynamical Models in Neuroscience From a Closed-Loop Control Perspective, IEEE Reviews in Biomedical Engineering 16 (2023), p. 708, Eqs. (8)-(9).
https://doi.org/10.1109/RBME.2022.3180559

Symbols: C_M membrane capacitance; r axon radius; R axial resistivity; I_ion sum of HH sodium, potassium and leak currents; n potassium activation; m sodium activation; h sodium inactivation. All V, n, m and h are fields of x and t. I_app is the externally applied current I in the review. Gating dynamics are omitted from this deliberately simplified slide. For simulation, gating equations/functions, parameters, initial profiles and boundary conditions must also be specified.
'@
    $hhSlide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $notes

    $deck.Save()
    $hhSlide.Export((Join-Path $checkDir 'distributed_hh_slide.png'), 'PNG', 1920, 1080)
    # A one-slide PDF is convenient for reviewing the resulting slide.
    $reviewDeck = $app.Presentations.Add(0)
    $null = $reviewDeck.Slides.InsertFromFile($deckPath, 0, $hhSlide.SlideIndex, $hhSlide.SlideIndex)
    $reviewDeck.PageSetup.SlideWidth = $deck.PageSetup.SlideWidth
    $reviewDeck.PageSetup.SlideHeight = $deck.PageSetup.SlideHeight
    $reviewDeck.SaveAs((Join-Path $checkDir 'distributed_hh_slide.pdf'), 32)
    $reviewDeck.Close()
    Write-Output ('Saved slide ' + $hhSlide.SlideIndex + ' of ' + $deck.Slides.Count + ': ' + $deckPath)
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $app) { $app.Quit() }
}
