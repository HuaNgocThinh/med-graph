import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import json, csv, re, copy, logging
logging.disable(logging.CRITICAL)

from src.config import ICD10_DICT_PATH
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.fuzzy_matcher import FuzzyMatcher

ROOT = r"c:\Users\thinhlaluot\MedGraph"
OUT  = ROOT + r"\data\exports\icd10_removal_impact.csv"

with open(ROOT + r"\data\exports\icd10_synonyms_audit.csv", encoding="utf-8-sig") as f:
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

# ---------- dictionary surface index ----------
SURFACES = set()
for rec in RECORDS:
    SURFACES.add(rec["name_vi"].lower())
    for s in rec.get("synonyms", []):
        SURFACES.add(s.lower())
PAT = {s: re.compile(r"\b" + re.escape(s) + r"\b", re.IGNORECASE) for s in SURFACES}

def maximal_surfaces(text):
    """dict surface forms present in text, keeping only spans not strictly inside a longer span."""
    spans = [(s, m.start(), m.end()) for s, p in PAT.items() for m in p.finditer(text)]
    keep = {}
    for s, a, b in spans:
        if not any(a >= a2 and b <= b2 and (b2 - a2) > (b - a) for _, a2, b2 in spans):
            keep.setdefault(s, text[a:b])          # keep original casing of the occurrence
    return keep

SMAX  = {s["id"]: maximal_surfaces(s["text"]) for s in SAMPLES}
STEXT = {s["id"]: s["text"] for s in SAMPLES}

def raw_hits(surface):
    p = PAT.get(surface.lower()) or re.compile(r"\b" + re.escape(surface) + r"\b", re.IGNORECASE)
    return sorted(s["id"] for s in SAMPLES if p.search(s["text"]))

def max_hits(surface):
    return sorted(sid for sid, mm in SMAX.items() if surface.lower() in mm)

# ---------- linkers ----------
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

def sig(res):  return (res.get("code"), res.get("standard_name"))
def fmt(res):  return f'{res.get("code")}|{res.get("standard_name")}|{res.get("method")}'

# ---------- graph ----------
DISEASE = [n for n in NODES if "DISEASE" in n["labels"]]
RELS_BY_NODE = {}
for r in RELS:
    RELS_BY_NODE.setdefault(r["aid"], []).append(r)
    RELS_BY_NODE.setdefault(r["bid"], []).append(r)
def rel_samples(r):
    return [x.strip() for x in (r["rprops"].get("source_sample_id") or "").split(",") if x.strip()]
def rel_label(r):
    return f'({r["a_name"]})-[:{r["rtype"]}]->({r["b_name"]}) [rid={r["rid"]}]'

# node -> supporting sample ids (from every rel touching it)
NODE_SAMPLES = {}
for n in DISEASE:
    ss = set()
    for r in RELS_BY_NODE.get(n["nid"], []):
        ss |= set(rel_samples(r))
    NODE_SAMPLES[n["nid"]] = sorted(x for x in ss if x in SMAX)

# which samples currently REPRODUCE node n exactly (code+name) from a dictionary surface?
def reproducers(n, linker):
    out = {}
    for sid in NODE_SAMPLES[n["nid"]]:
        hit = []
        for surf, occ in SMAX[sid].items():
            res = linker.link_disease(occ)
            if res.get("code") == n["props"]["code"] and res.get("standard_name") == n["props"]["name"]:
                hit.append(surf)
        if hit:
            out[sid] = sorted(hit)
    return out

REPRO_BEFORE = {n["nid"]: reproducers(n, BASE) for n in DISEASE}

rows, detail = [], []
for row in flagged:
    code, syn = row["icd_code"], row["synonym"]
    before = BASE.link_disease(syn)
    tmp    = TempLinker(without(code, syn))
    after  = tmp.link_disease(syn)
    changed = sig(before) != sig(after)

    mh, rh = max_hits(syn), raw_hits(syn)

    # nodes this synonym currently reproduces exactly
    aff_nodes, aff_rels, breaks = [], set(), []
    for n in DISEASE:
        rb = REPRO_BEFORE[n["nid"]]
        via = [sid for sid, surfs in rb.items() if syn.lower() in surfs]
        if not via:
            continue
        aff_nodes.append(n)
        ra = reproducers(n, tmp)          # after removing this one synonym
        lost_code = bool(rb) and not ra
        if lost_code:
            breaks.append((n, "loses ICD code -> " + after.get("code", "?")))
            for r in RELS_BY_NODE.get(n["nid"], []):
                aff_rels.add(rel_label(r))
        else:
            # node survives via other evidence; only the S-sourced edges are re-linked
            if sig(before)[1] != sig(after)[1]:
                breaks.append((n, "edges from S re-route to node named " + str(sig(after)[1])))
            for r in RELS_BY_NODE.get(n["nid"], []):
                if set(rel_samples(r)) & set(via):
                    aff_rels.add(rel_label(r))

    reroute_other_code = changed and after.get("code") not in ("ICD-UNKNOWN", before.get("code"))

    if breaks:
        verdict = "BREAKS_EXISTING_NODE"
    elif changed and (mh or aff_nodes or reroute_other_code):
        verdict = "CHANGES_LINKING"
    elif changed:
        verdict = "SAFE_TO_REMOVE"
    else:
        verdict = "SAFE_TO_REMOVE"

    rows.append({
        "icd_code": code, "synonym": syn, "classification": row["classification"],
        "appears_in_samples": ";".join(mh) if mh else "NONE",
        "affected_nodes": ";".join(f'{n["props"]["name"]} ({n["props"]["code"]}, id={n["nid"]})' for n in aff_nodes) or "NONE",
        "affected_relationships": ";".join(sorted(aff_rels)) or "NONE",
        "link_before": fmt(before), "link_after": fmt(after), "verdict": verdict,
    })
    detail.append(dict(code=code, syn=syn, before=fmt(before), after=fmt(after), changed=changed,
                       raw=rh, mx=mh, reroute=reroute_other_code,
                       nodes=[(n["nid"], n["props"]["name"], n["props"]["code"]) for n in aff_nodes],
                       breaks=[(n["nid"], n["props"]["name"], why) for n, why in breaks],
                       rels=sorted(aff_rels), verdict=verdict))

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["icd_code","synonym","classification","appears_in_samples",
                                      "affected_nodes","affected_relationships","link_before","link_after","verdict"])
    w.writeheader(); w.writerows(rows)
print("WROTE", OUT, len(rows), "rows")

with open(ROOT + r"\scratch\_item2e_detail2.json", "w", encoding="utf-8") as f:
    json.dump(detail, f, ensure_ascii=False, indent=1)

from collections import Counter
print(Counter(r["verdict"] for r in rows))
print()
for d in detail:
    if d["verdict"] != "SAFE_TO_REMOVE" or d["mx"] or d["nodes"]:
        print(f'[{d["verdict"]}] {d["code"]} | {d["syn"]}')
        print(f'    before {d["before"]}   after {d["after"]}   reroute_other_code={d["reroute"]}')
        print(f'    raw_hits={d["raw"]}  maximal_hits={d["mx"]}')
        print(f'    nodes={d["nodes"]}')
        print(f'    breaks={d["breaks"]}')
        for r in d["rels"]:
            print(f'      REL {r}')
        print()
