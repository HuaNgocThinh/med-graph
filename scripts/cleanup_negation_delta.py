"""
Script cleanup self-loop relationships in Neo4j database safely.
Deletes ONLY self-loop relationships (head == tail), preserving all nodes.
"""

import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("CleanupSelfLoops")


def cleanup_self_loops(client: Neo4jClient = None):
    client = client or Neo4jClient()
    if not client.is_online():
        logger.error("Neo4j offline!")
        return 0

    # Query to count existing self-loops
    count_res = client.execute_query("MATCH (a)-[r]->(a) RETURN count(r) AS cnt")
    loop_cnt = count_res[0]["cnt"] if count_res else 0
    logger.info(f"Found {loop_cnt} self-loop relationship(s) in Neo4j.")

    if loop_cnt > 0:
        # Correct Cypher query: DELETE r (NOT DETACH DELETE a)
        query = "MATCH (a)-[r]->(a) DELETE r"
        client.execute_query(query)
        logger.info(f"✅ Successfully deleted {loop_cnt} self-loop relationship(s). Nodes were NOT deleted.")

    return loop_cnt


if __name__ == "__main__":
    cleanup_self_loops()
