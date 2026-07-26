"""
Item 3c: list every DISEASE that appears in >=2 samples but whose HAS_SYMPTOM edges all
come from a single sample. Those are SUSPECTS for extraction drop-out, not proven bugs --
a sample can legitimately mention a disease without describing its symptoms.
Exports data/exports/symptom_gap_suspect.csv
"""
import sys, csv, json, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from src.graph.neo4j_client import Neo4jClient

c = Neo4jClient()
samples = json.load(open(BASE / "data/synthetic/synthetic_data.json", encoding="utf-8"))
texts = {s["id"]: s["text"] for s in samples}

# every sample id attached to any edge of a disease (in or out)
rows = c.execute_query("""
MATCH (d:DISEASE)-[r]-()
RETURN d.name AS disease, type(r) AS rel, r.source_sample_id AS sids
""")

involved, symptom_sids = {}, {}
for r in rows:
    d = r["disease"]
    sids = {s.strip() for s in str(r["sids"] or "").split(",") if s.strip()}
    involved.setdefault(d, set()).update(sids)
    if r["rel"] == "HAS_SYMPTOM":
        symptom_sids.setdefault(d, set()).update(sids)

suspects = []
for d, all_sids in sorted(involved.items()):
    sym = symptom_sids.get(d, set())
    if len(all_sids) >= 2 and len(sym) <= 1:
        missing = sorted(all_sids - sym)
        suspects.append({
            "Disease": d,
            "SamplesMentioningDisease": len(all_sids),
            "AllSampleIDs": ",".join(sorted(all_sids)),
            "SamplesWithSymptoms": ",".join(sorted(sym)) or "(none)",
            "SamplesWithoutSymptoms": ",".join(missing),
        })

out = BASE / "data/exports/symptom_gap_suspect.csv"
with open(out, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["Disease", "SamplesMentioningDisease", "AllSampleIDs",
                                      "SamplesWithSymptoms", "SamplesWithoutSymptoms"])
    w.writeheader()
    w.writerows(suspects)

print(f"Tong so DISEASE co canh: {len(involved)}")
print(f"NGHI NGO (>=2 sample nhung <=1 sample co trieu chung): {len(suspects)}")
print(f"Exported: {out}\n")
for s in suspects:
    print(f"  {s['Disease']}")
    print(f"     xuat hien o : {s['AllSampleIDs']}")
    print(f"     co trieu chung tu: {s['SamplesWithSymptoms']}")
    print(f"     thieu o     : {s['SamplesWithoutSymptoms']}")

# Keyword probe: do the "missing" samples actually contain symptom-ish language?
NEG = ("không", "chưa", "loại trừ", "không thấy")
print("\n" + "=" * 78)
print("DO NHANH: cac sample 'thieu' co chua tu chi trieu chung khong?")
print("=" * 78)
for s in suspects:
    for sid in s["SamplesWithoutSymptoms"].split(","):
        t = texts.get(sid, "")
        if not t:
            continue
        has_sym_word = bool(re.search(r"triệu chứng|đau|sốt|ho\b|khó thở|mệt|buồn nôn|ngứa", t, re.I))
        neg = [n for n in NEG if n in t.lower()]
        print(f"  {s['Disease'][:34]:34} {sid}: tu-trieu-chung={has_sym_word}  phu-dinh={neg}")
