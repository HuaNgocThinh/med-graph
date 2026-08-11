"""
Item B2: audit every gold item in TEST_EL_BENCHMARK and QA_TEST_BENCHMARK against what the
system and the corpus actually contain, and record whether the gold value is TRACEABLE to an
independent authority.

This does NOT fix anything. The point is to establish, per item, whether the gold label was
derived independently (from ICD-10/RxNorm/the corpus) or merely copied from the system it is
supposed to be grading -- which would make the whole benchmark circular.

Output: data/exports/benchmark_audit.csv
Usage:  python scripts/audit_benchmarks.py
"""
import csv
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from evaluation.evaluate_entity_linking import TEST_EL_BENCHMARK      # noqa: E402
from evaluation.evaluate_qa import QA_TEST_BENCHMARK                  # noqa: E402
from src.entity_linking.icd10_linker import ICD10Linker               # noqa: E402
from src.entity_linking.rxnorm_linker import RxNormLinker             # noqa: E402
from src.graph.neo4j_client import Neo4jClient                        # noqa: E402
from src.config import ICD10_DICT_PATH, RXNORM_DICT_PATH              # noqa: E402
from src.entity_linking.dict_loader import load_records               # noqa: E402

OUT = BASE / "data" / "exports" / "benchmark_audit.csv"
CORPUS = json.loads((BASE / "data/synthetic/synthetic_data.json").read_text(encoding="utf-8"))
CORPUS_TEXT = "\n".join(r["text"] for r in CORPUS).lower()


def dict_codes():
    """Every code the local dictionaries currently assert, for the circularity check."""
    icd = {r["code"] for r in load_records(ICD10_DICT_PATH)}
    payload = json.loads(RXNORM_DICT_PATH.read_text(encoding="utf-8"))
    drugs = payload["drugs"] if isinstance(payload, dict) else payload
    return icd, {f"RXCUI:{d['rxcui']}" for d in drugs}


def main():
    icd_codes, rx_codes = dict_codes()
    icd, rx = ICD10Linker(), RxNormLinker()
    client = Neo4jClient()
    online = client.is_online()

    rows = []

    # --- Entity-linking benchmark ---
    for it in TEST_EL_BENCHMARK:
        gold = it["expected_code"]
        actual = (icd.link_disease if it["type"] == "DISEASE" else rx.link_drug)(it["entity"])["code"]
        in_dict = gold in (icd_codes if it["type"] == "DISEASE" else rx_codes)
        in_corpus = it["entity"].lower() in CORPUS_TEXT
        # Traceability: a gold code is independently traceable only if we can point at an
        # authority for it. We have none recorded, so the honest answer is what we can observe:
        # whether the value merely echoes the local dictionary.
        trace = ("KHONG - trung khop tu dien noi bo, khong co nguon doc lap"
                 if in_dict else "KHONG - khong co trong tu dien va khong co nguon")
        rows.append({
            "benchmark": "EL", "id": it["entity"], "gold": gold, "actual": str(actual),
            "match": "YES" if gold == actual else "NO",
            "gold_in_local_dict": "YES" if in_dict else "NO",
            "input_in_corpus": "YES" if in_corpus else "NO",
            "traceable_to_authority": trace,
        })

    # --- QA benchmark ---
    for it in QA_TEST_BENCHMARK:
        kws = it["expected_keywords"]
        found, missing = [], []
        for kw in kws:
            hit = False
            if online:
                r = client.execute_query(
                    "MATCH (n) WHERE toLower(n.name) CONTAINS toLower($k) RETURN n.name AS n "
                    "LIMIT 3", {"k": kw})
                hit = bool(r)
            (found if hit else missing).append(kw)
        rows.append({
            "benchmark": "QA", "id": it["id"], "gold": " | ".join(kws),
            "actual": ("co trong do thi: " + ", ".join(found) if found else "(khong co gi)"),
            "match": "NO" if missing else "YES",
            "gold_in_local_dict": "-",
            "input_in_corpus": "YES" if it["question"][:20].lower() in CORPUS_TEXT else "n/a",
            "traceable_to_authority": (
                "KHONG - keyword khong co node nao trong do thi: " + ", ".join(missing)
                if missing else "mot phan - keyword khop node, nhung khop CHUOI CON"),
        })

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["benchmark", "id", "gold", "actual", "match",
                                          "gold_in_local_dict", "input_in_corpus",
                                          "traceable_to_authority"])
        w.writeheader()
        w.writerows(rows)

    print(f"{'bm':<4}{'muc':<24}{'gold':<15}{'thuc te':<15}{'khop':<6}truy nguon")
    print("=" * 118)
    for r in rows:
        print(f"{r['benchmark']:<4}{r['id'][:23]:<24}{r['gold'][:14]:<15}"
              f"{r['actual'][:14]:<15}{r['match']:<6}{r['traceable_to_authority'][:44]}")

    bad = [r for r in rows if r["match"] == "NO"]
    untraceable = [r for r in rows if r["traceable_to_authority"].startswith("KHONG")]
    print("\n" + "=" * 118)
    print(f"Tong muc gold          : {len(rows)}")
    print(f"Lech voi thuc te       : {len(bad)}")
    print(f"KHONG truy duoc ve nguon doc lap: {len(untraceable)}/{len(rows)}")
    print(f"\nCSV: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
