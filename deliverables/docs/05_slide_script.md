# Kịch bản slide thuyết trình — MINDX-Mart

**Họ và tên:** Bùi Quang Khánh  
**Chủ đề:** End-to-End Data Pipeline trên Microsoft Fabric  
**Quy mô:** 12 slide, khoảng 10–12 phút, chưa tính hỏi đáp.  
**Mạch kể:** dữ liệu chưa dùng được → quyết định xử lý → mô hình và chỉ số → bằng chứng đúng → giới hạn.

Đây là kịch bản để dựng slide, không phải file PowerPoint. Mỗi mục “Trên slide” là nội dung hiển thị; “Lời trình bày” dùng làm speaker notes. Không đưa toàn bộ lời nói lên màn hình.

## Slide 1 — Từ dữ liệu giao dịch thô đến báo cáo đáng tin cậy

**Thời lượng:** 20 giây.

**Trên slide:**
- MINDX-Mart — Data Engineering Level 3
- Microsoft Fabric · Medallion Architecture
- Bùi Quang Khánh

**Hình minh họa:** Một luồng ngắn CSV → Bronze → Silver → Gold. Không cần code ở slide mở đầu.

**Lời trình bày:**

“Em là Bùi Quang Khánh. Trong project này, em xây dựng pipeline bán lẻ trên Microsoft Fabric để chuyển dữ liệu giao dịch thô thành các bảng và báo cáo có thể kiểm tra được. Trọng tâm của bài là xử lý dữ liệu bất thường, tính chỉ số đúng cấp độ và có bước nghiệm thu thay vì chỉ chạy code thành công.”

**Chuyển ý:** “Đầu tiên, vì sao dữ liệu nguồn chưa thể dùng trực tiếp?”

## Slide 2 — Hai nguồn dữ liệu, ba yêu cầu nghiệp vụ

**Thời lượng:** 45 giây.

**Trên slide:**
- Sales: 5.250 dòng, 15 cột, giao dịch 2024–2025.
- Exchange rate: 24 tỷ giá USD → VND theo tháng.
- Báo cáo doanh thu VNĐ theo tháng và danh mục.
- Tỷ lệ đơn dùng mã theo địa điểm; loại Failed và feedback ngoài 1–5.

**Hình minh họa:** Hai thẻ nguồn CSV ở trái, hai thẻ báo cáo ở phải. Thêm ví dụ nhỏ: `twenty`, `$925.24`, JSON trong CSV.

**Lời trình bày:**

“Sales có 5.250 dòng và chứa thông tin khách hàng, mảng sản phẩm cùng thuộc tính đơn hàng. Nguồn thứ hai cung cấp tỷ giá theo tháng trong hai năm. Dữ liệu có dòng trùng, ngày khác định dạng, tuổi dạng chữ, số tiền có ký tự và điểm đánh giá không hợp lệ. Đề yêu cầu doanh thu theo tháng, danh mục và tỷ lệ sử dụng mã theo địa điểm. Vì vậy, em phải vừa chuẩn hóa dữ liệu, vừa xác định tập đơn nào được phép xuất hiện trong báo cáo.”

**Câu hỏi có thể gặp:** “Sao không dùng pandas?” — Dữ liệu nhỏ có thể dùng pandas; PySpark được chọn để đáp ứng đề và thực hành xử lý schema/Delta trên Fabric.

## Slide 3 — Kiến trúc: sáu hoạt động, ba tầng dữ liệu

**Thời lượng:** 55 giây.

**Trên slide:**
- Bronze: hai Copy CSV → Parquet.
- Silver: PySpark làm sạch → Delta sạch/cách ly.
- Gold: mô hình và ba bảng báo cáo.
- Acceptance: kiểm tra bảng đã ghi, xuất CSV và marker PASS.

**Hình minh họa:** Dùng ảnh thiết kế pipeline tại `submission/MINDX_Final_Project/diagrams/master_pipeline_design.png`. Ghi chú đây là sơ đồ thiết kế; dùng ảnh chạy Fabric thật ở slide 10.

**Lời trình bày:**

“Hai Copy Activity chạy độc lập và cùng nối vào Validate_Bronze. Notebook này chỉ chạy khi cả hai nguồn đã copy thành công. Sau đó, Silver, Gold và Acceptance chạy tuần tự theo dependency Succeeded. Mỗi batch có Run ID riêng để tách snapshot Bronze và báo cáo. Tuy nhiên, các bảng Silver và Gold có tên cố định và dùng full overwrite. Kiến trúc này cho phép truy lại dữ liệu đầu vào của một batch, đồng thời giữ bộ bảng hiện hành phục vụ phân tích.”

