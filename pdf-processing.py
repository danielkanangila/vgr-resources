import datetime
import re
from io import StringIO
from pdfminer.high_level import extract_text, extract_text_to_fp, extract_pages 
from pdfminer.layout import LAParams, LTTextContainer
import PyPDF2

file_path = "/mnt/d/vgr-resources/fr/pdf/FRN62-1231_The_Contest_VGR.pdf"

words_to_remove = [
    "LA  PAROLE  PARLÉE",
    "[Frère Branham donne cinq coups sur la chaire._N.D.É.]",
    "[L’assemblée dit : “Amen.”_N.D.É.]"
]
# print(docInfo)

def get_title(subject):
    subject.pop(0)
    # check for subtitle
    sub = " ".join(subject).split("–")
    title = None
    subtitle = None
    if len(sub) >= 2:
        title = sub.pop(0).strip()
        subtitle = " ".join(sub).strip().capitalize()
    else:
        title = " ".join(sub)

    # build full title
    full_title = f"{title} {subtitle.lower()}" if subtitle else title
    
    return title, subtitle, full_title
    

def get_datetitme_lang(date_lang):
    alfa_filter = "".join(list(filter(str.isalpha, date_lang)))
    # get lang and time
    if len(alfa_filter) >= 3:
        lang = alfa_filter[:-2] if len(alfa_filter) == 4 else alfa_filter[:-1]
    else:
        lang = "EN"
    # get date
    numeric_filter = list(filter(str.isdigit, date_lang))
    numeric_str = "".join(numeric_filter)
    str_date = f"19{numeric_str}"
    
    return datetime.datetime.strptime(str_date, '%Y%m%d').date(), lang, None

def parse_docinfio(docinfo):
    raw_subject = docinfo.get('/Subject').split(" ")
    title, subtitle, full_title = get_title(raw_subject)
    date, lang, time = get_datetitme_lang(docinfo.get('/Subject').split(" ").pop(0))
   
    return dict(
        author=docinfo.get("/Author"),
        title=title,
        subtitle=subtitle,
        full_title=full_title,
        date=date,
        lang=lang,
        time=time
    )

def has_dateref(text, docinfo):
    date_ref = docinfo.get('/Subject').split(" ").pop(0)
    try:
        text.index(date_ref)
    except:
        return None
    else:
        return True

def sanitize_content(text, docinfo):
    
    paragraph = text.replace('`', "")\
        .replace('^', "")\
        .replace("", "")\
        .replace("½", " ")\
        .replace("„", "")\
        .replace("…", "")\
        .replace("†", "")\
        .replace("‡", "")\
        .strip()\
        .split("\n")
    sanitized = [line for line in paragraph if line.strip() != ""]
    # print(sanitized)
    if not sanitized:
        return None
    if len(sanitized) == 1 and has_dateref(" ".join(sanitized), docinfo):
        return None

    return "\n".join(sanitized)

pdfFileObj = open(file_path, 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
docInfo = pdfReader.documentInfo

docinfo = parse_docinfio(pdfReader.documentInfo)
description = ""
# print(docinfo)
numPages = pdfReader.numPages
stopPage = numPages - 1
pages = extract_pages(file_path)


for page_layout in pages:
    page_id = page_layout.pageid
    for element in page_layout:
        if (isinstance(element, LTTextContainer)):
            # text_block = sanitize_content(element.get_text())
            if page_id == stopPage:
                continue
                description = text_block
            elif page_id == 1:
                if element.index == 0:
                    continue
                text_block = sanitize_content(element.get_text(), docInfo)
                print(text_block)
            elif page_id == 2:
                if element.index == 0 or element.index == 1:
                    continue
                print(sanitize_content(element.get_text(), docInfo))
                # if text_block != "":
                    # print()
                    # print(element.index, " ",text_block)
    #         pass
            # for text_line in element:
            #     text = text_line.get_text().strip()
            #     # Remove unnecessary character
            #     text = text.replace('`', "")
            #     text = text.replace('^', "")
            #     print(text)

pdfFileObj.close() 