# Cấu hình pipeline Fabric hiện tại

Pipeline: `mindx_master`. Lakehouse: `lh_mindx_final`. Workspace/Lakehouse UUID nằm trong `config.json`.

## Activities và dependency

| Activity | Loại | Notebook / Nguồn | Chạy sau |
|---|---|---|---|
| Copy_Sales | Copy | mindx_raw_sales_data.csv | — |
| Copy_Exchange | Copy | exchange_rate_2425.csv | — |
| Validate_Bronze | Notebook | 01_bronze_validation | Cả hai Copy |
| Silver | Notebook | 02_silver | Validate_Bronze |
| Gold | Notebook | 03_gold | Silver |
| Acceptance | Notebook | 04_acceptance | Gold |

Tất cả đường nối là Succeeded. Hai Copy không nối với nhau.

## Copy Source

Cùng connection Lakehouse, root **Files**. Directory: `Source`. Source format DelimitedText; UTF-8, header bật, delimiter comma, quote và escape đều là double quote (`"`). Copy_Sales có 15 cột, Copy_Exchange có 5 cột. Mapping source/sink đều String, không skip dòng lỗi hoặc tự chuyển kiểu.

## Copy Destination

Cùng Lakehouse, root **Files**, format Parquet (Snappy).

| Activity | Directory — nhập qua Add dynamic content | File name |
|---|---|---|
| Copy_Sales | `@concat('Bronze/', pipeline().RunId, '/sales')` | sales.parquet |
| Copy_Exchange | `@concat('Bronze/', pipeline().RunId, '/exchange_rate')` | exchange_rate.parquet |

Không thêm Files/ vào Directory vì đã chọn root Files.

## Notebook Settings

Chọn đúng notebook, cùng connection/tài khoản có quyền và cùng default Lakehouse/runtime. Base parameters của **cả bốn** activity:

| Name | Type | Value |
|---|---|---|
| run_id | String | `@pipeline().RunId` qua Add dynamic content |
| source_folder | String | Source |
| bronze_folder | String | Bronze |
| reports_folder | String | Reports |
| table_schema | String | dbo |
| strict_project_snapshot | Bool | true |

Không cần tạo pipeline parameters khi dùng các giá trị literal ở trên. Nếu đổi folder/schema trong config, cập nhật cả Base parameters và hai Copy tương ứng.

Cell chứa sáu biến mặc định trong notebook phải có tag parameters; các file trong prepared đã có tag này. `table_schema=dbo` áp dụng Lakehouse bật schemas; nếu không có schema, dùng chuỗi rỗng và đồng bộ notebook.

## Spark session

Workspace settings → Data Engineering/Science → Spark settings → High concurrency: bật **For pipeline running multiple notebooks**. Ở Settings → Advanced settings của bốn Notebook Activity, đặt cùng **Session tag: mindx_final**. Giữ cùng Spark configuration, default Lakehouse và libraries. Thiết lập này không tăng quota capacity.

## Chạy và kiểm tra

Save, Validate nếu có, rồi Run. Chỉ dùng báo cáo sau khi Acceptance Succeeded và marker trong `Files/Reports/<run_id>/acceptance` có PASS. Gold ghi đè bảng báo cáo; không chạy hai batch đồng thời. Nếu lỗi giữa batch, sửa nguyên nhân rồi chạy lại, không dùng kết quả Gold đang ghi dở.

Run thành công đã ghi nhận: `46d7ce91-000d-4f37-a118-719fa2b51b3c`. Xem [kết quả nghiệm thu](../reports/fabric/README.md).
