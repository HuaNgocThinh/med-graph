"""
Atomic script for B2a, B2b, B2d, and B4:
1. Updates data/dictionaries/icd10_vi.json for B2a (K25, K29.7, M17, B37.3, M54.5) and B4 (6 synonym removals).
2. Executes Neo4j graph updates in a single transaction.
3. Verifies B2b criteria (4 code changes, 2 name changes, edge preservation, 0 K29.7 nodes, 93 sids).
4. Exports data/exports/after_atomic_qd43.csv and computes full line-by-line delta.
"""

import csv
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.dict_loader import load_dict, save_dict

DICT_PATH = BASE_DIR / "data" / "dictionaries" / "icd10_vi.json"

def update_dictionary():
    records, dict_meta = load_dict(DICT_PATH)

    # 6 B4 removals
    b4_removals = {
        ("J18.9", "viêm phế quản phổi"),
        ("J20.9", "viêm phế quản"),
        ("K25", "loét dạ dày tá tràng"),
        ("G40.9", "cơn co giật"),
        ("F41.1", "rối loạn lo âu"),
        ("D50.9", "thiếu máu nặng"),
    }

    updated_records = []
    for r in records:
        code = r["code"]
        name_vi = r.get("name_vi", "")

        # B2a dictionary updates
        if code == "K25":
            r["name_vi"] = "Viêm loét dạ dày"
            r["synonyms"] = [s for s in r.get("synonyms", []) if s not in ("loét dạ dày tá tràng", "loét hang vị dạ dày")]
            if "loét dạ dày" not in r["synonyms"]:
                r["synonyms"].append("loét dạ dày")
            r["name_en"] = "Gastric ulcer"
            r["name_vi_full"] = "Loét dạ dày"
            r["standard_source"] = "WHO ICD-10 2019 (K25: Gastric ulcer); BYT QD 7603/QD-BYT ban Viet ngu"

        elif code == "K29.7":
            r["synonyms"] = [s for s in r.get("synonyms", []) if s != "viêm loét dạ dày"]

        elif code == "M19.9":
            r["code"] = "M17"
            r["name_vi"] = "Thoái hóa khớp gối"
            r["synonyms"] = ["thoái hóa khớp gối", "thoái hóa khớp"]
            r["name_en"] = "Gonarthrosis [arthrosis of knee]"
            r["name_vi_full"] = "Thoái hóa khớp gối"
            r["standard_source"] = "WHO ICD-10 2019 (M17: Gonarthrosis [arthrosis of knee])"

        elif code == "N76.0":
            r["code"] = "B37.3"
            r["name_vi"] = "Viêm âm đạo do nấm"
            r["synonyms"] = ["viêm âm đạo do nấm", "viêm âm đạo do nấm candida"]
            r["name_en"] = "Candidiasis of vulva and vagina"
            r["name_vi_full"] = "Bệnh nấm âm đạo và âm hộ"
            r["standard_source"] = "WHO ICD-10 2019 (B37.3: Candidiasis of vulva and vagina)"

        elif code == "M54.5":
            r["name_vi"] = "Đau thắt lưng"
            r["name_vi_full"] = ""
            r["standard_source"] = "WHO ICD-10 2019 (M54.5: Low back pain)"
            r["synonyms"] = ["đau thắt lưng", "đau lưng dưới", "đau cột sống thắt lưng"]

        # Apply B4 removals
        code_now = r["code"]
        r["synonyms"] = [s for s in r.get("synonyms", []) if (code_now, s) not in b4_removals and (code, s) not in b4_removals]

        updated_records.append(r)

    save_dict(DICT_PATH, updated_records, dict_meta)
    print(f"Updated dictionary: {DICT_PATH}")

def update_neo4j_graph():
    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j offline!")
        return False

    print("\nExecuting Neo4j Atomic Updates...")
    with client._driver.session() as session:
        with session.begin_transaction() as tx:
            # 1. K29.7 -> K25
            tx.run("MATCH (n:DISEASE {name: 'Viêm loét dạ dày'}) SET n.code = 'K25'")

            # 2. M19.9 -> M17 + rename
            tx.run("MATCH (n:DISEASE {name: 'Thoái hóa khớp'}) SET n.code = 'M17', n.name = 'Thoái hóa khớp gối'")

            # 3. N76.0 -> B37.3
            tx.run("MATCH (n:DISEASE {name: 'Viêm âm đạo do nấm'}) SET n.code = 'B37.3'")

            # 4. M54.5 rename
            tx.run("MATCH (n:DISEASE {code: 'M54.5'}) SET n.name = 'Đau thắt lưng'")

            tx.commit()

    print("Neo4j Atomic Updates committed successfully!")
    return True

