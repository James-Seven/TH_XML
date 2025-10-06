from lxml import etree
from pathlib import Path
import sys

# ==== CẤU HÌNH ĐƯỜNG DẪN ====
# Nếu sinhvien.xml nằm cùng thư mục file này, giữ nguyên dòng dưới:
xml_path = Path(__file__).resolve().parent / "sinhvien.xml"

# Nếu file ở nơi khác, sửa ví dụ:
# xml_path = Path(r"d:\XML_BTN\buoi5\sinhvien.xml")

print(f"Đang tìm file XML ở: {xml_path}")
if not xml_path.exists():
    sys.exit("❌ Không tìm thấy sinhvien.xml! Hãy đảm bảo file nằm cùng thư mục với script hoặc sửa lại đường dẫn trong code.")

# ==== ĐỌC FILE XML ====
doc = etree.parse(str(xml_path))
print("✅ Đọc file thành công!\n")

# ==== DANH SÁCH 19 CÂU XPATH ====
queries = {
    "1. Tất cả sinh viên": "//student",
    "2. Tên tất cả sinh viên": "//student/name/text()",
    "3. ID sinh viên": "//student/id/text()",
    "4. Ngày sinh SV01": "//student[id='SV01']/date/text()",
    "5. Tất cả khóa học": "//course",
    "6. Thông tin sinh viên đầu tiên": "(//student)[1]",

    # 7-9: sẽ rỗng nếu không có enrollment/course gắn với từng student
    "7. ID SV học Vatly203": "//student[id = //enrollment[course='Vatly203']/studentRef]/name/text()",
    "8. Tên SV học Toan101": "//student[id = //enrollment[course='Toan101']/studentRef]/name/text()",
    "9. Tên SV học Vatly203": "//student[id = //enrollment[course='Vatly203']/studentRef]/name/text()",

    "10. Ngày sinh SV01": "//student[id='SV01']/date/text()",

    # 11: dùng union trong XPath 1.0
    "11. SV sinh năm 1997 (tên & ngày)": "(//student[substring(date,1,4)='1997']/name/text() | //student[substring(date,1,4)='1997']/date/text())",

    "12. SV sinh trước 1998": "//student[substring(date,1,4)<'1998']/name/text()",
    "13. Tổng số sinh viên": "count(//student)",

    # 14: không có enrollment ⇒ tất cả SV đều “chưa đăng ký” (đúng như bạn thấy)
    "14. SV chưa đăng ký môn": "//student[not(id = //enrollment/studentRef)]",

    "15. <date> sau <name> của SV01": "//student[id='SV01']/name/following-sibling::date[1]",
    "16. <id> trước <name> của SV02": "//student[id='SV02']/name/preceding-sibling::id[1]",

    # 17: rỗng nếu không có enrollment[@studentRef]
    "17. course của enrollment studentRef='SV03'": "//enrollment[studentRef='SV03']/course/text()",

    # 18: tên họ “Tran/Trần” (XML của bạn là Nguyễn, Lê nên rỗng)
    "18. SV họ Tran": "//student[starts-with(normalize-space(name),'Tran') or starts-with(normalize-space(name),'Trần')]",

    "19. Năm sinh SV01": "substring(//student[id='SV01']/date,1,4)",
}


# ==== THỰC THI CÁC CÂU XPATH ====
for title, xp in queries.items():
    try:
        result = doc.xpath(xp)
        if isinstance(result, float):  # count()
            print(f"{title}: {int(result)}")
        elif isinstance(result, list):
            if all(isinstance(x, str) for x in result):
                print(f"{title}: {result}")
            else:
                # In ra node XML dạng string
                print(f"{title}:")
                for node in result:
                    print(etree.tostring(node, pretty_print=True, encoding='unicode'))
        else:
            print(f"{title}: {result}")
    except Exception as e:
        print(f"⚠️ Lỗi khi chạy {title}: {e}")

print("\n✅ Hoàn tất kiểm tra XPath.")
