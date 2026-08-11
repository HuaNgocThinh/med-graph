"""
Graph Cleaner and Conflict Detection module for MedGraph-VI.
Scans extracted triples and Neo4j database for logical medical contradictions.
Logs detected conflicts to file for manual expert review (DOES NOT automatically delete edges).
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from src.config import DATA_DIR
from src.graph.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GraphCleaner")

LOG_PATH = DATA_DIR / "graph_conflicts.log"

class GraphCleaner:
    """Detects logical contradictions in medical triples."""

    def __init__(self, neo4j_client: Neo4jClient = None, log_file: Path = LOG_PATH):
        self.client = neo4j_client or Neo4jClient()
        self.log_file = log_file

    def detect_conflicts_in_triples(self, triples: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Scans a batch of triples for direct logical contradictions, semantic redundancy, and negated entity conflicts.
        """
        conflicts = []
        pair_map = {}

        for t in triples:
            head = t.get("head")
            tail = t.get("tail")

            # Check for negated entity conflict
            if t.get("negated", False):
                conflicts.append({
                    "type": "NEGATED_ENTITY_RELATION_CONFLICT",
                    "head": head,
                    "tail": tail,
                    "relation": t.get("relation"),
                    "details": "Triple involves a negated medical entity from source text."
                })

            key = (head, tail)
            if key not in pair_map:
                pair_map[key] = []
            pair_map[key].append(t)

        # Evaluate pairs for contradictory or redundant relation types
        for (h, t), triple_group in pair_map.items():
            rels = {item["relation"] for item in triple_group}
            
            # Contradiction: CONTRAINDICATED_FOR vs PRESCRIBED_FOR/TREATS
            if "CONTRAINDICATED_FOR" in rels and ("TREATS" in rels or "PRESCRIBED_FOR" in rels):
                conflicts.append({
                    "type": "CONTRADICTION_CONFLICT",
                    "head": h,
                    "tail": t,
                    "details": f"Node pair has conflicting relations: {list(rels)}",
                    "conflicting_triples": triple_group
                })

            # Semantic Redundancy: Both PRESCRIBED_FOR and TREATS between same pair
            if "PRESCRIBED_FOR" in rels and "TREATS" in rels:
                conflicts.append({
                    "type": "PRESCRIBED_FOR_VS_TREATS_REDUNDANCY",
                    "head": h,
                    "tail": t,
                    "details": "Node pair has redundant edge types (both PRESCRIBED_FOR and TREATS).",
                    "conflicting_triples": triple_group
                })

        if conflicts:
            self._log_conflicts(conflicts)

        return conflicts

    def audit_neo4j_conflicts(self) -> List[Dict[str, Any]]:
        """Queries Neo4j database for existing contradictory or redundant edges between same nodes."""
        queries = [
            ("CONTRAINDICATION_CONFLICT", """
MATCH (h)-[r1:CONTRAINDICATED_FOR]->(t), (h)-[r2:PRESCRIBED_FOR|TREATS]->(t)
RETURN h.name AS Head, t.name AS Tail, type(r1) AS Rel1, type(r2) AS Rel2
"""),
            ("PRESCRIBED_FOR_VS_TREATS_REDUNDANCY", """
MATCH (h)-[r1:PRESCRIBED_FOR]->(t), (h)-[r2:TREATS]->(t)
RETURN h.name AS Head, t.name AS Tail, type(r1) AS Rel1, type(r2) AS Rel2
""")
        ]
        conflicts = []
        for ctype, q in queries:
            records = self.client.execute_query(q)
            for rec in records:
                conflicts.append({
                    "type": ctype,
                    "head": rec.get("Head"),
                    "tail": rec.get("Tail"),
                    "details": f"Node pair has both '{rec.get('Rel1')}' and '{rec.get('Rel2')}' edges in Neo4j DB."
                })
        if conflicts:
            self._log_conflicts(conflicts)
        return conflicts

    def _log_conflicts(self, conflicts: List[Dict[str, Any]]):
        """Writes conflict logs to disk without modifying database graph."""
        with open(self.log_file, "a", encoding="utf-8") as f:
            for item in conflicts:
                f.write(json.dumps(item, ensure_ascii=False) + "\n")
        logger.warning(f"Logged {len(conflicts)} graph conflict(s) to '{self.log_file}' for manual review.")

if __name__ == "__main__":
    cleaner = GraphCleaner()
    sample = [
        {"head": "Ibuprofen", "relation": "TREATS", "tail": "Viêm loét dạ dày"},
        {"head": "Ibuprofen", "relation": "CONTRAINDICATED_FOR", "tail": "Viêm loét dạ dày"}
    ]
    detected = cleaner.detect_conflicts_in_triples(sample)
    print("Detected conflicts:", detected)
