import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import time, logging
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s:%(name)s:%(message)s")
logging.getLogger("RxNormLinker").setLevel(logging.DEBUG)

import requests
from src.config import RXNAV_API_BASE
from src.entity_linking.rxnorm_linker import RxNormLinker

print("RXNAV_API_BASE =", RXNAV_API_BASE)

# --- instrument requests.get so we can PROVE whether an HTTP call happens ---
HTTP_CALLS = []
_orig_get = requests.get
def traced_get(url, *a, **kw):
    t0 = time.time()
    try:
        r = _orig_get(url, *a, **kw)
        dt = time.time() - t0
        HTTP_CALLS.append((url, kw.get("params"), r.status_code, round(dt, 3)))
        print(f"[HTTP] GET {url} params={kw.get('params')} -> {r.status_code} in {dt:.3f}s")
        print(f"[HTTP] body: {r.text[:300]}")
        return r
    except Exception as e:
        dt = time.time() - t0
        HTTP_CALLS.append((url, kw.get("params"), f"EXC {type(e).__name__}: {e}", round(dt, 3)))
        print(f"[HTTP] GET {url} params={kw.get('params')} -> EXCEPTION {type(e).__name__}: {e} after {dt:.3f}s")
        raise
requests.get = traced_get

linker = RxNormLinker()
print("local dict records:", len(linker.records), " exact_map keys:", len(linker.exact_map))

for name in ["Metformin", "Aspirin", "Ibuprofen", "Rosuvastatin", "Dapagliflozin", "Semaglutide"]:
    HTTP_CALLS.clear()
    t0 = time.time()
    res = linker.link_drug(name)
    dt = time.time() - t0
    print(f"\n=== link_drug({name!r}) -> {res}  [elapsed {dt:.3f}s] http_calls_made={len(HTTP_CALLS)} {HTTP_CALLS}")

print("\n--- DIRECT forced call to the private RxNav method (bypassing local exact map) ---")
t0 = time.time()
direct = linker._call_rxnav_api("Metformin")
print("_call_rxnav_api('Metformin') ->", direct, f"[elapsed {time.time()-t0:.3f}s]")

print("\n--- RAW requests.get straight to RxNav (network reachability proof) ---")
t0 = time.time()
try:
    r = _orig_get(f"{RXNAV_API_BASE}/rxcui.json", params={"name": "Metformin"}, timeout=10)
    print("status:", r.status_code, "elapsed:", round(time.time()-t0, 3), "s")
    print("body:", r.text[:400])
except Exception as e:
    print("RAW CALL FAILED:", type(e).__name__, e, "after", round(time.time()-t0, 3), "s")
