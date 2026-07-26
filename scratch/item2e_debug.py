import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")
import json, re, logging
logging.disable(logging.CRITICAL)

ROOT = r"c:\Users\thinhlaluot\MedGraph"
SAMPLES = json.load(open(ROOT + r"\data\synthetic\synthetic_data.json", encoding="utf-8"))
T = {s["id"]: s["text"] for s in SAMPLES}
NODES = json.load(open(ROOT + r"\scratch\_graph_dump.json", encoding="utf-8"))["nodes"]
RELS = json.load(open(ROOT + r"\scratch\_rels2.json", encoding="utf-8"))

def rs(r): return [x.strip() for x in (r["rprops"].get("source_sample_id") or "").split(",") if x.strip()]

for nid in [82, 86, 59, 35, 62, 66, 6, 28, 61, 105, 12]:
    n = next(x for x in NODES if x["nid"] == nid)
    print(f'=== node {nid} {n["props"]["name"]} ({n["props"]["code"]})')
    ss = set()
    for r in RELS:
        if r["aid"] == nid or r["bid"] == nid:
            print(f'   {r["a_name"]} -[{r["rtype"]}]-> {r["b_name"]}   samples={rs(r)}')
            ss |= set(rs(r))
    for sid in sorted(ss):
        print(f'   [{sid}] {T.get(sid,"<NO SUCH SAMPLE>")}')
    print()
