COMMENT
Thread-safe local-input variant of xtra.mod.
stimulus is RANGE, not a shared GLOBAL. Bind im and ex only to data
owned by the same cell. Drive stimulus using Vector.play with a
point-process owner on that cell.
The NEURON extracellular solver remains separately restricted.
ENDCOMMENT
NEURON {
    SUFFIX xtra_ts
    THREADSAFE
    RANGE rx, er, x, y, z, stimulus
    POINTER im, ex
}
PARAMETER {
    rx=1 (megohm)
    x=0 (1)
    y=0 (1)
    z=0 (1)
    stimulus=0 (milliamp)
}
ASSIGNED {
    v (millivolts)
    ex (millivolts)
    im (milliamp/cm2)
    er (microvolts)
    area (micron2)
}
INITIAL {
    ex=stimulus*rx*1e6
    er=10*rx*im*area
}
BEFORE BREAKPOINT { ex=stimulus*rx*1e6 }
AFTER SOLVE { er=10*rx*im*area }

