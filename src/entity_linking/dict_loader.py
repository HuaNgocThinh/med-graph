"""
One loader for the reference dictionaries, so their on-disk shape can evolve without every
consumer growing its own isinstance() check.

History: rxnorm_vi.json was rebuilt into {"_provenance": {...}, "drugs": [...]} and every
reader had to be patched separately; dictionary_ner.py still carries a hand-written branch.
icd10_vi.json now needs the same treatment to hold its `_rules` block. Doing it in one place
means a future shape change is one edit, not six.

Accepted shapes:
    [ {...}, {...} ]                          legacy flat list
    { "_rules": ..., "diseases": [ ... ] }    icd10_vi.json
    { "_provenance": ..., "drugs": [ ... ] }  rxnorm_vi.json
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

RECORD_KEYS = ("diseases", "drugs", "records")


def load_dict(path: Path) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Return (records, metadata). metadata holds every non-record top-level key."""
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    if isinstance(data, list):
        return data, {}

    if isinstance(data, dict):
        for key in RECORD_KEYS:
            if isinstance(data.get(key), list):
                meta = {k: v for k, v in data.items() if k != key}
                return data[key], meta
        raise ValueError(
            f"{path.name}: dict shape with no record list; expected one of {RECORD_KEYS}, "
            f"got keys {sorted(data)}"
        )

    raise ValueError(f"{path.name}: unsupported top-level type {type(data).__name__}")


def load_records(path: Path) -> List[Dict[str, Any]]:
    return load_dict(path)[0]


def save_dict(path: Path, records: List[Dict[str, Any]], meta: Dict[str, Any],
              record_key: str = "diseases") -> None:
    """Write back preserving the metadata block. Metadata keys come first, for readability."""
    payload = dict(meta)
    payload[record_key] = records
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
