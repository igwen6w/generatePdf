from pypdf import PdfWriter, PdfReader, PageObject
from pypdf.generic import NameObject, DecodedStreamObject, ArrayObject, FloatObject, DictionaryObject, StreamObject

def create_transparent_text_layer(text_page):
    # 该函数用于创建一个将文本设置为透明的内容流，传入的参数是一个文字页对象。
    transparent_stream = DecodedStreamObject()
    transparent_stream.update({
        NameObject("/Type"): NameObject("/XObject"),
        NameObject("/Subtype"): NameObject("/Form"),
        NameObject("/FormType"): FloatObject(1),
        NameObject("/Matrix"): ArrayObject(
            [FloatObject(1), FloatObject(0), FloatObject(0), FloatObject(1), FloatObject(0), FloatObject(0)]),
    })

    # 设置透明度
    gs1 = DictionaryObject()
    gs1.update({
        NameObject("/Type"): NameObject("/ExtGState"),
        NameObject("/ca"): FloatObject(0.1),  # 透明度，0.5表示50%透明
        NameObject("/CA"): FloatObject(0.5),  # 描边透明度
    })

    resources = DictionaryObject()
    resources.update({
        NameObject("/ExtGState"): DictionaryObject({
            NameObject("/GS1"): gs1
        })
    })

    transparent_stream[NameObject("/Resources")] = resources

    # 处理内容流
    original_contents = text_page.get("/Contents")
    if isinstance(original_contents, ArrayObject):
        # 如果是多个内容流，将它们合并
        data = b"\n".join(stream.get_data() for stream in original_contents)
    elif isinstance(original_contents, StreamObject):
        # 如果是单个内容流
        data = original_contents.get_data()
    else:
        raise TypeError("Unexpected content type")

    # 添加透明度设置到内容流
    new_data = b"q\n/GS1 gs\n" + data + b"\nQ"
    transparent_stream.set_data(new_data)

    return transparent_stream


def create_invisible_text_layer(text_page):
    # 获取原始内容
    contents = text_page["/Contents"].get_object()
    if isinstance(contents, ArrayObject):
        data = b"".join(stream.get_data() for stream in contents)
    else:
        data = contents.get_data()

    # 创建新的内容流
    invisible_stream = DecodedStreamObject()
    invisible_stream.update({
        NameObject("/Type"): NameObject("/XObject"),
        NameObject("/Subtype"): NameObject("/Form"),
        NameObject("/FormType"): FloatObject(1),
        NameObject("/Matrix"): ArrayObject(
            [FloatObject(1), FloatObject(0), FloatObject(0), FloatObject(1), FloatObject(0), FloatObject(0)]),
    })

    # 添加渲染模式设置
    new_data = b"q\n3 Tr\n" + data + b"\nQ"
    invisible_stream.set_data(new_data)

    return invisible_stream


def merge_pdfs(image_pdf_path, text_pdf_path, output_path):
    # 该函数用于合并两个PDF文件，一个是图像的（作为背景），另一个是文字的（作为透明的覆盖层），最终输出合并后的PDF。
    pdf_writer = PdfWriter()

    image_pdf = PdfReader(image_pdf_path)
    text_pdf = PdfReader(text_pdf_path)

    if len(image_pdf.pages) != len(text_pdf.pages):
        raise ValueError("图片 PDF 和文本 PDF 的页数必须相同")

    for i in range(len(image_pdf.pages)):
        image_page = image_pdf.pages[i]
        text_page = text_pdf.pages[i]

        # 创建透明的文字层
        # transparent_text = create_transparent_text_layer(text_page)

        # 创建不可见的文字层
        invisible_text = create_invisible_text_layer(text_page)

        # 将不可见的文字层设置为内容流
        text_page[NameObject('/Contents')] = invisible_text

        # 将透明文字层添加到图片页面上
        image_page.merge_page(text_page)

        # 将合并后的页面添加到输出 PDF
        pdf_writer.add_page(image_page)

    # 将结果写入到输出文件
    with open(output_path, 'wb') as output_file:
        pdf_writer.write(output_file)


# 使用函数
merge_pdfs('files/demo.pdf', 'files/demo_txt.pdf', 'files/merged_plus.pdf')

