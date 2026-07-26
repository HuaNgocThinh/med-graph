"""Dump every node in Neo4j with label + degree, and flag synonym-collision pairs."""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.entity_normalizer import (
    normalize_disease_name, get_canonical_name, get_term_synonyms, SYNONYM_MAP
)

c = Neo4jClient()
nodes = c.execute_query("""
MATCH (n)
OPTIONAL MATCH (n)-[r]-()
RETURN n.name AS name, labels(n) AS labels, count(r) AS deg
ORDER BY labels(n)[0], n.name
""")
print(f"=== ALL {len(nodes)} NODES ===")
for n in nodes:
    print(f"  [{n['labels'][0] if n['labels'] else '?'}] {n['name']!r} (deg={n['deg']})")

names = [n["name"] for n in nodes if n.get("name")]
lower_to_name = {}
print("\n=== (A) EXACT COLLISION AFTER normalize_disease_name() ===")
groups = {}
for nm in names:
    k = normalize_disease_name(nm).lower()
    groups.setdefault(k, []).append(nm)
hit = False
for k, v in groups.items():
    if len(v) > 1:
        hit = True
        print(f"  {k!r} <- {v}")
if not hit:
    print("  none")

print("\n=== (B) SYNONYM COLLISION (two distinct nodes that are synonyms of each other) ===")
lowset = {nm.lower(): nm for nm in names}
seen = set()
hit = False
for a in names:
    syns = {s.lower().strip() for s in get_term_synonyms(a)}
    # also normalized forms of each synonym
    syns |= {normalize_disease_name(s).lower() for s in syns}
    for b in names:
        if a == b:
            continue
        pair = tuple(sorted([a, b]))
        if pair in seen:
            continue
        b_l = b.lower()
        b_norm = normalize_disease_name(b).lower()
        if b_l in syns or b_norm in syns:
            seen.add(pair)
            hit = True
            print(f"  SYNONYM PAIR: {pair[0]!r}  <->  {pair[1]!r}")
if not hit:
    print("  none")

print("\n=== (C) NODES whose get_canonical_name() differs from stored name ===")
hit = False
for nm in names:
    canon = get_canonical_name(nm)
    if canon != nm:
        hit = True
        print(f"  {nm!r} -> get_canonical_name -> {canon!r}")
if not hit:
    print("  none")
