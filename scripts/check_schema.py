"""
Reports declared-vs-actual Neo4j schema, and for any constraint that cannot be created,
the exact rows that violate it. Read-only: never deletes data to make a constraint fit.

Usage: python scripts/check_schema.py
"""
import sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

sys.path.insert(0, str(BASE / "scripts"))

from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.entity_normalizer import LEGACY_CODE_SENTINELS
from rebuild_rxnorm_dict import strip_dosage

c = Neo4jClient()
if not c.is_online():
    print("Neo4j offline."); sys.exit(1)

print("=" * 84)
print("DECLARED vs ACTUAL SCHEMA")
print("=" * 84)
missing = c.verify_schema()
existing = {r["name"] for r in c.execute_query("SHOW CONSTRAINTS") if r.get("name")}
existing |= {r["name"] for r in c.execute_query("SHOW INDEXES") if r.get("name")}
for n, k, _ in Neo4jClient.DECLARED_SCHEMA:
    print(f"  {'✅ TON TAI' if n in existing else '❌ THIEU  '}  {k:<10} {n}")

print("\n" + "=" * 84)
print("VI PHAM UNIQUENESS (vi sao constraint khong tao duoc)")
print("=" * 84)
for label, prop in (("DISEASE", "code"), ("DRUG", "code")):
    rows = c.execute_query(
        f"MATCH (n:{label}) WHERE n.{prop} IS NOT NULL "
        f"WITH n.{prop} AS v, count(*) AS cnt, collect(n.name) AS names "
        f"WHERE cnt > 1 RETURN v, cnt, names ORDER BY cnt DESC")
    print(f"\n  {label}.{prop}:")
    if not rows:
        print("    (khong vi pham)")
    for r in rows:
        if str(r["v"]).upper() in LEGACY_CODE_SENTINELS:
            kind = "SENTINEL CON SOT (phai la null)"
        elif len({strip_dosage(n).lower() for n in r["names"]}) == 1:
            kind = "CUNG HOAT CHAT, TACH NODE THEO LIEU"
        else:
            kind = "TRUNG MA THAT (hai thuoc khac nhau)"
        print(f"    [{kind}] {r['v']!r} x{r['cnt']}")
        for nm in r["names"][:8]:
            print(f"        - {nm}")

# Item 3c: a node with no code must never be counted as linked.
print("\n" + "=" * 84)
print("DEM DA LINK / CHUA LINK (item 3c)")
print("=" * 84)
for label in ("DISEASE", "DRUG", "SYMPTOM"):
    tot = c.execute_query(f"MATCH (n:{label}) RETURN count(n) AS c")[0]["c"]
    linked = c.execute_query(
        f"MATCH (n:{label}) WHERE n.code IS NOT NULL RETURN count(n) AS c")[0]["c"]
    sent = c.execute_query(
        f"MATCH (n:{label}) WHERE n.code IS NOT NULL AND toUpper(n.code) IN $s "
        f"RETURN count(n) AS c", {"s": sorted(x for x in LEGACY_CODE_SENTINELS if x)})[0]["c"]
    flag = "" if sent == 0 else f"  ⚠️ {sent} node dang bi dem la 'da link' nhung chi mang sentinel!"
    print(f"  {label:<8} {linked}/{tot} co code" + flag)

print("\n" + "=" * 84)
print("KET LUAN")
print("=" * 84)
print("""  'Chua link duoc' gio la null, khong con la chuoi sentinel. Neo4j BO QUA null khi
  kiem tra uniqueness, nen rang buoc da tro nen kha thi -- disease_code IS UNIQUE hien
  DA TON TAI (truoc day chua bao gio ton tai).

  drug_code IS UNIQUE con bi chan boi mot nguyen nhan DUY NHAT va da biet: cung mot
  hoat chat bi tach thanh nhieu node vi ten node co kem lieu (Meloxicam 15mg /
  Meloxicam 7.5mg -> deu la RXCUI:41493). Ma la DUNG; ontology moi la cai sai.
  Xem quyet dinh 2 trong docs/ontology_freeze.md. KHONG xoa du lieu de constraint chay.""")