**Chuyển ý:** “Tầng đầu tiên ưu tiên giữ nguyên dữ liệu, kể cả dữ liệu lỗi.”

## Slide 4 — Bronze: bảo toàn dữ liệu trước khi làm sạch

**Thời lượng:** 60 giây.

**Trên slide:**
- Giữ toàn bộ cột ở kiểu String; không loại trùng.
- Parquet tại `Files/Bronze/<RunId>/…`.
- Kiểm tra schema, số dòng và nội dung hai chiều.
- `exceptAll` phát hiện cả việc mất dòng trùng.

**Hình minh họa:** Ví dụ nguồn A, A, B và đích A, B; gạch dấu lỗi “mất một dòng A”. Bên cạnh là đường dẫn Bronze của một run.

**Lời trình bày:**

“Ở Bronze, em không chuyển tuổi thành số hay bỏ dấu đô la, vì suy luận kiểu quá sớm có thể biến dữ liệu lỗi thành null. Hai Copy chỉ đổi định dạng CSV sang Parquet, giữ nguyên cột và giá trị. Sau đó Validate_Bronze đọc lại CSV để đối chiếu. Em dùng exceptAll hai chiều, thay vì chỉ so các giá trị distinct, vì cần giữ cả số lần xuất hiện của bản ghi. Nếu nguồn có hai dòng giống nhau mà đích chỉ còn một, bước kiểm tra vẫn phải phát hiện.”

**Câu hỏi có thể gặp:** “Đổi định dạng có còn nguyên trạng?” — Giá trị/cấu trúc và số dòng được bảo toàn; không yêu cầu CSV và Parquet giống byte.

## Slide 5 — Silver: sửa được thì chuẩn hóa, chưa biết đúng thì cách ly

**Thời lượng:** 75 giây.

**Trên slide:**
- Parse ngày/JSON, chuẩn hóa tiền và thanh toán.
- Tuổi/email thiếu: giữ null khi không cản trở chỉ số.
- Phí vận chuyển âm: cách ly, không tự sửa thành 0.
- Đối soát: **5.250 = 250 trùng + 104 cách ly + 4.896 sạch**.

**Hình minh họa:** Luồng dữ liệu tách thành sạch và quarantine; bên dưới có `error_reason`, `raw_record`. Có thể thêm bảng ba ví dụ trước/sau ngắn.

**Lời trình bày:**

“Silver phân biệt lỗi có quy tắc sửa rõ với lỗi không có căn cứ để tự sửa. Ví dụ, twenty được đổi thành 20; các cách viết Credit Card được chuẩn hóa; JSON được tách thành cấu trúc có kiểu. Email thiếu không làm mất khả năng tính doanh thu nên vẫn giữ null. Ngược lại, em không biết phí vận chuyển âm phải sửa thành bao nhiêu, nên cách ly đơn và lưu lý do. Sau khi bỏ 250 dòng trùng và cách ly 104 đơn, còn 4.896 đơn sạch. Failed hoặc feedback 99 vẫn có thể được lưu Silver, nhưng bị gắn report_eligible=false để không vào báo cáo cuối.”

**Câu hỏi có thể gặp:** “Sao giữ Failed?” — Silver phục vụ kiểm toán; điều kiện báo cáo được áp dụng rõ ràng bằng cờ và khi tạo aggregate.

## Slide 6 — Mô hình Gold: tách cấp đơn và cấp sản phẩm

**Thời lượng:** 65 giây.

**Trên slide:**
- `fact_orders`: một dòng = một đơn — 4.896 dòng.
- `fact_order_items`: một dòng = một item — 9.850 dòng.
- Năm dimension: Date, Customer, Location, Payment, Product.
- Product key dùng `(product_id, category)`.

**Hình minh họa:** Dùng `deliverables/docs/erd.png`. Tô nổi hai fact và nhãn grain. Nếu chữ nhỏ, chia thành ERD tổng quan và phóng to vùng fact.

**Lời trình bày:**

“Điểm quan trọng của mô hình là grain, tức một dòng đại diện cho cái gì. Một đơn có nhiều sản phẩm nên em tách fact_orders và fact_order_items. Fact đơn phù hợp đếm đơn và phân tích mã giảm giá; fact dòng sản phẩm phù hợp phân tích danh mục. Mô hình có hai nhánh fact và dimension, không phải một star đơn chỉ có một fact. Mã sản phẩm trong nguồn không xác định duy nhất danh mục, nên khóa kỹ thuật sản phẩm dùng cả mã và danh mục. Các quan hệ được kiểm tra bằng code, không mặc định Lakehouse tự cưỡng chế khóa ngoại.”

