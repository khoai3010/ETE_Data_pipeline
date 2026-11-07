# MINDX-Mart — Microsoft Fabric Final Project

Project chỉ giữ bản chạy trên Microsoft Fabric. Pipeline `mindx_master` đã chạy thành công với sáu activity theo ảnh và JSON nghiệm thu người dùng cung cấp. Xem [kết quả Fabric](deliverables/reports/fabric/README.md).

Để học cách giải thích pipeline, từng bảng, công thức và log, đọc [tài liệu ôn bảo vệ](deliverables/docs/04_defense_guide.md). Tài liệu có ví dụ từ CSV thật, truy vấn demo và câu hỏi thường gặp.

Bản dễ đọc trong Word: [defense_guild.docx](deliverables/docs/defense_guild.docx). Để dựng slide, dùng [kịch bản thuyết trình Word](deliverables/docs/slide_presentation_script.docx) hoặc [bản Markdown](deliverables/docs/05_slide_script.md). Kịch bản gồm 12 slide chính khoảng 10–12 phút, speaker notes và phần hỏi đáp dự phòng. Có thể tạo lại hai file Word bằng `python deliverables/build_study_documents.py` (cần python-docx, đã có trên máy hiện tại).

## Bộ bài nộp

Thư mục sinh trên máy: `submission/MINDX_Final_Project/`. File nén: `submission/MINDX_Final_Project.zip`. Báo cáo ghi tên **Bùi Quang Khánh**; kèm bốn notebook, ERD, ảnh thiết kế pipeline, dữ liệu và JSON nghiệm thu. Thư mục submission không đưa vào Git vì chứa nhiều bản sao có thể tạo lại bằng script.

Ảnh thiết kế pipeline được vẽ từ kiến trúc, không phải ảnh chụp giao diện Fabric. Để thêm ảnh chạy thật bạn đã chụp, lưu vào `submission/MINDX_Final_Project/diagrams/master_pipeline_fabric.png`, rồi chạy:

```powershell
python deliverables/package_submission.py
```

Script sẽ nhúng ảnh vào báo cáo và cập nhật ZIP. Script đóng gói dùng `matplotlib` và `python-docx` (đã có trên máy hiện tại); việc chạy code trên Fabric không cần các thư viện này. Nếu bổ sung notebook export có outputs từ Fabric, đặt riêng vào `submission/MINDX_Final_Project/evidence/fabric_exports` để không bị thay bằng bản mã gốc khi đóng gói lại.

## Cấu trúc

```text
deliverables/
  fabric/
    config.json                    # Workspace, Lakehouse và tham số
    configure.py                   # Kiểm tra/đồng bộ cấu hình cục bộ
    MANUAL_BINDINGS.md              # Cấu hình pipeline trên Fabric
    prepared/
      01_bronze_validation.ipynb
      02_silver.ipynb
      03_gold.ipynb
      04_acceptance.ipynb
      inputs/
        mindx_raw_sales_data.csv
        exchange_rate_2425.csv
  docs/
    project_requirements.docx       # Đề bài gốc
    01_business_rules.md            # Quy tắc xử lý dữ liệu
    03_erd.md                       # Mô hình PK/FK
    erd.png                        # Ảnh ERD
  reports/fabric/
    README.md
    acceptance_46d7ce91-000d-4f37-a118-719fa2b51b3c.json
```

## Chạy trên Fabric

1. Lấy hai CSV từ tài nguyên khóa học và đặt vào `deliverables/fabric/prepared/inputs` (dữ liệu thô không được công khai trên GitHub). Upload chúng vào `Files/Source` của Lakehouse `lh_mindx_final`.
2. Import bốn notebook trong `deliverables/fabric/prepared`, gắn cùng Lakehouse làm default.
3. Cấu hình theo [MANUAL_BINDINGS](deliverables/fabric/MANUAL_BINDINGS.md). Pipeline hiện tại trên Fabric đã được tạo; không cần tạo lại nếu vẫn dùng workspace/Lakehouse hiện tại.
4. Bật High concurrency cho pipeline trong workspace, đặt cùng Session tag `mindx_final` cho bốn Notebook Activity. Chỉ chạy một batch tại một thời điểm.
5. Run pipeline; cả sáu activity phải Succeeded. Kết quả ở `Files/Reports/<PipelineRunId>/`; marker `acceptance/part-*.txt` phải có `status=PASS`.

```text
Copy_Sales ----+--> Validate_Bronze --> Silver --> Gold --> Acceptance
Copy_Exchange -+
```

Trong pipeline, luôn truyền `run_id` bằng dynamic content `@pipeline().RunId`. Không chạy riêng notebook với `run_id=manual` nếu chưa có Bronze manual.

## Kiểm tra cấu hình trên máy

Sau khi clone repo, tạo cấu hình cá nhân (chỉ cần làm một lần; không ghi đè nếu đã có cấu hình):

```powershell
Copy-Item deliverables/fabric/config.example.json deliverables/fabric/config.json
```

Điền workspace_url, lakehouse_url và tên Lakehouse của bạn. File config.json riêng không được đưa vào Git. Notebook trong repo giữ metadata của Lakehouse đã dùng cho project; nếu dùng Lakehouse khác, chạy lệnh --write bên dưới để gắn lại trước khi import.

Kiểm tra cấu hình chỉ cần Python, không cần Java/PySpark hoặc thư viện ngoài. Tại thư mục gốc project:

```powershell
python deliverables/fabric/configure.py
```

Nếu đổi workspace/Lakehouse hoặc tham số: sửa `config.json`, rồi đồng bộ file notebook cục bộ:

```powershell
python deliverables/fabric/configure.py --write
```

Lệnh không cập nhật tài nguyên Fabric. Sau khi thay đổi, cập nhật/import lại notebook tương ứng và kiểm tra Base parameters của pipeline. Bốn notebook hiện tại không bị thay đổi bởi lần dọn này; không cần import lại chỉ vì đã dọn thư mục.

## Mốc đối soát của bộ CSV hiện tại

- 4.896 đơn Silver; 104 đơn cách ly; 9.850 dòng sản phẩm; 24 tỷ giá.
- Tổng cộng 15 bảng; 2.669 đơn đủ điều kiện báo cáo, trong đó 885 Completed.
- Doanh thu theo tập lọc đề bài: 68.128.580.695,61 VNĐ.
- Doanh thu chỉ Completed: 22.440.017.306,84 VNĐ.

Bản chạy cục bộ, môi trường Java/Spark, installer lớn và gói triển khai cũ đã được loại bỏ. Việc dọn chỉ tác động file trên máy, không thay đổi pipeline hoặc dữ liệu trên Fabric. Phần gom bài nộp thực hiện sau.

## Tạo lại tài liệu và bộ nộp

Các thư viện ở đây chỉ dùng trên máy để tạo Word/hình/ZIP, không cần cài vào notebook Fabric:

```powershell
python -m pip install -r requirements.txt
python deliverables/build_study_documents.py
python deliverables/package_submission.py
```

Để Word ôn bảo vệ kèm ảnh thiết kế pipeline khi dựng lại từ repo mới clone, có thể chạy package_submission.py trước build_study_documents.py. Ảnh chụp Fabric thật và các notebook export có outputs cần tự bổ sung từ workspace; script không tự tải bằng chứng trên dịch vụ.
