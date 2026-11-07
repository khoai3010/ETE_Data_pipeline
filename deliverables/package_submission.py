"""Build the submission folder and ZIP. Requires matplotlib and python-docx."""
from pathlib import Path
from decimal import Decimal
import hashlib
import json
import os
import shutil
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'deliverables'
OUT = ROOT / 'submission' / 'MINDX_Final_Project'
AUTHOR = 'Bùi Quang Khánh'
os.environ.setdefault('MPLCONFIGDIR', tempfile.mkdtemp(prefix='mindx-plot-'))

def money(value):
    return f'{Decimal(value):,.2f}'.replace(',', '_').replace('.', ',').replace('_', '.') + ' VNĐ'

def pipeline_image(path):
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.patches import FancyBboxPatch
    fig, ax = plt.subplots(figsize=(16, 4.6))
    ax.axis('off'); ax.set(xlim=(0, 1), ylim=(0, 1))
    def box(x, y, w, h, title, body):
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=0.008',facecolor='#edf4fc',edgecolor='#245882'))
        ax.text(x+w/2,y+h*.69,title,ha='center',va='center',weight='bold',fontsize=11)
        ax.text(x+w/2,y+h*.28,body,ha='center',va='center',fontsize=9)
    def arrow(start, end):
        ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','lw':1.5,'color':'#38556e'})
    box(.01,.64,.17,.23,'Copy_Sales','CSV to Parquet')
    box(.01,.16,.17,.23,'Copy_Exchange','CSV to Parquet')
    for x,title,body in [(.25,'Validate_Bronze','Schema and source checks'),(.45,'Silver','Cleaning and quarantine'),
                         (.65,'Gold','Model and business reports'),(.85,'Acceptance','Validation and CSV export')]:
        box(x,.39,.14,.27,title,body.replace(' and ','\nand '))
    arrow((.18,.75),(.25,.58)); arrow((.18,.27),(.25,.46))
    for x in [.39,.59,.79]: arrow((x,.525),(x+.06,.525))
    ax.set_title('MINDX-Mart | Master pipeline design',fontsize=17,pad=18)
    ax.text(.5,.035,'Design diagram, not a Fabric UI screenshot. All dependencies: Succeeded. Shared session tag: mindx_final.',ha='center',fontsize=10)
    fig.savefig(path,dpi=200,bbox_inches='tight'); plt.close(fig)