**Câu hỏi có thể gặp:** “4.896 customer có phải người thật?” — Chỉ là 4.896 hồ sơ phân biệt theo tên/email/điện thoại; thiếu customer_id ổn định.

## Slide 7 — Tránh sai doanh thu khi một đơn có nhiều sản phẩm

**Thời lượng:** 75 giây.

**Trên slide:**
- Không cộng lặp `total_amount` sau khi bung items.
- Phân bổ tiền đơn theo tỷ trọng `price × quantity`.
- Gán phần dư làm tròn vào dòng cuối.
- Quy đổi bằng tỷ giá đúng tháng của đơn.

**Hình minh họa:** Bảng ví dụ thật TXN-103535, đơn ngày 31/08/2025:

| Danh mục | Tiền hàng USD | Tiền phân bổ USD | VNĐ, rate = 25.440 |
|---|---:|---:|---:|
| Clothing | 150,93 | 153,55 | 3.906.312,00 |
| Home & Kitchen | 758,54 | 771,69 | 19.631.793,60 |
| Tổng | 909,47 | **925,24** | **23.538.105,60** |

**Lời trình bày:**

“Đây là một đơn thật trong CSV. Hai dòng sản phẩm có tiền hàng lần lượt 150,93 và 758,54 USD, nhưng tổng tiền đơn là 925,24 USD. Nếu sau khi bung items em cộng tổng tiền đơn trên mỗi dòng, đơn sẽ bị tính hai lần. Vì vậy, em phân bổ 925,24 USD theo tỷ trọng tiền hàng, được 153,55 và 771,69 USD. Tổng hai khoản phải khớp chính xác tổng tiền đơn; phần dư làm tròn được gán vào dòng cuối. Sau đó, từng dòng nhân tỷ giá tháng 8/2025 là 25.440 để tổng hợp theo danh mục.”

**Câu hỏi có thể gặp:** “Sao không cộng shipping?” — Nguồn không đảm bảo total_amount bằng tiền hàng cộng shipping; bài chọn total_amount làm tổng kiểm soát và không cộng phí lần nữa.

## Slide 8 — Định nghĩa doanh thu quyết định cách đọc kết quả

**Thời lượng:** 50 giây.

**Trên slide:**
- Tập theo đề: khác Failed, feedback 1–5 → **2.669 đơn**.
- Doanh thu tập theo đề: **68,13 tỷ VNĐ**.
- Tập Completed đủ điều kiện: **885 đơn**, **22,44 tỷ VNĐ**.
- Hai định nghĩa khác nhau; không gọi tất cả là tiền đã thu.

**Hình minh họa:** Hai cột cùng đơn vị tỷ VNĐ: 68,13 và 22,44. Ghi rõ số tiền trên slide được làm tròn; số chính xác ở JSON/báo cáo.

**Lời trình bày:**

“Em giữ một báo cáo theo điều kiện nguyên văn của đề. Điều kiện này loại Failed và feedback không hợp lệ, nhưng vẫn có thể giữ Pending hoặc Refunded. Vì vậy, em bổ sung báo cáo chỉ Completed để người đọc phân biệt. Tổng theo đề khoảng 68,13 tỷ, còn Completed khoảng 22,44 tỷ đồng. Sự khác biệt thể hiện vai trò của định nghĩa nghiệp vụ. Em không gọi các số này là lợi nhuận hoặc doanh thu thuần sau hoàn tiền vì nguồn không có đủ dữ liệu chi phí và hoàn trả.”

**Chuyển ý:** “Báo cáo khuyến mãi cũng cần xác định đúng đơn vị đếm.”

## Slide 9 — Khuyến mãi: đo tỷ lệ sử dụng mã, tránh đếm lặp

**Thời lượng:** 50 giây.

**Trên slide:**
- Nhóm theo `location`, tính trên fact đơn đã lọc.
- Tỷ lệ = đơn có mã / tổng đơn hợp lệ × 100.
- Một đơn nhiều sản phẩm vẫn chỉ đếm một lần.
- Đọc phần trăm cùng số đơn; chưa kết luận tác động nhân quả.

