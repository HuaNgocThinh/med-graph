"""
Item B3: quarantine gate for the evaluation benchmarks.

Why the benchmarks are quarantined rather than repaired
-------------------------------------------------------
`TEST_EL_BENCHMARK` and `QA_TEST_BENCHMARK` were committed in 324a149 "first commit",
in the SAME commit as data/dictionaries/*.json, by the same author, on the same day, and
have not been touched since -- not even by e64df49, which changed 86 lines of those
dictionaries. No script in the repository generates them.

The gold code for "Amlor" is RXCUI:4337. At 324a149 the dictionary record whose synonym list
contained "amlor" was {"rxcui": "4337", "name_en": "Amlodipine", ...}. 4337 is fentanyl. The
benchmark and the artefact it is supposed to grade carry the SAME wrong value.

A benchmark that agrees with the system because it was derived from the system measures
nothing. Fixing the four mismatched rows would make the numbers look right while leaving the
circularity intact -- and would destroy the evidence. So the benchmarks stay exactly as they
are, and running them requires an explicit, visible opt-in.

See docs/benchmark_quarantine.md. They will be REBUILT in Phase 7 from hand-assigned labels.

Same principle as Neo4jClient.execute_query(raise_on_error=True): silence must be a declared
decision, not a default.
"""
import sys

ALLOW_FLAG = "--allow-unvalidated-benchmark"

# Flip to True only when the benchmark has been rebuilt and independently validated.
BENCHMARK_VALIDATED = False

_BANNER = """
{bar}
KHONG CHAY: BENCHMARK CHUA DUOC XAC THUC DOC LAP
{bar}
  Benchmark '{name}' dang bi CACH LY.

  Ly do: nhan gold va tu dien duoc tao trong CUNG MOT COMMIT (324a149), cung tac gia,
  cung ngay, va khong co script nao sinh ra chung. Gia tri gold cua 'Amlor' la
  RXCUI:4337 -- dung bang gia tri SAI dang nam trong tu dien luc do (4337 = fentanyl).
  Mot benchmark dong y voi he thong vi duoc chep ra tu he thong thi khong do duoc gi.

  Ket qua chay ra KHONG DUNG DUOC cho luan van hay bao cao.

  Chi tiet    : docs/benchmark_quarantine.md
  Audit tung muc: data/exports/benchmark_audit.csv  (chay scripts/audit_benchmarks.py)

  Van muon chay de kham pha thi them co:
      python -m evaluation.{module} {flag}
{bar}
"""


def require_validated_benchmark(name: str, module: str, argv=None) -> None:
    """Abort unless the benchmark is validated or the caller explicitly opts in."""
    argv = sys.argv if argv is None else argv
    if BENCHMARK_VALIDATED:
        return

    if ALLOW_FLAG in argv:
        bar = "!" * 78
        print(f"\n{bar}\n"
              f"CANH BAO: dang chay benchmark CHUA XAC THUC ('{name}').\n"
              f"Con so thu duoc KHONG dung de danh gia, bao cao hay dua vao luan van.\n"
              f"Xem docs/benchmark_quarantine.md.\n"
              f"{bar}\n", flush=True)
        return

    print(_BANNER.format(bar="=" * 78, name=name, module=module, flag=ALLOW_FLAG), flush=True)
    sys.exit(2)
