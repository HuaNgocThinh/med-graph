import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

from src.graph.neo4j_client import Neo4jClient

c = Neo4jClient()
print("ONLINE:", c.is_online())

q = [
    ("total_nodes", "MATCH (n) RETURN count(n) AS v"),
    ("total_rels", "MATCH ()-[r]->() RETURN count(r) AS v"),
    ("distinct_names", "MATCH (n) RETURN count(DISTINCT n.name) AS v"),
]
for k, s in q:
    print(k, "=", c.execute_query(s)[0]["v"])

print("\n-- label distribution --")
for r in c.execute_query("MATCH (n) UNWIND labels(n) AS l RETURN l AS label, count(*) AS c ORDER BY c DESC"):
    print(f"   {r['label']}: {r['c']}")

print("\n-- A: exact name shared by >1 node (any label) --")
rows = c.execute_query(
    "MATCH (n) WITH n.name AS name, count(*) AS c, collect(DISTINCT labels(n)[0]) AS lbls "
    "WHERE c > 1 RETURN name, c, lbls ORDER BY name")
print("   groups =", len(rows))
for r in rows:
    print("   ", r)

print("\n-- B: case/whitespace-insensitive name shared by >1 node --")
rows = c.execute_query(
    "MATCH (n) WITH toLower(trim(n.name)) AS k, count(*) AS c, collect(n.name) AS names, "
    "collect(labels(n)[0]) AS lbls WHERE c > 1 RETURN k, c, names, lbls ORDER BY k")
print("   groups =", len(rows))
for r in rows:
    print("   ", r)

print("\n-- C: names that exist under BOTH a DISEASE-ish and a SYMPTOM-ish label --")
rows = c.execute_query(
    "MATCH (a:DISEASE), (b:SYMPTOM) WHERE toLower(trim(a.name)) = toLower(trim(b.name)) "
    "RETURN a.name AS disease_name, b.name AS symptom_name")
print("   pairs =", len(rows))
for r in rows:
    print("   ", r)

print("\n-- D: CSV-level collision: same (Head,Relation,Tail) triple exported from different label pairs --")
rows = c.execute_query(
    "MATCH (h)-[r]->(t) WITH h.name AS H, type(r) AS R, t.name AS T, "
    "collect(DISTINCT labels(h)[0] + '->' + labels(t)[0]) AS labelpairs, count(*) AS c "
    "WHERE c > 1 RETURN H, R, T, labelpairs, c")
print("   groups =", len(rows))
for r in rows:
    print("   ", r)

c.close()
