"""
Graph Builder module for MedGraph-VI.
Converts extracted triples and linked entities into Cypher MERGE queries and loads them into Neo4j.
"""

import logging
from typing import List, Dict, Any
from src.graph.neo4j_client import Neo4jClient

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

            head_name = head_info.get("standard_name", item.get("head", "Unknown"))
            head_code = head_info.get("code", "UNKNOWN")
            head_type = head_info.get("type", "Entity").upper()

            tail_name = tail_info.get("standard_name", item.get("tail", "Unknown"))
            tail_code = tail_info.get("code", "UNKNOWN")
            tail_type = tail_info.get("type", "Entity").upper()

            query = f"""
MERGE (h:{head_type} {{name: $head_name}})
ON CREATE SET h.code = $head_code, h.created_at = timestamp()
MERGE (t:{tail_type} {{name: $tail_name}})
ON CREATE SET t.code = $tail_code, t.created_at = timestamp()
MERGE (h)-[r:{rel_type}]->(t)
ON CREATE SET r.confidence = $confidence, r.negated = $negated, r.temporal = $temporal
ON MATCH SET r.confidence = CASE WHEN r.confidence >= $confidence THEN r.confidence ELSE $confidence END
"""
            params = {
                "head_name": head_name,
                "head_code": head_code,
                "tail_name": tail_name,
                "tail_code": tail_code,
                "confidence": confidence,
                "negated": negated,
                "temporal": temporal
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
        "temporal_context": "present"
    }]
    queries = builder.build_graph(sample_triples)
    print("Generated Cypher:", queries[0])
