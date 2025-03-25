# 读取PDF
import PyPDF2

# 分析PDF的layout，提取文本
from pdfminer.high_level import extract_pages, extract_text
from pdfminer.layout import LTTextContainer, LTChar, LTRect, LTFigure

# 从PDF的表格中提取文本
import pdfplumber

# 从PDF中提取图片
from PIL import Image
from pdf2image import convert_from_path

# 运行OCR从图片中提取文本
import pytesseract

# 清除过程中的各种过程文件
import os

# 从页面中提取表格内容


def extract_table(pdf_path, page_num, table_num):
    # 打开PDF文件
    pdf = pdfplumber.open(pdf_path)
    # 查找已检查的页面
    table_page = pdf.pages[page_num]
    # 提取适当的表格
    table = table_page.extract_tables()[table_num]
    return table


# 将表格转换为适当的格式
def table_converter(table):
    table_string = ""
    # 遍历表格的每一行
    for row_num in range(len(table)):
        row = table[row_num]
        # 从warp的文字删除线路断路器
        cleaned_row = [
            item.replace("\n", " ")
            if item is not None and "\n" in item
            else "None"
            if item is None
            else item
            for item in row
        ]
        # 将表格转换为字符串，注意'|'、'\n'
        table_string += "|" + "|".join(cleaned_row) + "|" + "\n"
    # 删除最后一个换行符
    table_string = table_string[:-1]
    return table_string


def text_extraction(element):
    # 从行元素中提取文本
    line_text = element.get_text()

    # 探析文本的格式
    # 用文本行中出现的所有格式初始化列表
    line_formats = []
    for text_line in element:
        if isinstance(text_line, LTTextContainer):
            # 遍历文本行中的每个字符
            for character in text_line:
                if isinstance(character, LTChar):
                    # 追加字符的font-family
                    line_formats.append(character.fontname)
                    # 追加字符的font-size
                    line_formats.append(character.size)
    # 找到行中唯一的字体大小和名称
    format_per_line = list(set(line_formats))

    # 返回包含每行文本及其格式的元组
    return (line_text, format_per_line)


# 创建一个从pdf中裁剪图像元素的函数
def crop_image(element, pageObj):
    # 获取从PDF中裁剪图像的坐标
    [image_left, image_top, image_right, image_bottom] = [
        element.x0,
        element.y0,
        element.x1,
        element.y1,
    ]
    # 使用坐标(left, bottom, right, top)裁剪页面
    pageObj.mediabox.lower_left = (image_left, image_bottom)
    pageObj.mediabox.upper_right = (image_right, image_top)
    # 将裁剪后的页面保存为新的PDF
    cropped_pdf_writer = PyPDF2.PdfWriter()
    cropped_pdf_writer.add_page(pageObj)
    # 将裁剪好的PDF保存到一个新文件
    with open("cropped_image.pdf", "wb") as cropped_pdf_file:
        cropped_pdf_writer.write(cropped_pdf_file)


# 创建一个将PDF内容转换为image的函数
def convert_to_images(
    input_file,
):
    images = convert_from_path(input_file)
    image = images[0]
    output_file = "PDF_image.png"
    image.save(output_file, "PNG")


# 创建从图片中提取文本的函数
def image_to_text(image_path):
    # 读取图片
    img = Image.open(image_path)
    # 从图片中抽取文本
    text = pytesseract.image_to_string(img)
    return text


if __name__ == "__main__":
    # 查找PDF路径
    pdf_path = "../Downloads/2404.06109v1.pdf"

    # 创建一个PDF文件对象
    pdfFileObj = open(pdf_path, "rb")
    # 创建一个PDF阅读器对象
    pdfReaded = PyPDF2.PdfReader(pdfFileObj)

    # 创建字典以从每个图像中提取文本
    text_per_page = {}
    # 我们从PDF中提取页面
    for pagenum, page in enumerate(extract_pages(pdf_path)):
        # 初始化从页面中提取文本所需的变量
        pageObj = pdfReaded.pages[pagenum]
        page_text = []
        line_format = []
        text_from_images = []
        text_from_tables = []
        page_content = []
        # 初始化检查表的数量
        table_num = 0
        first_element = True
        table_extraction_flag = False
        # 打开pdf文件
        pdf = pdfplumber.open(pdf_path)
        # 查找已检查的页面
        page_tables = pdf.pages[pagenum]
        # 找出本页上的表格数目
        tables = page_tables.find_tables()

        # 找到所有的元素
        page_elements = [(element.y1, element) for element in page._objs]
        # 对页面中出现的所有元素进行排序
        page_elements.sort(key=lambda a: a[0], reverse=True)

        # 查找组成页面的元素
        for i, component in enumerate(page_elements):
            # 提取PDF中元素顶部的位置
            pos = component[0]
            # 提取页面布局的元素
            element = component[1]

            # 检查该元素是否为文本元素
            if isinstance(element, LTTextContainer):
                # 检查文本是否出现在表中
                if table_extraction_flag == False:
                    # 使用该函数提取每个文本元素的文本和格式
                    (line_text, format_per_line) = text_extraction(element)
                    # 将每行的文本追加到页文本
                    page_text.append(line_text)
                    # 附加每一行包含文本的格式
                    line_format.append(format_per_line)
                    page_content.append(line_text)
                else:
                    # 省略表中出现的文本
                    pass

            # 检查元素中的图像
            if isinstance(element, LTFigure):
                # 从PDF中裁剪图像
                crop_image(element, pageObj)
                # 将裁剪后的pdf转换为图像
                convert_to_images("cropped_image.pdf")
                # 从图像中提取文本
                image_text = image_to_text("PDF_image.png")
                text_from_images.append(image_text)
                page_content.append(image_text)
                # 在文本和格式列表中添加占位符
                page_text.append("image")
                line_format.append("image")

            # 检查表的元素
            if isinstance(element, LTRect):
                # 如果第一个矩形元素
                if first_element == True and (table_num + 1) <= len(tables):
                    # 找到表格的边界框
                    lower_side = page.bbox[3] - tables[table_num].bbox[3]
                    upper_side = element.y1
                    # 从表中提取信息
                    table = extract_table(pdf_path, pagenum, table_num)
                    # 将表信息转换为结构化字符串格式
                    table_string = table_converter(table)
                    # 将表字符串追加到列表中
                    text_from_tables.append(table_string)
                    page_content.append(table_string)
                    # 将标志设置为True以再次避免该内容
                    table_extraction_flag = True
                    # 让它成为另一个元素
                    first_element = False
                    # 在文本和格式列表中添加占位符
                    page_text.append("table")
                    line_format.append("table")

                # 检查我们是否已经从页面中提取了表
                if element.y0 >= lower_side and element.y1 <= upper_side:
                    pass
                elif not isinstance(page_elements[i + 1][1], LTRect):
                    table_extraction_flag = False
                    first_element = True
                    table_num += 1

        # 创建字典的键
        dctkey = "Page_" + str(pagenum)
        # 将list的列表添加为页键的值
        text_per_page[dctkey] = [
            page_text,
            line_format,
            text_from_images,
            text_from_tables,
            page_content,
        ]

    # 关闭pdf文件对象
    pdfFileObj.close()

    # 删除已创建的过程文件
    os.remove("cropped_image.pdf")
    os.remove("PDF_image.png")

    # 显示页面内容
    result = "".join(text_per_page["Page_0"][4])
    print(result)
