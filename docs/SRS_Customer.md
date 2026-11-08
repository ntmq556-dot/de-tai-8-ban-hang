# Software Requirements Specification (SRS)
## Module: Quản lý Khách hàng (Customer Management)
**Dự án:** Hệ thống Quản lý Bán hàng (Retail Management System - Đề tài 8)  
**Nhóm trưởng / M1:** Nguyễn Trần Minh Quân  

---

## 1. Introduction (Phần giới thiệu)
### 1.1 Purpose (Mục đích)
Tài liệu này xác định và mô tả chi tiết các yêu cầu về chức năng và phi chức năng đối với **Module Quản lý Khách hàng**. Tài liệu làm cơ sở kỹ thuật phục vụ trực tiếp cho nhóm phát triển (Developer) viết mã nguồn, đội ngũ kiểm thử (Tester) xây dựng kịch bản kiểm tra, quản lý dự án (Project Manager) theo dõi tiến độ và bàn giao cho khách hàng[cite: 1, 2].

### 1.2 Scope (Phạm vi)
* **Tên sản phẩm phần mềm:** Hệ thống Quản lý Bán hàng - Module Quản lý Khách hàng.
* **Hệ thống sẽ làm:** Cho phép thêm mới khách hàng, tìm kiếm tra cứu nhanh theo số điện thoại hoặc mã khách hàng, cập nhật thông tin liên lạc, phân loại trạng thái hoạt động và lưu trữ lịch sử dữ liệu vào cơ sở dữ liệu SQLite cục bộ.
* **Hệ thống sẽ không làm:** Không tích hợp tính năng gửi tin nhắn SMS/Email tự động qua nhà mạng bên thứ ba ở phiên bản cục bộ này.
* **Mục tiêu và lợi ích kinh doanh:** Chuẩn hóa dữ liệu khách hàng cho cửa hàng bán lẻ, giúp nhân viên tra cứu nhanh chóng khi thanh toán đơn hàng, hỗ trợ tối ưu hóa quy trình chăm sóc khách hàng.

### 1.3 Definitions, Acronyms, and Abbreviations (Định nghĩa, từ viết tắt)
* **SRS:** Software Requirements Specification (Tài liệu Yêu cầu Phần mềm).
* **FR:** Functional Requirement (Yêu cầu chức năng của hệ thống).
* **NFR:** Non-Functional Requirement (Yêu cầu phi chức năng).
* **SQLite:** Hệ quản trị cơ sở dữ liệu quan hệ dạng tệp cục bộ dùng cho ứng dụng desktop.
* **M1:** Thành viên 1 (Vai trò Trưởng nhóm kiêm phụ trách Module Khách hàng).

### 1.4 References (Tài liệu tham khảo)
* Tiêu chuẩn quốc tế IEEE Std 830-1998 về lập tài liệu yêu cầu phần mềm[cite: 1].
* Tài liệu định hướng đề tài đồ án môn học: *Đề tài 8 - Hệ thống Quản lý Bán hàng*.

### 1.5 Overview (Tổng quan tài liệu)
Cấu trúc tài liệu tiếp theo gồm: Phần 2 mô tả tổng quan góc nhìn, chức năng và ràng buộc hệ thống; Phần 3 liệt kê chi tiết các yêu cầu chức năng, hiệu năng và giao diện; Phần 4 chứa phụ lục sơ đồ UML minh họa[cite: 1].

---

## 2. Overall Description (Mô tả tổng quan)
### 2.1 Product Perspective (Góc nhìn sản phẩm)
Đây là một module thành phần cốt lõi bên trong ứng dụng **Retail Management System**, hoạt động như một phần mềm độc lập chạy trên máy tính cá nhân (Desktop App), kết nối trực tiếp với cơ sở dữ liệu nhúng SQLite cục bộ mà không phụ thuộc vào hệ thống đám mây bên ngoài.

### 2.2 Product Functions (Các chức năng chính của sản phẩm)
* Quản lý thông tin chi tiết cá nhân khách hàng.
* Tra cứu, tìm kiếm dữ liệu khách hàng theo thời gian thực.
* Cập nhật và chỉnh sửa thông tin khi có thay đổi.
* Quản lý trạng thái hoạt động của khách hàng trong hệ thống.

### 2.3 User Characteristics (Đặc điểm người dùng)
* **Nhân viên thu ngân / Bán hàng:** Có kỹ năng sử dụng máy tính cơ bản, chịu trách nhiệm nhập liệu thông tin khách hàng mới phát sinh tại quầy và tra cứu thông tin nhanh.
* **Quản trị viên / Nhóm trưởng (Admin):** Có chuyên môn CNTT, quản lý toàn bộ cấu trúc cơ sở dữ liệu, phân quyền và kiểm soát toàn vẹn dữ liệu.

