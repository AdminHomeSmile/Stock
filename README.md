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

## Web Interface

โปรเจกต์นี้มีหน้าเว็บสำหรับจัดการสต๊อกที่ `public/index.html` พร้อม Vercel Web Analytics สำหรับติดตามการใช้งาน

เมื่อ deploy บน Vercel:
- หน้าหลัก `/` จะแสดงเว็บอินเตอร์เฟซสำหรับจัดการสต๊อก
- API endpoints ยังคงใช้งานได้ตามปกติ
- Analytics จะติดตามการเข้าชมและการใช้งานอัตโนมัติ

## Vercel Web Analytics

โปรเจกต์นี้ติดตั้ง `@vercel/analytics` แล้ว:
- ติดตาม page views และ user interactions
- ไม่ต้องตั้งค่าเพิ่มเติม analytics จะทำงานอัตโนมัติเมื่อ deploy บน Vercel
- ดูข้อมูล analytics ได้ที่ Vercel Dashboard > Analytics

## Deploy ไปยัง Vercel

1. Push โค้ดขึ้น GitHub repository
2. Import repository นี้ใน Vercel
3. ไปที่ Vercel Dashboard > Analytics และกด "Enable" เพื่อเปิดใช้งาน analytics
4. Vercel จะอ่าน `vercel.json` และ deploy Python API จาก `api/index.py` พร้อมกับหน้าเว็บ
5. ทดสอบหน้าเว็บที่ `/` และ API endpoints เช่น `GET /products`

รันเทสต์:

```bash
python -m unittest -v
```