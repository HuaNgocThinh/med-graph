"""
Item 3: remove the false relationships produced by the 'viêm'/'đau' fuzzy-match bug,
after verifying for EACH one that the correct relationship the source text supports is
already present in the graph (item 3a: re-point, do not merely delete).

Root cause (already fixed in src/): NER lifted the bare words 'viêm' (from "giảm viêm"/
"kháng viêm") and 'đau' (from "giảm đau") out of the treatment-intent clause; ICD10Linker
fuzzy-matched 'viêm' -> 'Viêm phổi' J18.9 at 0.90, and 'đau' survived as an unlinked
DISEASE because the stop-word branch still returned a usable standard_name.

Usage: python scratch/fix_meloxicam.py [--apply]
Without --apply it only reports (dry run).
"""
import sys, csv
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.graph.neo4j_client import Neo4jClient

APPLY = "--apply" in sys.argv
neo = Neo4jClient()
if not neo.is_online():
    print("ABORT: Neo4j offline."); sys.exit(1)

# (head, relation, bogus_tail) -> why it is wrong
BOGUS = [
    ("Meloxicam 15mg",  "PRESCRIBED_FOR", "Viêm phổi"),
    ("Meloxicam 7.5mg", "PRESCRIBED_FOR", "Viêm phổi"),
    ("Meloxicam 15mg",  "PRESCRIBED_FOR", "đau"),
    ("Meloxicam 7.5mg", "PRESCRIBED_FOR", "đau"),
    ("Trimebutin 200mg", "PRESCRIBED_FOR", "đau"),
    ("Celecoxib 200mg", "PRESCRIBED_FOR", "đau"),
]

# What each sample's text actually supports, per item 3a
CORRECT = {
    "syn_014": ("Celecoxib 200mg", "Thoái hóa khớp", "Thoái hóa khớp gối"),
    "syn_063": ("Meloxicam 15mg", "Thoát vị đĩa đệm cột sống thắt lưng", "Thoát vị đĩa đệm cột sống thắt lưng"),
    "syn_067": ("Meloxicam 15mg", "Viêm gân vai", "Viêm gân vai"),
    "syn_078": ("Trimebutin 200mg", "Ruột kích thích", "Ruột kích thích"),
    "syn_080": ("Meloxicam 15mg", "Thoái hóa khớp", "Thoái hóa khớp gối hai bên"),
    "syn_091": ("Meloxicam 7.5mg", "Đau lưng dưới", "đau thắt lưng cấp"),
    "syn_096": ("Meloxicam 15mg", "Đau lưng dưới", "đau thắt lưng cấp"),
    # syn_089 deliberately absent: its text says "chẩn đoán xác định đau" -- there is NO
    # valid diagnosis string in the source. Inventing one would be fabrication.
}


def counts():
    n = neo.execute_query("MATCH (n) RETURN count(n) AS c")[0]["c"]
    r = neo.execute_query("MATCH ()-[x]->() RETURN count(x) AS c")[0]["c"]
    s = set()
    for x in neo.execute_query("MATCH ()-[r]->() RETURN r.source_sample_id AS s"):
        for p in str(x["s"] or "").split(","):
            if p.strip():
                s.add(p.strip())
    return n, r, s


n0, r0, s0 = counts()
print("=" * 96)
print(f"TRUOC: nodes={n0} rels={r0} sids={len(s0)}   (APPLY={APPLY})")
print("=" * 96)

log_rows = []
print("\n### BUOC 1: xac minh quan he DUNG da ton tai chua (re-point check)\n")
for sid, (drug, correct_tail, text_dx) in sorted(CORRECT.items()):
    hit = neo.execute_query(
        "MATCH (a)-[r]->(b) WHERE a.name=$a AND b.name=$b AND r.source_sample_id CONTAINS $s "
        "RETURN type(r) AS t, r.source_sample_id AS sid",
        {"a": drug, "b": correct_tail, "s": sid})
    status = "DA CO" if hit else "THIEU -> CAN TAO"
    print(f"  {sid}: '{text_dx}' -> {drug} -[PRESCRIBED_FOR]-> {correct_tail}   [{status}]")
    if hit:
        print(f"        (canh hien co: {hit[0]['t']}, sid={hit[0]['sid']})")
    log_rows.append({"source_sample_id": sid, "action": "VERIFY_CORRECT_EDGE", "head": drug,
                     "relation": "PRESCRIBED_FOR", "tail": correct_tail,
                     "reason": f"van ban chan doan '{text_dx}'", "status": status})

