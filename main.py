from flask import Flask, render_template, url_for, request, redirect, session, flash
from tinydb import TinyDB, Query
import re

app = Flask(__name__)
app.secret_key = 'your-secret-key'  # 🔐 ตั้งค่าสำหรับ session

db = TinyDB('db.json')
User = Query()

sub_member_db = TinyDB('sub_member.json')
sub_query = Query()

admin_db= TinyDB('admin.json')
admin_query = Query()


# หน้า login
from flask import session, redirect, url_for, request, render_template
from tinydb import TinyDB, Query

db = TinyDB('db.json')
User = Query()

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # ✅ ดึง user จาก TinyDB
        user = admin_db.search((User.username == username) & (User.password == password))

        if user:
            session['logged_in'] = True
            return redirect(url_for('select'))
        else:
            flash('ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง', 'danger')

    return render_template('login.html')

@app.route('/select', methods=['GET'])
def select():
    if request.method == 'GET':
        if not session.get('logged_in'):
            return redirect(url_for('login'))

    return render_template('select_mode.html')

# ออกจากระบบ
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('ออกจากระบบแล้ว', 'info')
    return redirect(url_for('login'))

@app.route('/')
def landing():
    return render_template("landing.html")

def clean_name(name):
    # ตัดช่องว่าง และอักขระพิเศษด้านหน้า
    cleaned = name.strip()  # ลบช่องว่างหน้า-หลัง
    cleaned = re.sub(r'^[^a-zA-Zก-๙]+', '', cleaned)  # ตัดอักขระนำหน้า
    return cleaned.lower()

@app.route('/member')
def member():
    members = db.all()

    leaders = [m for m in members if '[ Leader ]' in m['name']]
    others = [m for m in members if '[ Leader ]' not in m['name']]

    leaders_sorted = sorted(leaders, key=lambda x: clean_name(x['name']))
    others_sorted = sorted(others, key=lambda x: clean_name(x['name']))

    sorted_members = leaders_sorted + others_sorted

    return render_template("index.html", members=sorted_members)



@app.route('/sub-member')
def sub_member():
    members = sub_member_db.all()

    # แยกตามกลุ่ม
    leaders = [m for m in members if '[ Leader ]' in m['name']]
    staffs = [m for m in members if '[ STAFF ]' in m['name'] and '[ Leader ]' not in m['name']]
    others = [m for m in members if '[ Leader ]' not in m['name'] and '[ STAFF ]' not in m['name']]

    # เรียงชื่อแต่ละกลุ่ม
    leaders_sorted = sorted(leaders, key=lambda x: clean_name(x['name']))
    staffs_sorted = sorted(staffs, key=lambda x: clean_name(x['name']))
    others_sorted = sorted(others, key=lambda x: clean_name(x['name']))

    # รวมลำดับ: Leader > Staff > อื่นๆ
    sorted_members = leaders_sorted + staffs_sorted + others_sorted

    return render_template("sub_member.html", members=sorted_members)

# 🔐 หน้าผู้ดูแลระบบ
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        link = request.form['link']
        db.insert({
            'name': name,
            'link': link,
        })
        return redirect(url_for('admin'))

    members = db.all()
    return render_template('admin.html', members=members)

@app.route('/delete/<int:item_id>')
def delete(item_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    db.remove(doc_ids=[item_id])
    return redirect(url_for('admin'))

#---------------------------------------------------------------------------------------------------------
# 🔐 หน้าผู้ดูแลระบบ
@app.route('/admin_submember', methods=['GET', 'POST'])
def admin_submember():
    if not session.get('logged_in'):
        return redirect(url_for('login'))

    if request.method == 'POST':
        name = request.form['name']
        link = request.form['link']
        sub_member_db.insert({
            'name': name,
            'link': link,
        })
        return redirect(url_for('admin_submember'))

    members = sub_member_db.all()
    return render_template('admin_submember.html', members=members)

@app.route('/delete_submember/<int:item_id>')
def delete_submember(item_id):
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    sub_member_db.remove(doc_ids=[item_id])
    return redirect(url_for('admin_submember'))
#---------------------------------------------------------------------------------------------------------

@app.route('/search', methods=['GET', 'POST'])
def search():
    results = []
    if request.method == 'POST':
        keyword = request.form['keyword'].lower()

        # ค้นหาใน db1
        results_db1 = [
            item for item in db.all()
            if keyword in item.get('name', '').lower() or keyword in item.get('link', '').lower()
        ]

        # ค้นหาใน db2
        results_db2 = [
            item for item in sub_member_db.all()
            if keyword in item.get('name', '').lower() or keyword in item.get('link', '').lower()
        ]

        # รวมผลลัพธ์จากทั้งสองฐานข้อมูล
        results = results_db1 + results_db2

    return render_template("search.html", results=results)
if __name__ == '__main__':
    app.run(host='0.0.0.0')
