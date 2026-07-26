import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import re, json, requests
from src.graph.neo4j_client import Neo4jClient

B = "https://rxnav.nlm.nih.gov/REST"

c = Neo4jClient(); c.is_online()
rows = c.execute_query(
    "MATCH (n) WHERE n:DRUG OR n:DRUG_GROUP RETURN labels(n)[0] AS lbl, n.name AS name, n.code AS code ORDER BY n.name"
)
c.close()

RX = re.compile(r"^RXCUI:(\d+)$")
ok = bad = unresolvable = 0
print(f"{'name':38} {'stored':14} {'RxNav name for stored rxcui':38} verdict")
for r in rows:
    m = RX.match(str(r["code"]))
    if not m:
        continue
    cui = m.group(1)
    resp = requests.get(f"{B}/rxcui/{cui}/property.json", params={"propName": "RxNorm Name"}, timeout=10)
    try:
        pv = resp.json()["propConceptGroup"]["propConcept"][0]["propValue"]
    except Exception:
        pv = "<no concept / inactive>"
        unresolvable += 1
    node_head = re.split(r"\s*\d", r["name"])[0].strip().lower()
    verdict = "MATCH" if pv != "<no concept / inactive>" and (
        pv.lower().startswith(node_head[:6]) or node_head.startswith(pv.lower()[:6])
    ) else "MISMATCH"
    if verdict == "MATCH":
        ok += 1
    else:
        bad += 1
    print(f"{r['name'][:38]:38} {r['code']:14} {pv[:38]:38} {verdict}")

print(f"\nverified MATCH={ok}  MISMATCH={bad}  (of which rxcui not resolvable at RxNav={unresolvable})")
