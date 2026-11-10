$ErrorActionPreference = 'Stop'
$projectRoot = Split-Path -Parent $PSScriptRoot
$deckPath = Join-Path $PSScriptRoot 'Closed-loop Control of neural activity dynamics.pptx'
$checkDir = Join-Path $projectRoot 'build\hh_neuron_slide'
$assetPath = Join-Path $PSScriptRoot 'assets\brette2015_fig3a_recording_hh.png'
$ink = 37 + 256*37 + 65536*41
$muted = 100 + 256*108 + 65536*116
$modelBlue = 70 + 256*94 + 65536*176

function Add-Text([string]$name, [string]$text, [single]$x, [single]$y,
                  [single]$width, [single]$height, [single]$size, [int]$color) {
    $shape = $script:comparisonSlide.Shapes.AddTextbox(1, $x, $y, $width, $height)
    $shape.Name = $name
    $shape.TextFrame.MarginLeft = 0
    $shape.TextFrame.MarginRight = 0
    $shape.TextFrame.MarginTop = 0
    $shape.TextFrame.MarginBottom = 0
    $shape.TextFrame.WordWrap = -1
    $shape.TextFrame.AutoSize = 0
    $shape.TextFrame.TextRange.Text = $text
    $shape.TextFrame.TextRange.Font.Name = 'Aptos'
    $shape.TextFrame.TextRange.Font.Size = $size
    $shape.TextFrame.TextRange.Font.Color.RGB = $color
    $shape.TextFrame.TextRange.ParagraphFormat.SpaceBefore = 0
    $shape.TextFrame.TextRange.ParagraphFormat.SpaceAfter = 0
}

$app = $null
$deck = $null
try {
    $app = New-Object -ComObject PowerPoint.Application
    $app.DisplayAlerts = 1
    $app.AutomationSecurity = 3
    $deck = $app.Presentations.Open($deckPath, 0, 0, 0)
    for ($index = $deck.Slides.Count; $index -ge 1; $index--) {
        $slide = $deck.Slides.Item($index)
        if (($slide.Tags.Item('CODEX_HH_SLIDE') -eq '1') -or
            ($slide.Tags.Item('CODEX_MODEL_COMPARISON') -eq '1')) {
            $slide.Delete()
        }
    }
    $script:comparisonSlide = $deck.Slides.AddSlide($deck.Slides.Count+1, $deck.Slides.Item(2).CustomLayout)
    $comparisonSlide.Tags.Add('CODEX_MODEL_COMPARISON', '1')
    $comparisonSlide.Name = 'Recording_vs_single_compartment_HH'
    $comparisonSlide.Shapes.Title.TextFrame.TextRange.Text = 'Spike initiation: recording vs. HH'
    Add-Text 'Comparison subtitle' 'Recorded cortical spikes and single-compartment Hodgkin-Huxley examples' 36 76 648 20 14 $muted

    $picture = $comparisonSlide.Shapes.AddPicture($assetPath, 0, -1, 60, 111, 600, 243.01)
    $picture.Name = 'Brette 2015 Figure 3A experimental and HH spike waveforms'
    $picture.AlternativeText = 'Figure 3A from Brette (2015). Left: recorded human pyramidal-cell spikes in vitro. Right: single-compartment Hodgkin-Huxley model spikes for squid giant axon and rat interneuron. Comparison of spike-onset shape across different preparations, not a matched fit to the recorded cell.'

    Add-Text 'Comparison interpretation' 'Spike-onset comparison across different preparations; not a fit to the same cell.' 60 358 620 16 10.5 $muted
    Add-Text 'Figure attribution' 'Brette (2015), Fig. 3A; adapted from Testa-Silva et al. (2014) and Sengupta et al. (2010). CC BY.' 36 378 648 11 7.5 $muted
    $notes = @'
Figure source: Romain Brette (2015), What Is the Most Realistic Single-Compartment Model of Spike Initiation?, PLoS Computational Biology 11(4):e1004114, Figure 3A, supplied PDF page 6.
https://doi.org/10.1371/journal.pcbi.1004114

The left plot shows recorded human pyramidal-cell spikes in vitro. The right traces show single-compartment HH model spikes for squid giant axon and rat interneuron. Brette uses these examples to illustrate a sharper onset (a kink) in the cortical recording than in these single-compartment HH examples. These are different preparations and not the same neuron under identical input. There is no fit-accuracy percentage to report.

The review identifies Figure 3A as adapted from references [18] and [19]: Testa-Silva et al. (2014), High Bandwidth Synaptic Communication and Frequency Tracking in Human Neocortex, PLoS Biology 12:e1002007; Sengupta et al. (2010), Action Potential Energy Efficiency Varies Among Neuron Types in Vertebrates and Invertebrates, PLoS Computational Biology 6:e1000840.
https://doi.org/10.1371/journal.pbio.1002007
https://doi.org/10.1371/journal.pcbi.1000840

Image extracted without changing the plotted data, labels or scale bars. Provided under the article's Creative Commons Attribution license. This slide concerns single-compartment HH examples, not a validation of the distributed HH cable equation or a population model.
'@
    $comparisonSlide.NotesPage.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = $notes
    $deck.Save()
    $comparisonSlide.Export((Join-Path $checkDir 'measurement_model_slide.png'), 'PNG', 1920, 1080)
    $reviewDeck = $app.Presentations.Add(0)
    $null = $reviewDeck.Slides.InsertFromFile($deckPath, 0, $comparisonSlide.SlideIndex, $comparisonSlide.SlideIndex)
    $reviewDeck.PageSetup.SlideWidth = $deck.PageSetup.SlideWidth
    $reviewDeck.PageSetup.SlideHeight = $deck.PageSetup.SlideHeight
    $reviewDeck.SaveAs((Join-Path $checkDir 'measurement_model_slide.pdf'), 32)
    $reviewDeck.Close()
    Write-Output ('Saved slide ' + $comparisonSlide.SlideIndex + ' of ' + $deck.Slides.Count + ': ' + $deckPath)
} finally {
    if ($null -ne $deck) { $deck.Close() }
    if ($null -ne $app) { $app.Quit() }
}
