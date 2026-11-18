"""Bindings for the opt-in thread-safe mechanisms; no shared RNG objects."""
from neuron import h
def bind_noise(noise, cell_id, seed=3695, stream=0):
    rng=h.Random()
    rng.Random123(int(seed),int(cell_id),int(stream))
    rng.normal(0,1)
    noise.setRNG(rng)
    return rng  # Caller must retain this reference for the whole simulation.
def bind_population_noise(populations, seed=3695):
    owners=[]
    for population in populations:
        for cell_id in population:
            if not cell_id.local:continue
            cell=cell_id._cell
            if hasattr(cell,"noise"):
                cell._noise_rng=bind_noise(cell.noise,int(cell_id),seed)
                owners.append(cell._noise_rng)
    return owners
def play_stimulus(cortical_population, values, times):
    for cell_id in cortical_population:
        if not cell_id.local:continue
        cell=cell_id._cell
        cell._dbs_values_owner=values
        cell._dbs_times_owner=times
        for segment in cell.collateral:
            values.play(cell.noise,segment.xtra_ts._ref_stimulus,times,1)
def require_supported_full_network_threads(threads):
    if int(threads)!=1:
        raise RuntimeError(
            "This full network uses NEURON extracellular(), which this backend "
            "does not support with multiple threads. Thread-safe mechanisms alone "
            "do not remove that solver restriction. Use independent processes or "
            "a separately validated distributed-network implementation.")

