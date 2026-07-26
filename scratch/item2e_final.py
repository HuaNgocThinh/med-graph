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
OUT   = ROOT + r"\data\exports\icd10_removal_impact.csv"

with open(AUDIT, encoding="utf-8-sig") as f:
    audit = list(csv.DictReader(f))
flagged = [r for r in audit if r["violates_rule"].strip().upper() == "YES"]

with open(ICD10_DICT_PATH, encoding="utf-8") as f:
    RECORDS = json.load(f)
with open(ROOT + r"\data\synthetic\synthetic_data.json", encoding="utf-8") as f:
    SAMPLES = json.load(f)
with open(ROOT + r"\scratch\_graph_dump.json", encoding="utf-8") as f:
    NODES = json.load(f)["nodes"]
with open(ROOT + r"\scratch\_rels2.json", encoding="utf-8") as f:
    RELS = json.load(f)

REC_BY_CODE = {r["code"]: r for r in RECORDS}

# ---- dictionary surface index ----
SURF2CODES = {}
for rec in RECORDS:
    SURF2CODES.setdefault(rec["name_vi"].lower(), set()).add(rec["code"])
    for s in rec.get("synonyms", []):
        SURF2CODES.setdefault(s.lower(), set()).add(rec["code"])
PAT = {s: re.compile(r"\b" + re.escape(s) + r"\b", re.IGNORECASE) for s in SURF2CODES}

def maximal(text):
    spans = [(s, m.start(), m.end()) for s, p in PAT.items() for m in p.finditer(text)]
    out = set()
    for s, a, b in spans:
        if not any(a >= a2 and b <= b2 and (b2 - a2) > (b - a) for _, a2, b2 in spans):
            out.add(s)
    return out

SMAX = {s["id"]: maximal(s["text"]) for s in SAMPLES}
STEXT = {s["id"]: s["text"] for s in SAMPLES}

def raw_hits(surface):
    p = PAT.get(surface.lower()) or re.compile(r"\b" + re.escape(surface) + r"\b", re.IGNORECASE)
    return [s["id"] for s in SAMPLES if p.search(s["text"])]

def max_hits(surface):
    return sorted([sid for sid, mm in SMAX.items() if surface.lower() in mm])

# surfaces present maximally in sample sid that resolve to icd code C
def surfaces_for_code(sid, code):
    return sorted(s for s in SMAX[sid] if code in SURF2CODES.get(s, set()))

# ---- linkers ----
BASE = ICD10Linker()
class TempLinker(ICD10Linker):
    def __init__(self, records):
        self.dict_path = ICD10_DICT_PATH
        self.records = records
        self.exact_map = self._build_exact_map()
        self.fuzzy_matcher = FuzzyMatcher(score_cutoff=88.0)

def without(code, synonym):
    recs = copy.deepcopy(RECORDS)
    for r in recs:
        if r["code"] == code:
            r["synonyms"] = [s for s in r.get("synonyms", []) if s.lower() != synonym.lower()]
    return recs

def sig(res):
    return (res.get("code"), res.get("standard_name"))
def fmt(res):
    return f'{res.get("code")}|{res.get("standard_name")}|{res.get("method")}'

# ---- graph indexes ----
DISEASE = [n for n in NODES if "DISEASE" in n["labels"]]
NODE_BY_NAME = {}
for n in DISEASE:
    NODE_BY_NAME.setdefault(n["props"]["name"], []).append(n)

def rel_samples(r):
    return [x.strip() for x in (r["rprops"].get("source_sample_id") or "").split(",") if x.strip()]

RELS_BY_NODE = {}
for r in RELS:
    RELS_BY_NODE.setdefault(r["aid"], []).append(r)
    RELS_BY_NODE.setdefault(r["bid"], []).append(r)

def rel_label(r):
    return f'({r["a_name"]})-[:{r["rtype"]}]->({r["b_name"]}) [rid={r["rid"]}]'

rows = []
detail = []
for row in flagged:
    code, syn = row["icd_code"], row["synonym"]
    rec = REC_BY_CODE.get(code)
    before = BASE.link_disease(syn)
    after = TempLinker(without(code, syn)).link_disease(syn)
    changed = sig(before) != sig(after)
    expected_name = get_canonical_name(rec["name_vi"]) if rec else ""

    rh, mh = raw_hits(syn), max_hits(syn)

    # target node: the node this synonym would have produced
    target_nodes = [n for n in DISEASE if n["props"]["name"] == expected_name]

    aff_nodes, aff_rels, sole_support_nodes = [], [], []
    for n in target_nodes:
        nrels = RELS_BY_NODE.get(n["nid"], [])
        support = {}                    # sample -> surfaces of this code present
        for r in nrels:
            for sid in rel_samples(r):
                if sid in SMAX:
                    support[sid] = surfaces_for_code(sid, code)
        samples_via_syn = [s for s in sorted(support) if syn.lower() in support[s]]
        if not samples_via_syn:
            continue
        aff_nodes.append(n)
        # rels whose source samples include one where the synonym is the live surface
        for r in nrels:
            if set(rel_samples(r)) & set(samples_via_syn):
                aff_rels.append(r)
        # does every supporting sample rely ONLY on this synonym?
        evidenced = {s: v for s, v in support.items() if v}
        if evidenced and all(v == [syn.lower()] for v in evidenced.values()):
            sole_support_nodes.append(n)

    if changed and sole_support_nodes:
        verdict = "BREAKS_EXISTING_NODE"
    elif changed and aff_rels:
        verdict = "BREAKS_EXISTING_NODE" if any(sig(after)[1] != expected_name for _ in [0]) else "CHANGES_LINKING"
    elif changed:
        verdict = "CHANGES_LINKING"
    else:
        verdict = "SAFE_TO_REMOVE"

    rows.append({
        "icd_code": code,
        "synonym": syn,
        "classification": row["classification"],
        "appears_in_samples": ";".join(mh) if mh else "NONE",
        "affected_nodes": ";".join(f'{n["props"]["name"]} ({n["props"]["code"]}, id={n["nid"]})' for n in aff_nodes) or "NONE",
        "affected_relationships": ";".join(sorted({rel_label(r) for r in aff_rels})) or "NONE",
        "link_before": fmt(before),
        "link_after": fmt(after),
        "verdict": verdict,
    })
    detail.append(dict(code=code, syn=syn, expected=expected_name, before=fmt(before), after=fmt(after),
                       changed=changed, raw=rh, mx=mh,
                       aff_nodes=[(n["nid"], n["props"]["name"], n["props"]["code"]) for n in aff_nodes],
                       sole=[(n["nid"], n["props"]["name"]) for n in sole_support_nodes],
                       aff_rels=sorted({rel_label(r) for r in aff_rels}),
                       rel_samples={rel_label(r): rel_samples(r) for r in aff_rels}))

with open(ROOT + r"\scratch\_item2e_detail.json", "w", encoding="utf-8") as f:
    json.dump(detail, f, ensure_ascii=False, indent=1)

for d in detail:
    if d["mx"] or d["aff_nodes"]:
        print(f'{d["code"]:>7} | {d["syn"]}')
        print(f'          before {d["before"]}  -> after {d["after"]}  changed={d["changed"]}')
        print(f'          raw={d["raw"]}  maximal={d["mx"]}')
        print(f'          aff_nodes={d["aff_nodes"]}  sole={d["sole"]}')
        for rl in d["aff_rels"]:
            print(f'            REL {rl}  samples={d["rel_samples"][rl]}')
        print()

from collections import Counter
print(Counter(r["verdict"] for r in rows))
print("total flagged:", len(rows))
