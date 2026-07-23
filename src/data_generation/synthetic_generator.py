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

TEMPLATES = [
    "nội khoa", "ngoại khoa", "kê đơn thuốc", "tiền sử bệnh lý",
    "sản phụ khoa", "nhi khoa", "da liễu", "tiết niệu", "huyết học"
]

SYSTEM_PROMPT = """Bạn là chuyên gia y tế và tạo dữ liệu huấn luyện NLP tiếng Việt.
Nhiệm vụ của bạn là sinh ra các đoạn văn bản y tế giả lập tiếng Việt chất lượng cao.
Mỗi văn bản phải tuân thủ các yêu cầu:
1. Độ phủ chuyên khoa rộng: Tim mạch, Tiêu hóa, Hô hấp, Cơ xương khớp, Nội tiết, Thần kinh, Sản phụ khoa, Nhi khoa, Da liễu, Tiết niệu, Huyết học.
2. Chứa các tên bệnh (ICD-10 tiếng Việt) và tên thuốc (RxNorm tiếng Việt) thực tế.
3. Đa dạng cú pháp: có câu chứa phủ định ("không có", "chưa ghi nhận", "loại trừ", "không thấy"), có câu chứa thời gian ("3 ngày trước", "hiện tại", "tiền sử 2 năm"), có câu chứa nhiều thực thể.
4. Trả về đúng định dạng JSON array với các trường: "id", "text", "template_type".
"""

