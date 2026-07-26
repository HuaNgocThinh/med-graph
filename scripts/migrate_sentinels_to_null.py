"""
Item 3a: replace the string sentinels 'ICD-UNKNOWN' / 'RXCUI-UNKNOWN' (and the stray 'UNKNOWN'
/ 'N/A' spellings) on existing nodes with null, i.e. remove the `code` property entirely.

Why: Neo4j's uniqueness constraint IGNORES null but treats equal strings as duplicates. With 15
DRUG nodes all holding the literal 'RXCUI-UNKNOWN', 'REQUIRE d.code IS UNIQUE' could never be
created -- and because execute_query() swallowed the failure, init_schema() reported success
while the constraint did not exist. The sentinel made a declared invariant unachievable AND
invisible. It also reads as a value, so an unlinked node can be miscounted as linked.

Only the `code` property is removed. No node, label, or relationship is touched. Nothing is
deleted: a node whose only code was a sentinel never carried information in the first place.

Usage:
  python scripts/migrate_sentinels_to_null.py            # dry run + before CSV
  python scripts/migrate_sentinels_to_null.py --apply
"""
import csv
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.graph.neo4j_client import Neo4jClient                             # noqa: E402
from src.entity_linking.entity_normalizer import LEGACY_CODE_SENTINELS     # noqa: E402

EXPORTS = BASE / "data" / "exports"
BEFORE = EXPORTS / "before_sentinel_migration.csv"
AFTER = EXPORTS / "after_sentinel_migration.csv"
LOG = EXPORTS / "sentinel_migration_log.csv"
APPLY = "--apply" in sys.argv

SENTINELS = sorted(s for s in LEGACY_CODE_SENTINELS if s)


def snapshot(client, path):
    rows = client.execute_query(
        "MATCH (n) WHERE n.name IS NOT NULL "
        "RETURN n.name AS name, labels(n)[0] AS label, n.code AS code ORDER BY label, n.name")
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["label", "name", "code"])
        for r in rows:
            w.writerow([r["label"], r["name"], r["code"] if r["code"] is not None else ""])
    return rows


def totals(client):
    n = client.execute_query("MATCH (n) RETURN count(n) AS c")[0]["c"]
    r = client.execute_query("MATCH ()-[r]->() RETURN count(r) AS c")[0]["c"]
    s = client.execute_query(
        "MATCH ()-[r]->() WHERE r.source_sample_id IS NOT NULL "
        "UNWIND split(r.source_sample_id, ',') AS x RETURN count(DISTINCT trim(x)) AS c")[0]["c"]
    return n, r, s


def main():
    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j OFFLINE - dung lai, khong ghi gi.")
        return 1

    before_totals = totals(client)
    before = snapshot(client, BEFORE)
    print(f"Do thi truoc: {before_totals[0]} node / {before_totals[1]} quan he / "
          f"{before_totals[2]} SourceSampleID")
    print(f"Snapshot: {BEFORE.name}\n")

    victims = [r for r in before if r["code"] is not None and str(r["code"]).upper() in SENTINELS]
    print(f"Node dang mang sentinel dang chuoi: {len(victims)}")
    print(dict(Counter(str(r["code"]) for r in victims)))
    print(dict(Counter(r["label"] for r in victims)), "\n")

    print("=" * 84)
    for r in victims:
        print(f"  [{r['label']:<8}] {r['name']:<48} {r['code']!r} -> null")
    print("=" * 84)

    LOG.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["label", "name", "old_code", "new_code", "reason"])
        w.writeheader()
        for r in victims:
            w.writerow({
                "label": r["label"], "name": r["name"], "old_code": r["code"], "new_code": "",
                "reason": "sentinel dang chuoi -> null. Node chua link duoc; gia tri nay khong "
                          "mang thong tin nao, nhung lam rang buoc UNIQUE khong the tao duoc.",
            })
    print(f"Log: {LOG}")

    if not APPLY:
        print("\n[DRY RUN] Chua ghi gi. Chay lai voi --apply.")
        return 0

    res = client.execute_query(
        "MATCH (n) WHERE n.code IS NOT NULL AND toUpper(n.code) IN $s "
        "REMOVE n.code RETURN count(n) AS c", {"s": SENTINELS})
    print(f"\nDA XOA thuoc tinh code khoi {res[0]['c']} node.")

    after = snapshot(client, AFTER)
    after_totals = totals(client)
    left = [r for r in after if r["code"] is not None and str(r["code"]).upper() in SENTINELS]
    print(f"Do thi sau : {after_totals[0]} node / {after_totals[1]} quan he / "
          f"{after_totals[2]} SourceSampleID")
    print(f"Sentinel con lai: {len(left)}")
    print(f"[3a] Node/quan he/SourceSampleID giu nguyen: "
          f"{'PASS' if before_totals == after_totals else 'FAIL'}")

    # Only the `code` property may differ, and only in the sentinel direction.
    b = {(r["label"], r["name"]): r["code"] for r in before}
    a = {(r["label"], r["name"]): r["code"] for r in after}
    assert set(b) == set(a), "Tap node thay doi - khong duoc phep"
    unexpected = [k for k in b if b[k] != a[k] and str(b[k]).upper() not in SENTINELS]
    print(f"[3a] Thay doi ngoai y muon (node khong mang sentinel bi doi ma): {len(unexpected)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
