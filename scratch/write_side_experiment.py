"""
Item 1b: prove EXPERIMENTALLY that the write side canonicalizes folk terms.

Feeds a folk-worded sentence through the same pipeline stages run_pipeline.py uses
(NER ensemble -> ConText -> LLM RE + rule RE -> ICD10/RxNorm linking -> GraphBuilder),
with source_sample_id = 'syn_test_001'.

run_pipeline.py itself is NOT invoked, deliberately: it re-indexes every sample id to
syn_{n:03d} and rewrites data/synthetic/synthetic_data.json, which would corrupt the
real dataset. The per-sample stages below are copied from run_pipeline.py:167-240.

PASS: no new node named 'Tiểu đường'; the new edge lands on the existing
'Đái tháo đường týp 2' node and that edge carries syn_test_001.

Usage:
  python scratch/write_side_experiment.py run       # run the experiment (writes to Neo4j)
  python scratch/write_side_experiment.py cleanup   # remove every trace of syn_test_001
"""
import sys, json
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
BASE = Path(__file__).resolve().parent.parent
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))

from src.llm_client import LLMClient
from src.ner.ner_ensemble import NEREnsemble
from src.negation_temporal.context_processor import ConTextProcessor
from src.relation_extraction.llm_re import LLMRelationExtractor
from src.relation_extraction.rule_based_re import RuleBasedRelationExtractor
from src.entity_linking.icd10_linker import ICD10Linker
from src.entity_linking.rxnorm_linker import RxNormLinker
from src.entity_linking.entity_normalizer import get_canonical_name
from src.graph.neo4j_client import Neo4jClient
from src.graph.graph_builder import GraphBuilder

TEST_ID = "syn_test_001"
SNAPSHOT = BASE / "data" / "exports" / ".write_test_nodes_before.json"

MODE = sys.argv[1] if len(sys.argv) > 1 else "run"

# Scenario 2 isolates the synonym-canonicalization layer: 'đau bao tử' is NOT in
# icd10_vi.json, so ICD10Linker returns method='unlinked' and cannot rescue it.
# Whatever folds it onto the existing 'Viêm loét dạ dày' node is our layer alone.
SCENARIO = sys.argv[2] if len(sys.argv) > 2 else "linked"
if SCENARIO == "isolated":
    TEST_TEXT = "Bệnh nhân được chẩn đoán đau bao tử, kê Omeprazole 20mg."
    EXPECT_NODE = "Viêm loét dạ dày"
    FOLK_FORMS = ("đau bao tử", "Đau bao tử")
else:
    TEST_TEXT = "Bệnh nhân được chẩn đoán tiểu đường, kê Metformin 500mg."
    EXPECT_NODE = "Đái tháo đường týp 2"
    FOLK_FORMS = ("tiểu đường", "bệnh tiểu đường")
neo = Neo4jClient()
if not neo.is_online():
    print("ABORT: Neo4j offline.")
    sys.exit(1)


def node_names():
    """
    Node identity here is the PAIR (label, name), not the name. Comparing by name alone
    hid a real duplicate: a :SYMPTOM 'Viêm loét dạ dày' created beside the real :DISEASE one
    showed up as "no new nodes" while the node count rose by 1. Returns "LABEL\\tname" keys.
    """
    out = []
    for r in neo.execute_query("MATCH (n) RETURN n.name AS name, labels(n) AS labels"):
        if r.get("name"):
            for lb in (r.get("labels") or ["?"]):
                out.append(f"{lb}\t{r['name']}")
    return sorted(out)


def counts():
    rels = neo.execute_query("MATCH ()-[r]->() RETURN count(r) AS c")[0]["c"]
    nodes = neo.execute_query("MATCH (n) RETURN count(n) AS c")[0]["c"]
    sids = set()
    for r in neo.execute_query("MATCH ()-[r]->() RETURN r.source_sample_id AS s"):
        for p in str(r["s"] or "").split(","):
            if p.strip():
                sids.add(p.strip())
    return nodes, rels, len(sids)


