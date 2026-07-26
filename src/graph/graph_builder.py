"""
Graph Builder module for MedGraph-VI.
Converts extracted triples and linked entities into Cypher MERGE queries and loads them into Neo4j.
Includes source_sample_id tracking for full data traceability and DRUG_GROUP node labeling.
"""

import csv
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Set
from src.config import DATA_DIR
from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.entity_normalizer import (
    get_canonical_name, is_drug_group, normalize_disease_name, is_generic_term,
    normalize_code,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GraphBuilder")

LABEL_CONFLICTS_CSV = DATA_DIR / "exports" / "label_conflicts.csv"
REJECTED_ENTITIES_CSV = DATA_DIR / "exports" / "rejected_entities.csv"

class GraphBuilder:
    """Constructs knowledge graph nodes and edges via Cypher MERGE queries."""

    def __init__(self, neo4j_client: Neo4jClient = None):
        self.client = neo4j_client or Neo4jClient()

    # ---- Write-path guards -------------------------------------------------
    # build_graph() is the ONLY path by which anything reaches Neo4j, which makes it the
    # single choke point where the generic-term gate can actually be enforced. Enforcing it
    # only inside the linker was not enough: run_pipeline does
    #   raw_head = head_info.get("standard_name") or item.get("head", "Unknown")
    # so a rejected link silently falls back to the raw NER string and the node gets built
    # anyway. Both guards below run immediately before MERGE, after every normalization.

    def _existing_codes(self) -> Dict[str, str]:
        """
        Snapshot of code -> node name, for the duplicate-code guard.

        'drug_code IS UNIQUE' is declared in neo4j_client.py but does NOT exist in the
        database: CREATE CONSTRAINT fails because every unlinked drug shares the literal
        'RXCUI-UNKNOWN' sentinel, and execute_query() swallows the error, so the failure
        looked like success. That is how Metformin and Methotrexate both came to hold
        RXCUI:6809. Until the sentinel becomes null the DB cannot enforce it, so we do.
        """
        codes: Dict[str, str] = {}
        rows = self.client.execute_query(
            "MATCH (n) WHERE n.code IS NOT NULL "
            "RETURN n.name AS name, n.code AS code, labels(n)[0] AS label")
        for r in rows:
            code = normalize_code(r.get("code"))
            if code:
                codes[code] = r.get("name", "")
        return codes

    def _existing_labels_by_name(self) -> Dict[str, Set[str]]:
        """Snapshot of name -> {labels} already in the graph, for label-conflict detection."""
        mapping: Dict[str, Set[str]] = {}
        for rec in self.client.execute_query("MATCH (n) RETURN n.name AS name, labels(n) AS labels"):
            nm = rec.get("name")
            if nm:
                mapping.setdefault(nm, set()).update(rec.get("labels") or [])
        return mapping

    @staticmethod
    def _append_csv(path: Path, fieldnames: List[str], row: Dict[str, Any]):
        path.parent.mkdir(parents=True, exist_ok=True)
        exists = path.exists()
        with open(path, "a", encoding="utf-8-sig", newline="") as f:
            w = csv.DictWriter(f, fieldnames=fieldnames)
            if not exists:
                w.writeheader()
            w.writerow(row)

    def build_graph(self, triples_with_metadata: List[Dict[str, Any]]) -> List[str]:
        """
        Converts enriched triples into Cypher MERGE statements and inserts them into Neo4j.
        Returns list of executed Cypher queries.
        """
        cypher_queries = []
        existing_labels = self._existing_labels_by_name()
        existing_codes = self._existing_codes()

        for item in triples_with_metadata:
            negated = item.get("negated", False)
            if negated:
                logger.info(f"Skipping negated triple ({item.get('head')} -[{item.get('relation')}]-> {item.get('tail')}) from Neo4j active graph insertion.")
                continue

            head_info = item.get("head_info", {})
            tail_info = item.get("tail_info", {})
            rel_type = item.get("relation", "RELATED_TO").upper()
            confidence = item.get("confidence", 0.9)
            temporal = item.get("temporal_context", "unknown")
            sample_id = item.get("source_sample_id", "unknown")

            raw_head = head_info.get("standard_name") or item.get("head", "Unknown")
            raw_tail = tail_info.get("standard_name") or item.get("tail", "Unknown")

            head_name = get_canonical_name(raw_head)
            head_code = normalize_code(head_info.get("code"))
            
            # Determine Node Label for Head
            if is_drug_group(head_name) or head_info.get("type") == "DRUG_GROUP":
                head_type = "DRUG_GROUP"
            else:
                head_type = head_info.get("type", "Entity").upper()
                if head_type not in ("DRUG", "DISEASE", "SYMPTOM", "PROCEDURE", "DRUG_GROUP"):
                    head_type = "DRUG" if is_drug_group(head_name) else "Entity"

            # WRITE-SIDE synonym canonicalization. normalize_disease_name() strips the
            # 'Bệnh/Hội chứng/...' prefixes AND folds folk synonyms onto the medical standard
            # form ('Tiểu đường' -> 'Đái tháo đường'), so a folk-worded extraction can never
            # create a second node for a concept that already exists. text_to_cypher applies
            # the identical normalization at query time — both ends must stay in sync.
            if head_type in ("DISEASE", "SYMPTOM"):
                head_name = normalize_disease_name(head_name)

            tail_name = get_canonical_name(raw_tail)
            tail_code = normalize_code(tail_info.get("code"))

            # Determine Node Label for Tail
            if is_drug_group(tail_name) or tail_info.get("type") == "DRUG_GROUP":
                tail_type = "DRUG_GROUP"
            else:
                tail_type = tail_info.get("type", "Entity").upper()
                if tail_type not in ("DRUG", "DISEASE", "SYMPTOM", "PROCEDURE", "DRUG_GROUP"):
                    tail_type = "Entity"

            if tail_type in ("DISEASE", "SYMPTOM"):
                tail_name = normalize_disease_name(tail_name)

            # Merge TREATS and PRESCRIBED_FOR for Drug-Disease pairs to PRESCRIBED_FOR
            if head_type in ("DRUG", "DRUG_GROUP") and tail_type == "DISEASE":
                if rel_type in ("TREATS", "PRESCRIBED_FOR"):
                    rel_type = "PRESCRIBED_FOR"
            elif tail_type in ("DRUG", "DRUG_GROUP") and head_type == "DISEASE":
                if rel_type in ("TREATS", "PRESCRIBED_FOR"):
                    rel_type = "PRESCRIBED_FOR"
            # Keep TREATS for Drug-Symptom pairs
            elif head_type in ("DRUG", "DRUG_GROUP") and tail_type == "SYMPTOM":
                if rel_type in ("TREATS", "PRESCRIBED_FOR"):
                    rel_type = "TREATS"
            elif tail_type in ("DRUG", "DRUG_GROUP") and head_type == "SYMPTOM":
                if rel_type in ("TREATS", "PRESCRIBED_FOR"):
                    rel_type = "TREATS"

            # GUARD 1 - generic-term gate (the single authority in entity_normalizer).
            # Refuses to create a node for a string that is not a clinical entity, e.g. the
            # bare 'viêm' NER lifts out of "giảm viêm"/"kháng viêm", or 'đau' out of "giảm đau".
            rejected = None
            for role, nm, ntype in (("head", head_name, head_type), ("tail", tail_name, tail_type)):
                if is_generic_term(nm, ntype):
                    rejected = (role, nm, ntype)
                    break
            if rejected:
                role, nm, ntype = rejected
                logger.warning(
                    f"🚫 REJECTED generic entity: {role}={nm!r} as {ntype} "
                    f"({head_name} -[{rel_type}]-> {tail_name}, sample={sample_id}). Not written to Neo4j."
                )
                self._append_csv(
                    REJECTED_ENTITIES_CSV,
                    ["source_sample_id", "role", "entity", "label", "relation", "head", "tail", "reason"],
                    {"source_sample_id": sample_id, "role": role, "entity": nm, "label": ntype,
                     "relation": rel_type, "head": head_name, "tail": tail_name,
                     "reason": "generic term rejected by is_generic_term()"},
                )
                continue

            # GUARD 2 - label conflict. Node identity here is the PAIR (label, name), so
            # MERGE (t:SYMPTOM {name:'Viêm loét dạ dày'}) happily creates a SECOND node beside
            # the existing :DISEASE one. Rather than silently duplicating, or silently merging
            # across labels (which would be wrong for names valid under both, e.g. 'sốt'),
            # refuse the write and make the conflict loud and reviewable.
            conflict = None
            for role, nm, ntype in (("head", head_name, head_type), ("tail", tail_name, tail_type)):
                prior = existing_labels.get(nm)
                if prior and ntype not in prior:
                    conflict = (role, nm, ntype, sorted(prior))
                    break
            if conflict:
                role, nm, ntype, prior = conflict
                logger.warning(
                    f"⚠️ LABEL CONFLICT: {role}={nm!r} requested as {ntype} but already exists as "
                    f"{prior} (sample={sample_id}). Refusing to create a duplicate node."
                )
                self._append_csv(
                    LABEL_CONFLICTS_CSV,
                    ["source_sample_id", "role", "entity", "requested_label", "existing_labels",
                     "relation", "head", "tail"],
                    {"source_sample_id": sample_id, "role": role, "entity": nm,
                     "requested_label": ntype, "existing_labels": "|".join(prior),
                     "relation": rel_type, "head": head_name, "tail": tail_name},
                )
                continue

            # GUARD 3 - duplicate code. Enforces in code what 'drug_code IS UNIQUE' was
            # supposed to enforce in the database but never did.
            dup = None
            for role, nm, code in (("head", head_name, head_code), ("tail", tail_name, tail_code)):
                if not code:      # unlinked -> null, never a shared sentinel value
                    continue
                owner = existing_codes.get(str(code))
                if owner and owner != nm:
                    dup = (role, nm, code, owner)
                    break
            if dup:
                role, nm, code, owner = dup
                logger.warning(
                    f"⚠️ DUPLICATE CODE: {role}={nm!r} claims {code} which already belongs to "
                    f"{owner!r} (sample={sample_id}). Refusing the write — two different drugs "
                    f"cannot share one RxCUI."
                )
                self._append_csv(
                    LABEL_CONFLICTS_CSV,
                    ["source_sample_id", "role", "entity", "requested_label", "existing_labels",
                     "relation", "head", "tail"],
                    {"source_sample_id": sample_id, "role": role, "entity": nm,
                     "requested_label": f"DUPLICATE_CODE:{code}", "existing_labels": owner,
                     "relation": rel_type, "head": head_name, "tail": tail_name},
                )
                continue

            query = f"""
MERGE (h:{head_type} {{name: $head_name}})
ON CREATE SET h.code = $head_code, h.created_at = timestamp()
MERGE (t:{tail_type} {{name: $tail_name}})
ON CREATE SET t.code = $tail_code, t.created_at = timestamp()
MERGE (h)-[r:{rel_type}]->(t)
ON CREATE SET r.confidence = $confidence, r.negated = $negated, r.temporal = $temporal, r.source_sample_id = $sample_id
ON MATCH SET r.confidence = CASE WHEN r.confidence >= $confidence THEN r.confidence ELSE $confidence END,
             r.source_sample_id = CASE WHEN r.source_sample_id CONTAINS $sample_id THEN r.source_sample_id ELSE r.source_sample_id + ',' + $sample_id END
"""
            params = {
                "head_name": head_name,
                "head_code": head_code,
                "tail_name": tail_name,
                "tail_code": tail_code,
                "confidence": confidence,
                "negated": negated,
                "temporal": temporal,
                "sample_id": sample_id
            }

            self.client.execute_query(query, params)
            # Keep the snapshot current so a conflict introduced earlier in THIS batch is
            # caught too, not just conflicts against nodes that predate the run.
            existing_labels.setdefault(head_name, set()).add(head_type)
            existing_labels.setdefault(tail_name, set()).add(tail_type)
            for _nm, _code in ((head_name, head_code), (tail_name, tail_code)):
                if _code:
                    existing_codes.setdefault(str(_code), _nm)
            cypher_queries.append(query.strip())

        logger.info(f"Loaded {len(triples_with_metadata)} triples into Neo4j Knowledge Graph.")
        return cypher_queries

if __name__ == "__main__":
    builder = GraphBuilder()
    sample_triples = [{
        "head": "Paracetamol 500mg",
        "relation": "TREATS",
        "tail": "Viêm họng cấp",
        "confidence": 0.95,
        "head_info": {"standard_name": "Paracetamol 500mg", "code": "RXCUI:161", "type": "DRUG"},
        "tail_info": {"standard_name": "Viêm họng cấp", "code": "J02.9", "type": "DISEASE"},
        "negated": False,
        "temporal_context": "present",
        "source_sample_id": "syn_001"
    }]
    queries = builder.build_graph(sample_triples)
    print("Generated Cypher:", queries[0])
