"""Create readable Word editions of the defense guide and slide script."""
from pathlib import Path
import re
import zipfile
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.opc.constants import RELATIONSHIP_TYPE as RT

ROOT=Path(__file__).resolve().parent.parent
DOCS=ROOT/'deliverables/docs'
AUTHOR='Bùi Quang Khánh'

def inline(paragraph,text):
    pattern=r'(\*\*[^*]+\*\*|`[^`]+`|\[[^\]]+\]\([^)]+\))'
    for token in re.split(pattern,text):
        if not token:continue
        if token.startswith('**') and token.endswith('**'):
            paragraph.add_run(token[2:-2]).bold=True
        elif token.startswith('`') and token.endswith('`'):
            r=paragraph.add_run(token[1:-1]);r.font.name='Consolas';r.font.size=Pt(9)
        elif re.fullmatch(r'\[[^\]]+\]\([^)]+\)',token):
            label,url=re.match(r'\[([^\]]+)\]\(([^)]+)\)',token).groups()
            hyperlink=OxmlElement('w:hyperlink')
            hyperlink.set(qn('r:id'),paragraph.part.relate_to(url,RT.HYPERLINK,is_external=True))
            run=OxmlElement('w:r');props=OxmlElement('w:rPr');color=OxmlElement('w:color');color.set(qn('w:val'),'23618C');props.append(color)
            run.append(props);value=OxmlElement('w:t');value.text=label;run.append(value);hyperlink.append(run);paragraph._p.append(hyperlink)
        else:paragraph.add_run(token)

def shade(paragraph,color='F2F5F8'):
    shd=OxmlElement('w:shd');shd.set(qn('w:fill'),color);paragraph._p.get_or_add_pPr().append(shd)

def setup(title,subtitle,slides):
    doc=Document();section=doc.sections[0]
    section.page_width=Inches(8.27);section.page_height=Inches(11.69)
    section.top_margin=Inches(.7);section.bottom_margin=Inches(.65)
    section.left_margin=Inches(.75);section.right_margin=Inches(.75)
    normal=doc.styles['Normal'];normal.font.name='Arial';normal.font.size=Pt(11)
    normal.paragraph_format.line_spacing=1.15;normal.paragraph_format.space_after=Pt(7)
    for name,size in [('Title',27),('Subtitle',14),('Heading 1',17),('Heading 2',13),('Heading 3',11)]:
        style=doc.styles[name];style.font.name='Arial';style.font.size=Pt(size)
        if name.startswith('Heading'):style.font.color.rgb=RGBColor.from_string('194D70')
    doc.core_properties.author=AUTHOR;doc.core_properties.title=title
    doc.core_properties.subject='MINDX-Mart | Data Engineering Level 3 | Microsoft Fabric'
    doc.add_heading(title,0);doc.add_paragraph(subtitle,style='Subtitle')
    p=doc.add_paragraph();p.add_run('Họ và tên: ').bold=True;p.add_run(AUTHOR)
    doc.add_paragraph('Project: MINDX-Mart — Microsoft Fabric — Medallion Architecture')
    if slides:
        doc.add_paragraph('12 slide chính · khoảng 10–12 phút · có slide dự phòng và speaker notes')
        doc.add_paragraph('Cách dùng: lấy phần “Trên slide” để dựng PowerPoint; phần “Lời trình bày” để tập nói. Ví dụ minh họa và số liệu thực tế đã được phân biệt trong kịch bản.')
    else:
        doc.add_paragraph('Cách dùng: đọc theo thứ tự từ pipeline đến bảng và chỉ số; ôn các câu hỏi ở cuối; dùng Navigation Pane của Word để chuyển giữa các mục.')
        doc.add_paragraph('Tài liệu bám theo mã notebook và kết quả nghiệm thu. Các hướng cải tiến được tách khỏi tính năng đã triển khai.')
    footer=section.footer.paragraphs[0]
    footer.add_run(AUTHOR+' | MINDX-Mart | Trang ')
    field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');footer._p.append(field)
    doc.add_page_break()
    return doc

