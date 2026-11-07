# Dữ liệu nguồn của project

Thư mục có hai CSV được cấp trong khóa học:

- `mindx_raw_sales_data.csv`: 5.250 dòng, gồm 15 cột.
- `exchange_rate_2425.csv`: 24 dòng tỷ giá USD→VND theo tháng.

Hai file dữ liệu mẫu được đưa vào repo theo yêu cầu của chủ project để có thể tái lập kết quả. Sau khi clone, dùng đúng các file này để đối soát với JSON nghiệm thu.

Schema sales: order_id, order_date, customer_info, customer_age, location, device_type, items, payment_method, currency, discount_code, shipping_cost, total_amount, order_status, loyalty_points, feedback_score.

Schema tỷ giá: year, month, from_currency, to_currency, exchange_rate.

Khi chạy Fabric, upload hai file vào `Files/Source` của Lakehouse. Không chạy lại notebook sinh dữ liệu ngẫu nhiên nếu muốn đối soát với các mốc nghiệm thu đã lưu.
