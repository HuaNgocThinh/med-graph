import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from src.ner.ner_ensemble import NEREnsemble
from src.negation_temporal.context_processor import ConTextProcessor
from src.llm_client import LLMClient

text = "Bệnh nhân nữ 42 tuổi, nhập viện vì Cơn đau thắt ngực cấp tính. Tiền sử chưa ghi nhận Bệnh Gút. Bác sĩ chỉ định Aspirin 81mg và Atorvastatin để điều trị."

llm_client = LLMClient()
ner_ensemble = NEREnsemble(llm_client=llm_client)
context_proc = ConTextProcessor()

entities = ner_ensemble.extract_entities(text)
processed = context_proc.process_entities(text, entities)

print("Entities negation status:")
for e in processed:
    print(f"Entity: {e['entity']}, Type: {e['type']}, Negated: {e.get('negated', False)}, Temporal: {e.get('temporal', False)}")