def build_report(acceptance):
    from docx import Document
    from docx.shared import Inches, Pt
    doc = Document()
    section = doc.sections[0]
    section.top_margin=Inches(.7); section.bottom_margin=Inches(.7)
    normal=doc.styles['Normal']; normal.font.name='Arial'; normal.font.size=Pt(10)
    normal.paragraph_format.space_after=Pt(6)
    doc.add_heading('FINAL PROJECT — DATA ENGINEERING LEVEL 3',0)
    doc.add_paragraph('MINDX-Mart: End-to-End Data Pipeline trên Microsoft Fabric',style='Subtitle')
    doc.add_paragraph('Họ và tên: '+AUTHOR)
    doc.add_paragraph('Ngày hoàn thành pipeline: 06/11/2026. Báo cáo dựa trên kết quả nghiệm thu Fabric của lần chạy thành công được đính kèm.')
    doc.add_heading('1. Mục tiêu và phạm vi',1)
    doc.add_paragraph('Xây dựng pipeline tự động cho dữ liệu bán lẻ 2024–2025 theo kiến trúc Medallion. Bronze dùng Data Factory Copy Activity để chuyển hai CSV thành Parquet; Silver dùng PySpark làm sạch và cách ly dữ liệu lỗi vào Delta Tables; Gold xây mô hình dữ liệu và báo cáo doanh thu VNĐ, tỷ lệ sử dụng mã khuyến mãi theo địa điểm.')
    doc.add_paragraph('Đầu vào: mindx_raw_sales_data.csv gồm 5.250 dòng và 15 cột; exchange_rate_2425.csv gồm 24 dòng tỷ giá USD→VND theo tháng. Dữ liệu có JSON lồng nhau, định dạng ngày hỗn hợp, giá trị thiếu, dòng trùng và các lỗi có chủ ý.')
    doc.add_heading('2. Kiến trúc và master pipeline',1)
    doc.add_picture(str(OUT/'diagrams/master_pipeline_design.png'),width=Inches(6.4))
    doc.add_paragraph('Hình 1. Sơ đồ thiết kế pipeline; đây là hình mô tả kiến trúc, không phải ảnh chụp giao diện Fabric.',style='Caption')
    doc.add_paragraph('Hai Copy chạy độc lập. Validate_Bronze chỉ chạy khi cả hai Copy Succeeded; tiếp theo là Silver → Gold → Acceptance. Mỗi lần chạy ghi Bronze riêng ở Files/Bronze/<PipelineRunId>/sales và exchange_rate. Cả bốn Notebook Activity nhận cùng run_id từ @pipeline().RunId. Lakehouse mặc định là lh_mindx_final, schema dbo.')
    doc.add_paragraph('Bronze giữ toàn bộ cột ở kiểu String. Validate_Bronze so sánh schema, số dòng và exceptAll hai chiều với CSV gốc để kiểm tra cả nội dung lẫn số lần lặp. Silver/Gold được ghi full overwrite. Chỉ dùng báo cáo khi Acceptance Succeeded và marker cuối có status=PASS.')
    doc.add_heading('3. Quy tắc Silver và quyết định chất lượng',1)
    rules=[
      'Loại bản ghi trùng hoàn toàn; nếu một order_id có nội dung xung đột thì cách ly các phiên bản thay vì chọn ngẫu nhiên.',
      'Parse ngày theo ISO và dd/MM/yyyy HH:mm; parse customer_info và mảng items bằng schema tường minh; giữ nguyên vị trí item_index khi bung mảng.',
      'Chuyển tuổi twenty/thirty-five thành 20/35; tuổi không hợp lệ để null. Email thiếu giữ null; thiết bị thiếu gán Unknown.',
      'Chuẩn hóa ba cách viết Credit Card; bỏ ký tự $ ở tổng tiền và dùng Decimal để xử lý tài chính.',
      'Cách ly phí vận chuyển âm hoặc các trường bắt buộc không hợp lệ; giữ error_reason và raw_record để giải thích lỗi.',
      'Failed và feedback thiếu/99 vẫn có thể được giữ ở Silver phục vụ kiểm toán, nhưng report_eligible=false nên không vào chỉ số cuối.',
      'Tỷ giá phải có khóa năm/tháng/cặp tiền duy nhất, USD→VND, giá trị dương. Thiếu tỷ giá cho đơn hợp lệ làm Gold dừng, không thay bằng tỷ giá mặc định.'
    ]
    for text in rules:doc.add_paragraph(text,style='List Bullet')
    doc.add_paragraph('Đối soát nguồn: 5.250 = 250 dòng trùng bị loại + 104 đơn cách ly do shipping_cost âm + 4.896 đơn Silver. Có 9.850 dòng sản phẩm sau xử lý; bảng tỷ giá sạch có 24 dòng, quarantine tỷ giá rỗng. Không loại đơn chỉ vì thiếu thuộc tính không bắt buộc như email hoặc tuổi.')
    doc.add_heading('4. Mô hình Gold và ERD',1)
    doc.add_picture(str(OUT/'diagrams/erd.png'),width=Inches(6.1))
    doc.add_paragraph('Hình 2. Mô hình Gold với hai fact dùng chung dimension; PK/FK thể hiện trên sơ đồ.',style='Caption')
    doc.add_paragraph('fact_orders có grain một đơn hàng; fact_order_items có grain một dòng sản phẩm nguồn, khóa (order_id, item_index). Các dimension gồm ngày, hồ sơ khách hàng, địa điểm, phương thức thanh toán và sản phẩm. Hai fact dùng chung dimension ngày; item fact liên hệ tới đơn qua order_id. Mô hình hai fact giúp tách phép đếm đơn và phép cộng tiền sản phẩm.')
    doc.add_paragraph('Mã sản phẩm trong dữ liệu có thể xuất hiện ở nhiều danh mục; product_key được tạo từ (product_id, category). Không có customer_id ổn định nên customer_key là hash(name, email, phone), chỉ đại diện hồ sơ nguồn. Dimension ngày bao phủ 731 ngày từ 01/01/2024 đến 31/12/2025. Các quan hệ được notebook kiểm tra bằng phép đối chiếu khóa; không tuyên bố Lakehouse tự cưỡng chế PK/FK.')
    doc.add_heading('5. Công thức chỉ số và tránh đếm lặp',1)
    doc.add_paragraph('Tập theo điều kiện đề: đơn Silver hợp lệ, order_status khác Failed và feedback_score trong 1–5. Feedback null cũng bị loại khỏi tập báo cáo. Vì điều kiện nguyên văn vẫn bao gồm Pending/Refunded, có thêm báo cáo chỉ Completed để người đọc phân biệt doanh thu của đơn hoàn tất; không coi toàn bộ tập theo đề là tiền thực thu.')
    for text in [
      'line_subtotal_usd = price × quantity.',
      'allocated_revenue_usd = total_amount_usd × line_subtotal_usd / tổng line_subtotal_usd của đơn; làm tròn cent, gán phần dư vào dòng cuối để tổng phân bổ khớp chính xác total_amount_usd.',
      'allocated_revenue_vnd = allocated_revenue_usd × exchange_rate, join theo năm/tháng/currency của ngày đơn. Tổng hợp theo năm, tháng và category.',
      'discount_order_pct = số đơn có discount_code không rỗng / tổng số đơn đủ điều kiện × 100, nhóm theo location. Tính từ fact_orders để không đếm lặp đơn nhiều sản phẩm.'
    ]:doc.add_paragraph(text,style='List Bullet')
    doc.add_paragraph('Không cộng total_amount lặp lại sau khi bung items; không cộng shipping_cost thêm lần nữa. Nguồn không có số tiền giảm giá nên không tự trừ tiền từ discount_code. Không ép total_amount bằng tổng sản phẩm cộng shipping_cost vì dữ liệu nguồn không đảm bảo đẳng thức đó.')
    doc.add_paragraph('Ba bảng báo cáo: gold_monthly_revenue_category; gold_monthly_completed_revenue_category; gold_promotion_by_location. Mỗi bảng doanh thu có 120 nhóm tháng/danh mục; bảng khuyến mãi có 2.425 địa điểm.')
    doc.add_heading('6. Kết quả nghiệm thu thực tế trên Fabric',1)
    rows=[('Trạng thái','PASS; sáu activity Succeeded theo ảnh chạy người dùng cung cấp'),('Engine / Spark','Fabric PySpark / '+acceptance['spark_version']),
       ('Run ID',acceptance['run_id']),('Đơn Silver','4.896'),('Đơn cách ly','104'),('Dòng sản phẩm Silver','9.850'),
       ('Tỷ giá / quarantine tỷ giá','24 / 0'),('Tổng bảng','15'),('Đơn đủ điều kiện / Completed','2.669 / 885'),
       ('Doanh thu tập theo đề',money(acceptance['revenue_vnd'])),('Doanh thu Completed',money(acceptance['completed_revenue_vnd']))]
    table=doc.add_table(rows=1,cols=2); table.style='Light Shading Accent 1'
    table.rows[0].cells[0].text='Chỉ số';table.rows[0].cells[1].text='Kết quả'
    for label,value in rows:
        cells=table.add_row().cells;cells[0].text=label;cells[1].text=value
    doc.add_paragraph('Acceptance kiểm tra số dòng, khóa/quan hệ, điều kiện loại Failed/feedback lỗi, tổng phân bổ từng đơn và đối soát doanh thu, sau đó xuất ba báo cáo CSV và marker PASS. Kết quả nằm tại Files/Reports/'+acceptance['run_id']+'/. JSON trong evidence được lưu từ nội dung người dùng cung cấp; không phải dữ liệu do script đóng gói truy vấn lại dịch vụ.')
    screenshot=OUT/'diagrams/master_pipeline_fabric.png'
    if screenshot.exists():
        doc.add_picture(str(screenshot),width=Inches(6.4));doc.add_paragraph('Hình 3. Ảnh pipeline Fabric do học viên bổ sung.',style='Caption')
    else:
        doc.add_paragraph('Ảnh pipeline thực tế đã được người dùng cung cấp trong cuộc trò chuyện nhưng chưa lưu thành file trong project. Bộ hiện tại kèm sơ đồ thiết kế và JSON nghiệm thu; nên bổ sung ảnh chụp gốc vào diagrams/master_pipeline_fabric.png để tăng bằng chứng trình bày.')
    doc.add_heading('7. Nhận xét và giới hạn',1)
    doc.add_paragraph('Sự khác biệt lớn giữa tổng theo điều kiện đề và tổng Completed cho thấy cần định nghĩa trạng thái đơn khi diễn giải doanh thu. 2.425 địa điểm chỉ có 2.669 đơn đủ điều kiện, nên mẫu theo từng địa điểm rất nhỏ; tỷ lệ dùng mã phải được đọc cùng số đơn. Không kết luận tác động nhân quả của khuyến mãi hoặc lợi nhuận khi thiếu số tiền giảm giá, chi phí chiến dịch và nhóm đối chứng.')
    doc.add_paragraph('Dữ liệu là giả lập; không có danh tính khách hàng ổn định hoặc thông tin hoàn tiền để tính net revenue. Batch hiện tại là full snapshot, không phải incremental/SCD. Không có transaction chung cho 15 bảng: nếu pipeline lỗi giữa chừng thì không công bố kết quả đang ghi dở, cần sửa lỗi rồi chạy lại theo luồng kiểm tra.')
    doc.add_paragraph('Một lần chạy Fabric thành công được chứng minh bởi ảnh và JSON người dùng cung cấp. Khả năng chạy lại đã được kiểm tra cục bộ trước đó, nhưng chưa có bằng chứng một lần chạy lại toàn bộ Fabric thành công được lưu trong bộ này.')
    doc.add_heading('8. Xử lý giới hạn tài nguyên và tái lập',1)
    doc.add_paragraph('Lần đầu Gold gặp TooManyRequestsForCapacity (HTTP 430) trước khi tạo được Livy session. Workspace đã bật High concurrency cho pipeline; bốn Notebook Activity dùng cùng Session tag mindx_final, default Lakehouse/runtime và chạy tuần tự. Lần chạy được đính kèm sau đó đã thành công. Session sharing giúp tái sử dụng phiên, không làm tăng quota của capacity.')
    doc.add_paragraph('Để tái lập: upload hai CSV vào Files/Source, import bốn notebook, gắn Lakehouse, dựng hai Copy và nối bốn Notebook Activity theo setup/pipeline_configuration.md. Mọi activity notebook nhận cùng @pipeline().RunId; report_eligible và các assertion được giữ nguyên. Chi tiết nguồn, folder và schema có trong setup/config.json. Notebook 01 kiểm tra Bronze, không thay thế Data Factory Copy Activity.')
    footer=section.footer.paragraphs[0];footer.text='Bùi Quang Khánh | MINDX-Mart — Data Engineering Level 3'
    doc.save(OUT/'report.docx')

