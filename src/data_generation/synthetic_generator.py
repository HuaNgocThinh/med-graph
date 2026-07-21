"""
Stage A: Synthetic Medical Text Generation module.
Uses LLMClient (with Gemini/OpenAI/Anthropic or Mock mode) to generate 50-100 structured Vietnamese medical text samples.
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any
from src.config import SYNTHETIC_DATA_DIR
from src.llm_client import LLMClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger("SyntheticGenerator")

TEMPLATES = ["nội khoa", "ngoại khoa", "kê đơn thuốc", "tiền sử bệnh lý"]

SYSTEM_PROMPT = """Bạn là chuyên gia y tế và tạo dữ liệu huấn luyện NLP tiếng Việt.
Nhiệm vụ của bạn là sinh ra các đoạn văn bản y tế giả lập tiếng Việt chất lượng cao.
Mỗi văn bản phải tuân thủ các yêu cầu:
1. Chứa các tên bệnh (ICD-10 tiếng Việt) và tên thuốc (RxNorm tiếng Việt) thực tế.
2. Đa dạng cú pháp: có câu chứa phủ định ("không có", "chưa ghi nhận", "loại trừ", "không thấy"), có câu chứa thời gian ("3 ngày trước", "hiện tại", "tiền sử 2 năm"), có câu chứa nhiều thực thể.
3. Trả về đúng định dạng JSON array với các trường: "id", "text", "template_type".
"""

class SyntheticDataGenerator:
    """Generator for synthetic Vietnamese clinical text."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()

    def generate_batch(self, num_samples: int = 50) -> List[Dict[str, Any]]:
        """Generates synthetic medical text samples via LLM."""
        logger.info(f"Generating {num_samples} synthetic medical text samples...")
        
        prompt = f"""Hãy sinh ngẫu nhiên {num_samples} đoạn văn bản y tế tiếng Việt theo các template ({', '.join(TEMPLATES)}).
Định dạng đầu ra là JSON Array không chứa văn bản dư thừa:
[
  {{
    "id": "syn_001",
    "template_type": "nội khoa",
    "text": "Bệnh nhân nam 50 tuổi có tiền sử Cao huyết áp..."
  }}
]
"""
        results = self.llm.generate_json(prompt, system_prompt=SYSTEM_PROMPT)
        
        # Validation and fallback padding if LLM generated fewer samples or invalid list
        if not isinstance(results, list) or len(results) == 0:
            logger.warning("LLM response was not a valid list. Generating fallback template set.")
            results = self._generate_fallback_templates(num_samples)

        # Ensure correct ID format
        for idx, item in enumerate(results):
            if not isinstance(item, dict):
                continue
            item["id"] = f"syn_{idx+1:03d}"
            if "template_type" not in item:
                item["template_type"] = TEMPLATES[idx % len(TEMPLATES)]

        logger.info(f"Successfully generated {len(results)} synthetic medical samples.")
        return results

    def save_to_file(self, data: List[Dict[str, Any]], filename: str = "synthetic_data.json") -> Path:
        """Saves generated synthetic samples to disk."""
        output_path = SYNTHETIC_DATA_DIR / filename
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        logger.info(f"Saved synthetic dataset to '{output_path}'")
        return output_path

    def _generate_fallback_templates(self, num_samples: int) -> List[Dict[str, Any]]:
        """Fallback deterministic dataset generator for offline / local CPU operation."""
        base_samples = [
            {"template_type": "nội khoa", "text": "Bệnh nhân nam 54 tuổi có tiền sử Đái tháo đường týp 2 và Cao huyết áp 3 năm nay. Hiện tại ho kéo dài và khó thở. Bác sĩ kê Metformin 500mg và Paracetamol."},
            {"template_type": "ngoại khoa", "text": "Bệnh nhân nữ 42 tuổi nhập viện 2 ngày trước vì Cơn đau thắt ngực cấp. Tiền sử chưa ghi nhận Bệnh Gút. Chỉ định Aspirin 81mg và Atorvastatin."},
            {"template_type": "kê đơn thuốc", "text": "Bệnh nhân bị Viêm loét dạ dày kèm trào ngược dạ dày. Không phát hiện Tiêu chảy cấp. Chống chỉ định với Ibuprofen. Đã dùng Omeprazole 20mg."},
            {"template_type": "tiền sử bệnh lý", "text": "Khám lâm sàng chưa thấy dấu hiệu Hen phế quản. Bệnh nhân có tiền sử Viêm mũi dị ứng từ 6 tháng trước, hiện tại không sốt."},
            {"template_type": "nội khoa", "text": "Bệnh nhân chẩn đoán Nhồi máu não cấp tính. Không có tiền sử Suy giáp. Điều trị bằng Clopidogrel 75mg kết hợp Atorvastatin 20mg."}
        ]
        
        expanded = []
        for i in range(num_samples):
            template = base_samples[i % len(base_samples)].copy()
            template["id"] = f"syn_{i+1:03d}"
            expanded.append(template)
        return expanded

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    samples = generator.generate_batch(num_samples=50)
    generator.save_to_file(samples)
