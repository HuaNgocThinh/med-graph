import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import csv
import unicodedata
from collections import defaultdict

from src.graph.neo4j_client import Neo4jClient

OUT = r"c:\Users\thinhlaluot\MedGraph\data\exports\label_collision_scan.csv"

c = Neo4jClient()
c.connect()

rows = c.execute_query(
    "MATCH (n) RETURN elementId(n) AS eid, n.name AS name, labels(n) AS labels, "
    "size([(n)--() | 1]) AS degree, "
    "size([(n)<--() | 1]) AS in_degree, "
    "size([(n)-->() | 1]) AS out_degree "
    "ORDER BY n.name"
)
print(f"nodes fetched: {len(rows)}")


def norm_key(s):
    t = unicodedata.normalize("NFC", s or "")
    return " ".join(t.split()).casefold()


exact_count = defaultdict(int)
norm_count = defaultdict(int)
exact_labels = defaultdict(set)
norm_labels = defaultdict(set)
for r in rows:
    exact_count[r["name"]] += 1
    norm_count[norm_key(r["name"])] += 1
    exact_labels[r["name"]].update(r["labels"])
    norm_labels[norm_key(r["name"])].update(r["labels"])

out_rows = []
for r in rows:
    nm = r["name"]
    nk = norm_key(nm)
    if exact_count[nm] > 1 and len(exact_labels[nm]) > 1:
        ctype = "EXACT_NAME_DIFFERENT_LABELS"
    elif exact_count[nm] > 1:
        ctype = "EXACT_NAME_DUPLICATE_SAME_LABEL"
    elif norm_count[nk] > 1 and len(norm_labels[nk]) > 1:
        ctype = "NEAR_COLLISION_DIFFERENT_LABELS"
    elif norm_count[nk] > 1:
        ctype = "NEAR_COLLISION_SAME_LABEL"
    else:
        ctype = "NONE"

    sids = []
    for e in c.execute_query(
        "MATCH (n)-[rel]-() WHERE elementId(n)=$eid RETURN rel.source_sample_id AS sid",
        {"eid": r["eid"]},
    ):
        s = e.get("sid")
        if s:
            for part in str(s).split(","):
                part = part.strip()
                if part and part not in sids:
                    sids.append(part)

    out_rows.append({
        "name": nm,
        "labels": "|".join(sorted(r["labels"])),
        "label_count_on_node": len(r["labels"]),
        "nodes_with_this_exact_name": exact_count[nm],
        "distinct_labels_for_this_exact_name": len(exact_labels[nm]),
        "normalized_key": nk,
        "nodes_with_this_normalized_key": norm_count[nk],
        "distinct_labels_for_normalized_key": len(norm_labels[nk]),
        "collision_type": ctype,
        "degree": r["degree"],
        "in_degree": r["in_degree"],
        "out_degree": r["out_degree"],
        "source_sample_ids": ";".join(sids),
    })

with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(out_rows[0].keys()))
    w.writeheader()
    w.writerows(out_rows)

summary = defaultdict(int)
for r in out_rows:
    summary[r["collision_type"]] += 1
print("collision_type summary:", dict(summary))
print(f"wrote {len(out_rows)} rows -> {OUT}")
c.close()