def table(doc,lines):
    rows=[[c.strip() for c in line.strip().strip('|').split('|')] for line in lines]
    rows=[r for r in rows if not all(re.fullmatch(r':?-+:?',c.replace(' ','')) for c in r)]
    width=len(rows[0]);t=doc.add_table(rows=0,cols=width);t.style='Light Shading Accent 1'
    for i,row in enumerate(rows):
        cells=t.add_row().cells
        for cell,text in zip(cells,row):
            p=cell.paragraphs[0];inline(p,text)
            for r in p.runs:r.font.size=Pt(9)
        if i==0:
            repeat=OxmlElement('w:tblHeader');t.rows[i]._tr.get_or_add_trPr().append(repeat)
            for cell in cells:
                for r in cell.paragraphs[0].runs:r.bold=True
    doc.add_paragraph()

def codeblock(doc,language,lines):
    if language=='mermaid':
        image=ROOT/'submission/MINDX_Final_Project/diagrams/master_pipeline_design.png'
        if image.exists():
            doc.add_picture(str(image),width=Inches(6.6));doc.add_paragraph('Sơ đồ thiết kế pipeline, không phải ảnh chụp giao diện Fabric.',style='Caption')
            return
    p=doc.add_paragraph();shade(p)
    for i,line in enumerate(lines):
        if i:p.add_run().add_break()
        run=p.add_run(line);run.font.name='Consolas';run.font.size=Pt(8.5)
    p.paragraph_format.space_before=Pt(5);p.paragraph_format.space_after=Pt(9)

def convert(source,destination,title,subtitle,slides=False):
    lines=source.read_text(encoding='utf-8').splitlines()
    doc=setup(title,subtitle,slides);i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('# '):i+=1;continue
        if line.startswith('```'):
            language=line[3:].strip();block=[];i+=1
            while i<len(lines) and not lines[i].strip().startswith('```'):
                block.append(lines[i]);i+=1
            codeblock(doc,language,block);i+=1;continue
        if line.startswith('|'):
            group=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                group.append(lines[i]);i+=1
            table(doc,group);continue
        heading=re.match(r'^(#{2,4})\s+(.+)$',line)
        if heading:
            level=len(heading.group(1))-1;text=heading.group(2)
            if slides and level==1 and (text.startswith('Slide ') or text.startswith('Phụ lục')):
                doc.add_page_break()
            doc.add_heading(text,level=level)
            if not slides and text.startswith('9. Toàn bộ'):
                doc.add_picture(str(DOCS/'erd.png'),width=Inches(6.3))
                doc.add_paragraph('ERD Gold — hai fact và các dimension.',style='Caption')
            i+=1;continue
        bullet=re.match(r'^[-*]\s+(.+)$',line)
        numbered=re.match(r'^\d+\.\s+(.+)$',line)
        if bullet:
            p=doc.add_paragraph(style='List Bullet');inline(p,bullet.group(1))
        elif numbered:
            p=doc.add_paragraph(style='List Number');inline(p,numbered.group(1))
        else:
            p=doc.add_paragraph();inline(p,line)
        i+=1
    doc.save(destination)
    with zipfile.ZipFile(destination) as z:assert z.testzip() is None
    print(destination.name,'paragraphs:',len(doc.paragraphs),'tables:',len(doc.tables),'images:',len(doc.inline_shapes))

if __name__=='__main__':
    convert(DOCS/'04_defense_guide.md',DOCS/'defense_guild.docx',
        'TÀI LIỆU ÔN BẢO VỆ PROJECT','Pipeline · Dữ liệu · Mô hình · Chỉ số · Log · Hỏi đáp')
    convert(DOCS/'05_slide_script.md',DOCS/'slide_presentation_script.docx',
        'KỊCH BẢN SLIDE THUYẾT TRÌNH','12 slide chính, lời trình bày và câu hỏi dự phòng',slides=True)
