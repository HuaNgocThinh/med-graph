# Knowledge Graph Coverage Criteria

This document defines the minimum quality and density standards required for the MedGraph-VI Knowledge Graph to ensure high-accuracy, traceable question answering.

## Minimum Coverage Standards

To stop the data expansion loop, the following conditions must be met for every entity present in the graph database:

### 1. Disease Coverage
- **Symptom Density**: Every `DISEASE` node must have at least **2** `HAS_SYMPTOM` relationships pointing to `SYMPTOM` nodes.
- **Treatment Density**: Every `DISEASE` node must have at least **1** treatment relationship (`PRESCRIBED_FOR` or `TREATS`) coming from a `DRUG` or `DRUG_GROUP` node.

### 2. Drug/Drug Group Coverage
- **Clinical Association**: Every `DRUG` or `DRUG_GROUP` node must have at least **1** outgoing relationship (`PRESCRIBED_FOR`, `TREATS`, or `CONTRAINDICATED_FOR`) pointing to a `DISEASE` or `SYMPTOM` node. 
- Orphan nodes (nodes with 0 clinical relations) are prohibited.

---

## Termination of Data Expansion

The automated data expansion loop (`expand_coverage_loop.py`) operates iteratively. It will terminate when:
1. **Zero Gaps Remaining**: All existing disease and drug nodes satisfy the minimum density standards.
2. **Safe Limit Reached**: The loop completes 5 rounds of targeted generation. This safety guard prevents infinite API calls in case of pipeline extraction failures.
