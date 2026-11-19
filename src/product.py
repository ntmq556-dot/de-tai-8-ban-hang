import sqlite3
import os
from datetime import datetime

# Tìm đường dẫn tới file retail_shop.db ở thư mục gốc của dự án
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
DB_PATH = os.path.join(BASE_DIR, "retail_shop.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_catalog_tables():
    """Khởi tạo các bảng riêng cho Module Sản phẩm & Danh mục nếu chưa có."""
    with get_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                created_at TEXT NOT NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sku TEXT NOT NULL UNIQUE,
                name TEXT NOT NULL,
                category_id INTEGER,
                price REAL NOT NULL CHECK(price >= 0),
                stock INTEGER NOT NULL DEFAULT 0 CHECK(stock >= 0),
                description TEXT DEFAULT '',
                is_active INTEGER NOT NULL DEFAULT 1,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS price_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                old_price REAL NOT NULL,
                new_price REAL NOT NULL,
                changed_at TEXT NOT NULL,
                FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE CASCADE
            )
        """)

        # Thêm danh mục mẫu nếu bảng categories đang rỗng
        cursor.execute("SELECT COUNT(*) AS cnt FROM categories")
        if cursor.fetchone()["cnt"] == 0:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            sample_categories = [
                ("Đồ uống", "Nước giải khát, cà phê, trà đóng chai", 1, now),
                ("Bánh kẹo", "Snack, bánh quy, kẹo các loại", 1, now),
                ("Gia dụng", "Đồ dùng sinh hoạt và tiện ích gia đình", 1, now),
            ]
            cursor.executemany(
                "INSERT INTO categories (name, description, is_active, created_at) VALUES (?, ?, ?, ?)",
                sample_categories,
            )

        conn.commit()


# --- QUẢN LÝ DANH MỤC ---

def get_all_categories(only_active=False):
    init_catalog_tables()
    with get_connection() as conn:
        if only_active:
            rows = conn.execute(
                "SELECT * FROM categories WHERE is_active = 1 ORDER BY name ASC"
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM categories ORDER BY id DESC"
            ).fetchall()
        return [dict(r) for r in rows]


def add_category(name, description=""):
    init_catalog_tables()
    clean_name = (name or "").strip()
    clean_desc = (description or "").strip()

    if not clean_name:
        return False, "Tên danh mục không được để trống."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with get_connection() as conn:
            conn.execute(
                "INSERT INTO categories (name, description, is_active, created_at) VALUES (?, ?, 1, ?)",
                (clean_name, clean_desc, now),
            )
            conn.commit()
        return True, f"Đã thêm danh mục '{clean_name}'."
    except sqlite3.IntegrityError:
        return False, f"Danh mục '{clean_name}' đã tồn tại."


def toggle_category_status(category_id):
    init_catalog_tables()
    with get_connection() as conn:
        row = conn.execute(
            "SELECT id, name, is_active FROM categories WHERE id = ?", (category_id,)
        ).fetchone()
        if not row:
            return False, "Không tìm thấy danh mục."

        new_status = 0 if row["is_active"] == 1 else 1
        conn.execute(
            "UPDATE categories SET is_active = ? WHERE id = ?", (new_status, category_id)
        )
        conn.commit()
        status_text = "kích hoạt" if new_status == 1 else "ẩn"
        return True, f"Đã {status_text} danh mục '{row['name']}'."


# --- QUẢN LÝ SẢN PHẨM, GIÁ & MÔ TẢ ---

def get_all_products(include_inactive=True):
    init_catalog_tables()
    query = """
        SELECT p.*, c.name AS category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
    """
    if not include_inactive:
        query += " WHERE p.is_active = 1"
    query += " ORDER BY p.id DESC"

    with get_connection() as conn:
        rows = conn.execute(query).fetchall()
        return [dict(r) for r in rows]


def add_product(sku, name, category_id, price, stock, description=""):
    init_catalog_tables()
    clean_sku = (sku or "").strip().upper()
    clean_name = (name or "").strip()
    clean_desc = (description or "").strip()

    if not clean_sku or not clean_name:
        return False, "Mã SKU và tên sản phẩm là bắt buộc."

    try:
        price_val = float(price)
        stock_val = int(stock)
    except (ValueError, TypeError):
        return False, "Giá bán và số lượng tồn kho không hợp lệ."

    if price_val < 0 or stock_val < 0:
        return False, "Giá bán và số lượng tồn kho phải lớn hơn hoặc bằng 0."

    cat_id = int(category_id) if category_id else None
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with get_connection() as conn:
            conn.execute(
                """
                INSERT INTO products (sku, name, category_id, price, stock, description, is_active, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, 1, ?)
                """,
                (clean_sku, clean_name, cat_id, price_val, stock_val, clean_desc, now),
            )
            conn.commit()
        return True, f"Đã thêm sản phẩm '{clean_name}' ({clean_sku})."
    except sqlite3.IntegrityError:
        return False, f"Mã SKU '{clean_sku}' đã tồn tại."


def update_product(product_id, name, category_id, new_price, stock, description, is_active=1):
    """Cập nhật giá bán, mô tả, danh mục, tồn kho và ghi lịch sử nếu giá thay đổi."""
    init_catalog_tables()
    clean_name = (name or "").strip()
    clean_desc = (description or "").strip()

    if not clean_name:
        return False, "Tên sản phẩm không được để trống."

    try:
        price_val = float(new_price)
        stock_val = int(stock)
        cat_id = int(category_id) if category_id else None
        active_val = 1 if str(is_active) in ("1", "True", "true", "on") else 0
    except (ValueError, TypeError):
        return False, "Dữ liệu cập nhật không hợp lệ."

    if price_val < 0 or stock_val < 0:
        return False, "Giá bán và số lượng tồn kho không thể âm."

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with get_connection() as conn:
        current = conn.execute(
            "SELECT id, price FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        if not current:
            return False, "Không tìm thấy sản phẩm."

        old_price = float(current["price"])

        conn.execute(
            """
            UPDATE products
            SET name = ?, category_id = ?, price = ?, stock = ?, description = ?, is_active = ?, updated_at = ?
            WHERE id = ?
            """,
            (clean_name, cat_id, price_val, stock_val, clean_desc, active_val, now, product_id),
        )

        if old_price != price_val:
            conn.execute(
                """
                INSERT INTO price_history (product_id, old_price, new_price, changed_at)
                VALUES (?, ?, ?, ?)
                """,
                (product_id, old_price, price_val, now),
            )

        conn.commit()

    return True, f"Đã cập nhật sản phẩm '{clean_name}'."


def get_price_history(limit=20):
    init_catalog_tables()
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT ph.*, p.sku, p.name AS product_name
            FROM price_history ph
            JOIN products p ON ph.product_id = p.id
            ORDER BY ph.id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [dict(r) for r in rows]


# --- TÌM KIẾM SẢN PHẨM NHANH TRÊN GIAO DIỆN BÁN HÀNG ---

def search_products_fast(keyword="", category_id="", only_in_stock=False):
    init_catalog_tables()
    kw = f"%{(keyword or '').strip()}%"
    sql = """
        SELECT p.*, c.name AS category_name
        FROM products p
        LEFT JOIN categories c ON p.category_id = c.id
        WHERE p.is_active = 1
          AND (p.name LIKE ? OR p.sku LIKE ? OR p.description LIKE ?)
    """
    params = [kw, kw, kw]

    if category_id:
        try:
            sql += " AND p.category_id = ?"
            params.append(int(category_id))
        except ValueError:
            pass

    if only_in_stock:
        sql += " AND p.stock > 0"

    sql += " ORDER BY p.name ASC"

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
        return [dict(r) for r in rows]
