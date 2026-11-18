"""Append-only scalar observations for the local dashboard."""
import json
import math

class Observer:
    def __init__(self, path):
        self.file = path.open("w", encoding="utf-8", buffering=1)

    def __call__(self, time_s, beta_uv, amplitude_ma):
        values = (time_s, beta_uv, amplitude_ma)
        if not all(math.isfinite(v) for v in values):
            return
        self.file.write(json.dumps(dict(zip(
            ("time_s", "beta_uv", "amplitude_ma"), values)), allow_nan=False) + "\n")

    def close(self):
        self.file.close()
