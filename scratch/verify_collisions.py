import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

from src.graph.neo4j_client import Neo4jClient

c = Neo4jClient()
c.connect()

def show(title, q, params=None):
    print(f"\n--- {title} ---")
    print(f"Cypher: {q}")
    res = c.execute_query(q, params or {})
    if not res:
        print("   (no rows)")
    for r in res:
        print(f"   {r}")
    return res

# A. Pure-Cypher: names appearing under 2+ distinct labels
show("A. Names under 2+ distinct labels (pure Cypher)",
     "MATCH (n) WITH n.name AS name, collect(DISTINCT labels(n)) AS lbls, count(*) AS c "
     "WHERE size(lbls) > 1 RETURN name, lbls, c")

# B. Pure-Cypher: any name shared by more than one node at all
show("B. Names shared by >1 node (any labels)",
     "MATCH (n) WITH n.name AS name, count(*) AS c, collect(DISTINCT labels(n)) AS lbls "
     "WHERE c > 1 RETURN name, c, lbls")

# C. Case/whitespace-insensitive collisions in pure Cypher
show("C. trim+toLower name shared by >1 node",
     "MATCH (n) WITH toLower(trim(n.name)) AS k, count(*) AS c, "
     "collect(n.name) AS names, collect(labels(n)) AS lbls "
     "WHERE c > 1 RETURN k, c, names, lbls")

# D. Any node carrying more than one label
show("D. Nodes with >1 label",
     "MATCH (n) WHERE size(labels(n)) > 1 RETURN n.name AS name, labels(n) AS labels")

# E. Nodes with no label
show("E. Nodes with 0 labels",
     "MATCH (n) WHERE size(labels(n)) = 0 RETURN n.name AS name, properties(n) AS props")

# F. The known historical case
show("F. Nodes whose name contains 'Viem loet da day' (unaccented match via CONTAINS on real string)",
     "MATCH (n) WHERE n.name CONTAINS 'loét dạ dày' RETURN n.name AS name, labels(n) AS labels, "
     "size([(n)--() | 1]) AS degree")

# G. Names with leading/trailing whitespace (latent collision risk)
show("G. Names where trim(name) <> name",
     "MATCH (n) WHERE trim(n.name) <> n.name RETURN n.name AS name, labels(n) AS labels")

# H. Relationship + total counts for sanity
show("H. Total nodes / rels",
     "MATCH (n) OPTIONAL MATCH ()-[r]->() RETURN count(DISTINCT n) AS nodes, count(DISTINCT r) AS rels")

c.close()
