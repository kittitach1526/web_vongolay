from tinydb import TinyDB, Query

# สร้างหรือเชื่อมต่อกับฐานข้อมูล
db = TinyDB('admin.json')



# สร้าง Query สำหรับการค้นหา
User = Query()

# ค้นหาข้อมูลที่ username เป็น 'admin'
result = db.search(User.username == 'admin')

# แสดงผลลัพธ์การค้นหา
print(result)