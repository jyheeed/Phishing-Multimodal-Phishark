"""Readable scientific PDF from Markdown, with bookmarks, page numbers and an actual TOC."""
from pathlib import Path
import re,json
from html import escape
from reportlab.platypus import BaseDocTemplate,PageTemplate,Frame,Paragraph,Spacer,PageBreak,NextPageTemplate,LongTable,TableStyle,Image,KeepTogether
from reportlab.platypus.tableofcontents import TableOfContents
from reportlab.lib.pagesizes import A4,landscape
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
ROOT=Path(__file__).resolve().parents[1]

class ScientificDocument(BaseDocTemplate):
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and flowable.style.name in ('Chapter','Section'):
            text=flowable.getPlainText();level=0 if flowable.style.name=='Chapter' else 1
            key='section-'+str(self.seq.nextf('section'))
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(text,key,level,False)
            self.notify('TOCEntry',(level,text,self.page,key))

def main():
    font=Path('C:/Windows/Fonts/segoeui.ttf');bold=Path('C:/Windows/Fonts/segoeuib.ttf')
    if not font.is_file():font=Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf');bold=font.with_name('DejaVuSans-Bold.ttf')
    if not font.is_file() or not bold.is_file():raise RuntimeError('Segoe UI or DejaVu Sans required for PDF')
    pdfmetrics.registerFont(TTFont('Body',str(font)));pdfmetrics.registerFont(TTFont('BodyBold',str(bold)))
    pdfmetrics.registerFontFamily('Body',normal='Body',bold='BodyBold',italic='Body',boldItalic='BodyBold')
    styles=getSampleStyleSheet()
    normal=ParagraphStyle('Body',fontName='Body',fontSize=11,leading=16.2,spaceAfter=8,splitLongWords=True)
    title=ParagraphStyle('CoverTitle',parent=normal,fontName='BodyBold',fontSize=25,leading=33,textColor=colors.HexColor('#10243C'),spaceAfter=24)
    chapter=ParagraphStyle('Chapter',parent=normal,fontName='BodyBold',fontSize=18,leading=24,spaceBefore=4,spaceAfter=16,textColor=colors.HexColor('#10243C'),keepWithNext=True)
    section=ParagraphStyle('Section',parent=normal,fontName='BodyBold',fontSize=12.5,leading=17,spaceBefore=13,spaceAfter=8,textColor=colors.HexColor('#123F55'),keepWithNext=True)
    cell=ParagraphStyle('Cell',parent=normal,fontSize=7.8,leading=10,spaceAfter=0)
    cell_head=ParagraphStyle('CellHead',parent=cell,fontName='BodyBold',textColor=colors.HexColor('#10243C'))
    caption=ParagraphStyle('Caption',parent=normal,fontSize=8.4,leading=12,textColor=colors.HexColor('#42566B'),spaceAfter=12)
    table_caption=ParagraphStyle('TableCaption',parent=caption,keepWithNext=True)
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle('TOC0',parent=normal,fontSize=10,leading=14,spaceBefore=7),ParagraphStyle('TOC1',parent=normal,fontSize=8.5,leading=12,leftIndent=14,firstLineIndent=0,spaceBefore=2)]
    source=ROOT/'reports/PHISHARK2026_RAPPORT_FINAL.md';target=source.with_suffix('.pdf')
    w,h=A4;lw,lh=landscape(A4);margin=45
    doc=ScientificDocument(str(target),pagesize=A4,leftMargin=margin,rightMargin=margin,topMargin=47,bottomMargin=45,title='PhiShark2026 — Mémoire scientifique CRISP-DM',author='Projet académique PhiShark2026')
    def footer(canvas,document):
        wide=document.pageTemplate.id=='wide';pw,ph=landscape(A4) if wide else A4
        canvas.setPageSize((pw,ph));canvas.saveState();canvas.setFont('Body',8);canvas.setFillColor(colors.HexColor('#52677C'))
        canvas.drawString(margin,23,'PhiShark2026 · mémoire scientifique · résultats internes vérifiés')
        canvas.drawRightString(pw-margin,23,str(document.page));canvas.restoreState()
    doc.addPageTemplates([PageTemplate(id='portrait',pagesize=A4,frames=[Frame(margin,45,w-2*margin,h-92,id='body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer),PageTemplate(id='wide',pagesize=landscape(A4),frames=[Frame(margin,45,lw-2*margin,lh-92,id='wide_body',leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0)],onPage=footer)])
    def inline(text):
        text=escape(text)
        text=re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)',lambda m:'<link href="'+m[2].replace('&amp;','&')+'" color="#176B80">'+m[1]+'</link>',text)
        text=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'\1',text)
        text=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',text)
        text=re.sub(r'`([^`]+)`',r'<font color="#126A65">\1</font>',text)
        return text
    story=[];lines=source.read_text(encoding='utf8').splitlines();i=0;figures=0;tables=0
    def pagebreak():
        if story and not isinstance(story[-1],PageBreak):story.append(PageBreak())
    while i<len(lines):
        line=lines[i].strip()
        if not line:i+=1;continue
        if line.startswith('|'):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith('|'):
                values=[v.strip() for v in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?',v) for v in values):rows.append(values)
                i+=1
            n=len(rows[0]);wide=n>=12
            if wide:story.extend([NextPageTemplate('wide')]);pagebreak()
            usable=(lw if wide else w)-2*margin
            longest=max(len(row[0]) for row in rows)
            first=min(180,max(65,longest*3.8),usable*.39)
            if n==1:widths=[usable]
            elif rows[0][0] in ('model','case','modèle','feature','Étude','ID / RQ'):widths=[first]+[(usable-first)/(n-1)]*(n-1)
            else:widths=[usable/n]*n
            cells=[]
            for r,row in enumerate(rows):
                assert len(row)==n,(rows[0],row)
                cells.append([Paragraph(inline(value.replace('_','_\u200b').replace('+','+\u200b')),cell_head if r==0 else cell) for value in row])
            t=LongTable(cells,colWidths=widths,repeatRows=1,hAlign='LEFT')
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#E2EEEF')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F7F9FB')]),('VALIGN',(0,0),(-1,-1),'TOP'),('GRID',(0,0),(-1,-1),.25,colors.HexColor('#C9D3DE')),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5)]))
            story.extend([t,Spacer(1,12)]);tables+=1
            if wide:story.append(NextPageTemplate('portrait'));pagebreak()
            continue
        picture=re.fullmatch(r'!\[(.*?)\]\((.*?)\)',line)
        if picture:
            path=(source.parent/picture[2]).resolve()
            if not path.is_relative_to(ROOT):raise ValueError('Image outside workspace')
            obj=Image(str(path));scale=min((w-2*margin)/obj.imageWidth,350/obj.imageHeight)
            obj.drawWidth=obj.imageWidth*scale;obj.drawHeight=obj.imageHeight*scale
            story.append(KeepTogether([obj,Spacer(1,7),Paragraph(inline(picture[1]),caption)]));figures+=1;i+=1;continue
        if line.startswith('#'):
            level=len(line)-len(line.lstrip('#'));text=line[level:].strip()
            if level==1:
                story.extend([Spacer(1,60),Paragraph(inline(text),title)]);i+=1;continue
            if level==2:
                pagebreak();story.append(Paragraph(inline(text),chapter))
                if text=='Sommaire':
                    story.append(toc);i+=1
                    while i<len(lines) and not lines[i].startswith('## '):i+=1
                    continue
            else:story.append(Paragraph(inline(text),section))
            i+=1;continue
        paragraph=[line];i+=1
        while i<len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#','|','![')):
            paragraph.append(lines[i].strip());i+=1
        story.append(Paragraph(inline(' '.join(paragraph)),table_caption if line.startswith('**Tableau ') else normal))
    doc.multiBuild(story,maxPasses=6)
    (ROOT/'artifacts/scientific_writing/pdf_build.json').write_text(json.dumps(dict(figures=figures,tables=tables,toc=True,bookmarks=True,font_size_body=11,body_leading=16.2),indent=2),encoding='utf8')
    print('PDF generated:',target)

if __name__=='__main__':main()