def main():
    for folder in ['notebooks','diagrams','data','evidence','setup']:(OUT/folder).mkdir(parents=True,exist_ok=True)
    acceptance_path=next((SOURCE/'reports/fabric').glob('acceptance_*.json'))
    acceptance=json.loads(acceptance_path.read_text(encoding='utf-8'))
    assert acceptance['status']=='PASS'
    copied=[]
    for source in sorted((SOURCE/'fabric/prepared').glob('0[1-4]_*.ipynb')):
        target=OUT/'notebooks'/source.name;shutil.copyfile(source,target);copied.append((source,target))
        nb=json.loads(target.read_text(encoding='utf-8'));assert nb['nbformat']==4
    assert len(copied)==4
    for source in sorted((SOURCE/'fabric/prepared/inputs').glob('*.csv')):
        target=OUT/'data'/source.name;shutil.copyfile(source,target);copied.append((source,target))
    for source,target in [(SOURCE/'docs/erd.png',OUT/'diagrams/erd.png'),(acceptance_path,OUT/'evidence/fabric_acceptance.json'),
       (SOURCE/'fabric/config.json',OUT/'setup/config.json'),(SOURCE/'fabric/MANUAL_BINDINGS.md',OUT/'setup/pipeline_configuration.md')]:
        shutil.copyfile(source,target);copied.append((source,target))
    # The guide is relocated into the package: make its one local link self-contained.
    guide=OUT/'setup/pipeline_configuration.md'
    guide.write_text(guide.read_text(encoding='utf-8').replace('../reports/fabric/README.md','../evidence/fabric_acceptance.json'),encoding='utf-8')
    for source,target in copied:
        if target!=guide:assert hashlib.sha256(source.read_bytes()).digest()==hashlib.sha256(target.read_bytes()).digest()
    pipeline_image(OUT/'diagrams/master_pipeline_design.png')
    build_report(acceptance)
    screenshot=(OUT/'diagrams/master_pipeline_fabric.png').exists()
    readme=f'''# Final Project — Bùi Quang Khánh

Microsoft Fabric, kiến trúc Bronze → Silver → Gold. Run đã nghiệm thu: `{acceptance['run_id']}`; status PASS.

## Nội dung nộp

| Yêu cầu đề bài | File |
|---|---|
| Hình ảnh ERD | diagrams/erd.png |
| Hình ảnh thiết kế master pipeline | diagrams/master_pipeline_design.png |
| Notebook các layer | notebooks/01_bronze_validation.ipynb, 02_silver.ipynb, 03_gold.ipynb, 04_acceptance.ipynb |
| Báo cáo giải thích bài làm | report.docx |
| Kết quả nghiệm thu Fabric | evidence/fabric_acceptance.json |
| Dữ liệu để tái lập | data/*.csv |
| Cấu hình tái lập pipeline | setup/config.json, setup/pipeline_configuration.md |

Notebook 01 kiểm tra Bronze sau Data Factory Copy Activity; việc ingest CSV→Parquet thực hiện bằng hai Copy trong pipeline, không phải bằng notebook.

Các notebook là bản mã được dùng để import. Không chèn outputs giả vào notebook; để kèm outputs thực tế, có thể bổ sung bản export từ Fabric vào evidence/fabric_exports/. JSON nghiệm thu và ảnh chạy người dùng gửi xác nhận pipeline thành công.

Ảnh master_pipeline_design.png là sơ đồ thiết kế, không phải ảnh chụp giao diện Fabric. Ảnh pipeline thật trong chat {'đã có tại diagrams/master_pipeline_fabric.png' if screenshot else 'chưa lưu thành file trong bộ này; nên lưu vào diagrams/master_pipeline_fabric.png trước khi gửi bài'}. Khi bổ sung ảnh, chạy lại script đóng gói để báo cáo nhúng ảnh và ZIP được cập nhật.

## Chạy lại

Upload hai CSV vào Files/Source, import bốn notebook và gắn cùng default Lakehouse, cấu hình sáu activity theo setup/pipeline_configuration.md. Chạy toàn bộ pipeline, chỉ dùng kết quả sau Acceptance PASS. Giữ cùng run_id từ @pipeline().RunId và Session tag mindx_final. Không chạy đồng thời hai batch vì Silver/Gold dùng overwrite.

## Chỉ số đã xác nhận

15 bảng; 4.896 đơn Silver; 104 đơn cách ly; 9.850 dòng sản phẩm; 24 tỷ giá; 2.669 đơn đủ điều kiện; 885 Completed. Doanh thu tập theo đề: {money(acceptance['revenue_vnd'])}; doanh thu Completed: {money(acceptance['completed_revenue_vnd'])}.

Nguồn bằng chứng: JSON và ảnh Fabric do học viên cung cấp, không phải truy vấn dịch vụ trong lúc đóng gói. Thời điểm hoàn tất run: 06/11/2026 12:14:12 giờ Việt Nam. Một lần chạy lại toàn bộ Fabric thành công chưa được bổ sung bằng chứng.
'''
    (OUT/'README.md').write_text(readme,encoding='utf-8')
    manifest={str(p.relative_to(OUT)).replace('\\','/'):hashlib.sha256(p.read_bytes()).hexdigest()
              for p in sorted(OUT.rglob('*')) if p.is_file() and p.name!='SHA256SUMS.json'}
    (OUT/'SHA256SUMS.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    archive=OUT.parent/'MINDX_Final_Project.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for path in sorted(OUT.rglob('*')):
            if path.is_file():z.write(path,str(path.relative_to(OUT.parent)))
    print('Submission:',OUT)
    print('ZIP:',archive,'bytes:',archive.stat().st_size)
    print('Original Fabric screenshot included:',screenshot)

if __name__=='__main__':main()
