import os
import sys
from pathlib import Path
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field

# Đảm bảo import được các module trong thư mục src bất kể vị trí khởi chạy
CURRENT_DIR = Path(__file__).resolve().parent
if str(CURRENT_DIR) not in sys.path:
    sys.path.insert(0, str(CURRENT_DIR))

from predict import extract_medical_info
from graph_builder import MedGraphBuilder

# 1. Khởi tạo FastAPI App
app = FastAPI(
    title="MedGraph-VI API",
    description="REST API trích xuất thực thể y tế, quan hệ và đồng bộ Đồ thị tri thức Neo4j.",
    version="1.0.0",
)


# 2. Định nghĩa Pydantic Schema cho Request Body
class MedicalRecord(BaseModel):
    text: str = Field(
        ...,
        description="Văn bản mô tả bệnh án hoặc triệu chứng lâm sàng của bệnh nhân.",
        example="Bác sĩ kê đơn Paracetamol để điều trị triệu chứng đau đầu cho bệnh nhân.",
    )


# 3. Health Check Endpoint
@app.get("/health", status_code=status.HTTP_200_OK, tags=["Health Check"])
def health_check():
    """
    Endpoint kiểm tra trạng thái hoạt động của Service.
    """
    return {"status": "ok", "message": "MedGraph-VI API is running"}


# 4. Extraction API Endpoint
@app.post("/api/v1/extract", status_code=status.HTTP_200_OK, tags=["Extraction"])
def extract_and_build_graph(request: MedicalRecord):
    """
    API trích xuất thông tin y tế (NER & RE) bằng mô hình PhoBERT AI,
    tự động lưu bộ ba tri thức (Triplet) vào Neo4j nếu phát hiện quan hệ hợp lệ.
    """
    if not request.text or len(request.text.strip()) < 5:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Văn bản đầu vào không được để trống và phải có ít nhất 5 ký tự.",
        )

    # Cấu hình thông số Neo4j
    URI = "bolt://localhost:7687"
    USER = "neo4j"
    PASSWORD = os.getenv("NEO4J_PASSWORD", "medgraph_secret_password")

    builder = MedGraphBuilder(URI, USER, PASSWORD)
    neo4j_synced = False
    message = "Đã trích xuất thông tin thành công."

    try:
        # Bước 1: Trích xuất thực thể và quan hệ bằng AI Model
        result = extract_medical_info(request.text)

        # Bước 2: Kiểm tra và nạp lên Neo4j nếu có quan hệ thực thể
        if (
            result
            and result.get("relation")
            and result["relation"] != "NONE"
            and result.get("entity_1")
            and result.get("entity_2")
        ):
            e1_name = result["entity_1"]["text"]
            e1_type = result["entity_1"]["type"]
            e2_name = result["entity_2"]["text"]
            e2_type = result["entity_2"]["type"]
            relation = result["relation"]

            builder.add_triplet(e1_name, e1_type, relation, e2_name, e2_type)
            neo4j_synced = True
            message = (
                f"Đã trích xuất thành công và đồng bộ bộ ba "
                f"({e1_name}:{e1_type}) -[{relation}]-> ({e2_name}:{e2_type}) lên Neo4j!"
            )
        else:
            message = "Đã trích xuất thành công. Bỏ qua đồng bộ Neo4j do không có quan hệ (Relation == 'NONE')."

        return {
            "status": "success",
            "message": message,
            "data": result,
            "neo4j_synced": neo4j_synced,
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Xảy ra lỗi trong quá trình xử lý AI/Graph: {str(e)}",
        )
    finally:
        builder.close()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
