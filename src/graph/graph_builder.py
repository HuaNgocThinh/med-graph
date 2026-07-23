"""
Graph Builder module for MedGraph-VI.
Converts extracted triples and linked entities into Cypher MERGE queries and loads them into Neo4j.
Includes source_sample_id tracking for full data traceability and DRUG_GROUP node labeling.
"""

import logging
from typing import List, Dict, Any
from src.graph.neo4j_client import Neo4jClient
from src.entity_linking.entity_normalizer import get_canonical_name, is_drug_group, normalize_disease_name

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("GraphBuilder")

class GraphBuilder:
    """Constructs knowledge graph nodes and edges via Cypher MERGE queries."""

    def __init__(self, neo4j_client: Neo4jClient = None):
        self.client = neo4j_client or Neo4jClient()

    def build_graph(self, triples_with_metadata: List[Dict[str, Any]]) -> List[str]:
        """
        Converts enriched triples into Cypher MERGE statements and inserts them into Neo4j.
        Returns list of executed Cypher queries.
        """
        cypher_queries = []

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
            head_code = head_info.get("code", "UNKNOWN")
            
            # Determine Node Label for Head
            if is_drug_group(head_name) or head_info.get("type") == "DRUG_GROUP":
                head_type = "DRUG_GROUP"
            else:
                head_type = head_info.get("type", "Entity").upper()
                if head_type not in ("DRUG", "DISEASE", "SYMPTOM", "PROCEDURE", "DRUG_GROUP"):
                    head_type = "DRUG" if is_drug_group(head_name) else "Entity"

            if head_type in ("DISEASE", "SYMPTOM"):
                head_name = normalize_disease_name(head_name)

            tail_name = get_canonical_name(raw_tail)
            tail_code = tail_info.get("code", "UNKNOWN")

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
