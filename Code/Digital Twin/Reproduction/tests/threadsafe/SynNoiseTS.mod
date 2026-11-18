COMMENT
Thread-safe variant of the supplied SynNoise mechanism.
Each instance must receive its own h.Random configured with Random123
and normal(0,1). The Python owner must retain that Random object.
Preserves the original variance: normrand(0,std) uses std as variance,
despite the legacy parameter name.
ENDCOMMENT

NEURON {
    POINT_PROCESS SynNoiseTS
    THREADSAFE
    RANGE i, del, dur, f0, f1, r, torn, std, bias
    ELECTRODE_CURRENT i
    POINTER rng
}
UNITS { (nA) = (nanoamp) }
PARAMETER {
    del=50 (ms)
    dur=200 (ms)
    torn=500 (ms)
    std=0.2 (nA)
    f0=0.001 (nA)
    f1=0.002 (nA)
    r=60
    bias=0 (nA)
}
ASSIGNED {
    ival (nA)
    i (nA)
    amp (nA)
    noise (nA)
    on (1)
    rng
}
VERBATIM
double nrn_random_pick(void*);
void* nrn_random_arg(int);
ENDVERBATIM

INITIAL {
    if (has_rng() == 0) {
VERBATIM
        hoc_execerror("SynNoiseTS requires a private Random123 stream", (char*)0);
ENDVERBATIM
    }
    i=0
    on=0
    net_send(del,1)
}
BEFORE BREAKPOINT {
    if (on) {
        noise = sqrt(std*1(/nA))*normal_draw()*1(nA)
        amp = f0+0.5*(f1-f0)*(tanh((t-torn)/(r/3)/(1(ms))-3)+1)
        ival=amp+noise+bias
    } else {
        ival=0
    }
}
BREAKPOINT { i=ival }
NET_RECEIVE(w) {
    if (flag==1) {
        if (on==0) {
            on=1
            net_send(dur,1)
        } else {
            on=0
        }
    }
}
PROCEDURE setRNG() {
VERBATIM
    void** pv = (void**)(&_p_rng);
    if (ifarg(1)) {
        *pv=nrn_random_arg(1);
    } else {
        hoc_execerror("SynNoiseTS.setRNG requires an h.Random object", (char*)0);
    }
ENDVERBATIM
}
FUNCTION has_rng() {
VERBATIM
    _lhas_rng = _p_rng ? 1.0 : 0.0;
ENDVERBATIM
}
FUNCTION normal_draw() {
VERBATIM
    _lnormal_draw = nrn_random_pick(_p_rng);
ENDVERBATIM
}

