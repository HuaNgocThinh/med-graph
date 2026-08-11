"""
Neo4j Python Driver Client Wrapper.
Handles database connection, query execution, constraints, and error handling.
"""

import logging
from typing import List, Dict, Any, Optional
from src.config import NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Neo4jClient")


class Neo4jQueryError(RuntimeError):
    """A Cypher statement did not execute. Carries the statement and the driver error."""

    def __init__(self, query: str, error: BaseException, offline: bool = False):
        self.query = query
        self.error = error
        self.offline = offline
        super().__init__(f"{'Neo4j OFFLINE' if offline else type(error).__name__}: {error}")


class QueryResult(list):
    """
    A list of records that also says whether the query actually ran.

    execute_query() used to return a bare [] for BOTH 'the query ran and matched nothing' and
    'the query blew up'. Those are opposite facts and the caller could not tell them apart --
    that single ambiguity produced every silent failure this project has hit (see
    docs/silent_failures.md). Callers that opt out of raising get this instead, so
    `if not rows:` still works while `rows.ok` reveals the truth.
    """

    def __init__(self, records=(), ok: bool = True, error: Optional[BaseException] = None,
                 query: str = "", offline: bool = False):
        super().__init__(records)
        self.ok = ok
        self.error = error
        self.query = query
        self.offline = offline

    @property
    def failed(self) -> bool:
        return not self.ok

    def __repr__(self):
        if self.ok:
            return f"QueryResult(ok=True, {len(self)} rows)"
        return f"QueryResult(ok=False, {'OFFLINE' if self.offline else 'ERROR'}: {self.error})"


