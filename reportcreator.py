from reportlab.lib.colors import Color
from reportlab.pdfgen import canvas
from reportlab.lib import pdfencrypt
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Frame
from reportlab.pdfbase import ttfonts
from reportlab.pdfbase import pdfmetrics
from PySide2.QtWidgets import QFileDialog
from PySide2.QtCore import QSysInfo
from datetime import datetime


# Функция генерации отчёта
def generate_report(module_name, module_success, result, message, parent=None):
    directory = QFileDialog().getExistingDirectory(parent, 'Директория для сохранения отчёта')
    if directory != '':
        enc = pdfencrypt.StandardEncryption('3s7cmSzfMT', canModify=0)
        p = canvas.Canvas(f'{directory}/{module_name}_report.pdf', encrypt=enc)
        pdfmetrics.registerFont(ttfonts.TTFont('TimesNewRoman', 'times.ttf'))
        pdfmetrics.registerFont(ttfonts.TTFont('TimesNewRomanBold', 'timesbd.ttf'))
        p.setTitle(f'{module_name}_report')
        main_header_style = ParagraphStyle('header_style', fontName='TimesNewRomanBold', fontSize=18,
                                           alignment=1, spaceAfter=9, spaceBefore=9)
        block_header_style = ParagraphStyle('header_style', fontName='TimesNewRomanBold', fontSize=14,
                                            alignment=1, spaceAfter=9, spaceBefore=9)
        normal_style = ParagraphStyle('normal_style', fontName='TimesNewRoman', fontSize=14,
                                      alignment=1, spaceAfter=9, spaceBefore=9)
        success_normal_style = ParagraphStyle('success_normal_style', fontName='TimesNewRoman',
                                              fontSize=14, textColor=Color(0, 255, 0, 1),
                                              alignment=1, spaceAfter=9, spaceBefore=9)
        failure_normal_style = ParagraphStyle('failure_normal_style', fontName='TimesNewRoman',
                                              fontSize=14, textColor=Color(255, 0, 0, 1),
                                              alignment=1, spaceAfter=9, spaceBefore=9)
        story = [
            Paragraph(f'Отчёт о выполнении модуля "{module_name}"', main_header_style),
            Paragraph(f'Операционная система: {QSysInfo.prettyProductName()}.', normal_style),
            Paragraph(f'Дата и время генерации отчёта: {datetime.now().strftime("%d.%m.%Y %H:%M:%S.")}',
                      normal_style)
        ]
        if module_success == 'True':
            story.append(Paragraph(message, success_normal_style))
        else:
            story.append(Paragraph(message, failure_normal_style))
        for i in range(0, len(result)):
            story.append(Paragraph(f'Блок №{i + 1}', block_header_style))
            for j in range(0, len(result[i]) - 1):
                story.append(Paragraph(f'Результат выполнения команды №{j + 1}:', normal_style))
                if result[i][j][0] == 0:
                    story.append(Paragraph(f'{result[i][j][1].strip()}', success_normal_style))
                else:
                    story.append(Paragraph(f'{result[i][j][1].strip()}', failure_normal_style))
        f = Frame(0, 0, A4[0], A4[1])
        for s in story:
            while f.add(s, p) == 0:
                f.split(s, p)
                f = Frame(0, 0, A4[0], A4[1])
                p.showPage()
        p.setAuthor('ВКР')
        p.setCreator('ВКР')
        p.save()
