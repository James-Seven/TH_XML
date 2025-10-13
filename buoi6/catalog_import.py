# pip install lxml mysql-connector-python
import sys
import mysql.connector
from lxml import etree

# ---- Cấu hình ----
xml_file = "catalog.xml"
xsd_file = "catalog.xsd"

# ---- Bước 1: Parse XML và XSD ----
xml_doc = etree.parse(xml_file)
xsd_doc = etree.parse(xsd_file)
schema = etree.XMLSchema(xsd_doc)

# ---- Bước 2: Validate ----
if not schema.validate(xml_doc):
    print("XML không hợp lệ:")
    for error in schema.error_log:
        print(" -", error.message)
    sys.exit(1)
print("XML hợp lệ với XSD")

# ---- Bước 3: Kết nối MySQL ----
conn = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="",
    database="ecommerce"
)
cur = conn.cursor()

# ---- Bước 4: Tạo bảng nếu chưa có ----
cur.execute("""
CREATE TABLE IF NOT EXISTS Categories (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL
) ENGINE=InnoDB CHARSET=utf8mb4
""")
cur.execute("""
CREATE TABLE IF NOT EXISTS Products (
    id VARCHAR(64) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    price DECIMAL(12,2) NOT NULL,
    currency VARCHAR(16) NOT NULL,
    stock INT NOT NULL,
    categoryRef VARCHAR(64) NOT NULL,
    FOREIGN KEY (categoryRef) REFERENCES Categories(id)
        ON UPDATE CASCADE
        ON DELETE RESTRICT
) ENGINE=InnoDB CHARSET=utf8mb4
""")


# ---- Bước 5: Upsert từ XML ----
for c in xml_doc.xpath("//catalog/categories/category"):
    cid = (c.get("id") or "").strip()
    cname = (c.text or "").strip()
    if not cid:
        continue
    cur.execute("""
        INSERT INTO Categories (id, name)
        VALUES (%s, %s)
        ON DUPLICATE KEY UPDATE name = VALUES(name)
    """, (cid, cname))

for p in xml_doc.xpath("//catalog/products/product"):
    pid = (p.get("id") or "").strip()
    categoryRef = (p.get("categoryRef") or "").strip()
    if not pid or not categoryRef:
        continue
    name = (p.findtext("name") or "").strip()
    price_el = p.find("price")
    stock_el = p.find("stock")
    price = float((price_el.text or "0").strip())
    currency = (price_el.get("currency") or "USD").strip()
    stock = int((stock_el.text or "0").strip())
    cur.execute("""
        INSERT INTO Products (id, name, price, currency, stock, categoryRef)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            name=VALUES(name), price=VALUES(price),
            currency=VALUES(currency), stock=VALUES(stock),
            categoryRef=VALUES(categoryRef)
    """, (pid, name, price, currency, stock, categoryRef))
conn.commit()
cur.close()
conn.close()
print("Đồng bộ dữ liệu vào MySQL thành công.")
