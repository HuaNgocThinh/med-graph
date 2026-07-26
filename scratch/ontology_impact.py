"""Measure the blast radius of each pending ontology decision. Read-only."""
import sys, re, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))
from src.graph.neo4j_client import Neo4jClient

c = Neo4jClient()
assert c.is_online()


def rels(name):
    return c.execute_query(
        "MATCH (n {name:$n})-[r]-(m) RETURN type(r) AS t, m.name AS other, "
        "startNode(r).name AS a, endNode(r).name AS b, r.source_sample_id AS sid", {"n": name})


def show(name, tag):
    rows = c.execute_query("MATCH (n {name:$n}) RETURN labels(n)[0] AS l, n.code AS code", {"n": name})
    if not rows:
        print(f"  [{tag}] {name!r}: KHONG CO NODE")
        return
    rr = rels(name)
    print(f"  [{tag}] :{rows[0]['l']} {name!r} code={rows[0]['code']!r}  bac={len(rr)}")
    for r in rr:
        print(f"        ({r['a']})-[:{r['t']}]->({r['b']})   sid={r['sid']}")


print("=" * 96)
print("QUYET DINH 1: 'Cao huyet ap' -> 'Tang huyet ap'")
print("=" * 96)
for n in ("Cao huyết áp", "Tăng huyết áp"):
    show(n, "1")
corpus = json.loads((BASE / "data/synthetic/synthetic_data.json").read_text(encoding="utf-8"))
for pat in ("cao huyết áp", "tăng huyết áp"):
    hits = [r["id"] for r in corpus if pat in r["text"].lower()]
    print(f"    corpus {pat!r}: {len(hits)} mau {hits}")
print("    file/test nhac den:")
import subprocess
out = subprocess.run(["grep", "-rn", "-il", "cao huyết áp", "--include=*.py", "--include=*.json",
                      "src", "app", "tests", "evaluation", "data/dictionaries", "run_pipeline.py"],
                     capture_output=True, text=True, encoding="utf-8").stdout
print("      " + "\n      ".join(out.strip().splitlines()))

print()
print("=" * 96)
print("QUYET DINH 2: ten node thuoc = hoat chat, lieu -> thuoc tinh quan he")
print("=" * 96)
drugs = c.execute_query(
    "MATCH (n:DRUG) OPTIONAL MATCH (n)-[r]-() "
    "RETURN n.name AS name, n.code AS code, count(r) AS deg ORDER BY n.name")
DOSE = re.compile(r"\s*\d+([.,]\d+)?\s*(mg|mcg|g|ml|ui|iu)\b.*$", re.I)
withdose = [d for d in drugs if DOSE.search(d["name"])]
print(f"  Node DRUG: {len(drugs)} | co kem lieu trong ten: {len(withdose)} | khong kem: {len(drugs)-len(withdose)}")
groups = {}
for d in drugs:
    groups.setdefault(DOSE.sub("", d["name"]).strip().lower(), []).append(d)
split = {k: v for k, v in groups.items() if len(v) > 1}
print(f"  Sau khi gop theo hoat chat: {len(groups)} node (giam {len(drugs)-len(groups)})")
print(f"  Hoat chat dang bi tach thanh nhieu node: {len(split)}")
for k, v in split.items():
    print(f"    {k}: " + ", ".join(f"{x['name']}(bac={x['deg']},code={x['code']})" for x in v))
    tgt = {}
    for x in v:
        for r in rels(x["name"]):
            tgt.setdefault(r["other"], []).append(x["name"])
    dup = {t: s for t, s in tgt.items() if len(set(s)) > 1}
    if dup:
        print(f"        -> CUNG TRO TOI: {dup}")
tot_rel = c.execute_query("MATCH (:DRUG)-[r]-() RETURN count(r) AS c")[0]["c"]
print(f"  Quan he cham vao node DRUG (se phai mang them thuoc tinh lieu): {tot_rel}")

print()
print("=" * 96)
print("QUYET DINH 3: 3 ma ICD sai")
print("=" * 96)
for n in ("Viêm loét dạ dày", "Thoái hóa khớp", "Viêm âm đạo do nấm"):
    show(n, "3")

print()
print("=" * 96)
print("QUYET DINH 4 + muc 1e")
print("=" * 96)
for n in ("Viêm phổi", "Viêm phế quản cấp", "Loét dạ dày", "Trào ngược dạ dày thực quản"):
    show(n, "4")
