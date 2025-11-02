import subprocess
from docxtpl import DocxTemplate
import fitz


def doc_creation(template_name, input_information):
    result = fitz.open()
    for info in input_information:
        full_tempalate_path = f'D:\python_projects\python\pasport_print\{template_name}'
        doc = DocxTemplate(full_tempalate_path)

        doc.render(info)
        doc.save(r'D:\python_projects\python\pasport_print\to_add.docx')

        path_of = r'C:\Program Files\LibreOffice\program\soffice.exe'
        subprocess.run([
            path_of,
            "--headless",
            "--convert-to", "pdf",
            "--outdir", "./",
            "to_add.docx"
        ])

        with fitz.open(r'D:\python_projects\python\pasport_print\to_add.pdf') as mfile:
            result.insert_pdf(mfile)
    result.save(
        r'D:\python_projects\python\pasport_print\static\pdf\result.pdf')

    return
