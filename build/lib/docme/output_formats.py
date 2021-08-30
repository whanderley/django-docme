import pdfkit
import os


class OutputFormat(object):

    def __init__(self, html_string, docs_dir):
        self.html_string = html_string
        self.docs_dir = docs_dir

    @classmethod
    def save(cls, html_string, output_formats, docs_dir):
        class_formats = {
            'pdf': PdfFormat,
            'html': HtmlFormat
        }
        for output_format in output_formats:
            output_format in class_formats and\
                class_formats[output_format](html_string, docs_dir).save()

class PdfFormat(OutputFormat):

    def save(self):
        options = {
            'page-size': 'Letter',
            'margin-top': '0.5in',
            'margin-right': '0.75in',
            'margin-bottom': '0.5in',
            'margin-left': '0.75in',
            'encoding': "UTF-8",
            'footer-left': "This is a footer",
            'footer-line': '',
            'footer-font-size': '7',
            '--footer-right': 'right footer',
            'enable-local-file-access': None,
            'custom-header': [
                ('Accept-Encoding', 'gzip')
            ],
            'no-outline': None
        }
        path = os.path.join(self.docs_dir, "doc.pdf")
        config = pdfkit.configuration()
        pdfkit.from_string(self.html_string,
                           path, configuration=config,
                           options=options)


class HtmlFormat(OutputFormat):

    def save(self):
        html_path = os.path.join(self.docs_dir, "doc.html")
        html_doc = open(html_path, "w+")
        html_doc.writelines(self.html_string)
        html_doc.close()
