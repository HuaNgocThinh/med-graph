import os
import sys
from neo4j import GraphDatabase


class MedGraphBuilder:
    """
    Class quản lý kết nối và tạo bộ ba tri thức (Knowledge Graph Triplets) trên cơ sở dữ liệu Neo4j.
    """

    def __init__(self, uri: str, user: str, password: str):
        """
        Khởi tạo kết nối driver đến Neo4j Database.
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        """
        Đóng kết nối driver an toàn.
        """
        if self.driver:
            self.driver.close()

    def add_triplet(
        self,
        entity1_name: str,
        entity1_type: str,
        relation: str,
        entity2_name: str,
        entity2_type: str,
    ):
        """
        Thêm một bộ ba tri thức (Node 1 -[Relation]-> Node 2) vào cơ sở dữ liệu Neo4j.

        LƯU Ý KỸ THUẬT:
        - Label của Node (entity1_type, entity2_type) và Type của Relationship (relation)
          không thể truyền qua Cypher Parameter ($param). Do đó bắt buộc dùng f-string.
        - Thuộc tính 'name' của thực thể BẮT BUỘC truyền qua Cypher Parameter ($e1_name, $e2_name)
          để chống lỗi Cypher Injection.
        """
        query = (
            f"MERGE (n1:{entity1_type} {{name: $e1_name}}) "
            f"MERGE (n2:{entity2_type} {{name: $e2_name}}) "
            f"MERGE (n1)-[r:{relation}]->(n2)"
        )

        def _execute_tx(tx):
            tx.run(query, e1_name=entity1_name, e2_name=entity2_name)

        with self.driver.session() as session:
            session.execute_write(_execute_tx)


if __name__ == "__main__":
    # Khởi tạo kết nối đến Neo4j Database (để thông số mặc định local)
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = "medgraph_secret_password"

    print(f"⏳ Đang kết nối tới Neo4j tại {URI}...")
    builder = MedGraphBuilder(URI, USER, PASSWORD)

    try:
        # Đẩy thử bộ ba tri thức thu được từ dự đoán trước đó
        e1_name = "Paracetamol"
        e1_type = "DRUG"
        relation = "TREATS"
        e2_name = "đau đầu"
        e2_type = "SYMPTOM"

        builder.add_triplet(e1_name, e1_type, relation, e2_name, e2_type)
        print(
            f"✅ Đã đẩy thành công bộ ba: ({e1_name}) -[{relation}]-> ({e2_name}) lên Neo4j!"
        )
    except Exception as e:
        print(f"⚠️ Lỗi kết nối/thực thi Neo4j: {e}")
        print("💡 Lưu ý: Hãy đảm bảo dịch vụ Neo4j Server đang chạy tại bolt://localhost:7687")
    finally:
        builder.close()
        print("🔌 Đã đóng kết nối Neo4j an toàn.")
