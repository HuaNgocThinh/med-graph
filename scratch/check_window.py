import sys
sys.stdout.reconfigure(encoding="utf-8")

text = "Bệnh nhân nữ 42 tuổi, nhập viện vì Cơn đau thắt ngực cấp tính. Tiền sử chưa ghi nhận Bệnh Gút. Bác sĩ chỉ định Aspirin 81mg và Atorvastatin để điều trị."
ent_text = "Aspirin 81mg"

start = text.find(ent_text)
end = start + len(ent_text)
window_chars = 45

pre_window = text[max(0, start - window_chars):start]
post_window = text[end:min(len(text), end + window_chars)]

print(f"Entity: {ent_text}")
print(f"Pre-window: '{pre_window}'")
print(f"Post-window: '{post_window}'")
