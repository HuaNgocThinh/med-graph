"""
Item 5a + 5c: remove medically-wrong synonyms from data/dictionaries/icd10_vi.json.

Approved for removal:
  * all 30 rows the impact analysis rated SAFE_TO_REMOVE (linking is byte-identical before
    and after, or the string matches no sample text and no node);
  * plus I63 'tai biến mạch máu não', explicitly approved despite being CHANGES_LINKING,
    because folding haemorrhagic stroke into cerebral infarction is a serious clinical error
    (thrombolysis vs reversal of anticoagulation -- opposite management).

NOT touched here: the remaining 6 BREAKS_EXISTING_NODE and 6 CHANGES_LINKING rows, which
are still awaiting per-case approval.

Usage:
  python scripts/prune_icd10_synonyms.py            # dry run
  python scripts/prune_icd10_synonyms.py --apply
"""
import sys, json, csv
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

DICT = BASE / "data" / "dictionaries" / "icd10_vi.json"
IMPACT = BASE / "data" / "exports" / "icd10_removal_impact.csv"
AUDIT = BASE / "data" / "exports" / "icd10_synonyms_audit.csv"
LOG = BASE / "data" / "exports" / "icd10_prune_log.csv"
APPLY = "--apply" in sys.argv

# Explicitly approved beyond the SAFE_TO_REMOVE set (item 5c)
FORCE_REMOVE = {("I63", "tai biến mạch máu não")}

impact = list(csv.DictReader(open(IMPACT, encoding="utf-8-sig")))
audit = {(r["icd_code"], r["synonym"]): r for r in csv.DictReader(open(AUDIT, encoding="utf-8-sig"))}

targets = {}
for r in impact:
    key = (r["icd_code"], r["synonym"])
    if r["verdict"] == "SAFE_TO_REMOVE" or key in FORCE_REMOVE:
        why = "SAFE_TO_REMOVE (linking khong doi / khong xuat hien trong corpus)" \
            if r["verdict"] == "SAFE_TO_REMOVE" else "DUYET TAY 5c (sai lam sang nang)"
        targets[key] = {
            "verdict": r["verdict"], "approval": why,
            "classification": r.get("classification", ""),
            "medical_reason": (audit.get(key) or {}).get("reason", ""),
        }

print(f"So synonym se bo: {len(targets)}  "
      f"(SAFE_TO_REMOVE {sum(1 for v in targets.values() if v['verdict']=='SAFE_TO_REMOVE')}, "
      f"duyet tay {sum(1 for v in targets.values() if v['verdict']!='SAFE_TO_REMOVE')})\n")

records = json.load(open(DICT, encoding="utf-8"))
before_total = sum(len(r.get("synonyms", [])) for r in records)

log_rows, removed = [], 0
print("=" * 108)
for rec in records:
    code = rec["code"]
    keep = []
    for syn in rec.get("synonyms", []):
        key = (code, syn)
        if key in targets:
            t = targets[key]
            removed += 1
            print(f"  BO  [{code:>7}] {rec['name_vi'][:26]:<28} <- {syn!r}")
            print(f"         phan loai: {t['classification']}  | {t['approval']}")
            if t["medical_reason"]:
                print(f"         ly do y hoc: {t['medical_reason'][:110]}")
            log_rows.append({
                "icd_code": code, "name_vi": rec["name_vi"], "removed_synonym": syn,
                "classification": t["classification"], "verdict": t["verdict"],
                "approval": t["approval"], "medical_reason": t["medical_reason"],
            })
        else:
            keep.append(syn)
    rec["synonyms"] = keep

after_total = sum(len(r.get("synonyms", [])) for r in records)
print("=" * 108)
print(f"\nsynonym truoc: {before_total}  ->  sau: {after_total}   (bo {removed})")
missing = set(targets) - {(r["icd_code"], r["removed_synonym"]) for r in log_rows}
if missing:
    print(f"⚠️ {len(missing)} muc tieu KHONG tim thay trong tu dien: {sorted(missing)}")

LOG.parent.mkdir(parents=True, exist_ok=True)
with open(LOG, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["icd_code", "name_vi", "removed_synonym",
                                      "classification", "verdict", "approval", "medical_reason"])
    w.writeheader(); w.writerows(log_rows)
print(f"Log: {LOG}")

if APPLY:
    backup = DICT.with_suffix(".json.pre_prune_backup")
    if not backup.exists():
        backup.write_text(json.dumps(json.load(open(DICT, encoding="utf-8")),
                                     ensure_ascii=False, indent=2), encoding="utf-8")
    DICT.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"DA GHI {DICT.name}. Backup: {backup.name}")
else:
    print("[DRY RUN] Chua ghi gi. Chay lai voi --apply.")
