import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import json, csv, re, copy, logging
logging.disable(logging.CRITICAL)

from src.config import ICD10_DICT_PATH
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.fuzzy_matcher import FuzzyMatcher
from src.entity_linking.entity_normalizer import get_canonical_name

ROOT = r"c:\Users\thinhlaluot\MedGraph"
AUDIT = ROOT + r"\data\exports\icd10_synonyms_audit.csv"
SYN   = ROOT + r"\data\synthetic\synthetic_data.json"
DUMP  = ROOT + r"\scratch\_graph_dump.json"

# ---------- load ----------
with open(AUDIT, encoding="utf-8-sig") as f:
    audit = [r for r in csv.DictReader(f)]
flagged = [r for r in audit if r["violates_rule"].strip().upper() == "YES"]
print("audit rows:", len(audit), " flagged YES:", len(flagged))

with open(ICD10_DICT_PATH, encoding="utf-8") as f:
    RECORDS = json.load(f)
print("icd10 records:", len(RECORDS))

with open(SYN, encoding="utf-8") as f:
    SAMPLES = json.load(f)
print("samples:", len(SAMPLES))

with open(DUMP, encoding="utf-8") as f:
    G = json.load(f)
NODES, RELS = G["nodes"], G["rels"]

# ---------- surface-form index over the whole dictionary ----------
# surface (lowercased) -> list of (code, kind)
SURFACES = {}
for rec in RECORDS:
    if "name_vi" in rec:
        SURFACES.setdefault(rec["name_vi"].lower(), []).append((rec["code"], "name_vi"))
    for s in rec.get("synonyms", []):
        SURFACES.setdefault(s.lower(), []).append((rec["code"], "synonym"))
print("distinct dictionary surface forms:", len(SURFACES))

_PATTERNS = {s: re.compile(r"\b" + re.escape(s) + r"\b", re.IGNORECASE) for s in SURFACES}

def maximal_matches(text):
    """Return dict surface -> list of (start,end) for matches NOT contained in a longer match."""
    spans = []
    for s, pat in _PATTERNS.items():
        for m in pat.finditer(text):
            spans.append((s, m.start(), m.end()))
    maximal = {}
    for s, a, b in spans:
        contained = any((a >= a2 and b <= b2 and (b2 - a2) > (b - a)) for _, a2, b2 in spans)
        if not contained:
            maximal.setdefault(s, []).append((a, b))
    return maximal

SAMPLE_MAX = {smp["id"]: maximal_matches(smp["text"]) for smp in SAMPLES}
SAMPLE_TEXT = {smp["id"]: smp["text"] for smp in SAMPLES}

# raw substring presence (no maximality filter)
def raw_hits(surface):
    pat = _PATTERNS[surface] if surface in _PATTERNS else re.compile(r"\b"+re.escape(surface)+r"\b", re.IGNORECASE)
    return [smp["id"] for smp in SAMPLES if pat.search(smp["text"])]

def max_hits(surface):
    return [sid for sid, mm in SAMPLE_MAX.items() if surface.lower() in mm]

# ---------- linkers ----------
BASE = ICD10Linker()

class TempLinker(ICD10Linker):
    def __init__(self, records):
        self.dict_path = ICD10_DICT_PATH
        self.records = records
        self.exact_map = self._build_exact_map()
        self.fuzzy_matcher = FuzzyMatcher(score_cutoff=88.0)

def records_without(code, synonym):
    recs = copy.deepcopy(RECORDS)
    hit = False
    for r in recs:
        if r["code"] == code:
            syns = r.get("synonyms", [])
            new = [s for s in syns if s.lower() != synonym.lower()]
            if len(new) != len(syns):
                hit = True
            r["synonyms"] = new
    return recs, hit

def fmt(res):
    return f'{res.get("code")}|{res.get("standard_name")}|{res.get("method")}'

# ---------- graph indexes ----------
node_by_id = {n["nid"]: n for n in NODES}
disease_nodes = [n for n in NODES if "DISEASE" in n["labels"]]
# code -> nodes
nodes_by_code = {}
for n in disease_nodes:
    nodes_by_code.setdefault(n["props"].get("code"), []).append(n)

def rel_samples(r):
    v = r["rprops"].get("source_sample_id") or ""
    return [x.strip() for x in v.split(",") if x.strip()]

# node id -> rels touching it
rels_by_node = {}
for r in RELS:
    pass
# need endpoint ids; re-query if missing
print("rel keys:", sorted(RELS[0].keys()))

REPORT = []
for row in flagged:
    code = row["icd_code"]; synonym = row["synonym"]
    rec = next((r for r in RECORDS if r["code"] == code), None)
    before = BASE.link_disease(synonym)
    recs2, removed_ok = records_without(code, synonym)
    after = TempLinker(recs2).link_disease(synonym)
    expected_name = get_canonical_name(rec["name_vi"]) if rec else None
    REPORT.append(dict(row=row, code=code, synonym=synonym, rec=rec,
                       before=before, after=after, removed_ok=removed_ok,
                       expected_name=expected_name,
                       raw=raw_hits(synonym), mx=max_hits(synonym)))

print()
print("=" * 110)
for e in REPORT:
    print(f'{e["code"]:>7} | {e["synonym"]}')
    print(f'          removed_from_dict={e["removed_ok"]}  expected_node_name={e["expected_name"]!r}')
    print(f'          BEFORE {fmt(e["before"])}   conf={e["before"].get("confidence")}')
    print(f'          AFTER  {fmt(e["after"])}   conf={e["after"].get("confidence")}')
    print(f'          changed={fmt(e["before"]) != fmt(e["after"])}')
    print(f'          raw_sample_hits={e["raw"]}')
    print(f'          maximal_sample_hits={e["mx"]}')
    ex = nodes_by_code.get(e["code"], [])
    print(f'          neo4j nodes with code {e["code"]}: {[(n["nid"], n["props"]["name"]) for n in ex]}')
    print()

with open(ROOT + r"\scratch\_item2e_report.json", "w", encoding="utf-8") as f:
    json.dump([{k: v for k, v in e.items() if k != "rec"} for e in REPORT], f, ensure_ascii=False, indent=1)
print("saved intermediate report")
