import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import json, re, time, logging
logging.getLogger().setLevel(logging.WARNING)

import requests
from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.entity_linking.icd10_linker import ICD10Linker

HTTP_LOG = []
_orig_get = requests.get
def traced_get(url, *a, **kw):
    r = _orig_get(url, *a, **kw)
    HTTP_LOG.append((url, kw.get("params"), r.status_code))
    return r
requests.get = traced_get

c = Neo4jClient()
assert c.is_online()
nodes = c.execute_query(
    "MATCH (n) RETURN labels(n) AS labels, n.name AS name, n.code AS code, properties(n) AS props "
    "ORDER BY labels(n)[0], n.name"
)
c.close()
print("nodes fetched:", len(nodes))

rx = RxNormLinker()
icd = ICD10Linker()

local_rxcuis = {str(r["rxcui"]) for r in rx.records}
print("local dict rxcuis:", len(local_rxcuis))

PLACEHOLDERS = {"UNKNOWN", "RXCUI-UNKNOWN", "ICD-UNKNOWN", "", None}
RXCUI_RE = re.compile(r"^RXCUI:(\d+)$")
ICD_RE = re.compile(r"^[A-Z]\d{2}(\.\d+)?$")

rows = []
mismatches = []
audit = []

for n in nodes:
    label = n["labels"][0]
    name = n["name"]
    stored = n["code"]
    stored_is_real = stored not in PLACEHOLDERS

    mapped_code = ""
    source = "UNKNOWN"
    conf = ""
    method = ""
    http_before = len(HTTP_LOG)

    if label in ("DRUG", "DRUG_GROUP"):
        res = rx.link_drug(name)
        method = res["method"]
        conf = res["confidence"]
        http_used = len(HTTP_LOG) > http_before
        if stored_is_real:
            mapped_code = stored
            m = RXCUI_RE.match(stored)
            if m:
                if m.group(1) in local_rxcuis:
                    source = "RXNORM_LOCAL"
                elif res["code"] == stored and method == "rxnav_api":
                    source = "RXNAV_API"
                else:
                    source = "UNKNOWN"
            else:
                source = "UNKNOWN"
        else:
            mapped_code = res["code"]
            if res["code"] in PLACEHOLDERS or res["code"] == "RXCUI-UNKNOWN":
                source = "UNKNOWN"
                conf = res["confidence"]
            elif method == "rxnav_api":
                source = "RXNAV_API"
            else:
                source = "RXNORM_LOCAL"
        if stored_is_real and res["code"] != stored:
            mismatches.append((label, name, stored, res["code"], method))

    elif label == "DISEASE":
        res = icd.link_disease(name)
        method = res["method"]
        conf = res["confidence"]
        if stored_is_real:
            mapped_code = stored
            source = "ICD10" if ICD_RE.match(str(stored)) else "UNKNOWN"
        else:
            mapped_code = res["code"]
            source = "ICD10" if ICD_RE.match(str(res["code"])) else "UNKNOWN"
        if stored_is_real and res["code"] != stored:
            mismatches.append((label, name, stored, res["code"], method))

    else:  # SYMPTOM or anything else - no linker exists for these
        method = "no_linker"
        if stored_is_real:
            mapped_code = stored
            source = "ICD10" if ICD_RE.match(str(stored)) else "UNKNOWN"
        else:
            mapped_code = "UNKNOWN"
            source = "UNKNOWN"
        conf = ""

    if source == "UNKNOWN":
        conf = "" if conf in (0.0, None) else conf

    rows.append({
        "entity_name": name,
        "entity_type": label,
        "mapped_code": mapped_code,
        "code_source": source,
        "confidence": conf,
    })
    audit.append((label, name, stored, mapped_code, source, method, conf))

print("\nHTTP calls made during full-graph pass:", len(HTTP_LOG))
for h in HTTP_LOG:
    print("   ", h)

print("\nstored-vs-linker mismatches:", len(mismatches))
for m in mismatches:
    print("   ", m)

# ---- stats ----
from collections import Counter
print("\ncode_source counts:", Counter(r["code_source"] for r in rows))
print("per-type source:", Counter((r["entity_type"], r["code_source"]) for r in rows))

drugs = [r for r in rows if r["entity_type"] == "DRUG"]
real = [r for r in drugs if RXCUI_RE.match(str(r["mapped_code"]))]
unk = [r for r in drugs if not RXCUI_RE.match(str(r["mapped_code"]))]
print(f"\nDRUG nodes total={len(drugs)} real_rxcui={len(real)} unknown={len(unk)} pct={100.0*len(real)/len(drugs):.2f}%")
print("DRUG unknown list:", [(r['entity_name'], r['mapped_code']) for r in unk])

dg = [r for r in rows if r["entity_type"] == "DRUG_GROUP"]
dgreal = [r for r in dg if RXCUI_RE.match(str(r["mapped_code"]))]
print(f"DRUG_GROUP total={len(dg)} real_rxcui={len(dgreal)} -> {[(r['entity_name'], r['mapped_code']) for r in dg]}")

import csv, os
out = r"c:\Users\thinhlaluot\MedGraph\data\exports\entity_linking_status.csv"
os.makedirs(os.path.dirname(out), exist_ok=True)
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["entity_name", "entity_type", "mapped_code", "code_source", "confidence"])
    w.writeheader()
    w.writerows(rows)
print("\nWROTE", out, "rows:", len(rows))
