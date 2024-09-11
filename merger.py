from pypdf import PdfWriter

merger = PdfWriter()

for pdf in ["files/demo.pdf", "files/demo_txt.pdf"]:
    merger.append(pdf)

merger.write("files/merger.pdf")
merger.close()