import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import re
import csv
import json
from collections import defaultdict
from src.graph.neo4j_client import Neo4jClient

DOSAGE_RE = re.compile(r"\d+(?:[.,]\d+)?\s*(?:mg|mcg|ml|g|%|iu|ui)\b|\d+\s*(?:mg|mcg|ml|g)?\s*/\s*(?:tuần|ngày|ml)|\d+\s*%|/\s*tuần",
                       re.IGNORECASE)
# Simpler primary regex the task asked for
TASK_RE = re.compile(r"\d+(?:[.,]\d+)?\s*(mg|mcg|ml|g|%|/tuần)", re.IGNORECASE)

STRIP_RE = re.compile(
    r"\s*\d+(?:[.,]\d+)?\s*(?:mg|mcg|ml|g|iu|ui)(?:\s*/\s*(?:tuần|ngày|ml|kg))?\b"
    r"|\s*\d+(?:[.,]\d+)?\s*/\s*\d+(?:[.,]\d+)?\s*(?:mg|mcg|ml|g)\b"
    r"|\s*\d+(?:[.,]\d+)?\s*%",
    re.IGNORECASE)

c = Neo4jClient()
assert c.is_online()

rows = c.execute_query("""
MATCH (n)
WHERE n:DRUG OR n:DRUG_GROUP
OPTIONAL MATCH (n)-[r]-()
RETURN n.name AS name, n.code AS code, labels(n) AS labels,
       count(r) AS degree
ORDER BY name
""")

# in/out degree detail
detail = c.execute_query("""
MATCH (n)
WHERE n:DRUG OR n:DRUG_GROUP
RETURN n.name AS name,
       size([(n)-[r]->() | r]) AS out_degree,
       size([(n)<-[r]-() | r]) AS in_degree
""")
dmap = {d["name"]: d for d in detail}

print(f"TOTAL drug-ish nodes: {len(rows)}")

with_dose, without_dose = [], []
for r in rows:
    nm = r["name"] or ""
    if TASK_RE.search(nm):
        with_dose.append(r)
    else:
        without_dose.append(r)

print(f"WITH dosage token   : {len(with_dose)}")
print(f"WITHOUT dosage token: {len(without_dose)}")

def base(nm):
    b = STRIP_RE.sub("", nm)
    b = re.sub(r"\s+", " ", b).strip(" -/,").strip()
    return b.lower()

groups = defaultdict(list)
for r in rows:
    groups[base(r["name"])].append(r)

print("\n=== Ingredients mapping to 2+ distinct nodes ===")
multi = {k: v for k, v in groups.items() if len(v) > 1}
if not multi:
    print("(none)")
for k, v in sorted(multi.items()):
    print(f"\nBASE '{k}'  -> {len(v)} nodes")
    for r in v:
        d = dmap.get(r["name"], {})
        print(f"   name={r['name']!r} labels={r['labels']} code={r['code']!r} "
              f"degree={r['degree']} (out={d.get('out_degree')}, in={d.get('in_degree')})")

print("\n=== ALL nodes (name | labels | code | degree | dosage? | base) ===")
for r in rows:
    nm = r["name"] or ""
    print(f"{nm!r:42} | {','.join(r['labels']):10} | {r['code']!r:20} | deg={r['degree']:<3} | "
          f"dosage={'Y' if TASK_RE.search(nm) else 'N'} | base={base(nm)!r}")

out_csv = r"c:\Users\thinhlaluot\MedGraph\data\exports\drug_naming_consistency_survey.csv"
with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["name", "labels", "code", "degree", "out_degree", "in_degree",
                "has_dosage_token", "base_ingredient", "nodes_sharing_base"])
    for r in rows:
        nm = r["name"] or ""
        b = base(nm)
        d = dmap.get(nm, {})
        w.writerow([nm, "|".join(r["labels"]), r["code"], r["degree"],
                    d.get("out_degree"), d.get("in_degree"),
                    "Y" if TASK_RE.search(nm) else "N", b, len(groups[b])])
print(f"\nCSV written: {out_csv}")

c.close()
