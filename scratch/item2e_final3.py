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

SURFACES = set()
for rec in RECORDS:
    SURFACES.add(rec["name_vi"].lower())
    for s in rec.get("synonyms", []):
        SURFACES.add(s.lower())
PAT = {s: re.compile(r"\b" + re.escape(s) + r"\b", re.IGNORECASE) for s in SURFACES}

def maximal_surfaces(text):
    spans = [(s, m.start(), m.end()) for s, p in PAT.items() for m in p.finditer(text)]
    keep = {}
    for s, a, b in spans:
        if not any(a >= a2 and b <= b2 and (b2 - a2) > (b - a) for _, a2, b2 in spans):
            keep.setdefault(s, text[a:b])
    return keep

SMAX = {s["id"]: maximal_surfaces(s["text"]) for s in SAMPLES}

def raw_hits(surface):
    p = PAT.get(surface.lower()) or re.compile(r"\b" + re.escape(surface) + r"\b", re.IGNORECASE)
    return sorted(s["id"] for s in SAMPLES if p.search(s["text"]))
def max_hits(surface):
    return sorted(sid for sid, mm in SMAX.items() if surface.lower() in mm)

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

def sig(res): return (res.get("code"), res.get("standard_name"))
def fmt(res): return f'{res.get("code")}|{res.get("standard_name")}|{res.get("method")}'

DISEASE = [n for n in NODES if "DISEASE" in n["labels"]]
RELS_BY_NODE = {}
for r in RELS:
    RELS_BY_NODE.setdefault(r["aid"], []).append(r)
    RELS_BY_NODE.setdefault(r["bid"], []).append(r)
def rel_samples(r): return [x.strip() for x in (r["rprops"].get("source_sample_id") or "").split(",") if x.strip()]
def rel_label(r): return f'({r["a_name"]})-[:{r["rtype"]}]->({r["b_name"]}) [rid={r["rid"]}]'

NODE_SAMPLES = {}
for n in DISEASE:
    ss = set()
    for r in RELS_BY_NODE.get(n["nid"], []):
        ss |= set(rel_samples(r))
    NODE_SAMPLES[n["nid"]] = sorted(x for x in ss if x in SMAX)

def reproducers(n, linker):
    """sample -> [dictionary surfaces in that sample whose link result == this node's (code,name)]"""
    out = {}
    for sid in NODE_SAMPLES[n["nid"]]:
        hit = [surf for surf, occ in SMAX[sid].items()
               if sig(linker.link_disease(occ)) == (n["props"]["code"], n["props"]["name"])]
        if hit:
            out[sid] = sorted(hit)
    return out

REPRO_BEFORE = {n["nid"]: reproducers(n, BASE) for n in DISEASE}

rows, detail = [], []
for row in flagged:
    code, syn, sl = row["icd_code"], row["synonym"], row["synonym"].lower()
    before = BASE.link_disease(syn)
    tmp    = TempLinker(without(code, syn))
    after  = tmp.link_disease(syn)
    changed = sig(before) != sig(after)
    name_changes = before.get("standard_name") != after.get("standard_name")
    mh, rh = max_hits(syn), raw_hits(syn)

    matched_nodes, aff_nodes, aff_rels, why = [], [], set(), []
    for n in DISEASE:
        rb = REPRO_BEFORE[n["nid"]]
        via = [sid for sid, surfs in rb.items() if sl in surfs]
        if not via:
            continue
        matched_nodes.append(n)
        via_sole = [sid for sid in via if rb[sid] == [sl]]   # S is the ONLY anchor in that sample
        if not via_sole:
            continue                                        # node anchored by another surface everywhere
        ra = reproducers(n, tmp)
        if not ra:
            aff_nodes.append(n)
            why.append(f'node id={n["nid"]} "{n["props"]["name"]}" LOSES code {n["props"]["code"]} -> {after.get("code")}')
            for r in RELS_BY_NODE.get(n["nid"], []):
                aff_rels.add(rel_label(r))
        elif name_changes:
            aff_nodes.append(n)
            why.append(f'node id={n["nid"]} "{n["props"]["name"]}" keeps {n["props"]["code"]} via {sorted(ra)}, '
                       f'but edges from {via_sole} re-route to a node named "{after.get("standard_name")}"')
            for r in RELS_BY_NODE.get(n["nid"], []):
                if set(rel_samples(r)) & set(via_sole):
                    aff_rels.add(rel_label(r))

    reroute_other_code = changed and after.get("code") not in ("ICD-UNKNOWN", before.get("code"))

    if aff_nodes:
        verdict = "BREAKS_EXISTING_NODE"
    elif changed and (mh or matched_nodes or reroute_other_code):
        verdict = "CHANGES_LINKING"
    else:
        verdict = "SAFE_TO_REMOVE"

    rows.append({
        "icd_code": code, "synonym": syn, "classification": row["classification"],
        "appears_in_samples": ";".join(mh) if mh else "NONE",
        "affected_nodes": ";".join(f'{n["props"]["name"]} ({n["props"]["code"]}, id={n["nid"]})' for n in aff_nodes) or "NONE",
        "affected_relationships": ";".join(sorted(aff_rels)) or "NONE",
        "link_before": fmt(before), "link_after": fmt(after), "verdict": verdict,
    })
    detail.append(dict(code=code, syn=syn, verdict=verdict, before=fmt(before), after=fmt(after),
                       changed=changed, raw=rh, mx=mh, reroute=reroute_other_code,
                       matched=[(n["nid"], n["props"]["name"], n["props"]["code"]) for n in matched_nodes],
                       affected=[(n["nid"], n["props"]["name"], n["props"]["code"]) for n in aff_nodes],
                       why=why, rels=sorted(aff_rels)))

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["icd_code","synonym","classification","appears_in_samples",
                                      "affected_nodes","affected_relationships","link_before","link_after","verdict"])
    w.writeheader(); w.writerows(rows)

json.dump(detail, open(ROOT + r"\scratch\_item2e_detail3.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)

from collections import Counter
print("WROTE", OUT, len(rows), "rows")
print(Counter(r["verdict"] for r in rows))
print()
for v in ["BREAKS_EXISTING_NODE", "CHANGES_LINKING"]:
    print("#" * 30, v)
    for d in detail:
        if d["verdict"] != v: continue
        print(f'  {d["code"]} | {d["syn"]}')
        print(f'     before {d["before"]}  ->  after {d["after"]}')
        print(f'     maximal_sample_hits={d["mx"]}   raw_sample_hits={d["raw"]}   reroute_other_code={d["reroute"]}')
        print(f'     matched_nodes={d["matched"]}')
        for w_ in d["why"]: print(f'     ! {w_}')
        for r in d["rels"]: print(f'       REL {r}')
        print()
print("#" * 30, "SAFE_TO_REMOVE")
for d in detail:
    if d["verdict"] == "SAFE_TO_REMOVE":
        print(f'  {d["code"]:>7} | {d["syn"]:<34} before {d["before"]:<50} after {d["after"]:<55} samples={d["mx"] or "NONE"} nodes={d["matched"] or "NONE"}')
