# Stock

ระบบตัวอย่างสำหรับจัดการสต๊อกสินค้าทดลอง โดยรองรับ:

- ตั้งค่าสินค้าเริ่มต้น 4 รายการ
- บันทึกรายชื่อผู้มีสิทธิ์เบิก (และเพิ่มได้ในอนาคต)
- การเบิกสินค้า: ระบุผู้เบิก, ลูกค้า/บริษัท, โครงการ/สถานที่, วัตถุประสงค์, วันที่เบิก, รายการสินค้า
- ตัดสต๊อกทันทีเมื่อเบิก
- การรับคืนสินค้า: ต้องระบุชื่อทีมงานผู้รับคืน

โปรเจกต์นี้รองรับการใช้งานผ่าน HTTP API สำหรับ deploy บน Vercel โดยใช้ `api/index.py` เป็น entrypoint
และยังคงใช้ `stock_system.py` เป็น business logic หลัก

## Run tests

```bash
python -m unittest -v
```

## Run API locally

1. ติดตั้ง dependency

```bash
pip install -r requirements.txt
```

2. รัน Flask app

```bash
flask --app api.index run
```

3. ทดสอบ endpoint ตัวอย่าง

```bash
curl http://127.0.0.1:5000/api/products
```

## API endpoints

- `GET /api/products` - แสดงรายการสินค้า
- `POST /api/products` - เพิ่มสินค้า
- `POST /api/borrowers` - เพิ่มผู้มีสิทธิ์เบิก
- `POST /api/requisitions` - สร้างใบเบิกสินค้า
- `POST /api/returns` - รับคืนสินค้า
- `GET /api/requisitions` - แสดงรายการใบเบิก

ตัวอย่าง `POST /api/requisitions`:

```json
{
  "borrower": "Thisalinee Bunlert",
  "customer": "ABC Co., Ltd.",
  "project_or_location": "Project A",
  "purpose": "Demo",
  "requisition_date": "2026-06-06",
  "items": {
    "Sealant MS 541": 2
  }
}
```

## Deploy on Vercel

1. Push โค้ดขึ้น GitHub repository
2. ไปที่ Vercel > Add New Project
3. เลือก repository `AdminHomeSmile/Stock`
4. Deploy ได้ทันที (โปรเจกต์มี `vercel.json` และ `api/index.py` พร้อมใช้งาน)

หมายเหตุ: ใน serverless environment state จะอยู่ในหน่วยความจำของ instance ชั่วคราว
หากมี cold start หรือ scale out ข้อมูลที่เพิ่มผ่าน API อาจไม่คงอยู่ถาวร
