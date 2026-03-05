import PyPDF2

with open(r'c:\Users\user\Downloads\oasis.pdf', 'rb') as f:
    reader = PyPDF2.PdfReader(f)
    print(f'Pages: {len(reader.pages)}')
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        print(f'--- Page {i+1} ---')
        print(text)
