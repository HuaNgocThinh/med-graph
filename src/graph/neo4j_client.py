"""
Neo4j Python Driver Client Wrapper.
Handles database connection, query execution, constraints, and error handling.
"""

import logging
from typing import List, Dict, Any, Optional
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Neo4jClient")

class Neo4jClient:
    """Wrapper class for interacting with Neo4j Graph Database."""

    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None

    def connect(self) -> bool:
        """Establishes connection to Neo4j database instance."""
        try:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._driver.verify_connectivity()
            logger.info(f"Successfully connected to Neo4j at '{self.uri}'")
            return True
        except Exception as e:
            logger.warning(f"Could not connect to Neo4j at '{self.uri}': {e}. Graph operations will run in memory/simulation mode.")
            self._driver = None
            return False

    def is_online(self) -> bool:
        """Checks if Neo4j database is connected and online."""
        if not self._driver:
            return self.connect()
        try:
            self._driver.verify_connectivity()
            return True
        except Exception:
            self._driver = None
            return False

    def close(self):
        """Closes driver instance connection."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed.")

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Executes a Cypher query and returns list of record dictionaries."""
        if not self._driver:
            if not self.connect():
                logger.warning("Query skipped because Neo4j is offline.")
                return []

        try:
            with self._driver.session() as session:
                result = session.run(query, parameters or {})
                return [record.data() for record in result]
        except Exception as e:
            logger.error(f"Error executing Cypher query:\nQuery: {query}\nError: {e}")
            return []

    def init_schema(self):
        """Initializes Neo4j uniqueness constraints and performance indexes."""
        queries = [
            "CREATE CONSTRAINT disease_code IF NOT EXISTS FOR (d:DISEASE) REQUIRE d.code IS UNIQUE;",
            "CREATE CONSTRAINT drug_code IF NOT EXISTS FOR (d:DRUG) REQUIRE d.code IS UNIQUE;",
            "CREATE INDEX entity_name_idx IF NOT EXISTS FOR (n:Entity) ON (n.name);"
        ]
        for q in queries:
            self.execute_query(q)
        logger.info("Initialized Neo4j schema constraints and indexes.")

if __name__ == "__main__":
    client = Neo4jClient()
    connected = client.connect()
    if connected:
        client.init_schema()
        client.close()
