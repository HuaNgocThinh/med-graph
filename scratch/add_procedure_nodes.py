import json
from src.graph.neo4j_client import Neo4jClient

def main():
    client = Neo4jClient()
    if not client.is_online():
        print("Neo4j is offline!")
        return

    procedure_triples = [
        {'proc_name': 'Phẫu thuật nội soi', 'proc_surface': 'phẫu thuật nội soi', 'disease': 'Viêm ruột thừa cấp', 'dis_surface': 'Viêm ruột thừa cấp', 'sid': 'syn_005', 'negated': False},
        {'proc_name': 'Siêu âm', 'proc_surface': 'siêu âm', 'disease': 'Viêm ruột thừa cấp', 'dis_surface': 'Viêm ruột thừa cấp', 'sid': 'syn_005', 'negated': False},
        {'proc_name': 'Điện tâm đồ', 'proc_surface': 'điện tâm đồ', 'disease': 'Cao huyết áp', 'dis_surface': 'Cao huyết áp', 'sid': 'syn_011', 'negated': False},
        {'proc_name': 'Nội soi dạ dày', 'proc_surface': 'Nội soi dạ dày', 'disease': 'Viêm loét dạ dày', 'dis_surface': 'Viêm loét dạ dày tá tràng', 'sid': 'syn_012', 'negated': False},
        {'proc_name': 'Xét nghiệm HbA1c', 'proc_surface': 'Xét nghiệm HbA1c', 'disease': 'Đái tháo đường týp 2', 'dis_surface': 'Đái tháo đường tuýp 2', 'sid': 'syn_015', 'negated': False},
        {'proc_name': 'Chụp MRI', 'proc_surface': 'chụp MRI', 'disease': 'Bệnh Migraine', 'dis_surface': 'Đau nửa đầu (Migraine)', 'sid': 'syn_016', 'negated': False},
        {'proc_name': 'Xét nghiệm nước tiểu', 'proc_surface': 'Xét nghiệm nước tiểu', 'disease': 'Nhiễm trùng đường tiết niệu', 'dis_surface': 'Nhiễm khuẩn đường tiết niệu', 'sid': 'syn_020', 'negated': False},
        {'proc_name': 'Siêu âm', 'proc_surface': 'Siêu âm', 'disease': 'Sỏi thận', 'dis_surface': 'Sỏi thận', 'sid': 'syn_031', 'negated': False},
        {'proc_name': 'Vật lý trị liệu', 'proc_surface': 'vật lý trị liệu', 'disease': 'Tai biến mạch máu脑', 'dis_surface': 'Tai biến mạch máu脑', 'sid': 'syn_038', 'negated': False},
        {'proc_name': 'Truyền máu', 'proc_surface': 'truyền máu', 'disease': 'Tan máu bẩm sinh', 'dis_surface': 'Tan máu bẩm sinh (Thalassemia)', 'sid': 'syn_043', 'negated': True},
        {'proc_name': 'Phẫu thuật nội soi cắt ruột thừa', 'proc_surface': 'phẫu thuật nội soi cắt ruột thừa', 'disease': 'Viêm ruột thừa cấp', 'dis_surface': 'Viêm ruột thừa cấp', 'sid': 'syn_069', 'negated': False},
        {'proc_name': 'Điện não đồ', 'proc_surface': 'điện não đồ', 'disease': 'Động kinh', 'dis_surface': 'Động kinh', 'sid': 'syn_073', 'negated': False},
        {'proc_name': 'Phẫu thuật nội soi cắt ruột thừa', 'proc_surface': 'phẫu thuật nội soi cắt ruột thừa', 'disease': 'Viêm ruột thừa cấp', 'dis_surface': 'Viêm ruột thừa cấp', 'sid': 'syn_088', 'negated': False},
        {'proc_name': 'Phẫu thuật nội soi cắt ruột thừa', 'proc_surface': 'phẫu thuật nội soi cắt ruột thừa', 'disease': 'Viêm ruột thừa cấp', 'dis_surface': 'Viêm ruột thừa cấp', 'sid': 'syn_092', 'negated': False},
        {'proc_name': 'Phẫu thuật', 'proc_surface': 'phẫu thuật', 'disease': 'Viêm ruột thừa cấp', 'dis_surface': 'Viêm ruột thừa cấp', 'sid': 'syn_095', 'negated': False},
    ]

    cypher_cmd = """
    MERGE (p:PROCEDURE {name: $proc_name})
    ON CREATE SET p.first_surface = $proc_surface, p.created_at = datetime()
    MERGE (d:DISEASE {name: $disease})
    ON CREATE SET d.first_surface = $dis_surface, d.created_at = datetime()
    MERGE (p)-[r:PERFORMED_FOR]->(d)
    SET r.confidence = 0.95,
        r.negated = $negated,
        r.source_sample_id = $sid,
        r.head_surface = $proc_surface,
        r.tail_surface = $dis_surface
    """

    for item in procedure_triples:
        client.execute_query(cypher_cmd, parameters=item)

    print("Successfully added PROCEDURE nodes & PERFORMED_FOR edges to Neo4j.")
    schema = client.get_graph_schema(force_refresh=True)
    print("Updated Graph Schema:")
    print(json.dumps(schema, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
