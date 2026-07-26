import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import csv
import unicodedata
from collections import defaultdict

from src.graph.neo4j_client import Neo4jClient

OUT_CSV = r"c:\Users\thinhlaluot\MedGraph\scratch\label_collisions.csv"

client = Neo4jClient()
if not client.connect():
    print("FATAL: could not connect to Neo4j")
    sys.exit(1)

# ---------- Step 1: pull every node ----------
rows = client.execute_query("MATCH (n) RETURN id(n) AS nid, n.name AS name, labels(n) AS labels")
print(f"TOTAL_NODES = {len(rows)}")

# node count via count() as an independent cross-check
cnt = client.execute_query("MATCH (n) RETURN count(n) AS c")
print(f"COUNT_QUERY  = {cnt}")

# label distribution
dist = client.execute_query(
    "MATCH (n) UNWIND labels(n) AS l RETURN l AS label, count(*) AS c ORDER BY c DESC"
)
print("LABEL_DISTRIBUTION:")
for d in dist:
    print(f"   {d['label']}: {d['c']}")

# nodes with null/missing name
nulls = [r for r in rows if r["name"] is None]
print(f"NODES_WITH_NULL_NAME = {len(nulls)}")
for r in nulls:
    print(f"   id={r['nid']} labels={r['labels']}")

# ---------- Step 2: exact-name grouping ----------
by_name = defaultdict(list)  # name -> list of (nid, tuple(labels))
for r in rows:
    if r["name"] is None:
        continue
    by_name[r["name"]].append((r["nid"], tuple(sorted(r["labels"]))))

exact_conflicts = {}
for name, entries in by_name.items():
    distinct_labelsets = {ls for _, ls in entries}
    flat_labels = set()
    for ls in distinct_labelsets:
        flat_labels.update(ls)
    if len(distinct_labelsets) > 1 or len(entries) > 1:
        exact_conflicts[name] = entries

print(f"\nEXACT_NAME_CONFLICTS (same exact name, >1 node) = {len(exact_conflicts)}")
for name, entries in exact_conflicts.items():
    print(f"   '{name}' -> {entries}")

# ---------- Step 3: near-collisions (case / whitespace / unicode-normalisation) ----------
def norm_key(s):
    # strip surrounding whitespace, collapse internal runs, casefold, NFC-normalise
    t = unicodedata.normalize("NFC", s)
    t = " ".join(t.split())
    return t.casefold()

by_norm = defaultdict(list)
for r in rows:
    if r["name"] is None:
        continue
    by_norm[norm_key(r["name"])].append((r["nid"], r["name"], tuple(sorted(r["labels"]))))

near_conflicts = {}
for k, entries in by_norm.items():
    if len(entries) > 1:
        near_conflicts[k] = entries

print(f"\nNEAR_COLLISION_GROUPS (normalised name shared by >1 node) = {len(near_conflicts)}")
for k, entries in near_conflicts.items():
    print(f"   key='{k}'")
    for nid, nm, ls in entries:
        print(f"       id={nid} name={nm!r} labels={ls}")

# ---------- Step 4: degree + source_sample_id per conflicting node ----------
report_ids = set()
for entries in exact_conflicts.values():
    for nid, _ in entries:
        report_ids.add(nid)
for entries in near_conflicts.values():
    for nid, _, _ in entries:
        report_ids.add(nid)

detail_rows = []
for nid in sorted(report_ids):
    d = client.execute_query(
        "MATCH (n) WHERE id(n)=$nid "
        "RETURN n.name AS name, labels(n) AS labels, "
        "size([(n)--() | 1]) AS degree, "
        "size([(n)-->() | 1]) AS out_degree, "
        "size([(n)<--() | 1]) AS in_degree",
        {"nid": nid},
    )
    if not d:
        continue
    d = d[0]
    e = client.execute_query(
        "MATCH (n)-[r]-(m) WHERE id(n)=$nid "
        "RETURN type(r) AS rel, r.source_sample_id AS sid, m.name AS other, labels(m) AS other_labels",
        {"nid": nid},
    )
    sids = []
    for rec in e:
        s = rec.get("sid")
        if s:
            for part in str(s).split(","):
                part = part.strip()
                if part and part not in sids:
                    sids.append(part)
    detail_rows.append(
        {
            "node_id": nid,
            "name": d["name"],
            "labels": "|".join(sorted(d["labels"])),
            "degree": d["degree"],
            "in_degree": d["in_degree"],
            "out_degree": d["out_degree"],
            "source_sample_ids": ";".join(sids) if sids else "",
            "edges": " || ".join(
                f"{rec['rel']}->{rec['other']}[{'|'.join(sorted(rec['other_labels']))}]" for rec in e
            ),
        }
    )

print("\nCONFLICT_NODE_DETAIL:")
for r in detail_rows:
    print(f"   {r}")

# ---------- CSV output ----------
with open(OUT_CSV, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(
        f,
        fieldnames=[
            "collision_type",
            "group_key",
            "node_id",
            "name",
            "labels",
            "degree",
            "in_degree",
            "out_degree",
            "source_sample_ids",
            "edges",
        ],
    )
    w.writeheader()
    detail_by_id = {r["node_id"]: r for r in detail_rows}
    for name, entries in exact_conflicts.items():
        for nid, _ in entries:
            row = dict(detail_by_id[nid])
            row["collision_type"] = "exact_name"
            row["group_key"] = name
            w.writerow(row)
    for k, entries in near_conflicts.items():
        for nid, _, _ in entries:
            row = dict(detail_by_id[nid])
            row["collision_type"] = "near_collision_normalised"
            row["group_key"] = k
            w.writerow(row)

print(f"\nCSV written: {OUT_CSV} ({len(detail_rows)} conflict nodes, "
      f"{len(exact_conflicts)} exact groups, {len(near_conflicts)} near groups)")

client.close()
