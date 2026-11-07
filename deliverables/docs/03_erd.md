# ERD Gold

Khóa hash dùng SHA-256 trên JSON struct để tránh ghép chuỗi mơ hồ. Date key yyyyMMdd. Các fact chứa FK vào dimension; fact_order_items dùng (order_id,item_index) làm khóa. item_index là vị trí trong mảng nguồn, giữ được hai dòng sản phẩm giống nhau trong một đơn.

```mermaid
erDiagram
  gold_dim_date ||--o{ gold_fact_orders : date_key
  gold_dim_customer ||--o{ gold_fact_orders : customer_key
  gold_dim_location ||--o{ gold_fact_orders : location_key
  gold_dim_payment_method ||--o{ gold_fact_orders : payment_key
  gold_fact_orders ||--|{ gold_fact_order_items : order_id
  gold_dim_date ||--o{ gold_fact_order_items : date_key
  gold_dim_product ||--o{ gold_fact_order_items : product_key
  gold_fact_orders {
    string order_id PK
    int date_key FK
    string customer_key FK
    string location_key FK
    string payment_key FK
    decimal total_amount_usd
    decimal exchange_rate
    boolean report_eligible
    boolean has_discount
    string order_status
  }
  gold_fact_order_items {
    string order_id PK,FK
    int item_index PK
    int date_key FK
    string product_key FK
    decimal line_subtotal_usd
    decimal allocated_revenue_usd
    decimal allocated_revenue_vnd
  }
  gold_dim_date {
    int date_key PK
    date full_date
    int year
    int month
  }
  gold_dim_customer {
    string customer_key PK
    string customer_name
    string customer_email
    string customer_phone
  }
  gold_dim_location {
    string location_key PK
    string location
  }
  gold_dim_payment_method {
    string payment_key PK
    string payment_method
  }
  gold_dim_product {
    string product_key PK
    string product_id
    string category
  }
```

Dimension ngày phủ liên tục 2024-01-01 đến 2025-12-31. Tỷ giá đã join vào fact_orders theo năm/tháng/currency; không join bảng tỷ giá lần nữa trong BI. Customer age và feedback nằm tại fact_orders vì là thuộc tính ghi nhận tại giao dịch.

Đây là nguồn sơ đồ để xuất ảnh, chưa phải ảnh chụp ERD từ Fabric. Không dùng dữ liệu khách hàng trong ảnh trình bày công khai.
