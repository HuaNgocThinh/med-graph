import sys; sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, r"c:\Users\thinhlaluot\MedGraph")

import json, csv, os
from collections import Counter

SRC = r"c:\Users\thinhlaluot\MedGraph\data\dictionaries\icd10_vi.json"
OUT = r"c:\Users\thinhlaluot\MedGraph\data\exports\icd10_synonyms_audit.csv"

TS = "TRUE_SYNONYM"
SD = "SYMPTOM_AS_DISEASE"
CN = "CATEGORY_NARROWING"
OT = "OTHER"

# (code, synonym) -> (classification, reason)
J = {
 # I10 Bệnh cao huyết áp
 ("I10", "tăng huyết áp"): (TS, "Thuật ngữ y khoa chuẩn cho cao huyết áp; cùng khái niệm, cùng mức cam kết"),
 ("I10", "cao huyết áp"): (TS, "Cách nói thông dụng của tăng huyết áp; cùng khái niệm"),
 ("I10", "bệnh tăng huyết áp"): (TS, "Chỉ thêm tiền tố 'bệnh'; cùng khái niệm"),
 # E11 ĐTĐ týp 2
 ("E11", "tiểu đường týp 2"): (TS, "Tên dân gian của đái tháo đường týp 2; cùng khái niệm, cùng mức đặc hiệu"),
 ("E11", "tiểu đường tuýp 2"): (OT, "Biến thể chính tả týp/tuýp của cùng một cụm từ"),
 ("E11", "đái tháo đường loại 2"): (TS, "'loại 2' = 'týp 2'; cùng khái niệm"),
 ("E11", "bệnh tiểu đường"): (CN, "'Đái tháo đường' là nhóm bệnh (týp 1 E10, thai kỳ O24, thứ phát); gán cứng vào E11 bỏ sót týp 1 vốn có trong chính từ điển này"),
 ("E11", "đái tháo đường tuýp 2"): (OT, "Biến thể chính tả týp/tuýp của chính name_vi"),
 # E10
 ("E10", "tiểu đường týp 1"): (TS, "Tên dân gian của đái tháo đường týp 1; cùng khái niệm"),
 ("E10", "tiểu đường tuýp 1"): (OT, "Biến thể chính tả týp/tuýp"),
 # J18.9 Viêm phổi
 ("J18.9", "viêm phổi cấp"): (TS, "Viêm phổi J18.9 vốn là bệnh cảnh cấp; 'cấp' không đổi mức cam kết"),
 ("J18.9", "viêm phế quản phổi"): (CN, "Bronchopneumonia là thể giải phẫu riêng, mã J18.0 khác J18.9; là một thành viên chứ không đồng nhất với viêm phổi nói chung"),
 ("J18.9", "viêm đường hô hấp dưới"): (CN, "LRTI là nhóm rộng gồm viêm phế quản, viêm tiểu phế quản, viêm phổi; thu hẹp thành viêm phổi là gán chẩn đoán"),
 ("J18.9", "viêm phổi cộng đồng"): (OT, "Biến thể đặc hiệu theo bối cảnh mắc bệnh; CAP không có mã riêng, vẫn về J18.9 khi chưa rõ tác nhân"),
 # J20.9 Viêm phế quản cấp
 ("J20.9", "viêm phế quản"): (CN, "'Viêm phế quản' không định tính bao cả viêm phế quản mạn (J42) và COPD (J44); ép về thể cấp là thu hẹp nhóm và cam kết tính cấp"),
 ("J20.9", "viêm phế quản cấp tính"): (OT, "'cấp tính' = 'cấp'; biến thể từ ngữ của chính name_vi"),
 # K35.8 Viêm ruột thừa cấp
 ("K35.8", "viêm ruột thừa"): (TS, "Viêm ruột thừa không định tính trên lâm sàng luôn là thể cấp; viêm ruột thừa mạn là thực thể gây tranh cãi và hiếm"),
 ("K35.8", "viêm ruột thừa cấp tính"): (OT, "'cấp tính' = 'cấp'; biến thể từ ngữ"),
 # I50.9 Suy tim sung huyết
 ("I50.9", "suy tim"): (TS, "I50.9 là 'suy tim không đặc hiệu'; 'sung huyết' là mô tả bệnh cảnh chứ không phải thực thể khác"),
 ("I50.9", "suy tim sung huyết mạn"): (OT, "Thêm định tính mạn tính, vẫn cùng mã I50.9"),
 # M51.2
 ("M51.2", "thoát vị đĩa đệm"): (CN, "Thoát vị đĩa đệm có thể ở cổ (M50.2) hay ngực; ép về thắt lưng là thu hẹp nhóm về một vị trí"),
 ("M51.2", "thoát vị đĩa đệm cột sống thắt lưng"): (OT, "Trùng lặp y hệt name_vi; entry thừa (rule 4)"),
 # M54.3
 ("M54.3", "đau thần kinh tọa"): (OT, "Trùng lặp y hệt name_vi; entry thừa (rule 4)"),
 ("M54.3", "đau dây thần kinh tọa"): (OT, "Biến thể từ ngữ (thêm 'dây') của cùng một thuật ngữ"),
 # E78.5
 ("E78.5", "mỡ máu cao"): (TS, "Tên dân gian của rối loạn lipid máu; đã được phê duyệt trong canonical map"),
 ("E78.5", "tăng lipid máu"): (TS, "E78.5 chính là hyperlipidaemia không đặc hiệu; cùng khái niệm"),
 ("E78.5", "rối loạn chuyển hóa lipid"): (TS, "Cùng khái niệm rối loạn chuyển hóa lipid máu; E78.5 là mã catch-all của khối E78"),
 ("E78.5", "tăng cholesterol máu"): (CN, "Tăng cholesterol đơn thuần là E78.0, một thành viên; rối loạn lipid máu còn gồm tăng triglyceride, giảm HDL, thể hỗn hợp"),
 ("E78.5", "rối loạn lipid máu"): (OT, "Trùng lặp y hệt name_vi; entry thừa (rule 4)"),
 # H36.0
 ("H36.0", "bệnh võng mạc đái tháo đường"): (CN, "H36.0 đúng ra chính là bệnh võng mạc ĐTĐ, còn name_vi 'biến chứng võng mạc' là nhóm rộng (còn gồm võng mạc do THA, bong võng mạc); hai vế lệch mức đặc hiệu"),
 ("H36.0", "biến chứng võng mạc"): (OT, "Trùng lặp y hệt name_vi; entry thừa (rule 4)"),
 # J45
 ("J45", "bệnh hen"): (TS, "Cùng khái niệm hen phế quản"),
 ("J45", "hen suyễn"): (TS, "Tên thông dụng của hen phế quản; cùng khái niệm"),
 ("J45", "hen phế quản mạn"): (OT, "Hen vốn là bệnh mạn tính; 'mạn' là định tính thừa, vẫn cùng mã J45"),
 # J44
 ("J44", "COPD"): (OT, "Viết tắt tiếng Anh của chính name_vi"),
 ("J44", "tắc nghẽn phổi mạn tính"): (OT, "Biến thể trật tự từ của tên chính thức COPD"),
 # K29.7 Viêm dạ dày
 ("K29.7", "viêm dạ dày cấp"): (OT, "Định tính cấp tính của cùng một bệnh; hướng đi từ hẹp về rộng nên không gán chẩn đoán mới"),
 ("K29.7", "đau dạ dày"): (SD, "Đau thượng vị là TRIỆU CHỨNG, không phải chẩn đoán: có thể do viêm dạ dày, GERD, sỏi mật, tụy, thậm chí NMCT thành dưới"),
 ("K29.7", "viêm loét dạ dày"): (CN, "Loét là tổn thương mất niêm mạc, thực thể riêng (K25 cũng có trong chính từ điển này) với nguy cơ chảy máu/thủng và phác đồ khác viêm dạ dày đơn thuần"),
 ("K29.7", "viêm hang vị dạ dày"): (OT, "Biến thể đặc hiệu theo vị trí giải phẫu của cùng bệnh viêm dạ dày"),
 # K25 Loét dạ dày
 ("K25", "loét dạ dày tá tràng"): (CN, "Loét dạ dày-tá tràng là nhóm gồm loét tá tràng (K26, thực tế còn hay gặp hơn); ép về K25 bỏ mất vị trí tá tràng"),
 ("K25", "loét hang vị dạ dày"): (OT, "Loét hang vị là loét dạ dày theo vị trí, vẫn thuộc K25"),
 # K21.9
 ("K21.9", "GERD"): (OT, "Viết tắt tiếng Anh của trào ngược dạ dày thực quản"),
 ("K21.9", "trào ngược dạ dày"): (TS, "Dạng nói rút gọn thông dụng của cùng khái niệm"),
 ("K21.9", "trào ngược thực quản"): (TS, "Dạng nói rút gọn thông dụng của cùng khái niệm"),
 # N39.0
 ("N39.0", "nhiễm trùng tiểu"): (TS, "Cách nói thông dụng của nhiễm trùng đường tiết niệu"),
 ("N39.0", "nhiễm khuẩn tiết niệu"): (TS, "'nhiễm khuẩn' = 'nhiễm trùng'; cùng khái niệm"),
 ("N39.0", "nhiễm khuẩn đường tiết niệu"): (TS, "Biến thể từ vựng nhiễm trùng/nhiễm khuẩn của chính name_vi"),
 ("N39.0", "viêm đường tiết niệu"): (TS, "Trong thực hành tiếng Việt dùng thay thế được cho nhiễm trùng tiết niệu; cùng mức cam kết"),
 # I20
 ("I20", "đau thắt ngực"): (TS, "'Đau thắt ngực' là thuật ngữ chuẩn cho angina (khác 'đau ngực' chung chung); cùng khái niệm"),
 ("I20", "đau ngực do thiếu máu cục bộ"): (TS, "Định nghĩa mô tả của cơn đau thắt ngực; cùng khái niệm"),
 ("I20", "cơn đau thắt ngực cấp tính"): (OT, "Định tính về tính cấp; đau thắt ngực không ổn định vẫn nằm trong khối I20"),
 # I21
 ("I21", "nhồi máu cơ tim"): (TS, "NMCT không định tính trên lâm sàng là NMCT cấp; cùng khái niệm"),
 ("I21", "đột quỵ tim"): (CN, "Từ báo chí mơ hồ, được dùng cho cả ngừng tim đột ngột/đột tử tim lẫn NMCT; ép về I21 là cam kết quá mức vào một chẩn đoán cấp cứu (rule 3)"),
 # I63
 ("I63", "đột quỵ não"): (CN, "Đột quỵ là nhóm gồm cả xuất huyết não (I61) ~15-20% ca, xử trí ngược nhau (tiêu sợi huyết vs đảo đông); thu hẹp về nhồi máu là nguy hiểm"),
 ("I63", "tai biến mạch máu não"): (CN, "TBMMN bao gồm cả thể xuất huyết (I60/I61); không đồng nhất với nhồi máu não"),
 ("I63", "thiếu máu não cục bộ"): (CN, "Bao gồm cả cơn thiếu máu não thoáng qua (G45) vốn không có nhồi máu; ép về I63 là cam kết quá mức"),
 # J00
 ("J00", "cảm lạnh"): (TS, "J00 viêm mũi họng cấp chính là cảm lạnh thông thường; cùng khái niệm"),
 ("J00", "viêm họng cấp"): (CN, "Viêm họng cấp là J02 - thực thể riêng, có thể do liên cầu cần kháng sinh; đồng nhất với viêm mũi họng do virus gây xung đột với chính entry J02.9 trong từ điển"),
 ("J00", "nhiễm siêu vi hô hấp"): (CN, "Nhóm rất rộng (cúm, COVID, RSV, viêm tiểu phế quản, viêm phổi virus); thu hẹp về cảm lạnh thông thường là gán chẩn đoán"),
 # J02.9
 ("J02.9", "đau họng"): (SD, "Đau họng là TRIỆU CHỨNG: có thể do viêm họng, viêm amidan, trào ngược, viêm nắp thanh môn, áp xe thành sau họng, viêm giáp"),
 ("J02.9", "viêm họng hạt"): (CN, "Viêm họng hạt là viêm họng MẠN thể hạt (J31.2), không dùng kháng sinh; khác thực thể cấp J02.9"),
 # J03.9
 ("J03.9", "viêm amidan"): (OT, "Biến thể chính tả amiđan/amidan"),
 ("J03.9", "viêm amidan cấp"): (TS, "J03.9 chính là viêm amidan cấp không đặc hiệu; cùng khái niệm"),
 # J30.4
 ("J30.4", "dị ứng thời tiết"): (CN, "Cụm từ dân gian bao cả biểu hiện da (mề đay L50, chàm) lẫn hô hấp; ép riêng về viêm mũi dị ứng là thu hẹp"),
 ("J30.4", "viêm mũi dị ứng mạn"): (OT, "Định tính mạn tính, vẫn cùng mã J30.4"),
 # A09
 ("A09", "tiêu chảy cấp"): (SD, "Tiêu chảy cấp là TRIỆU CHỨNG: còn do virus, thẩm thấu, thuốc, kháng sinh/C.difficile, cường giáp, IBS; name_vi cam kết nguyên nhân nhiễm khuẩn"),
 ("A09", "nhiễm trùng tiêu hóa"): (TS, "Đồng nghĩa thực hành với viêm dạ dày ruột nhiễm khuẩn; cùng mức cam kết"),
 ("A09", "rối loạn tiêu hóa"): (CN, "Cụm từ ô rất rộng trong tiếng Việt (đầy bụng, khó tiêu, IBS, táo bón); quy về viêm dạ dày ruột nhiễm khuẩn là gán nguyên nhân"),
 # B18.2
 ("B18.2", "viêm gan C"): (OT, "Bỏ định tính 'mạn'; trên thực tế gần như toàn bộ ca HCV được chẩn đoán là thể mạn, viêm gan C cấp (B17.1) hiếm khi được phát hiện"),
 ("B18.2", "viêm gan vi rút C"): (OT, "Biến thể chính tả vi-rút/vi rút"),
 # B18.1
 ("B18.1", "viêm gan B"): (OT, "Bỏ định tính 'mạn'; ở vùng dịch tễ Việt Nam 'viêm gan B' trên thực hành là nhiễm HBV mạn"),
 ("B18.1", "viêm gan B mãn tính"): (TS, "'mãn tính' = 'mạn'; cùng khái niệm viêm gan B mạn"),
 ("B18.1", "viêm gan siêu vi B"): (TS, "'siêu vi' = 'vi-rút' (cách dùng miền Nam); cùng khái niệm"),
 # K76.0
 ("K76.0", "thoái hóa mỡ ở gan"): (TS, "Thuật ngữ giải phẫu bệnh của gan nhiễm mỡ; cùng khái niệm"),
 ("K76.0", "gan nhiễm mỡ không do rượu"): (OT, "Biến thể đặc hiệu theo nguyên nhân; K76.0 vốn đã loại trừ gan nhiễm mỡ do rượu (K70.0) nên vẫn đúng mã"),
 # M10.9
 ("M10.9", "gút"): (OT, "Biến thể viết hoa/thường của chính name_vi"),
 ("M10.9", "gout"): (OT, "Tên tiếng Anh của bệnh gút"),
 ("M10.9", "bệnh gút cấp"): (OT, "Đợt cấp của cùng một bệnh; M10.9 gút không đặc hiệu bao gồm cơn cấp"),
 ("M10.9", "viêm khớp gút"): (TS, "Biểu hiện khớp của bệnh gút, cùng mã M10.9; cùng khái niệm"),
 # M19.9
 ("M19.9", "thoái hóa khớp gối"): (CN, "Thoái hóa khớp gối có mã riêng M17 và là MỘT vị trí khớp; name_vi là thoái hóa khớp không đặc hiệu vị trí"),
 ("M19.9", "thoái hóa cột sống"): (CN, "Thoái hóa cột sống là spondylosis M47 - thực thể riêng ở cột sống, không phải thoái hóa khớp ngoại vi"),
 ("M19.9", "đau khớp mạn tính"): (SD, "Đau khớp mạn là TRIỆU CHỨNG: còn do viêm khớp dạng thấp, gút, lupus, viêm khớp vảy nến, đau xơ cơ"),
 # M06.9
 ("M06.9", "viêm đa khớp dạng thấp"): (TS, "Tên gọi cũ/đầy đủ của cùng bệnh viêm khớp dạng thấp"),
 # M54.5
 ("M54.5", "đau thắt lưng"): (TS, "Cùng khái niệm đau vùng thắt lưng; M54.5 vốn là mã triệu chứng"),
 ("M54.5", "đau cột sống thắt lưng"): (TS, "Biến thể từ ngữ của cùng khái niệm đau lưng dưới"),
 # G43.9
 ("G43.9", "đau đầu migraine"): (TS, "Cùng khái niệm migraine"),
 ("G43.9", "đau nửa đầu"): (TS, "Tên tiếng Việt quy ước của migraine; còn dư lượng mơ hồ với đau đầu cụm (G44.0) nhưng là chuẩn dùng"),
 # G40.9
 ("G40.9", "bệnh động kinh"): (TS, "Chỉ thêm tiền tố 'bệnh'; cùng khái niệm"),
 ("G40.9", "cơn co giật"): (SD, "Co giật là TRIỆU CHỨNG/biến cố (R56): động kinh đòi hỏi co giật tái diễn không do kích gợi; co giật còn do sốt cao, hạ đường huyết, sản giật, ngất, cai rượu, co giật tâm lý"),
 # F32.9
 ("F32.9", "trầm cảm"): (TS, "Cùng khái niệm rối loạn trầm cảm"),
 ("F32.9", "bệnh trầm cảm"): (TS, "Chỉ thêm tiền tố 'bệnh'; cùng khái niệm"),
 # F41.1
 ("F41.1", "rối loạn lo âu"): (CN, "Rối loạn lo âu là NHÓM (hoảng sợ F41.0, ám ảnh sợ F40, hỗn hợp lo âu-trầm cảm F41.2); lo âu lan tỏa chỉ là một thành viên"),
 ("F41.1", "lo âu mạn tính"): (SD, "Lo âu là TRIỆU CHỨNG cảm xúc; lo âu kéo dài đơn thuần chưa đủ tiêu chuẩn GAD và còn gặp trong trầm cảm, PTSD, lạm dụng chất"),
 # E03.9
 ("E03.9", "suy tuyến giáp"): (TS, "Cùng khái niệm suy giáp"),
 ("E03.9", "bệnh suy giáp"): (TS, "Chỉ thêm tiền tố 'bệnh'; cùng khái niệm"),
 # E05.9
 ("E05.9", "cường tuyến giáp"): (TS, "Cùng khái niệm cường giáp"),
 ("E05.9", "bệnh cường giáp"): (TS, "Chỉ thêm tiền tố 'bệnh'; cùng khái niệm"),
 ("E05.9", "Basedow"): (CN, "Basedow/Graves là MỘT nguyên nhân tự miễn của cường giáp, có mã riêng E05.0; cường giáp còn do bướu nhân độc, viêm giáp, amiodarone"),
 # N20.0
 ("N20.0", "sỏi đường tiết niệu"): (CN, "Sỏi tiết niệu là nhóm gồm sỏi niệu quản (N20.1) và sỏi bàng quang (N21.0); thu hẹp về sỏi thận bỏ sót thể tắc nghẽn cấp"),
 ("N20.0", "sỏi niệu quản"): (CN, "Sỏi niệu quản là N20.1 - thực thể riêng gây cơn đau quặn thận và tắc nghẽn, có thể cần can thiệp cấp"),
 # K80.2
 ("K80.2", "sỏi mật"): (CN, "'Sỏi mật' bao cả sỏi ống mật chủ (K80.5) gây vàng da, nhiễm trùng đường mật, viêm tụy; thu hẹp về sỏi túi mật bỏ sót thể nguy hiểm"),
 # A15.0
 ("A15.0", "bệnh lao"): (CN, "Lao là nhóm bệnh gồm lao ngoài phổi: lao màng não (A17), lao cột sống (A18.0), lao hạch (A18.2), lao kê (A19); thu hẹp về lao phổi rất nguy hiểm"),
 ("A15.0", "lao phế quản"): (CN, "Lao nội phế quản là A15.5 - thể riêng của lao đường hô hấp, không đồng nhất với lao nhu mô phổi A15.0"),
 # L20.9
 ("L20.9", "chàm cơ địa"): (TS, "'Chàm cơ địa' = 'viêm da cơ địa'; cùng khái niệm"),
 ("L20.9", "eczema"): (CN, "Eczema là thuật ngữ ô của cả khối L20-L30 gồm viêm da tiếp xúc (L23/L24), chàm đồng tiền, tổ đỉa - xử trí khác (tránh dị nguyên)"),
 # L70.0
 ("L70.0", "mụn trứng cá thông thường"): (TS, "L70.0 chính là acne vulgaris - mụn trứng cá thông thường; cùng khái niệm"),
 ("L70.0", "mụn trứng cá mức độ trung bình"): (CN, "Đây là MỘT bậc mức độ nặng, không phải từ đồng nghĩa; gán nó bằng 'mụn trứng cá' nói chung là cam kết mức độ không có căn cứ"),
 # N76.0
 ("N76.0", "viêm âm đạo do nấm"): (CN, "Viêm âm đạo do nấm Candida là B37.3 - MỘT nguyên nhân; viêm âm đạo còn do vi khuẩn (BV), Trichomonas, teo niêm mạc, điều trị khác hẳn"),
 ("N76.0", "nhiễm nấm âm đạo"): (CN, "Cùng vấn đề: nhiễm nấm âm đạo (B37.3) chỉ là một căn nguyên của viêm âm đạo"),
 # B35.9
 ("B35.9", "nhiễm nấm da"): (TS, "Cùng khái niệm nhiễm nấm da (dermatophytosis)"),
 ("B35.9", "nấm bẹn"): (CN, "Nấm bẹn (tinea cruris) là B35.6 - MỘT vị trí; nấm da còn có nấm chân B35.3, nấm da đầu B35.0"),
 # D69.3
 ("D69.3", "xuất huyết giảm tiểu cầu"): (OT, "Bỏ định tính 'vô căn'; vẫn là hội chứng xuất huyết do giảm tiểu cầu, D69.3 là quy chiếu mặc định (còn dư lượng mơ hồ với thể thứ phát/TTP)"),
 ("D69.3", "giảm tiểu cầu"): (SD, "Giảm tiểu cầu là KẾT QUẢ XÉT NGHIỆM: ở Việt Nam nguyên nhân hàng đầu là sốt xuất huyết Dengue, ngoài ra nhiễm khuẩn huyết, thuốc, xơ gan, lơ xê mi, TTP"),
 # D56.9
 ("D56.9", "tan máu bẩm sinh"): (TS, "Tên tiếng Việt chính thức của thalassemia trong truyền thông y tế; đã được phê duyệt trong canonical map"),
 ("D56.9", "bệnh thalassmia"): (OT, "Lỗi chính tả của 'thalassemia'"),
 # I48.9
 ("I48.9", "bệnh rung nhĩ"): (TS, "Chỉ thêm tiền tố 'bệnh'; cùng khái niệm"),
 ("I48.9", "loạn nhịp tim"): (CN, "Loạn nhịp tim là NHÓM (nhịp nhanh thất, block, nhịp nhanh trên thất, ngoại tâm thu); rung nhĩ chỉ là một thành viên - đúng ví dụ rule 1 đã bị bác"),
 # M75.2
 ("M75.2", "viêm quanh khớp vai"): (CN, "Viêm quanh khớp vai là cụm hội chứng rộng gồm đông cứng khớp vai (M75.0), rách chóp xoay (M75.1); viêm gân nhị đầu M75.2 chỉ là một thể"),
 ("M75.2", "đau vai"): (SD, "Đau vai là TRIỆU CHỨNG: còn do bệnh lý rễ cổ, chóp xoay, và đau lan từ cơ hoành/túi mật/NMCT"),
 # E27.4
 ("E27.4", "suy thượng thận"): (TS, "Dạng rút gọn của suy tuyến thượng thận; cùng khái niệm"),
 # E28.2
 ("E28.2", "hội chứng đa nang buồng trứng"): (TS, "Tên đầy đủ của cùng khái niệm PCOS"),
 ("E28.2", "PCOS"): (OT, "Viết tắt tiếng Anh của hội chứng buồng trứng đa nang"),
 # N40
 ("N40", "phì đại tuyến tiền liệt"): (TS, "Dạng rút gọn quy ước của phì đại lành tính TTL; cùng khái niệm"),
 ("N40", "u xơ tuyến tiền liệt"): (TS, "Tên tiếng Việt truyền thống của BPH; cùng khái niệm"),
 # D25.9
 ("D25.9", "bệnh u xơ tử cung"): (TS, "Chỉ thêm tiền tố 'bệnh'; cùng khái niệm"),
 # D50.9
 ("D50.9", "thiếu máu do thiếu sắt"): (TS, "Biến thể từ ngữ của chính name_vi; cùng khái niệm"),
 ("D50.9", "thiếu máu nặng"): (CN, "'Nặng' là MỨC ĐỘ chứ không phải căn nguyên; thiếu máu nặng còn do thalassemia (D56.9 trong chính từ điển này), thiếu B12/folate, tan máu, suy tủy, mất máu cấp, ác tính"),
}

