"""
Item 1.06a + 1.06d: find the words that ride along with a disease name in the corpus.

Two separate questions:
  1.06a -- exactly which surface forms exist for M54.5 (low back pain) and in which samples.
  1.06d -- across the whole corpus, what trails a known disease name? Time qualifiers
           ("giờ thứ 4", "3 năm nay"), severity ("mức độ trung bình"), setting ("cộng đồng"),
           course ("cấp", "mạn"). These belong to the ENCOUNTER, not to the diagnosis.

Nothing is applied here. This is the input list for the explicit modifier table (1.06c) and
later for the corpus-anchored naming change (plan A).

Read-only. Output: data/exports/modifier_candidates.csv
Usage: python scripts/scan_modifiers.py
"""
import csv
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE))

from src.config import ICD10_DICT_PATH                       # noqa: E402
from src.entity_linking.dict_loader import load_records      # noqa: E402

OUT = BASE / "data" / "exports" / "modifier_candidates.csv"
CORPUS = json.loads((BASE / "data/synthetic/synthetic_data.json").read_text(encoding="utf-8"))

# 1.06a: the three surface forms the user listed, plus the bare code term.
M54_FORMS = ["đau thắt lưng cấp", "đau nhói vùng thắt lưng", "đau thắt lưng",
             "đau lưng dưới", "đau lưng"]

# Words that end a clinical phrase; a modifier run stops here.
STOP = ("và", "kèm", "với", "do", "trên", "sau", "được", "hiện", "bác", "bệnh", "triệu",
        "chẩn", "điều", "chỉ", "lâm", "gồm", "là", "vì", "khi", "cho", "the", "này")


def main():
    print("=" * 104)
    print("1.06a  CAC DANG BE MAT CUA M54.5 TRONG CORPUS")
    print("=" * 104)
    seen_by_form = {}
    for form in M54_FORMS:
        hits = []
        for r in CORPUS:
            for m in re.finditer(r"(?<![\wÀ-ỹ])" + re.escape(form) + r"(?![\wÀ-ỹ])",
                                 r["text"], re.IGNORECASE):
                hits.append((r["id"], m.group(0)))
        seen_by_form[form] = hits
        ids = sorted({h[0] for h in hits})
        print(f"  {form!r:<30} {len(hits):>2} lan  o {len(ids)} mau  {ids}")

    print("\n  Nguyen van tung cau:")
    for r in CORPUS:
        for m in re.finditer(r"[^.*]*(thắt lưng|lưng dưới)[^.*]*\.", r["text"], re.IGNORECASE):
            print(f"    {r['id']}: {m.group(0).strip()}")

    # --- 1.06d ---
    names = []
    for rec in load_records(ICD10_DICT_PATH):
        names.append(rec["name_vi"])
        names.extend(rec.get("synonyms", []))
    names = sorted({n for n in names if n and len(n) > 4}, key=len, reverse=True)

    rows = []
    tally = Counter()
    examples = defaultdict(list)
    for r in CORPUS:
        text = r["text"]
        for nm in names:
            for m in re.finditer(r"(?<![\wÀ-ỹ])" + re.escape(nm) + r"(?![\wÀ-ỹ])",
                                 text, re.IGNORECASE):
                tail = text[m.end():m.end() + 40]
                # take the run of words after the name, up to a stop word or punctuation
                words = []
                for w in re.split(r"\s+", tail.strip()):
                    bare = w.strip(".,;:*()").lower()
                    if not bare or bare in STOP or re.search(r"[.,;:*]", w):
                        if re.match(r"^[\wÀ-ỹ]+[.,;:*]", w) and bare not in STOP:
                            words.append(w.strip(".,;:*()"))
                        break
                    words.append(w.strip("()"))
                    if len(words) >= 4:
                        break
                mod = " ".join(words).strip()
                if not mod:
                    continue
                tally[mod.lower()] += 1
                if len(examples[mod.lower()]) < 3:
                    examples[mod.lower()].append(f"{r['id']}: {nm} {mod}")
                rows.append({
                    "disease_name": nm, "modifier": mod, "sample_id": r["id"],
                    "full_phrase": f"{m.group(0)} {mod}".strip(),
                })

    print("\n" + "=" * 104)
    print("1.06d  BO NGU BAM VAO TEN BENH TRONG CORPUS")
    print("=" * 104)
    print(f"{'so lan':<8}{'bo ngu':<34}vi du")
    for mod, n in tally.most_common(40):
        print(f"{n:<8}{mod[:33]:<34}{examples[mod][0][:56]}")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["disease_name", "modifier", "sample_id", "full_phrase"])
        w.writeheader(); w.writerows(rows)
    print(f"\nTong: {len(rows)} lan xuat hien, {len(tally)} bo ngu khac nhau")
    print(f"CSV: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
