"""Compatibility entry point; component choices are in start_simulation.py."""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from start_simulation import create_simulation
from simulation_runner import run_cli

if __name__ == "__main__":
    run_cli(create_simulation)
