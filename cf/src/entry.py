"""Minimal Python Worker: FastAPI + scipy smoke test."""
from fastapi import FastAPI
from workers import asgi
from scipy.stats import nbinom

app = FastAPI()


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.get("/probe")
async def probe():
    import time
    import numpy as np
    from scipy.stats import nbinom as nb

    t = time.perf_counter()
    q = np.maximum.accumulate(
        np.array([nb.ppf(0.1, 10.0, 0.5), nb.ppf(0.5, 10.0, 0.5), nb.ppf(0.9, 10.0, 0.5)], dtype=int)
    )
    return {"quantiles": [int(x) for x in q], "ms": round((time.perf_counter() - t) * 1000, 3), "numpy": np.__version__}


Default = asgi.entrypoint(app)
