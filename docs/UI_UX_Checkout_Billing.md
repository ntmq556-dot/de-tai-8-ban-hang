# Tài liệu Thiết kế Giao diện Người dùng (UI/UX Prototype)
## Module 4: Thanh toán & In Hóa đơn (Checkout & Billing) — Thành viên 4

### 1. Mục tiêu thiết kế (UX Goals)
- **Tối ưu thao tác thu ngân (Speed & Efficiency):** Giảm thiểu số lần nhấp chuột, hỗ trợ quét mã SKU/Barcode tự động thêm vào giỏ hàng, gợi ý mệnh giá tiền mặt nhanh.
- **Phòng ngừa sai sót nhập liệu (Error Prevention):** Tự động kiểm tra tồn kho trước khi thêm vào giỏ, tính toán tự động tiền thừa, khóa thanh toán nếu số tiền khách đưa nhỏ hơn tổng hóa đơn.
- **Đồng bộ dữ liệu liên module:** Chuẩn hóa dữ liệu sản phẩm (tương thích đồng thời `id` và `product_id`) và tích hợp trực tiếp hệ thống tích điểm/đổi điểm khách hàng thành viên.

---

### 2. Kiến trúc Bố cục Màn hình (Wireframe & Layout Structure)
Giao diện chính (`/checkout`) áp dụng bố cục **2 cột bất đối xứng (7:5)** chuẩn POS:

```text
+-----------------------------------------------------------------------------------+
| THANH ĐIỀU HƯỚNG (POS BÁN HÀNG - MODULE 4)                                        |
+-----------------------------------------+-----------------------------------------+
| CỘT TRÁI (7 Phần) - CHỌN SẢN PHẨM       | CỘT PHẢI (5 Phần) - GIỎ HÀNG & T.TOÁN   |
| +-------------------------------------+ | +-------------------------------------+ |
| | Ô tìm kiếm nhanh / Quét SKU-Barcode | | | Bảng Giỏ hàng (Tên, Đ.Giá, +/- SL)  | |
| +-------------------------------------+ | +-------------------------------------+ |
| | Lưới thẻ Sản phẩm (Product Cards)   | | | Tra cứu Khách hàng (SĐT / Mã KH)    | |
| | [Mã SKU] [Tồn kho] | Tên | Đơn giá  | | | -> Đổi điểm tích lũy (1đ = 1.000đ)  | |
| +-------------------------------------+ | +-------------------------------------+ |
|                                         | | Tạm tính | Giảm giá | TỔNG THANH TOÁN | |
| +-------------------------------------+ | +-------------------------------------+ |
| | Bảng Lịch sử Hóa đơn vừa xuất       | | | Phương thức: [Tiền mặt|CK QR|Thẻ]  | |
| +-------------------------------------+ | | Tiền khách đưa -> Tự tính Tiền thừa | |
|                                         | | [ NÚT THANH TOÁN & IN HÓA ĐƠN ]     | |
+-----------------------------------------+-----------------------------------------+