def cleanup():
    print("\n" + "=" * 78)
    print("DỌN DẸP: gỡ mọi dấu vết của", TEST_ID)
    print("=" * 78)
    # 1. Relationships created solely by the test -> delete outright
    deleted = neo.execute_query(
        "MATCH ()-[r]->() WHERE r.source_sample_id = $sid DELETE r RETURN count(r) AS c",
        {"sid": TEST_ID})
    print(f"  Quan hệ do test tạo ra (xoá hẳn): {deleted[0]['c'] if deleted else 0}")

    # 2. Pre-existing relationships that merely had the test id appended -> strip it back out
    stripped = neo.execute_query("""
    MATCH ()-[r]->() WHERE r.source_sample_id CONTAINS $sid
    SET r.source_sample_id =
      reduce(acc = '', p IN [x IN split(r.source_sample_id, ',') WHERE trim(x) <> $sid] |
             CASE WHEN acc = '' THEN trim(p) ELSE acc + ',' + trim(p) END)
    RETURN count(r) AS c
    """, {"sid": TEST_ID})
    print(f"  Quan hệ cũ bị gắn thêm id (gỡ id ra): {stripped[0]['c'] if stripped else 0}")

    # 3. Nodes that did not exist before the experiment
    if SNAPSHOT.exists():
        before = set(json.load(open(SNAPSHOT, encoding="utf-8")))
        new_nodes = [n for n in node_names() if n not in before]
        if new_nodes:
            print(f"  Node mới sinh ra bởi test: {new_nodes}")
            for key in new_nodes:
                lb, nm = key.split("\t", 1)
                # Delete on the (label, name) PAIR. A name-only DETACH DELETE here would also
                # destroy a legitimate node of the same name under a different label.
                neo.execute_query(
                    f"MATCH (n:{lb}) WHERE n.name = $nm DETACH DELETE n", {"nm": nm})
            print(f"  -> đã xoá {len(new_nodes)} node")
        else:
            print("  Node mới sinh ra bởi test: (không có)")
    else:
        print("  ⚠️ Không có snapshot node trước đó, bỏ qua bước xoá node.")

    n, r, s = counts()
    print(f"\n  SAU DỌN DẸP: nodes={n}, relationships={r}, distinct SourceSampleID={s}")
    ok = (r == 199 and s == 93 and n == 198)
    print(f"  KHỚP TRẠNG THÁI GỐC (198/199/93): {'✅ ĐÚNG' if ok else '❌ SAI'}")
    leftover = neo.execute_query(
        "MATCH ()-[r]->() WHERE r.source_sample_id CONTAINS $sid RETURN count(r) AS c", {"sid": TEST_ID})
    print(f"  Còn sót dấu vết {TEST_ID}: {leftover[0]['c'] if leftover else 0}")
    return ok


if MODE == "cleanup":
    cleanup()
    sys.exit(0)

# ---------------- RUN ----------------
n0, r0, s0 = counts()
before_nodes = node_names()
json.dump(before_nodes, open(SNAPSHOT, "w", encoding="utf-8"), ensure_ascii=False)
disease_before = [r["name"] for r in neo.execute_query("MATCH (n:DISEASE) RETURN n.name AS name")]

print("=" * 78)
print("TRƯỚC THỰC NGHIỆM")
print("=" * 78)
print(f"  nodes={n0}  relationships={r0}  distinct SourceSampleID={s0}")
print(f"  DISEASE nodes: {len(disease_before)}")
print(f"  Có node {FOLK_FORMS[0]!r}? {'CÓ' if any(n.lower()==FOLK_FORMS[0].lower() for n in before_nodes) else 'KHÔNG'}")
print(f"  Có node {EXPECT_NODE!r}? {'CÓ' if EXPECT_NODE in before_nodes else 'KHÔNG'}")
print(f"\n  Câu test ({TEST_ID}): {TEST_TEXT!r}")

llm = LLMClient()
ner = NEREnsemble(llm_client=llm)
ctx = ConTextProcessor()
llm_re = LLMRelationExtractor(llm_client=llm)
rule_re = RuleBasedRelationExtractor()
icd, rx = ICD10Linker(), RxNormLinker()
builder = GraphBuilder(neo4j_client=neo)

