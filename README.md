# Stock

ระบบตัวอย่างสำหรับจัดการสต๊อกสินค้าทดลอง โดยรองรับ:

- ตั้งค่าสินค้าเริ่มต้น 4 รายการ
- บันทึกรายชื่อผู้มีสิทธิ์เบิก (และเพิ่มได้ในอนาคต)
- การเบิกสินค้า: ระบุผู้เบิก, ลูกค้า/บริษัท, โครงการ/สถานที่, วัตถุประสงค์, วันที่เบิก, รายการสินค้า
- ตัดสต๊อกทันทีเมื่อเบิก
- การรับคืนสินค้า: ต้องระบุชื่อทีมงานผู้รับคืน

## API สำหรับ Vercel

โปรเจกต์นี้รองรับการ deploy แบบ HTTP API บน Vercel โดยใช้ไฟล์ `api/index.py` (Flask + business logic จาก `stock_system.py`)

- `GET /products` รายการสินค้า
- `POST /products` เพิ่มสินค้า
- `POST /borrowers` เพิ่มผู้มีสิทธิ์เบิก
- `POST /requisitions` เบิกสินค้า
- `POST /returns` คืนสินค้า
- `GET /requisitions` รายการใบเบิก

ตัวอย่าง payload:

```json
{
  "borrower": "Thisalinee Bunlert",
  "customer": "ABC Co., Ltd.",
  "project_or_location": "Sample Project",
  "purpose": "Demo",
  "requisition_date": "2026-06-06",
  "items": {
    "Sealant MS 541": 1
  }
}
```

## Deploy ไปยัง Vercel

1. Push โค้ดขึ้น GitHub repository
2. Import repository นี้ใน Vercel
3. Vercel จะอ่าน `vercel.json` และ deploy Python API จาก `api/index.py`
4. ทดสอบ endpoint หลัง deploy เช่น `GET /products`

รันเทสต์:

```bash
python -m unittest -v
```