class SyntheticDataGenerator:
    """Generator for synthetic Vietnamese clinical text."""

    def __init__(self, llm_client: LLMClient = None):
        self.llm = llm_client or LLMClient()

    def generate_batch(self, num_samples: int = 50) -> List[Dict[str, Any]]:
        """Generates synthetic medical text samples via LLM."""
        logger.info(f"Generating {num_samples} synthetic medical text samples...")
        
        prompt = f"""Hãy sinh ngẫu nhiên {num_samples} đoạn văn bản y tế tiếng Việt thuộc các chuyên khoa (Tim mạch, Tiêu hóa, Hô hấp, Cơ xương khớp, Nội tiết, Thần kinh, Sản phụ khoa, Nhi khoa, Da liễu, Tiết niệu, Huyết học).
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
        if not isinstance(results, list) or len(results) < num_samples:
            logger.warning(f"LLM generated {len(results) if isinstance(results, list) else 0} samples, which is less than requested {num_samples}. Applying comprehensive fallback template set.")
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
        """Fallback deterministic dataset generator covering 11 medical specialties for 50 samples."""
        base_50_samples = [
            # 1-10: Existing audited samples
            {"template_type": "nội khoa", "text": "Bệnh nhân nam 54 tuổi, có tiền sử Đái tháo đường týp 2 và Cao huyết áp 3 năm nay. Hiện tại ho kéo dài và khó thở. Khám không thấy dấu hiệu Viêm phổi. Bệnh nhân được kê Paracetamol 500mg và Metformin."},
            {"template_type": "ngoại khoa", "text": "Bệnh nhân nữ 42 tuổi, nhập viện vì Cơn đau thắt ngực cấp tính. Tiền sử chưa ghi nhận Bệnh Gút. Bác sĩ chỉ định Aspirin 81mg và Atorvastatin để điều trị."},
            {"template_type": "kê đơn thuốc", "text": "Bệnh nhân Viêm loét dạ dày kèm trào ngược dạ dày. Không phát hiện Tiêu chảy cấp. Chống chỉ định với Ibuprofen. Đã kê Omeprazole 20mg."},
            {"template_type": "nội khoa", "text": "Bệnh nhân nam 65 tuổi nhập viện với chẩn đoán xác định Đái tháo đường tuýp 2. Hiện tại, bệnh nhân không có triệu chứng đau ngực hay khó thở, các chỉ số sinh tồn ổn định. Tiền sử 5 năm điều trị bằng Metformin nhưng chưa ghi nhận biến chứng võng mạc."},
            {"template_type": "ngoại khoa", "text": "Bệnh nhân nữ 32 tuổi được chỉ định phẫu thuật nội soi do Viêm ruột thừa cấp. Sau 3 ngày trước khi nhập viện, bệnh nhân đau âm ỉ vùng hố chậu phải. Kết quả siêu âm loại trừ các bệnh lý phụ khoa, không thấy dấu hiệu thủng tạng rỗng."},
            {"template_type": "kê đơn thuốc", "text": "Chỉ định điều trị cho bệnh nhân Viêm phế quản cấp: Amoxicillin 500mg uống 2 lần/ngày trong 7 ngày, kết hợp với Bromhexine 8mg để long đờm. Bệnh nhân không có tiền sử dị ứng với nhóm Penicillin."},
            {"template_type": "tiền sử bệnh lý", "text": "Bệnh nhân có tiền sử 2 năm mắc Hen phế quản, hiện đang kiểm soát tốt bằng Salbutamol khi cần thiết. Chưa ghi nhận các đợt cấp tính trong 6 tháng gần đây, không thấy dấu hiệu suy hô hấp khi gắng sức."},
            {"template_type": "nội khoa", "text": "Thăm khám lâm sàng bệnh nhân Suy tim sung huyết cho thấy tình trạng phù hai chi dưới. Bác sĩ đã kê đơn Furosemide 40mg và Lisinopril 10mg. Hiện tại, bệnh nhân không có dấu hiệu khó thở khi nằm đầu thấp."},
            {"template_type": "ngoại khoa", "text": "Bệnh nhân nam 45 tuổi nhập viện vì Thoát vị đĩa đệm cột sống thắt lưng. Tiền sử 1 năm đau thần kinh tọa, đã điều trị bảo tồn bằng Diclofenac nhưng không thuyên giảm. Hiện tại, bác sĩ loại trừ các tổn thương chèn ép tủy cấp tính."},
            {"template_type": "kê đơn thuốc", "text": "Đơn thuốc ngoại trú cho bệnh nhân Rối loạn lipid máu: Atorvastatin 20mg uống vào buổi tối. Bệnh nhân cần tái khám sau 1 tháng để kiểm tra chỉ số men gan, hiện tại không thấy tác dụng phụ đau cơ hay mệt mỏi."},

            # 11-15: Sản phụ khoa
            {"template_type": "sản phụ khoa", "text": "Bệnh nhân nữ 28 tuổi mang thai 12 tuần khám thai định kỳ. Chẩn đoán Viêm âm đạo do nấm. Bác sĩ chỉ định Clotrimazole đặt âm đạo. Tiền sử không có Tăng huyết áp thai kỳ."},
            {"template_type": "sản phụ khoa", "text": "Bệnh nhân nữ 38 tuổi nhập viện vì đau bụng dưới dữ dội. Kết quả siêu âm chẩn đoán U xơ tử cung kích thước 4cm. Hiện tại không sốt, không có dấu hiệu viêm phần phụ."},
            {"template_type": "sản phụ khoa", "text": "Bệnh nhân thai 34 tuần xuất hiện hiện tượng Phù hai chi dưới và nhức đầu. Chẩn đoán Tiền giật giật. Bác sĩ chỉ định Methyldopa để hạ huyết áp."},
            {"template_type": "sản phụ khoa", "text": "Bệnh nhân nữ 25 tuổi khám phụ khoa do khí hư bất thường. Chẩn đoán Viêm phần phụ mạn tính. Đã kê đơn Metronidazole 250mg uống 5 ngày."},
            {"template_type": "sản phụ khoa", "text": "Bệnh nhân thai 20 tuần kiểm tra sức khỏe. Tiền sử 3 năm điều trị Suy giáp bằng Levothyroxine. Khám lâm sàng thai nhi phát triển bình thường."},

            # 16-20: Nhi khoa
            {"template_type": "nhi khoa", "text": "Bệnh nhi nam 4 tuổi vào viện vì sốt cao và ho khò khè. Chẩn đoán Viêm phế quản co thắt. Bác sĩ kê Salbutamol khí dung và Paracetamol hạ sốt."},
            {"template_type": "nhi khoa", "text": "Bệnh nhi nữ 2 tuổi sốt cao 39 độ C kèm co giật toàn thân. Chẩn đoán Sốt cao co giật. Đã dùng Dexamethasone và Paracetamol để hạ sốt cấp tốc."},
            {"template_type": "nhi khoa", "text": "Bệnh nhi 18 tháng tuổi đi ngoài phân lỏng 5 lần/ngày. Chẩn đoán Tiêu chảy cấp. Chỉ định bù nước Oresol và không dùng kháng sinh Ciprofloxacin."},
            {"template_type": "nhi khoa", "text": "Bệnh nhi nam 6 tuổi đau tai phải và quấy khóc. Khám tai chẩn đoán Viêm tai giữa cấp. Bác sĩ chỉ định Amoxicillin 500mg uống trong 7 ngày."},
            {"template_type": "nhi khoa", "text": "Bệnh nhi 5 tuổi ho nhiều về đêm kèm sốt nhẹ. Khám họng phát hiện Viêm amiđan cấp. Chỉ định dùng Augmentin và Bromhexine long đờm."},

            # 21-25: Da liễu
            {"template_type": "da liễu", "text": "Bệnh nhân nam 29 tuổi nổi ngứa tổn thương dạng chàm ở hai cẳng tay. Chẩn đoán Viêm da cơ địa. Bác sĩ chỉ định Desloratadine 5mg và kem bôi da."},
            {"template_type": "da liễu", "text": "Bệnh nhân nữ 35 tuổi xuất hiện các nốt sẩn đỏ ngứa toàn thân sau khi ăn hải sản. Chẩn đoán Mày đay cấp. Đã kê Prednisolone 5mg để giảm phản ứng dị ứng."},
            {"template_type": "da liễu", "text": "Bệnh nhân nam 50 tuổi tổn thương vảy trắng trên nền da đỏ ở cùi trỏ. Chẩn đoán Vảy nến mạn tính. Hiện tại không có triệu chứng đau khớp."},
            {"template_type": "da liễu", "text": "Bệnh nhân nữ 22 tuổi xuất hiện mụn mủ ở mặt và lưng. Chẩn đoán Mụn trứng cá nhiễm khuẩn. Bác sĩ chỉ định Azithromycin 500mg."},
            {"template_type": "da liễu", "text": "Bệnh nhân ngứa ngáy vùng kẽ chân do nấm da chân. Chẩn đoán Nhiễm nấm da. Chỉ định bôi Clotrimazole 2 lần/ngày."},

            # 26-30: Tiết niệu
            {"template_type": "tiết niệu", "text": "Bệnh nhân nam 48 tuổi đau quặn thắt vùng thắt lưng phải. Kết quả chụp X-quang phát hiện Sỏi thận kích thước 7mm. Bác sĩ kê thuốc giảm đau Ibuprofen."},
            {"template_type": "tiết niệu", "text": "Bệnh nhân nữ 31 tuổi tiểu buốt, tiểu rắt kèm sốt nhẹ. Chẩn đoán Nhiễm trùng đường tiết niệu. Chỉ định điều trị bằng Cefuroxime 500mg."},
            {"template_type": "tiết niệu", "text": "Bệnh nhân nam 60 tuổi đái máu vi thể và đau hông lưng. Kết quả siêu âm chẩn đoán Sỏi niệu quản. Đã kê Ciprofloxacin 500mg ngừa nhiễm trùng."},
            {"template_type": "tiết niệu", "text": "Bệnh nhân nữ 52 tuổi tiểu nhiều lần và đau hạ vị. Chẩn đoán Viêm bàng quang cấp. Bác sĩ chỉ định Augmentin uống trong 5 ngày."},
            {"template_type": "tiết niệu", "text": "Bệnh nhân nam 55 tuổi tiền sử Sỏi thận 2 năm nay. Hiện tại kiểm tra chức năng thận bình thường, không có dấu hiệu suy thận."},

            # 31-35: Huyết học
            {"template_type": "huyết học", "text": "Bệnh nhân nữ 24 tuổi mệt mỏi, da xanh xao. Xét nghiệm công thức máu chẩn đoán Thiếu máu thiếu sắt. Bác sĩ kê Ferrous sulfate bổ sung sắt."},
            {"template_type": "huyết học", "text": "Bệnh nhân nam 40 tuổi xuất hiện nhiều nốt xuất huyết dưới da. Chẩn đoán Xuất huyết giảm tiểu cầu. Chỉ định dùng Prednisolone liều cao."},
            {"template_type": "huyết học", "text": "Bệnh nhân nữ 19 tuổi tiền sử bệnh lý gia đình mắc Thalassemia. Xét nghiệm hemoglobin giảm nhẹ, hiện tại không cần truyền máu."},
            {"template_type": "huyết học", "text": "Bệnh nhân nam 68 tuổi mệt mỏi kéo dài, sốt nhẹ về chiều. Xét nghiệm chẩn đoán Suy tủy xương. Bác sĩ chỉ định theo dõi chuyên khoa huyết học."},
            {"template_type": "huyết học", "text": "Bệnh nhân nữ 45 tuổi tiền sử huyết khối tĩnh mạch. Chẩn đoán Tăng đông máu. Bác sĩ chỉ định dùng Warfarin để phòng ngừa tắc mạch."},

            # 36-40: Thần kinh & Cơ xương khớp nâng cao
            {"template_type": "thần kinh", "text": "Bệnh nhân nữ 34 tuổi đau nửa đầu dữ dội kèm buồn nôn. Chẩn đoán Bệnh Migraine. Bác sĩ kê Paracetamol và dặn nghỉ ngơi nơi phòng tối."},
            {"template_type": "thần kinh", "text": "Bệnh nhân nam 70 tuổi đột ngột yếu nửa người trái. Chẩn đoán Nhồi máu não cấp. Chỉ định điều trị bằng Clopidogrel và Atorvastatin."},
            {"template_type": "cơ xương khớp", "text": "Bệnh nhân nam 52 tuổi sưng nóng đỏ đau khớp ngón chân cái. Chẩn đoán Bệnh Gút cấp. Chỉ định Allopurinol 300mg và Colchicine."},
            {"template_type": "cơ xương khớp", "text": "Bệnh nhân nữ 62 tuổi đau nhức hai khớp gối khi đi lại. Chẩn đoán Thoái hóa khớp gối. Bác sĩ chỉ định Glucosamine và Diclofenac khi đau."},
            {"template_type": "cơ xương khớp", "text": "Bệnh nhân nữ 45 tuổi cứng khớp buổi sáng kéo dài 1 giờ. Chẩn đoán Viêm khớp dạng thấp. Chỉ định dùng Prednisolone và Methotrexate."},

            # 41-45: Nội tiết & Tiêu hóa nâng cao
            {"template_type": "nội tiết", "text": "Bệnh nhân nam 36 tuổi hồi hộp đánh trống ngực, gầy sút cân. Chẩn đoán Cường giáp. Bác sĩ chỉ định dùng Methimazole 10mg."},
            {"template_type": "nội tiết", "text": "Bệnh nhân nữ 50 tuổi sợ lạnh, mệt mỏi, da khô. Chẩn đoán Suy giáp mạn tính. Chỉ định điều trị thay thế bằng Levothyroxine."},
            {"template_type": "nội tiết", "text": "Bệnh nhân nam 58 tuổi xét nghiệm mỡ máu tăng cao. Chẩn đoán Rối loạn lipid máu. Đã kê Atorvastatin 20mg uống buổi tối."},
            {"template_type": "tiêu hóa", "text": "Bệnh nhân nam 44 tuổi đau vùng thượng vị sau khi ăn. Chẩn đoán Viêm dạ dày HP dương tính. Đã kê Omeprazole kết hợp Amoxicillin."},
            {"template_type": "tiêu hóa", "text": "Bệnh nhân nữ 29 tuổi ợ chua, nóng rát sau xương ức. Chẩn đoán Trào ngược dạ dày thực quản. Chỉ định dùng Esomeprazole 40mg."},

            # 46-50: Hô hấp & Tim mạch nâng cao
            {"template_type": "hô hấp", "text": "Bệnh nhân nam 61 tuổi tiền sử 10 năm hút thuốc lá, khó thở khi gắng sức. Chẩn đoán Bệnh phổi tắc nghẽn mạn tính. Chỉ định Salbutamol xịt."},
            {"template_type": "hô hấp", "text": "Bệnh nhân nữ 33 tuổi ho hắt hơi khi thay đổi thời tiết. Chẩn đoán Viêm mũi dị ứng. Bác sĩ kê Desloratadine 5mg."},
            {"template_type": "tim mạch", "text": "Bệnh nhân nam 67 tuổi huyết áp đo tại phòng khám 160/95 mmHg. Chẩn đoán Bệnh cao huyết áp. Bác sĩ chỉ định Amlodipine 5mg."},
            {"template_type": "tim mạch", "text": "Bệnh nhân nữ 59 tuổi tiền sử Cao huyết áp 5 năm. Đang điều trị ổn định bằng Telmisartan 40mg, không có tác dụng phụ ho khan."},
            {"template_type": "tim mạch", "text": "Bệnh nhân nam 53 tuổi đau ngực trái lan ra vai. Chẩn đoán Cơn đau thắt ngực ổn định. Bác sĩ kê Aspirin 81mg và Lisinopril 10mg."}
        ]

        expanded = []
        for i in range(num_samples):
            template = base_50_samples[i % len(base_50_samples)].copy()
            template["id"] = f"syn_{i+1:03d}"
            expanded.append(template)
        return expanded

if __name__ == "__main__":
    generator = SyntheticDataGenerator()
    samples = generator.generate_batch(num_samples=50)
    generator.save_to_file(samples)
