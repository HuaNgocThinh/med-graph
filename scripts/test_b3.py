"""
B3: Verification script for:
B3a: link_disease() outputs for 3 modified nodes
B3b: Full corpus node-naming scan (all linked DISEASE nodes must appear verbatim in corpus)
B3c: normalize_disease_name() tests for M54.5 STRIP_BY_CODE rules
"""

import json
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.entity_normalizer import normalize_disease_name
from src.graph.neo4j_client import Neo4jClient

CORPUS_PATH = BASE_DIR / "data" / "synthetic" / "synthetic_data.json"
CORPUS = {r["id"]: r["text"] for r in json.loads(CORPUS_PATH.read_text(encoding="utf-8"))}

def main():
    linker = ICD10Linker()

    print("=" * 80)
    print("B3a: TEST NEO TÊN CHO 3 NODE VỪA ĐỔI MÃ")
    print("=" * 80)

    test_queries = [
        "thoái hóa khớp gối",
        "viêm âm đạo do nấm",
        "viêm loét dạ dày"
    ]

    for q in test_queries:
        res = linker.link_disease(q)
        print(f"Query: {q!r}")
        print(f"Result: {json.dumps(res, ensure_ascii=False, indent=2)}\n")

    print("=" * 80)
    print("B3c: TEST STRIP_BY_CODE CHO M54.5 ('Đau thắt lưng')")
    print("=" * 80)

    m545_test_cases = [
        "đau thắt lưng cấp",
        "đau thắt lưng",
        "đau nhói vùng thắt lưng",
        "đau thắt lưng mạn"
    ]

    for tc in m545_test_cases:
        norm = normalize_disease_name(tc)
        print(f"normalize_disease_name({tc!r}) -> {norm!r}")
        assert norm == "Đau thắt lưng", f"Expected 'Đau thắt lưng', got {norm!r}"

    print("\n" + "=" * 80)
    print("B3b: TEST QUÉT TOÀN BỘ (Corpus Verbatim Match for Linked DISEASE Nodes)")
    print("=" * 80)

    client = Neo4jClient()
    nodes = client.execute_query(
        "MATCH (n:DISEASE) WHERE n.code IS NOT NULL "
        "OPTIONAL MATCH (n)-[r]-() "
        "RETURN n.name AS name, n.code AS code, collect(r.source_sample_id) AS sids "
        "ORDER BY n.name"
    )

    fails = 0
    passes = 0

    for n in nodes:
        name = n["name"]
        code = n["code"]
        sids = sorted({s.strip() for blob in n["sids"] if blob for s in str(blob).split(",") if s.strip()})
        texts = [CORPUS[s] for s in sids if s in CORPUS]

        # Check verbatim presence in any of its attached source texts
        found = False
        matched_text_snippet = ""
        for t in texts:
            m = re.search(r"(?<![\wÀ-ỹ])" + re.escape(name) + r"(?![\wÀ-ỹ])", t, re.IGNORECASE)
            if m:
                found = True
                matched_text_snippet = m.group(0)
                break

        if found:
            passes += 1
            print(f"  [PASS] [{code:<7}] {name:<35} -> Matched verbatim: {matched_text_snippet!r}")
        else:
            fails += 1
            print(f"  [FAIL] [{code:<7}] {name:<35} -> NOT found in source texts ({sids})")

    print("\n" + "=" * 80)
    print(f"Full Scan Result: {passes} PASS, {fails} FAIL out of {len(nodes)} linked DISEASE nodes.")
    if fails == 0:
        print(">>> ALL LINKED DISEASE NODES PASS VERBATIM CORPUS SCAN!")
    else:
        print(f">>> WARNING: {fails} nodes failed verbatim scan!")

    return 0 if fails == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
