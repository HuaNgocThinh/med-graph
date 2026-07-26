# -*- coding: utf-8 -*-
"""Audit: (1) duplicate/synonym-collision nodes in Neo4j; (2) scan 96 samples for folk<->medical synonym candidates."""
import sys, io, json, re
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
from pathlib import Path
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.entity_normalizer import (
    normalize_disease_name, get_canonical_name, get_term_synonyms, SYNONYM_MAP, ALIAS_MAP
)

c = Neo4jClient()
print("ONLINE:", c.is_online())
rows = c.execute_query("MATCH (n) RETURN labels(n) AS l, n.name AS name")
nodes = [(r['l'][0] if r['l'] else '?', r['name']) for r in rows]
dis = [n for (l, n) in nodes if l in ('DISEASE', 'SYMPTOM')]

print("\n=== (1) NODE COLLISION CHECK (two DISEASE/SYMPTOM nodes resolving to same canonical) ===")
from collections import defaultdict
buckets = defaultdict(list)
for name in dis:
    canon = get_canonical_name(name).lower()
    norm = normalize_disease_name(name).lower()
    buckets[norm].append(name)
collision = False
for key, names in buckets.items():
    if len(set(names)) > 1:
        collision = True
        print("  COLLISION:", key, "<-", names)
if not collision:
    print("  No exact normalize collisions.")

print("\n=== (1b) SYNONYM-LINKED node pairs (two distinct DB nodes that are folk/medical synonyms) ===")
found_pairs = set()
for a in dis:
    syns = {s.lower() for s in get_term_synonyms(a)}
    for b in dis:
        if a == b:
            continue
        if b.lower() in syns:
            pair = tuple(sorted([a, b]))
            if pair not in found_pairs:
                found_pairs.add(pair)
                print("  SYNONYM PAIR (both exist as nodes!):", pair)
if not found_pairs:
    print("  No two distinct nodes are synonyms of each other. (No merge needed.)")

print("\n=== (2) SCAN 96 SAMPLES for disease-like terms & folk synonyms ===")
data = json.load(open(BASE / "data/synthetic/synthetic_data.json", encoding='utf-8'))
print("samples:", len(data))
# Collect all capitalised disease-ish phrases from texts
folk_markers = ['tiểu đường','đái tháo đường','cao huyết áp','tăng huyết áp','đau bao tử','đau dạ dày',
                'viêm loét dạ dày','đau tim','nhồi máu cơ tim','mỡ máu','rối loạn lipid','loạn nhịp',
                'rung nhĩ','tai biến','đột quỵ','nhồi máu não','đau nửa đầu','migraine','gút','gout',
                'copd','phổi tắc nghẽn','suy tim','thận hư','sỏi thận','tiểu đêm']
counts = {}
for item in data:
    t = item['text'].lower()
    for m in folk_markers:
        if m in t:
            counts.setdefault(m, []).append(item['id'])
for m, ids in sorted(counts.items(), key=lambda x: -len(x[1])):
    print(f"  {m!r}: {len(ids)}x  {ids}")
