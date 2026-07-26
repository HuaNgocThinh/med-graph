import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

from src.graph.neo4j_client import Neo4jClient

c = Neo4jClient()
print("online:", c.is_online())

print("\n--- label counts ---")
for r in c.execute_query("MATCH (n) UNWIND labels(n) AS l RETURN l AS label, count(*) AS cnt ORDER BY cnt DESC"):
    print(r)

print("\n--- sample DRUG node props ---")
for r in c.execute_query("MATCH (n:DRUG) RETURN properties(n) AS p LIMIT 3"):
    print(r)

print("\n--- sample DRUG_GROUP node props ---")
for r in c.execute_query("MATCH (n:DRUG_GROUP) RETURN properties(n) AS p LIMIT 5"):
    print(r)

print("\n--- rel type counts ---")
for r in c.execute_query("MATCH ()-[r]->() RETURN type(r) AS t, count(*) AS cnt ORDER BY cnt DESC"):
    print(r)

c.close()