**Hình minh họa:** Ví dụ **minh họa công thức**, không phải kết quả thực tế: 3/10 đơn dùng mã = 30%. Bên cạnh ghi “Báo cáo thực tế: 2.425 địa điểm”. Không gắn địa điểm thật hay tỷ lệ cụ thể khi chưa tải CSV Gold tương ứng.

**Lời trình bày:**

“Báo cáo khuyến mãi dùng fact_orders để tránh một đơn có nhiều sản phẩm bị đếm nhiều lần. Với từng địa điểm, em lấy số đơn có mã không rỗng chia tổng đơn đủ điều kiện. Ví dụ minh họa, ba trên mười đơn tương ứng 30%. Báo cáo thực tế có 2.425 địa điểm trên 2.669 đơn đủ điều kiện, nên mẫu theo địa điểm khá nhỏ. Một tỷ lệ cao chưa chắc có ý nghĩa nếu chỉ có một hoặc hai đơn. Chỉ số này đo việc sử dụng mã, chưa chứng minh mã làm tăng doanh thu.”

## Slide 10 — Nghiệm thu: không chỉ pipeline xanh mà số liệu phải khớp

**Thời lượng:** 60 giây.

**Trên slide:**
- Cả **6 activity Succeeded**, Acceptance **PASS**.
- **15 Delta Tables**; kiểm tra khóa và quan hệ.
- Đối soát số dòng, tiền từng đơn và tổng VNĐ.
- Reports có Run ID và marker cuối để truy vết.

**Hình minh họa:** Chèn ảnh chụp Fabric thật bạn đã gửi: sơ đồ pipeline cùng bảng sáu activity Succeeded. Thêm một khung JSON rút gọn: status, run_id, eligible_orders, revenue_vnd. Không đưa toàn bộ JSON hoặc ảnh chữ quá nhỏ lên slide.

**Lời trình bày:**

“Bằng chứng chính là lần chạy thực tế trên Fabric với cả sáu activity thành công. Acceptance đọc lại các bảng đã ghi để kiểm tra, không chỉ dựa vào biến trong Gold. Nó đối soát số đơn và dòng sản phẩm giữa Silver và fact, kiểm tra khóa/quan hệ, tổng phân bổ từng đơn, doanh thu quy đổi và số đơn khuyến mãi. Sau khi các kiểm tra qua, notebook xuất CSV và ghi marker PASS cuối cùng. Run ID cho phép tìm đúng thư mục đầu vào và báo cáo của lần chạy này.”

**Dữ kiện để trả lời khi được hỏi:** Run ID `46d7ce91-000d-4f37-a118-719fa2b51b3c`; hoàn tất 06/11/2026, khoảng 12:14 giờ Việt Nam. Số tiền chính xác: 68.128.580.695,61 VNĐ và 22.440.017.306,84 VNĐ.

## Slide 11 — Vấn đề vận hành thực tế: Spark capacity

**Thời lượng:** 40 giây.

**Trên slide:**
- Gold từng lỗi trước khi tạo Livy session.
- `TooManyRequestsForCapacity` — HTTP 430.
- Kiểm tra session, bật High concurrency cho pipeline.
- Cùng Session tag `mindx_final`; lần chạy sau thành công.

**Hình minh họa:** Một khung trích thông báo lỗi và một khung cấu hình Session tag. Chỉ dùng ảnh cấu hình thật nếu có; không dựng ảnh giả giao diện. Giữ slide gọn, không dán toàn bộ stack trace.

**Lời trình bày:**

“Một lỗi thực tế là Gold chưa tạo được Livy session vì chạm giới hạn Spark compute. Em phân biệt lỗi tài nguyên này với lỗi công thức hoặc dữ liệu. Em kiểm tra cấu hình chia sẻ phiên, dùng cùng session tag và cùng Lakehouse/runtime cho bốn notebook. Sau đó pipeline chạy thành công. Tuy nhiên, session sharing không tăng quota, và mức tải capacity dùng chung có thể thay đổi, nên em không khẳng định riêng một thay đổi là nguyên nhân duy nhất.”

## Slide 12 — Giá trị đạt được và bước phát triển tiếp

**Thời lượng:** 35 giây.

**Trên slide:**
- Pipeline có dữ liệu sạch/cách ly, mô hình và báo cáo được đối soát.
- Quy tắc rõ ràng, truy vết theo run, kiểm tra trước công bố.
- Hiện là full snapshot overwrite; chưa incremental/SCD/BI dashboard.
- Hướng tiếp: audit theo run, staging/publish, incremental và semantic model.

**Hình minh họa:** Hai cột “Đã triển khai” và “Phát triển tiếp”. Không đưa tính năng chưa làm vào cột hoàn thành.