### 2.4 Constraints (Các ràng buộc)
* **Ngôn ngữ lập trình:** Phát triển bằng ngôn ngữ Python (phiên bản 3.x).
* **Cơ sở dữ liệu:** Bắt buộc sử dụng SQLite làm bộ lưu trữ cục bộ.
* **Thời gian và quy mô:** Dự án phục vụ cho phạm vi cửa hàng bán lẻ độc lập, vận hành trên máy tính cá nhân có cấu hình thông thường.

### 2.5 Assumptions and Dependencies (Các giả định và phụ thuộc)
* **Giả định:** Người dùng tại quầy nhập chính xác số điện thoại định danh khách hàng.
* **Phụ thuộc:** Module Quản lý Khách hàng phụ thuộc và cung cấp dữ liệu liên kết cho **Module Đặt hàng (Order Management - M3)** nhằm ghi nhận lịch sử giao dịch mua bán.

---

## 3. Specific Requirements (Yêu cầu chi tiết)
### 3.1 External Interfaces (Giao diện bên ngoài)
* **Giao diện người dùng (UI):** Giao diện dạng cửa sổ ứng dụng (Desktop UI) với các thành phần: Ô tìm kiếm, Bảng hiển thị danh sách (Data Grid) và Form nhập liệu thông tin[cite: 1, 2].
* **Giao diện phần cứng:** Tương thích với màn hình độ phân giải từ HD (1366x768) trở lên, sử dụng chuột và bàn phím tiêu chuẩn[cite: 1, 2].
* **Giao diện phần mềm:** Tương tác với thư viện giao diện Python và Driver kết nối SQLite[cite: 1, 2].
* **Giao diện truyền thông:** Hoạt động cục bộ (Offline), không yêu cầu giao thức mạng phức tạp ngoại trừ việc đồng bộ mã nguồn qua Git[cite: 1, 2].

### 3.2 Functional Requirements (Yêu cầu chức năng)
* **FR-C01 (Thêm khách hàng):** Hệ thống phải cho phép thêm mới khách hàng khi người dùng nhập đầy đủ thông tin (Họ tên, SĐT). Số điện thoại phải là duy nhất[cite: 1, 2, 3].
* **FR-C02 (Sinh mã tự động):** Hệ thống phải tự động tạo mã định danh theo định dạng `KHxxx` (ví dụ: `KH001`, `KH002`) cho mỗi bản ghi mới[cite: 1, 2, 3].
* **FR-C03 (Tìm kiếm khách hàng):** Hệ thống phải trả về kết quả tìm kiếm chính xác ngay lập tức khi người dùng nhập chuỗi số điện thoại hoặc mã khách hàng[cite: 1, 2, 3].

### 3.3 Performance Requirements (Yêu cầu hiệu năng)
* **Thời gian phản hồi:** Thao tác tra cứu thông tin khách hàng phải hoàn tất với độ trễ dưới 1 giây[cite: 1, 2].
* **Khả năng lưu trữ:** Hỗ trợ lưu trữ hiệu quả các bảng dữ liệu quy mô dưới 100.000 bản ghi khách hàng mà không làm chậm ứng dụng[cite: 1, 2].

### 3.4 Logical Database Requirements (Yêu cầu cơ sở dữ liệu)
* Lưu trữ dưới dạng tệp cơ sở dữ liệu quan hệ SQLite với bảng `Customers` bao gồm các trường: `id` (Primary Key), `name`, `phone`, `email`, `address`[cite: 1, 2].
* Đảm bảo tính toàn vẹn dữ liệu thông qua ràng buộc `UNIQUE` trên trường số điện thoại (`phone`)[cite: 1, 2].

### 3.5 Design Constraints (Ràng buộc thiết kế)
* Kiến trúc mã nguồn phải tuân thủ hướng đối tượng (OOP) phân tách rõ tầng giao diện và tầng xử lý logic dữ liệu[cite: 1].

### 3.6 Software System Attributes (Các thuộc tính hệ thống)
* **Độ bảo mật (Security):** Giới hạn quyền truy cập tệp cơ sở dữ liệu cục bộ, kiểm tra dữ liệu đầu vào chống lỗi chèn mã độc[cite: 1, 2].
* **Tính sẵn sàng (Availability):** Ứng dụng khởi động nhanh chóng và hoạt động ổn định ngoại tuyến[cite: 1, 2].
* **Khả năng bảo trì (Maintainability):** Mã nguồn được chú thích rõ ràng, tuân thủ quy chuẩn đặt tên file, dễ dàng mở rộng tính năng[cite: 1, 2].
* **Tính di động (Portability):** Có thể đóng gói chạy trên các hệ điều hành phổ biến hỗ trợ Python và SQLite[cite: 1, 2].

---

## 4. Appendices (Phụ lục)
* **Sơ đồ Use Case (Use Case Diagram):**
* **Sơ đồ Quan hệ Thực thể (ERD - Entity Relationship Diagram):**
* **Sơ đồ Tuần tự (Sequence Diagram):**
* **Sơ đồ hoạt động (Activity Diagram - Luồng thêm khách hàng):**
 