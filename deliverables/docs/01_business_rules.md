# Quy tắc nghiệp vụ và dữ liệu

## Bronze

Giữ 15 cột sales và 5 cột exchange ở kiểu string, giữ nguyên giá trị. CSV → Parquet bằng Data Factory Copy Activity; không làm sạch ở Bronze. CSV có JSON chứa dấu phẩy: delimiter `,`, quote `"`, escape `"`, first row as header, UTF-8. Kiểm tra preview JSON trước khi chạy.

## Silver

- Loại bản ghi trùng hoàn toàn. Nếu cùng order_id nhưng nội dung khác nhau: cách ly tất cả phiên bản, không chọn ngẫu nhiên.
- Ngày: ISO timestamp hoặc dd/MM/yyyy HH:mm. Không có timezone nguồn, giữ thời gian như được cung cấp, không tự đổi múi giờ.
- Tuổi: twenty → 20; thirty-five → 35; unknown/trống/không hợp lệ → null. Chấp nhận tuổi 18–100. Không loại đơn chỉ vì thiếu tuổi.
- Email thiếu giữ null; thiết bị thiếu → Unknown. Không dùng email làm khóa khách hàng vì có null và có thể trùng.
- Chuẩn hóa Credit Card / CREDITCARD / credit_card → Credit Card.
- Bỏ ký tự $ ở đầu tổng tiền; tiền dùng decimal, không dùng float để tính báo cáo.
- customer_info phải parse được; items phải có ít nhất một dòng; mã sản phẩm/danh mục không rỗng, giá > 0, số lượng nguyên > 0.
- Ngày/mã đơn/tổng tiền/currency/trạng thái/phương thức thanh toán không hợp lệ, phí vận chuyển âm hoặc không parse được: cách ly đơn nguyên vẹn, lưu error_reason và raw_record.
- Feedback 99 hoặc null là lỗi chất lượng phục vụ báo cáo: giữ ở Silver cùng cờ report_eligible=false. Failed cũng giữ Silver để kiểm toán.
- Tỷ giá: khóa (year, month, from_currency, to_currency) duy nhất, năm 2024–2025, tháng 1–12, USD→VND, rate > 0. Khóa xung đột cách ly tất cả phiên bản.
- Thiếu tỷ giá cho đơn hợp lệ: dừng Gold, không gán tỷ giá mặc định hay bỏ đơn âm thầm.
- Dữ liệu cách ly không tự phục hồi. Sửa nguồn/quy tắc có giải thích, rồi chạy lại.

## Gold và doanh thu

Tập báo cáo theo đề: đơn ở Silver hợp lệ, status != Failed, feedback thuộc 1–5. Bao gồm Pending và Refunded theo điều kiện nguyên văn của đề; không gọi tập này là tiền đã thu.

Chọn phân bổ total_amount cho từng dòng theo tỷ trọng price × quantity. Tổng phân bổ phải khớp tổng tiền đơn (sai số tối đa 0.01 USD/đơn do làm tròn). Tổng tiền nguồn đã chứa khoản cộng thêm ngẫu nhiên, không cộng shipping_cost lần nữa. Không có số tiền giảm giá nên không tự trừ discount_code.

`gold_monthly_revenue_category`: doanh thu theo tập lọc nguyên văn đề. `gold_monthly_completed_revenue_category`: chỉ Completed, dùng để thuyết minh doanh thu hoàn tất. Không tính net revenue/refund vì thiếu dữ liệu hoàn tiền.

Tỷ lệ khuyến mãi = số đơn có mã không rỗng / tổng số đơn trong tập báo cáo × 100, nhóm theo location. Tính trên fact_orders, không tính trên dòng items. Đây là tỷ lệ sử dụng mã, không phải bằng chứng khuyến mãi gây tăng doanh thu.

Mã sản phẩm xuất hiện ở nhiều danh mục: dimension dùng (product_id, category). Nguồn không có customer_id ổn định: customer_key là hash(name,email,phone); chỉ là nhận diện hồ sơ nguồn, không khẳng định một người thực ngoài đời.

## Chạy lại

Batch snapshot toàn bộ dữ liệu; overwrite Delta Tables sau khi kiểm tra. Không tuyên bố hỗ trợ incremental. Chạy tuần tự, không chạy hai pipeline đồng thời. Khi lỗi giữa các bảng, sửa rồi chạy lại từ Silver; không công bố báo cáo khi pipeline chưa thành công hoàn toàn.