**Lời trình bày:**

“Kết quả chính của project là một pipeline Fabric đã chạy thành công, có quy tắc làm sạch giải thích được và các chỉ số được kiểm tra. Phạm vi hiện tại là batch full snapshot; em chưa triển khai incremental, SCD hay dashboard BI. Nếu phát triển tiếp, em sẽ ưu tiên audit theo run và cơ chế staging/publish để hạn chế các bảng bị trộn snapshot khi batch lỗi, sau đó mới mở rộng incremental và semantic model. Em xin kết thúc phần trình bày và nhận câu hỏi.”

## Phụ lục — Slide dự phòng cho hỏi đáp

Không cần trình bày tất cả; để cuối deck và mở khi được hỏi.

### Dự phòng A — Danh sách 15 bảng

Chia thành 5 Silver + 5 dimension + 2 fact + 3 aggregate. Dùng bảng thống kê trong JSON nghiệm thu. Đừng đưa 15 bảng cùng toàn bộ schema vào slide chính.

### Dự phòng B — Điều kiện report_eligible

Hiển thị `order_status != Failed AND feedback_score BETWEEN 1 AND 5`, null→false. Giải thích Failed/feedback lỗi có thể vẫn giữ Silver, nhưng không vào aggregate. 4.896 đơn sạch không đồng nghĩa tất cả được tính doanh thu.

### Dự phòng C — Ví dụ tiền làm tròn

Ví dụ minh họa một đơn 100 USD chia ba phần bằng nhau: 33,33 + 33,33 + 33,33 = 99,99; residual 0,01 được gán dòng cuối để khớp 100,00. Đây là ví dụ minh họa cơ chế, không phải dữ liệu đơn cụ thể trong nguồn.

### Dự phòng D — Chạy lại và giới hạn

Bronze có folder mới theo Run ID; Silver/Gold overwrite, không append lặp. Có bằng chứng một run Fabric thành công; chưa lưu bằng chứng run Fabric thứ hai toàn bộ thành công. Không nhận là đã chứng minh chạy lại trên dịch vụ nếu chưa bổ sung kết quả.

### Dự phòng E — Truy vấn demo

Chuẩn bị trước bốn truy vấn chỉ đọc: quarantine theo error_reason; fact theo report_eligible/status; doanh thu theo tháng/danh mục; khuyến mãi sắp theo total_orders. Truy vấn có sẵn ở mục 14 của tài liệu defense guide.

## Danh sách hình và số liệu cần chuẩn bị

| Tài nguyên | Nguồn | Dùng cho |
|---|---|---|
| ERD | deliverables/docs/erd.png | Slide 6 |
| Sơ đồ pipeline thiết kế | submission/MINDX_Final_Project/diagrams/master_pipeline_design.png | Slide 3 |
| Ảnh pipeline Fabric thật | Ảnh bạn đã chụp, lưu vào diagrams/master_pipeline_fabric.png nếu dùng bộ submission | Slide 10 |
| JSON PASS | submission/MINDX_Final_Project/evidence/fabric_acceptance.json | Slide 10, dự phòng A |
| Ví dụ TXN-103535 | CSV nguồn và defense guide mục 10 | Slide 7 |
| Bảng Gold theo tháng/địa điểm | CSV xuất từ Files/Reports/<run_id>/ | Biểu đồ chi tiết nếu muốn bổ sung |

## Nguyên tắc dựng và tập nói

- Mỗi slide chính chỉ giữ 3–4 ý; speaker notes để riêng.
- Thống nhất màu Bronze/Silver/Gold, font đủ lớn, tiền có đơn vị.
- Dùng dấu phẩy thập phân và dấu chấm phân cách hàng nghìn nhất quán. Khi ghi tỷ VNĐ, chú thích đã làm tròn.
- Không dùng biểu đồ theo địa điểm/danh mục nếu chưa có số liệu tương ứng để kiểm tra.
- Chuẩn bị ảnh chạy thành công để demo khi trial/capacity không sẵn sàng; không phụ thuộc hoàn toàn live demo.
- Luôn phân biệt dữ kiện thực tế, ví dụ minh họa và tính năng dự kiến.
- Tập nói ít nhất một lần với đồng hồ; nếu quá giờ, rút lời ở slide 2/4/11, giữ phần grain, doanh thu và Acceptance.
- Không nói project có incremental, SCD, dashboard Power BI, khóa ngoại tự cưỡng chế hoặc transaction chung 15 bảng.
