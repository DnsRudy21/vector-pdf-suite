import io, json, zipfile
from pathlib import Path
import fitz
from PIL import Image
from app.converter import PDFConverter

def pdf(path:Path,text:str="hello",pages:int=2)->Path:
    doc=fitz.open()
    for _ in range(pages): page=doc.new_page(); page.insert_text((72,72),text)
    doc.save(path); doc.close(); return path

def test_all_pdf_operations(tmp_path:Path)->None:
    a,b=pdf(tmp_path/"a.pdf"),pdf(tmp_path/"b.pdf","world",1); progress=lambda _:None
    merged=tmp_path/"merged.pdf"; PDFConverter.merge([a,b],merged,{},progress)
    assert PDFConverter.validate_pdf(merged)==3
    images=tmp_path/"images.zip"; PDFConverter.pdf_to_images([a],images,{"format":"png","dpi":72,"quality":80},progress)
    assert len(zipfile.ZipFile(images).namelist())==2
    split=tmp_path/"split.zip"; PDFConverter.split([a],split,{"split_mode":"each"},progress); assert len(zipfile.ZipFile(split).namelist())==2
    for name,method,options in [("compressed.zip",PDFConverter.optimize,{}),("protected.zip",PDFConverter.protect,{"password":"test1234"}),("watermark.zip",PDFConverter.watermark,{"watermark":"TEST"})]:
        target=tmp_path/name; method([a],target,options,progress); assert zipfile.is_zipfile(target)
    for target_type in ("word","excel"):
        target=tmp_path/f"{target_type}.zip"; PDFConverter.extract([a],target,{"target":target_type},progress); assert zipfile.is_zipfile(target)
    metadata=tmp_path/"metadata.json"; PDFConverter.metadata([a],metadata,{},progress); assert json.loads(metadata.read_text())[0]["pages"]==2

def test_images_to_pdf(tmp_path:Path)->None:
    sources=[]
    for index in range(2):
        path=tmp_path/f"{index}.png"; Image.new("RGB",(100,100),(index*100,20,30)).save(path); sources.append(path)
    output=tmp_path/"images.pdf"; PDFConverter.images_to_pdf(sources,output,{},lambda _:None)
    assert PDFConverter.validate_pdf(output)==2