with open(SRC, encoding="utf-8") as f:
    data = json.load(f)

rows = []
missing = []
for e in data:
    for s in e["synonyms"]:
        key = (e["code"], s)
        if key not in J:
            missing.append(key)
            continue
        cls, reason = J[key]
        rows.append({
            "icd_code": e["code"],
            "name_vi": e["name_vi"],
            "synonym": s,
            "classification": cls,
            "reason": reason,
            "violates_rule": "YES" if cls in (SD, CN) else "NO",
        })

if missing:
    print("!! UNJUDGED PAIRS:", missing)
    sys.exit(1)

extra = set(J) - {(e["code"], s) for e in data for s in e["synonyms"]}
if extra:
    print("!! JUDGEMENTS NOT IN SOURCE:", extra)
    sys.exit(1)

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["icd_code", "name_vi", "synonym", "classification", "reason", "violates_rule"])
    w.writeheader()
    w.writerows(rows)

print("rows written:", len(rows))
print(Counter(r["classification"] for r in rows))
print("violates YES:", sum(1 for r in rows if r["violates_rule"] == "YES"))
print("violates NO :", sum(1 for r in rows if r["violates_rule"] == "NO"))

print("\n--- REQUIRED 6 CHECKS ---")
req = [("K29.7", "đau dạ dày"), ("I48.9", "loạn nhịp tim"), ("J02.9", "đau họng"),
       ("J00", "viêm họng cấp"), ("A09", "tiêu chảy cấp"), ("D50.9", "thiếu máu nặng"),
       ("G40.9", "cơn co giật")]
for c, s in req:
    hit = [r for r in rows if r["icd_code"] == c and r["synonym"] == s]
    print(c, "|", s, "->", hit[0]["classification"], hit[0]["violates_rule"] if hit else "NOT FOUND")
