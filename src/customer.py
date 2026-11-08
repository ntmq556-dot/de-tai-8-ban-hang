import sqlite3
import re

class CustomerManager:
    def __init__(self, db_name="retail_shop.db"):
        self.db_name = db_name
        self.init_database()

    def init_database(self):
        """Khởi tạo bảng customers với điểm tích và hạng thành viên"""
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT UNIQUE NOT NULL,
                    email TEXT,
                    address TEXT,
                    points INTEGER DEFAULT 0,
                    member_level TEXT DEFAULT 'Bronze'
                )
            ''')

    def _is_valid_phone(self, phone):
        return bool(re.fullmatch(r"\d{9,11}", phone))

    def add_customer(self, customer_id, name, phone, email="", address=""):
        if not self._is_valid_phone(phone):
            return False, "Số điện thoại không hợp lệ (phải là 9-11 chữ số)."
        try:
            with sqlite3.connect(self.db_name) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO customers (id, name, phone, email, address)
                    VALUES (?, ?, ?, ?, ?)
                ''', (customer_id, name, phone, email, address))
            return True, f"Thêm khách hàng {name} ({customer_id}) thành công."
        except sqlite3.IntegrityError as e:
            if "UNIQUE constraint failed: customers.phone" in str(e):
                return False, f"Số điện thoại {phone} đã tồn tại trong hệ thống!"
            elif "UNIQUE constraint failed: customers.id" in str(e):
                return False, f"ID khách hàng {customer_id} đã tồn tại trong hệ thống!"
            else:
                return False, "Lỗi khi thêm khách hàng."

    def search_customer(self, phone):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers WHERE phone = ?', (phone,))
            row = cursor.fetchone()
        if row:
            return {
                "id": row[0], "name": row[1], "phone": row[2],
                "email": row[3], "address": row[4],
                "points": row[5], "member_level": row[6]
            }
        return None

    def update_customer(self, customer_id, name=None, phone=None, email=None, address=None):
        if phone is not None and not self._is_valid_phone(phone):
            return False, "Số điện thoại không hợp lệ (phải là 9-11 chữ số)."
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers WHERE id = ?', (customer_id,))
            if not cursor.fetchone():
                return False, f"Khách hàng với ID {customer_id} không tồn tại."
            fields = []
            values = []
            if name is not None:
                fields.append("name = ?")
                values.append(name)
            if phone is not None:
                fields.append("phone = ?")
                values.append(phone)
            if email is not None:
                fields.append("email = ?")
                values.append(email)
            if address is not None:
                fields.append("address = ?")
                values.append(address)
            values.append(customer_id)
            try:
                cursor.execute(f'''
                    UPDATE customers SET {", ".join(fields)} WHERE id = ?
                ''', values)
                if cursor.rowcount == 0:
                    return False, "Không cập nhật được thông tin."
                return True, "Cập nhật thông tin khách hàng thành công."
            except sqlite3.IntegrityError as e:
                if "UNIQUE constraint failed: customers.phone" in str(e):
                    return False, f"Số điện thoại {phone} đã tồn tại trong hệ thống!"
                else:
                    return False, "Lỗi khi cập nhật khách hàng."

    def delete_customer(self, identifier, by_id=True):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            if by_id:
                cursor.execute('DELETE FROM customers WHERE id = ?', (identifier,))
            else:
                cursor.execute('DELETE FROM customers WHERE phone = ?', (identifier,))
            if cursor.rowcount == 0:
                return False, "Không tìm thấy khách hàng để xóa."
            return True, "Xóa khách hàng thành công."

    # Loyalty program

    def add_points(self, customer_id, points_to_add):
        if points_to_add < 0:
            return False, "Số điểm cộng thêm phải là số dương."
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT points FROM customers WHERE id = ?', (customer_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Không tìm thấy khách hàng để cộng điểm."
            current_points = result[0] or 0
            new_points = current_points + points_to_add
            cursor.execute('UPDATE customers SET points = ? WHERE id = ?', (new_points, customer_id))
            new_level = self.get_member_level(new_points)
            cursor.execute('UPDATE customers SET member_level = ? WHERE id = ?', (new_level, customer_id))
            return True, f"Cộng {points_to_add} điểm thành công. Hạng thành viên hiện tại: {new_level}"

    def get_member_level(self, points):
        if points >= 10000:
            return "Platinum"
        elif points >= 5000:
            return "Gold"
        elif points >= 1000:
            return "Silver"
        else:
            return "Bronze"

    def redeem_points(self, customer_id, points_to_use):
        if points_to_use <= 0:
            return False, "Số điểm sử dụng phải lớn hơn 0."
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT points FROM customers WHERE id = ?', (customer_id,))
            result = cursor.fetchone()
            if not result:
                return False, "Không tìm thấy khách hàng để trừ điểm."
            current_points = result[0] or 0
            if current_points < points_to_use:
                return False, "Điểm tích lũy không đủ để sử dụng."
            new_points = current_points - points_to_use
            cursor.execute('UPDATE customers SET points = ? WHERE id = ?', (new_points, customer_id))
            new_level = self.get_member_level(new_points)
            cursor.execute('UPDATE customers SET member_level = ? WHERE id = ?', (new_level, customer_id))
            return True, f"Trừ {points_to_use} điểm thành công. Hạng thành viên hiện tại: {new_level}"

    def get_all_customers(self):
        with sqlite3.connect(self.db_name) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM customers ORDER BY id')
            rows = cursor.fetchall()
            customers = []
            for row in rows:
                customers.append({
                    "id": row[0],
                    "name": row[1],
                    "phone": row[2],
                    "email": row[3],
                    "address": row[4],
                    "points": row[5],
                    "member_level": row[6],
                })
            return customers
