"""
Item 4a: repo-wide audit of exception handlers that hide failures.

Motivation (item 4d): a handler that returns [] / None / {} on error makes a failed call
indistinguishable from a successful empty result. Every silent bug this project has hit came
from that single shape -- most recently CREATE CONSTRAINT failing while init_schema() reported
success, because Neo4jClient.execute_query() logged the error and returned [].

Classification:
  SWALLOW   -- error is discarded; caller cannot tell failure from an empty/normal result
  LOG_ONLY  -- error is logged but a normal-looking value is still returned
  OK        -- re-raises, or converts to a distinguishable error value

Usage:  python scripts/scan_swallowed_exceptions.py
"""
import ast
import sys
from collections import Counter
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE = Path(__file__).resolve().parent.parent
SKIP = {"__pycache__", ".git", "scratch", "venv", ".venv", "node_modules", "build"}


def classify(handler: ast.ExceptHandler):
    """Return (kind, how) for one except handler."""
    body = handler.body
    if any(isinstance(n, ast.Raise) for n in body):
        return "OK", "re-raises"

    if len(body) == 1:
        b = body[0]
        if isinstance(b, ast.Pass):
            return "SWALLOW", "pass"
        if isinstance(b, ast.Continue):
            return "SWALLOW", "continue"
        if isinstance(b, ast.Return):
            return "SWALLOW", "return " + (ast.unparse(b.value)[:44] if b.value else "None")

    has_log = any(
        isinstance(n, ast.Call)
        and ("log" in ast.unparse(n.func).lower() or ast.unparse(n.func) in ("print", "st.error", "st.warning"))
        for n in ast.walk(handler)
    )
    rets = [n for n in body if isinstance(n, ast.Return)]
    if has_log:
        tail = "returns " + ast.unparse(rets[0].value)[:34] if rets and rets[0].value else "no return"
        return "LOG_ONLY", f"logs, {tail}"
    if rets:
        return "SWALLOW", "return " + (ast.unparse(rets[0].value)[:44] if rets[0].value else "None")
    return "SWALLOW", ast.unparse(body[0])[:46]


def main():
    rows = []
    for p in sorted(BASE.rglob("*.py")):
        if any(s in p.parts for s in SKIP):
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as e:
            print(f"PARSE FAIL {p}: {e}")
            continue
        rel = p.relative_to(BASE).as_posix()
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                kind, how = classify(node)
                typ = ast.unparse(node.type) if node.type else "BARE"
                rows.append((kind, rel, node.lineno, typ, how))

    order = {"SWALLOW": 0, "LOG_ONLY": 1, "OK": 2}
    rows.sort(key=lambda r: (order[r[0]], r[1], r[2]))

    print(f"Tong so except handler (bo qua scratch/): {len(rows)}")
    print(dict(Counter(r[0] for r in rows)))
    print("=" * 106)
    for kind, f, ln, typ, how in rows:
        print(f"{kind:<9} {f}:{ln:<5} except {typ:<24} -> {how}")

    out = BASE / "data" / "exports" / "swallowed_exceptions_audit.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    import csv
    with open(out, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["kind", "file", "line", "exception_type", "behaviour"])
        w.writerows(rows)
    print(f"\nCSV: {out}")


if __name__ == "__main__":
    main()