class Neo4jClient:
    """Wrapper class for interacting with Neo4j Graph Database."""

    def __init__(self, uri: str = NEO4J_URI, user: str = NEO4J_USER, password: str = NEO4J_PASSWORD):
        self.uri = uri
        self.user = user
        self.password = password
        self._driver = None
        self.last_error_type: Optional[str] = None

    def connect(self) -> bool:
        """Establishes connection to Neo4j database instance."""
        try:
            from neo4j import GraphDatabase
            self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self._driver.verify_connectivity()
            self.last_error_type = None
            logger.info(f"Successfully connected to Neo4j at '{self.uri}'")
            return True
        except Exception as e:
            err_str = str(e).lower()
            if "auth" in err_str or "unauthorized" in err_str or "password" in err_str:
                self.last_error_type = "auth_failed"
            elif "connection refused" in err_str or "could not connect" in err_str or "serviceunavailable" in err_str:
                self.last_error_type = "connection_refused"
            elif "timeout" in err_str or "timed out" in err_str:
                self.last_error_type = "timeout"
            else:
                self.last_error_type = type(e).__name__.lower()

            logger.warning(f"Could not connect to Neo4j at '{self.uri}' ({self.last_error_type}): {e}. Graph operations will run in memory/simulation mode.")
            self._driver = None
            return False

    def is_online(self) -> bool:
        """Checks if Neo4j database is connected and online."""
        if not self._driver:
            return self.connect()
        try:
            self._driver.verify_connectivity()
            self.last_error_type = None
            return True
        except Exception as e:
            err_str = str(e).lower()
            if "auth" in err_str or "unauthorized" in err_str or "password" in err_str:
                self.last_error_type = "auth_failed"
            elif "connection refused" in err_str or "could not connect" in err_str or "serviceunavailable" in err_str:
                self.last_error_type = "connection_refused"
            elif "timeout" in err_str or "timed out" in err_str:
                self.last_error_type = "timeout"
            else:
                self.last_error_type = type(e).__name__.lower()

            logger.warning(f"Neo4j connectivity check failed ({self.last_error_type}): {e}")
            self._driver = None
            return False

    def close(self):
        """Closes driver instance connection."""
        if self._driver:
            self._driver.close()
            logger.info("Neo4j connection closed.")

    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None,
                      raise_on_error: bool = True) -> "QueryResult":
        """
        Executes a Cypher query and returns the records as a QueryResult.

        Item 4b -- root cause of this project's silent-failure family.
        Previously this method logged the error and returned a bare []. A failed statement was
        therefore indistinguishable from an empty match, which is how:
          * CREATE CONSTRAINT drug_code failed on duplicate 'RXCUI-UNKNOWN' values while
            init_schema() reported success, leaving uniqueness unenforced for the whole project;
          * a Neo4j outage produced confident "no data found" answers instead of an error.

        Now it RAISES Neo4jQueryError by default. Callers that legitimately expect failure
        (e.g. executing LLM-generated Cypher that may not parse, or a UI that must degrade
        rather than crash) pass raise_on_error=False and inspect `result.ok`.
        """
        if not self._driver:
            if not self.connect():
                msg = "Neo4j is OFFLINE -- query did not run. An empty result here would be a lie."
                logger.error(f"{msg}\nQuery: {query}")
                exc = ConnectionError(msg)
                if raise_on_error:
                    raise Neo4jQueryError(query, exc, offline=True)
                return QueryResult([], ok=False, error=exc, query=query, offline=True)

        try:
            with self._driver.session() as session:
                result = session.run(query, parameters or {})
                return QueryResult([record.data() for record in result], ok=True, query=query)
        except Exception as e:
            logger.error(f"Cypher FAILED ({type(e).__name__}): {e}\nQuery: {query}")
            if raise_on_error:
                raise Neo4jQueryError(query, e) from e
            return QueryResult([], ok=False, error=e, query=query)

    # Declared schema. Each entry: (name, kind, cypher).
    DECLARED_SCHEMA = [
        ("disease_code", "CONSTRAINT",
         "CREATE CONSTRAINT disease_code IF NOT EXISTS FOR (d:DISEASE) REQUIRE d.code IS UNIQUE"),
        ("drug_code", "CONSTRAINT",
         "CREATE CONSTRAINT drug_code IF NOT EXISTS FOR (d:DRUG) REQUIRE d.code IS UNIQUE"),
        ("entity_name_idx", "INDEX",
         "CREATE INDEX entity_name_idx IF NOT EXISTS FOR (n:Entity) ON (n.name)"),
    ]

    def init_schema(self):
        """
        Creates the declared constraints/indexes and then VERIFIES they exist.

        execute_query() swallows errors and returns [], so every CREATE CONSTRAINT here
        appeared to succeed while in fact none of the two uniqueness constraints was ever
        created -- 'drug_code IS UNIQUE' was declared but absent, which is how two DRUG nodes
        came to share RXCUI:6809. Declaring is not creating; this now checks.
        """
        failures = []
        for name, kind, q in self.DECLARED_SCHEMA:
            try:
                self.execute_query(q)
            except Neo4jQueryError as e:
                # Do not abort the pipeline, but do not pretend it worked either.
                failures.append((name, kind, e.error))
                logger.error(f"❌ Could not create {kind} {name}: {e.error}")
        if failures:
            logger.error(
                f"{len(failures)}/{len(self.DECLARED_SCHEMA)} schema objects could NOT be created. "
                f"Existing data violates them; run scripts/check_schema.py for the offending rows. "
                f"Nothing was deleted."
            )
        else:
            logger.info("Initialized Neo4j schema constraints and indexes.")
        self.verify_schema()
        return failures

    def verify_schema(self) -> List[Dict[str, Any]]:
        """
        Compares declared schema against what Neo4j actually has, and warns loudly about any
        gap. Same principle as the LIVE_NEO4J / SIMULATED_OFFLINE banner: a silent failure
        that looks like success is worse than a visible error. Returns the missing entries.
        """
        if not self.is_online():
            logger.warning("⚠️ SCHEMA CHECK SKIPPED: Neo4j offline.")
            return []

        existing = set()
        for row in self.execute_query("SHOW CONSTRAINTS"):
            if row.get("name"):
                existing.add(row["name"])
        for row in self.execute_query("SHOW INDEXES"):
            if row.get("name"):
                existing.add(row["name"])

        missing = [
            {"name": n, "kind": k, "cypher": q}
            for n, k, q in self.DECLARED_SCHEMA if n not in existing
        ]
        if missing:
            logger.warning("=" * 78)
            logger.warning(
                f"⚠️ SCHEMA DRIFT: {len(missing)}/{len(self.DECLARED_SCHEMA)} declared "
                f"constraint(s)/index(es) are DECLARED IN CODE BUT DO NOT EXIST in Neo4j."
            )
            for m in missing:
                logger.warning(f"   ✗ MISSING {m['kind']}: {m['name']}")
            logger.warning(
                "   Uniqueness here is NOT being enforced. A CREATE CONSTRAINT that fails "
                "because existing data violates it is reported by Neo4j but silently dropped "
                "by execute_query(). Run scripts/check_schema.py for the violating rows."
            )
            logger.warning("=" * 78)
        else:
            logger.info(f"✅ Schema verified: all {len(self.DECLARED_SCHEMA)} declared objects exist.")
        return missing

if __name__ == "__main__":
    client = Neo4jClient()
    connected = client.connect()
    if connected:
        client.init_schema()
        client.close()