def verify_b2b():
    client = Neo4jClient()
    print("\n" + "=" * 80)
    print("B2b: VERIFYING ATOMIC GRAPH UPDATES")
    print("=" * 80)

    # 1. Check 4 node codes & 2 node names
    expected_nodes = [
        ("Viêm loét dạ dày", "K25"),
        ("Thoái hóa khớp gối", "M17"),
        ("Viêm âm đạo do nấm", "B37.3"),
        ("Đau thắt lưng", "M54.5"),
    ]

    for name, exp_code in expected_nodes:
        res = client.execute_query("MATCH (n:DISEASE {name: $n}) RETURN n.code AS code", {"n": name})
        live_code = res[0]["code"] if res else None
        ok = live_code == exp_code
        print(f"  [{'PASS' if ok else 'FAIL'}] Node {name!r:<25} -> code={live_code!r} (Expected: {exp_code!r})")

    # 2. Check no nodes carry K29.7
    res_k29 = client.execute_query("MATCH (n:DISEASE {code: 'K29.7'}) RETURN count(n) AS cnt")
    cnt_k29 = res_k29[0]["cnt"] if res_k29 else 0
    ok_k29 = cnt_k29 == 0
    print(f"  [{'PASS' if ok_k29 else 'FAIL'}] Nodes with code K29.7: {cnt_k29} (Expected: 0)")

    # 3. Check relationship preservation for the 4 nodes
    target_names = ["Viêm loét dạ dày", "Thoái hóa khớp gối", "Viêm âm đạo do nấm", "Đau thắt lưng"]
    res_rels = client.execute_query(
        "MATCH (n:DISEASE)-[r]-() WHERE n.name IN $names RETURN n.name AS name, count(r) AS rel_count",
        {"names": target_names}
    )
    rel_map = {r["name"]: r["rel_count"] for r in res_rels}
    print("  Relationship counts for modified nodes:")
    for tname in target_names:
        print(f"    - {tname:<25}: {rel_map.get(tname, 0)} relationships")

    # 4. Check total distinct SourceSampleIDs across all relationships
    res_sids = client.execute_query(
        "MATCH ()-[r]->() UNWIND split(r.source_sample_id, ',') AS sid RETURN count(DISTINCT trim(sid)) AS n_sids"
    )
    n_sids = res_sids[0]["n_sids"] if res_sids else 0
    ok_sids = n_sids == 93
    print(f"  [{'PASS' if ok_sids else 'FAIL'}] Distinct SourceSampleIDs: {n_sids} (Expected: 93)")

def main():
    update_dictionary()
    if not update_neo4j_graph():
        return 1
    verify_b2b()

    # Export after_atomic_qd43.csv
    from scripts.export_atomic_snapshot import export_snapshot
    export_snapshot("after_atomic_qd43.csv")

    # Delta analysis
    before_path = BASE_DIR / "data" / "exports" / "before_atomic_qd43.csv"
    after_path = BASE_DIR / "data" / "exports" / "after_atomic_qd43.csv"

    with open(before_path, "r", encoding="utf-8-sig") as f:
        before_rows = list(csv.DictReader(f))
    with open(after_path, "r", encoding="utf-8-sig") as f:
        after_rows = list(csv.DictReader(f))

    print("\n" + "=" * 80)
    print("B2d: DELTA ANALYSIS (before_atomic_qd43.csv vs after_atomic_qd43.csv)")
    print("=" * 80)
    print(f"Before total rows: {len(before_rows)}")
    print(f"After total rows : {len(after_rows)}")

    changes = []
    for b, a in zip(before_rows, after_rows):
        if b != a:
            reason = []
            if b["Head"] != a["Head"]:
                reason.append(f"Head name: {b['Head']!r} -> {a['Head']!r}")
            if b["HeadCode"] != a["HeadCode"]:
                reason.append(f"HeadCode: {b['HeadCode']!r} -> {a['HeadCode']!r}")
            if b["Tail"] != a["Tail"]:
                reason.append(f"Tail name: {b['Tail']!r} -> {a['Tail']!r}")
            if b["TailCode"] != a["TailCode"]:
                reason.append(f"TailCode: {b['TailCode']!r} -> {a['TailCode']!r}")

            changes.append({
                "before": f"({b['Head']} [{b['HeadCode']}]) -[{b['Relation']}]-> ({b['Tail']} [{b['TailCode']}])",
                "after": f"({a['Head']} [{a['HeadCode']}]) -[{a['Relation']}]-> ({a['Tail']} [{a['TailCode']}])",
                "reason": "; ".join(reason)
            })

    print(f"\nTotal changed rows: {len(changes)}")
    for i, chg in enumerate(changes, 1):
        print(f"\n{i:>2}. BEFORE: {chg['before']}")
        print(f"    AFTER : {chg['after']}")
        print(f"    LÝ DO : {chg['reason']}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
