"""
Global Configuration for MedGraph-VI system.
Loads settings from environment variables with sensible defaults for local execution.
"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent

try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

# Data directories
DATA_DIR = BASE_DIR / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
SYNTHETIC_DATA_DIR = DATA_DIR / "synthetic"
ANNOTATED_DATA_DIR = DATA_DIR / "annotated"
DICTIONARIES_DIR = DATA_DIR / "dictionaries"

ICD10_DICT_PATH = DICTIONARIES_DIR / "icd10_vi.json"
RXNORM_DICT_PATH = DICTIONARIES_DIR / "rxnorm_vi.json"

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "gemini-2.0-flash")

GEMINI_MODEL_FALLBACK_LIST = [
    "gemini-2.5-flash-lite",
    "gemini-flash-lite-latest",
    "gemini-2.5-flash",
    "gemini-2.0-flash",
]


# Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "medgraph_secret_password")

# External APIs
RXNAV_API_BASE = os.getenv("RXNAV_API_BASE", "https://rxnav.nlm.nih.gov/REST")

# Evaluation output paths
EVALUATION_DIR = BASE_DIR / "evaluation"
ERROR_ANALYSIS_DIR = EVALUATION_DIR / "error_analysis"

# Ensure essential directories exist
for folder in [RAW_DATA_DIR, SYNTHETIC_DATA_DIR, ANNOTATED_DATA_DIR, DICTIONARIES_DIR, ERROR_ANALYSIS_DIR]:
    folder.mkdir(parents=True, exist_ok=True)