entities = ner.extract_entities(TEST_TEXT)
processed = ctx.process_entities(TEST_TEXT, entities)
print(f"\n[STAGE B/C] entities: {json.dumps(processed, ensure_ascii=False)}")

triples = llm_re.extract_relations(TEST_TEXT, processed)
rule_triples = rule_re.extract_relations(TEST_TEXT, processed)
triples = triples + [r for r in rule_triples if r not in triples]
print(f"[STAGE D] triples: {json.dumps(triples, ensure_ascii=False)}")

enriched = []
for t in triples:
    hs, ts = t["head"], t["tail"]
    ht = next((e["type"] for e in processed if e["entity"] == hs or get_canonical_name(e["entity"]) == hs), "Entity")
    tt = next((e["type"] for e in processed if e["entity"] == ts or get_canonical_name(e["entity"]) == ts), "Entity")
    hl = icd.link_disease(hs) if ht == "DISEASE" else (rx.link_drug(hs) if ht in ("DRUG", "DRUG_GROUP") else {"standard_name": get_canonical_name(hs), "code": "UNKNOWN", "method": "unlinked"})
    tl = icd.link_disease(ts) if tt == "DISEASE" else (rx.link_drug(ts) if tt in ("DRUG", "DRUG_GROUP") else {"standard_name": get_canonical_name(ts), "code": "UNKNOWN", "method": "unlinked"})
    hl["type"], tl["type"] = ht, tt
    ho = next((e for e in processed if e["entity"] == hs or get_canonical_name(e["entity"]) == hs), {})
    to = next((e for e in processed if e["entity"] == ts or get_canonical_name(e["entity"]) == ts), {})
    enriched.append({
        "head": get_canonical_name(hs), "relation": t["relation"], "tail": get_canonical_name(ts),
        "confidence": t["confidence"], "head_info": hl, "tail_info": tl,
        "negated": bool(ho.get("negated", False) or to.get("negated", False)),
        "temporal_context": ho.get("temporal_context", "unknown"),
        "source_sample_id": TEST_ID,
    })
print(f"[STAGE E] enriched: {json.dumps(enriched, ensure_ascii=False, indent=2)}")

builder.build_graph(enriched)

print("\n" + "=" * 78)
print("SAU THỰC NGHIỆM")
print("=" * 78)
after_nodes = node_names()
n1, r1, s1 = counts()
print(f"  nodes={n1} (delta {n1-n0:+d})  relationships={r1} (delta {r1-r0:+d})")
new_nodes = [n for n in after_nodes if n not in before_nodes]
print(f"  Node MỚI được tạo: {new_nodes if new_nodes else '(không có)'}")

folk_lower = {f.lower() for f in FOLK_FORMS}
made_folk_node = any(nm.strip().lower() in folk_lower for nm in after_nodes)
print(f"\n  [PASS 1] KHÔNG sinh node {FOLK_FORMS[0]!r}: {'❌ SAI - có sinh!' if made_folk_node else '✅ ĐÚNG'}")

edges = neo.execute_query(
    "MATCH (h)-[r]->(t) WHERE r.source_sample_id CONTAINS $sid "
    "RETURN h.name AS h, type(r) AS rel, t.name AS t, r.source_sample_id AS sid", {"sid": TEST_ID})
print(f"\n  Quan hệ mang {TEST_ID}:")
for e in edges:
    print(f"    {e['h']} -[{e['rel']}]-> {e['t']}   (sid={e['sid']})")

hit = [e for e in edges if e["t"] == "Đái tháo đường týp 2" or e["h"] == "Đái tháo đường týp 2"]
print(f"\n  [PASS 2] Quan hệ gắn vào node 'Đái tháo đường týp 2' có sẵn: {'✅ ĐÚNG' if hit else '❌ SAI'}")
print(f"  [PASS 3] Node đó có thêm SourceSampleID {TEST_ID}: "
      f"{'✅ ĐÚNG' if any(TEST_ID in (e['sid'] or '') for e in hit) else '❌ SAI'}")

print("\n>>> KẾT LUẬN 1b:", "PASS" if (not made_folk_node and hit) else "FAIL")
