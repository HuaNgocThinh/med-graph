"""
A/B the candidate FuzzyMatcher configurations against EVERY real term in the system,
so the threshold/scorer choice is measured, not guessed. Read-only.

Config A = current           : WRatio, cutoff 88, no guards
Config B = WRatio + guards   : WRatio, cutoff 88, stop-words + len-ratio >= 0.6
Config C = ratio + guards    : ratio,  cutoff 75, stop-words + len-ratio >= 0.6
"""
import sys, json, re
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from rapidfuzz import process, fuzz
from src.graph.neo4j_client import Neo4jClient

recs = json.load(open(BASE / "data/dictionaries/icd10_vi.json", encoding="utf-8"))
cands, cmap = [], {}
for it in recs:
    if it.get("name_vi"):
        cands.append(it["name_vi"]); cmap[it["name_vi"].lower()] = it
    for s in it.get("synonyms", []):
        cands.append(s); cmap[s.lower()] = it
exact = {k: v for k, v in cmap.items()}

STOP = {"bệnh", "bệnh nhân", "đau", "sốt", "ho", "bị", "trẻ", "bệnh nhi", "thuốc", "khám",
        "chẩn đoán", "tiền sử", "hiện tại", "triệu chứng", "lâm sàng", "chứng", "tình trạng",
        "hội chứng", "viêm", "nhiễm", "nhiễm trùng", "rối loạn", "hạn chế", "biến chứng",
        "giảm đau", "giảm viêm", "kháng viêm", "viêm nhiễm", "mạn tính", "cấp tính", "cấp"}


def link(q, scorer, cutoff, guards):
    cq = re.sub(r'\b\d+(?:mg|mcg|ml|g|%)\b', '', q.lower()).strip() or q.lower()
    if guards and (cq in STOP or len(cq) < 3):
        return ("REJECTED_GENERIC", None)
    if cq in exact:
        return (exact[cq]["code"], exact[cq]["name_vi"])
    r = process.extractOne(cq, cands, scorer=scorer, score_cutoff=cutoff)
    if not r:
        return ("UNLINKED", None)
    ms, score, _ = r
    if guards:
        if len(cq) / max(len(ms.lower()), 1) < 0.6:
            return ("REJECTED_SHORT", None)
    return (cmap[ms.lower()]["code"], cmap[ms.lower()]["name_vi"])


CONFIGS = {
    "A_current":   (fuzz.WRatio, 88.0, False),
    "B_wratio_g":  (fuzz.WRatio, 88.0, True),
    "C_ratio_g":   (fuzz.ratio,  75.0, True),
}

# Every term that matters: node names + all dict names/synonyms + known folk terms + the bug triggers
terms = set()
c = Neo4jClient()
for r in c.execute_query("MATCH (n) WHERE 'DISEASE' IN labels(n) OR 'SYMPTOM' IN labels(n) RETURN n.name AS n"):
    if r["n"]:
        terms.add(r["n"])
for it in recs:
    terms.add(it["name_vi"])
    terms.update(it.get("synonyms", []))
terms.update(["tiểu đường", "bệnh tiểu đường", "đau bao tử", "mỡ máu", "tan máu bẩm sinh",
              "viêm", "đau", "sốt", "ho", "bệnh", "giảm viêm", "kháng viêm", "giảm đau",
              "viêm nhiễm", "nhiễm"])
terms = sorted(t for t in terms if t)
print(f"So term kiem tra: {len(terms)}\n")

res = {name: {t: link(t, *cfg) for t in terms} for name, cfg in CONFIGS.items()}

for name in ("B_wratio_g", "C_ratio_g"):
    diff = [(t, res["A_current"][t], res[name][t]) for t in terms if res["A_current"][t] != res[name][t]]
    print("=" * 100)
    print(f"{name} vs A_current : {len(diff)} term doi ket qua")
    print("=" * 100)
    for t, a, b in diff:
        print(f"  {t!r:38} A={a[0]:16} -> {name.split('_')[0]}={b[0]}")
    print()

print("=" * 100)
print("KIEM TRA CHOT: 4 term bat buoc phai bi CHAN (muc 1e) + term GOOD phai SONG")
print("=" * 100)
for t in ["viêm", "đau", "sốt", "bệnh", "ho", "nhiễm", "giảm viêm", "kháng viêm", "giảm đau"]:
    print(f"  CHAN {t!r:12} A={res['A_current'][t][0]:16} B={res['B_wratio_g'][t][0]:18} C={res['C_ratio_g'][t][0]}")
print()
for t in ["tiểu đường", "bệnh tiểu đường", "tan máu bẩm sinh", "mỡ máu cao", "cao huyết áp",
          "viêm phổi", "đái tháo đường týp 2", "thoái hóa khớp gối"]:
    print(f"  SONG {t!r:24} A={res['A_current'][t][0]:10} B={res['B_wratio_g'][t][0]:10} C={res['C_ratio_g'][t][0]}")
