import sqlite3
import os
from datetime import datetime
from customer import CustomerManager

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "retail_shop.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_checkout_tables():
    """Khởi tạo bảng hóa đơn (orders) và chi tiết hóa đơn (order_details) đồng bộ với hệ thống."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id TEXT PRIMARY KEY,
                customer_id TEXT,
                subtotal REAL NOT NULL DEFAULT 0,
                discount_amount REAL NOT NULL DEFAULT 0,
                points_used INTEGER NOT NULL DEFAULT 0,
                points_earned INTEGER NOT NULL DEFAULT 0,
                total_amount REAL NOT NULL,
                amount_paid REAL NOT NULL,
                change_amount REAL NOT NULL DEFAULT 0,
                payment_method TEXT NOT NULL DEFAULT 'CASH',
                created_at TEXT NOT NULL,
                FOREIGN KEY (customer_id) REFERENCES customers(id) ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_details (
                detail_id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id TEXT NOT NULL,
                product_id INTEGER NOT NULL,
                product_name TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                subtotal REAL NOT NULL,
                FOREIGN KEY (order_id) REFERENCES orders(order_id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE RESTRICT
            )
        """)
        conn.commit()


def process_checkout(data):
    """
    Xử lý thanh toán trọn gói:
    1. Chuẩn hóa dữ liệu đầu vào (hỗ trợ cả 'id' và 'product_id').
    2. Kiểm tra tồn kho thực tế.
    3. Xử lý trừ điểm đổi quà & cộng điểm tích lũy (nếu có khách hàng).
    4. Lưu hóa đơn, chi tiết hóa đơn và trừ tồn kho trong 1 transaction an toàn.
    """
    init_checkout_tables()
    items = data.get("items", [])
    if not items:
        return False, "Giỏ hàng đang trống, không thể thanh toán.", None

    customer_id = (data.get("customer_id") or "").strip().upper() or None
    payment_method = (data.get("payment_method") or "CASH").strip().upper()
    points_to_use = max(0, int(data.get("points_used") or 0))
    amount_paid = float(data.get("amount_paid") or 0)

    cm = CustomerManager(db_name=DB_PATH)
    customer = None
    if customer_id:
        customer = cm.get_customer_by_id(customer_id)
        if not customer:
            return False, f"Không tìm thấy khách hàng mã {customer_id}.", None
        if points_to_use > customer["points"]:
            return False, f"Khách chỉ có {customer['points']} điểm, không đủ {points_to_use} điểm để đổi.", None

    # Quy đổi: 1 điểm = 1.000đ giảm giá
    discount_amount = points_to_use * 1000

    with get_connection() as conn:
        cursor = conn.cursor()
        validated_items = []
        subtotal = 0.0

        # Kiểm tra từng sản phẩm (đồng bộ cả product_id và id)
        for raw_item in items:
            pid = raw_item.get("product_id") or raw_item.get("id")
            qty = int(raw_item.get("quantity") or raw_item.get("qty") or 0)
            if not pid or qty <= 0:
                return False, "Dữ liệu sản phẩm trong giỏ hàng không hợp lệ.", None

            prod = cursor.execute(
                "SELECT id, sku, name, price, stock FROM products WHERE id = ? AND is_active = 1",
                (pid,),
            ).fetchone()

            if not prod:
                return False, f"Sản phẩm ID {pid} không tồn tại hoặc đã ngừng bán.", None
            if prod["stock"] < qty:
                return False, f"Sản phẩm '{prod['name']}' chỉ còn {prod['stock']} trong kho.", None

            item_sub = float(prod["price"]) * qty
            subtotal += item_sub
            validated_items.append({
                "product_id": prod["id"],
                "id": prod["id"],  # Trả về cả 2 key để tương thích mọi module
                "sku": prod["sku"],
                "product_name": prod["name"],
                "name": prod["name"],
                "unit_price": float(prod["price"]),
                "quantity": qty,
                "subtotal": item_sub,
                "new_stock": prod["stock"] - qty,
            })

        total_amount = max(0.0, subtotal - discount_amount)

        if payment_method == "CASH":
            if amount_paid < total_amount:
                return False, "Số tiền khách đưa chưa đủ để thanh toán.", None
            change_amount = amount_paid - total_amount
        else:
            amount_paid = total_amount
            change_amount = 0.0

        # Tích điểm: mỗi 10.000đ thanh toán thực tế được 1 điểm
        points_earned = int(total_amount // 10000) if customer else 0

        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        order_id = "HD" + datetime.now().strftime("%Y%m%d%H%M%S")

        # Lưu hóa đơn
        cursor.execute("""
            INSERT INTO orders (
                order_id, customer_id, subtotal, discount_amount,
                points_used, points_earned, total_amount, amount_paid,
                change_amount, payment_method, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            order_id, customer_id, subtotal, discount_amount,
            points_to_use, points_earned, total_amount, amount_paid,
            change_amount, payment_method, now_str
        ))

        # Lưu chi tiết & trừ tồn kho
        for v in validated_items:
            cursor.execute("""
                INSERT INTO order_details (order_id, product_id, product_name, quantity, unit_price, subtotal)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (order_id, v["product_id"], v["product_name"], v["quantity"], v["unit_price"], v["subtotal"]))

            cursor.execute(
                "UPDATE products SET stock = ?, updated_at = ? WHERE id = ?",
                (v["new_stock"], now_str, v["product_id"])
            )

        conn.commit()

    # Cập nhật điểm thành viên sau khi commit hóa đơn
    updated_customer = None
    if customer:
        if points_to_use > 0:
            cm.redeem_points(customer_id, points_to_use)
        if points_earned > 0:
            cm.add_points(customer_id, points_earned)
        updated_customer = cm.get_customer_by_id(customer_id)

    receipt_data = {
        "order_id": order_id,
        "created_at": now_str,
        "customer": updated_customer,
        "items": validated_items,
        "subtotal": subtotal,
        "discount_amount": discount_amount,
        "points_used": points_to_use,
        "points_earned": points_earned,
        "total_amount": total_amount,
        "amount_paid": amount_paid,
        "change_amount": change_amount,
        "payment_method": payment_method,
    }
    return True, "Thanh toán và xuất hóa đơn thành công!", receipt_data


def get_order_history(limit=20):
    init_checkout_tables()
    with get_connection() as conn:
        rows = conn.execute("""
            SELECT o.*, c.name AS customer_name, c.phone AS customer_phone
            FROM orders o
            LEFT JOIN customers c ON o.customer_id = c.id
            ORDER BY o.created_at DESC
            LIMIT ?
        """, (limit,)).fetchall()
        return [dict(r) for r in rows]