print("\n  syn_089: van ban ghi 'chan doan xac dinh dau' -- KHONG co chuoi chan doan hop le.")
print("           KHONG tu suy dien mot chan doan. Chi xoa canh sai, giu canh TREATS toi trieu chung.")
log_rows.append({"source_sample_id": "syn_089", "action": "NO_REPOINT", "head": "Meloxicam 15mg",
                 "relation": "PRESCRIBED_FOR", "tail": "(khong xac dinh)",
                 "reason": "van ban goc khong chua chan doan hop le ('chan doan xac dinh dau')",
                 "status": "BO NGO - cho nguoi dung quyet"})

print("\n### BUOC 2: cac quan he SAI se bi xoa\n")
to_delete = []
for h, rel, t in BOGUS:
    rows = neo.execute_query(
        f"MATCH (a)-[r:{rel}]->(b) WHERE a.name=$a AND b.name=$b "
        "RETURN r.source_sample_id AS sid", {"a": h, "b": t})
    for row in rows:
        sid = row["sid"]
        reason = ("'viem' tach ra tu 'giam viem'/'khang viem' bi fuzzy-match sang 'Viem phoi' J18.9 @0.90"
                  if t == "Viêm phổi" else
                  "'dau' tach ra tu 'giam dau', khong phai chan doan; node DISEASE 'dau' la rac")
        print(f"  XOA: {h} -[{rel}]-> {t}   sid={sid}")
        print(f"       ly do: {reason}")
        to_delete.append((h, rel, t, sid, reason))
        log_rows.append({"source_sample_id": sid, "action": "DELETE_RELATIONSHIP", "head": h,
                         "relation": rel, "tail": t, "reason": reason, "status": "SAI"})

print(f"\n  Tong quan he se xoa: {len(to_delete)}")

if not APPLY:
    print("\n[DRY RUN] Chua thay doi gi. Chay lai voi --apply de thuc hien.")
else:
    print("\n### BUOC 3: thuc hien\n")
    for h, rel, t, sid, _ in to_delete:
        neo.execute_query(
            f"MATCH (a)-[r:{rel}]->(b) WHERE a.name=$a AND b.name=$b DELETE r",
            {"a": h, "b": t})
        print(f"  da xoa: {h} -[{rel}]-> {t}")
    # Delete the junk :DISEASE 'đau' node only if it is now isolated.
    # Matched on (label, name), never on name alone -- a name-only delete would also remove
    # any legitimate node sharing the name under a different label.
    orph = neo.execute_query(
        "MATCH (n:DISEASE) WHERE n.name='đau' AND NOT (n)--() RETURN count(n) AS c")
    if orph and orph[0]["c"]:
        neo.execute_query("MATCH (n:DISEASE) WHERE n.name='đau' AND NOT (n)--() DELETE n")
        print("  da xoa node rac :DISEASE 'đau' (da co lap)")
        log_rows.append({"source_sample_id": "-", "action": "DELETE_NODE", "head": "đau",
                         "relation": "-", "tail": "-",
                         "reason": "node DISEASE rac sinh tu 'giam dau'; da co lap sau khi xoa canh",
                         "status": "SAI"})
    else:
        print("  node :DISEASE 'đau' VAN CON canh -> khong xoa (can kiem tra tay)")

    n1, r1, s1 = counts()
    print(f"\nSAU: nodes={n1} ({n1-n0:+d})  rels={r1} ({r1-r0:+d})  sids={len(s1)} ({len(s1)-len(s0):+d})")
    lost = s0 - s1
    print(f"SourceSampleID bi mat hoan toan: {len(lost)} {sorted(lost) if lost else '(khong mat cai nao)'}")

out = BASE / "data" / "exports" / "meloxicam_fix_log.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["source_sample_id", "action", "head", "relation", "tail", "reason", "status"])
    w.writeheader(); w.writerows(log_rows)
print(f"\nLog: {out}")
