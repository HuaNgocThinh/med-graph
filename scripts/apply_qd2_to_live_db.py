"""
Permanent QĐ2 Migration and Node Labeling script for Live Neo4j Database.
Ensures QĐ2 active ingredient migration is applied first, then node labels are set, resolving RxCUI uniqueness constraints.
"""

import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from src.graph.neo4j_client import Neo4jClient

DOSAGE_REGEX = re.compile(
    r'\s+('
    r'\d+(?:[\.,]\d+)?(?:/\d+)?'
    r'\s*'
    r'(?:mg|g|mcg|µg|ml|L|IU|UI|%)(?:/[a-zA-Zà-ỹ]+)?'
    r')\s*$',
    re.IGNORECASE
)

def parse_drug_name(name: str):
    match = DOSAGE_REGEX.search(name)
    if match:
        dosage = match.group(1).strip()
        active_ingredient = name[:match.start()].strip()
        return active_ingredient, dosage
    return name.strip(), ""


def relocate_node_edges(client: Neo4jClient, old_name: str, active_name: str, dosage: str):
    if dosage:
        client.execute_query("""
        MATCH (d {name: $old_name})-[r]-()
        WHERE r.dosage IS NULL OR r.dosage = ""
        SET r.dosage = $dosage
        """, {"old_name": old_name, "dosage": dosage})

    if old_name == active_name:
        return

    active_exists = bool(client.execute_query(
        "MATCH (d {name: $active_name}) RETURN d", {"active_name": active_name}
    ))

    if not active_exists:
        client.execute_query("""
        MATCH (d {name: $old_name})
        SET d.name = $active_name
        """, {"old_name": old_name, "active_name": active_name})
    else:
        # Move outgoing relationships
        out_rels = client.execute_query("""
        MATCH (old {name: $old_name})-[r]->(target)
        RETURN type(r) AS rel_type, target.name AS target_name,
               r.source_sample_id AS sample_id, r.dosage AS dosage, r.confidence AS confidence,
               r.negated AS negated, r.temporal AS temporal, r.head_surface AS head_surface, r.tail_surface AS tail_surface
        """, {"old_name": old_name})

        for r in out_rels:
            rel_type = r["rel_type"]
            target_name = r["target_name"]
            sample_id = r["sample_id"] or ""
            r_dosage = r["dosage"] or dosage or ""

            client.execute_query(f"""
            MATCH (active {{name: $active_name}}), (t {{name: $target_name}})
            CREATE (active)-[r_new:{rel_type}]->(t)
            SET r_new.source_sample_id = $sample_id,
                r_new.dosage = $r_dosage,
                r_new.confidence = $confidence,
                r_new.negated = $negated,
                r_new.temporal = $temporal,
                r_new.head_surface = $head_surface,
                r_new.tail_surface = $tail_surface
            """, {
                "active_name": active_name,
                "target_name": target_name,
                "sample_id": sample_id,
                "r_dosage": r_dosage,
                "confidence": r.get("confidence", 0.9),
                "negated": r.get("negated", False),
                "temporal": r.get("temporal", "unknown"),
                "head_surface": r.get("head_surface"),
                "tail_surface": r.get("tail_surface")
            })

        # Move incoming relationships
        in_rels = client.execute_query("""
        MATCH (source)-[r]->(old {name: $old_name})
        RETURN source.name AS source_name, type(r) AS rel_type,
               r.source_sample_id AS sample_id, r.dosage AS dosage, r.confidence AS confidence,
               r.negated AS negated, r.temporal AS temporal, r.head_surface AS head_surface, r.tail_surface AS tail_surface
        """, {"old_name": old_name})

        for r in in_rels:
            source_name = r["source_name"]
            rel_type = r["rel_type"]
            sample_id = r["sample_id"] or ""
            r_dosage = r["dosage"] or dosage or ""

            client.execute_query(f"""
            MATCH (s {{name: $source_name}}), (active {{name: $active_name}})
            CREATE (s)-[r_new:{rel_type}]->(active)
            SET r_new.source_sample_id = $sample_id,
                r_new.dosage = $r_dosage,
                r_new.confidence = $confidence,
                r_new.negated = $negated,
                r_new.temporal = $temporal,
                r_new.head_surface = $head_surface,
                r_new.tail_surface = $tail_surface
            """, {
                "source_name": source_name,
                "active_name": active_name,
                "sample_id": sample_id,
                "r_dosage": r_dosage,
                "confidence": r.get("confidence", 0.9),
                "negated": r.get("negated", False),
                "temporal": r.get("temporal", "unknown"),
                "head_surface": r.get("head_surface"),
                "tail_surface": r.get("tail_surface")
            })

        client.execute_query("MATCH (old {name: $old_name}) DETACH DELETE old", {"old_name": old_name})


