"""Local report PDF export with selectable text, tables and scientific figures."""
from pathlib import Path
import re
from html import escape
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,NextPageTemplate,PageBreak,Paragraph,Spacer,LongTable,TableStyle,Image
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]


def main():
    font=Path('C:/Windows/Fonts/segoeui.ttf');bold=Path('C:/Windows/Fonts/segoeuib.ttf')
    if not font.is_file():
        font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf')
        bold=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf')
    if not font.is_file() or not bold.is_file():
        raise RuntimeError('Install Segoe UI (Windows) or DejaVu Sans (Linux) to regenerate the PDF. The existing PDF is included.')
    pdfmetrics.registerFont(TTFont('Segoe',str(font)));pdfmetrics.registerFont(TTFont('SegoeBold',str(bold)))
    pdfmetrics.registerFontFamily('Segoe',normal='Segoe',bold='SegoeBold',italic='Segoe',boldItalic='SegoeBold')
    source=ROOT/'reports/PHISHARK2026_RAPPORT_FINAL.md';target=source.with_suffix('.pdf')
    styles=getSampleStyleSheet()
    for style in styles.byName.values():style.fontName='Segoe';style.leading=14;style.fontSize=9.5
    styles['Title'].fontName='SegoeBold';styles['Title'].fontSize=24;styles['Title'].leading=30
    for name,size in [('Heading1',17),('Heading2',13),('Heading3',11)]:
        styles[name].fontName='SegoeBold';styles[name].fontSize=size;styles[name].leading=size+5;styles[name].textColor=colors.HexColor('#10243C');styles[name].spaceBefore=13
    small=ParagraphStyle('TableCell',parent=styles['Normal'],fontSize=7,leading=9)
    def inline(text):
        text=escape(text)
        text=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',text)
        text=re.sub(r'`([^`]+)`',r'<font color="#149A91">\1</font>',text)
        text=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',text)
        return text
    width,height=A4;doc=BaseDocTemplate(str(target),pagesize=A4,leftMargin=44,rightMargin=44,topMargin=44,bottomMargin=44)
    def footer(canvas,document):
        canvas.setPageSize(landscape(A4) if document.pageTemplate.id=='wide' else A4)
        w,h=canvas._pagesize;canvas.setFont('Segoe',8);canvas.setFillColor(colors.HexColor('#52677C'))
        canvas.drawString(44,24,'PhiShark2026 · résultats FULL vérifiés · 24 novembre 2026');canvas.drawRightString(w-44,24,str(document.page))
    doc.addPageTemplates([PageTemplate(id='portrait',frames=[Frame(44,44,width-88,height-88,id='normal')],onPage=footer),
        PageTemplate(id='wide',pagesize=landscape(A4),frames=[Frame(38,38,height-76,width-76,id='large')],onPage=footer)])
    story=[];lines=source.read_text(encoding='utf-8').splitlines();i=0
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                values=[v.strip() for v in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',v or '-') for v in values):rows.append(values)
                i+=1
            wide=len(rows[0])>=10
            if wide:story.extend([NextPageTemplate('wide'),PageBreak()])
            usable=height-88 if wide else width-100;count=len(rows[0]);first=170 if wide else min(180,usable/count*2)
            widths=[first]+[(usable-first)/(count-1)]*(count-1) if count>1 else [usable]
            cells=[[Paragraph(inline(v.replace('_','_\u200b').replace('+','+\u200b')),small) for v in row] for row in rows]
            table=LongTable(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
            table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#DFEFED')),('VALIGN',(0,0),(-1,-1),'TOP'),
                ('GRID',(0,0),(-1,-1),.25,colors.HexColor('#CBD5E1')),('LEFTPADDING',(0,0),(-1,-1),5),('RIGHTPADDING',(0,0),(-1,-1),5),
                ('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4)]))
            story.extend([table,Spacer(1,12)])
            if wide:story.extend([NextPageTemplate('portrait'),PageBreak()])
            continue
        image=re.match(r'!\[(.*?)\]\((.*?)\)',line)
        if image:
            p=source.parent/image[2];obj=Image(str(p));scale=(width-110)/obj.imageWidth;obj.drawWidth=width-110;obj.drawHeight=obj.imageHeight*scale
            story.extend([obj,Paragraph(inline(image[1]),small),Spacer(1,14)]);i+=1;continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));story.append(Paragraph(inline(line[level:].strip()),styles['Title' if level==1 else 'Heading'+str(min(level-1,3))]));i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|','![')):
            paragraph.append(lines[i].strip());i+=1
        story.extend([Paragraph(inline(' '.join(paragraph)),styles['Normal']),Spacer(1,8)])
    doc.build(story);print(target)


if __name__=='__main__':main()
