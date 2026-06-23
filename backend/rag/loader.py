from pypdf import PdfReader


def load_pdf(path):

    reader=PdfReader(path)

    text=""

    for page in reader.pages:
        t=page.extract_text()

        if t:
            text+=t

    return text