def apply_node_labels(client: Neo4jClient):
    """Sets :DRUG, :DISEASE, and :SYMPTOM labels on all nodes in Neo4j."""
    diseases = [
        'Bệnh Migraine', 'Bệnh phổi tắc nghẽn mạn tính', 'Cao huyết áp', 'Cường giáp', 'Hen phế quản',
        'Loãng xương', 'Mụn trứng cá', 'Nhiễm trùng đường tiết niệu', 'Nhồi máu não', 'Nấm da',
        'Phì đại lành tính tuyến tiền liệt', 'Rung nhĩ', 'Ruột kích thích', 'Rối loạn lipid máu',
        'Rối loạn lo âu', 'Rối loạn lo âu lan tỏa', 'Suy giáp', 'Suy tim sung huyết', 'Suy tuyến thượng thận',
        'Sỏi thận', 'Thalassemia', 'Thiếu máu thiếu sắt', 'Thoái hóa khớp gối',
        'Thoát vị đĩa đệm cột sống thắt lưng', 'Trào ngược dạ dày thực quản', 'U xơ tử cung',
        'Viêm da cơ địa', 'Viêm dạ dày ruột nhiễm khuẩn', 'Viêm gan vi-rút B mạn', 'Viêm gân vai',
        'Viêm khớp dạng thấp', 'Viêm loét dạ dày', 'Viêm mũi dị ứng', 'Viêm mũi họng cấp',
        'Viêm phế quản cấp', 'Viêm phổi', 'Viêm ruột thừa cấp', 'Viêm âm đạo do nấm',
        'Xơ vữa động mạch cảnh', 'Đa nang buồng trứng', 'Đau thắt lưng', 'Đái tháo đường týp 2', 'Động kinh'
    ]
    client.execute_query("MATCH (n) WHERE n.name IN $diseases SET n:DISEASE", {"diseases": diseases})

    # Drug nodes (any non-disease node connected via drug relations or has code/drug name)
    client.execute_query("""
    MATCH (n)-[r:PRESCRIBED_FOR|CONTRAINDICATED_FOR]-()
    WHERE NOT n:DISEASE
    SET n:DRUG
    """)
    client.execute_query("""
    MATCH (n)-[r:TREATS]->()
    WHERE NOT n:DISEASE
    SET n:DRUG
    """)

    # Symptom nodes
    client.execute_query("""
    MATCH (n) WHERE NOT n:DISEASE AND NOT n:DRUG
    SET n:SYMPTOM
    """)


def run_live_qd2_migration():
    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j offline!")
        return

    print("Step 1: Migrating Meloxicam & Hydrocortisone...")
    relocate_node_edges(client, "Meloxicam 15mg", "Meloxicam", "15mg")
    relocate_node_edges(client, "Meloxicam 7.5mg", "Meloxicam", "7.5mg")
    relocate_node_edges(client, "Hydrocortisone 10mg", "Hydrocortisone", "10mg")
    relocate_node_edges(client, "Hydrocortisone", "Hydrocortisone", "")

    print("Step 2: Migrating all remaining drug nodes...")
    nodes = client.execute_query("MATCH (d) RETURN d.name AS name ORDER BY d.name")
    for row in nodes:
        name = row["name"]
        if name in ("Meloxicam", "Hydrocortisone"):
            continue
        ing, dos = parse_drug_name(name)
        if ing != name or dos:
            relocate_node_edges(client, name, ing, dos)

    print("Step 3: Labeling nodes (DRUG, DISEASE, SYMPTOM)...")
    apply_node_labels(client)

    print("Step 4: Ensuring drug_code constraint exists...")
    client.execute_query("CREATE CONSTRAINT drug_code IF NOT EXISTS FOR (d:DRUG) REQUIRE d.code IS UNIQUE")

    total_rels = client.execute_query("MATCH ()-[r]->() RETURN count(r) AS cnt")[0]["cnt"]
    drug_cnt = client.execute_query("MATCH (d:DRUG) RETURN count(d) AS cnt")[0]["cnt"]
    print(f"\n✅ Migration complete! Total relationships: {total_rels}, Total DRUG nodes: {drug_cnt}")


if __name__ == "__main__":
    run_live_qd2_migration()
