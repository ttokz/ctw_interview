import io
import os
import fitz  # PyMuPDF
import base64
import logging
from PIL import Image
from typing import Annotated
from tempfile import NamedTemporaryFile
from fastapi import FastAPI, File, UploadFile
from modules.es_db import ESearchClient
from modules.chunking import RCTsplitter
from modules.embedding import random_emb
from modules.image2text import groq_text_models
from pydantic import BaseModel


class Query(BaseModel):
    text: str


es_client = ESearchClient()

app = FastAPI()

logger = logging.getLogger(__name__)
WORK_DIR = os.path.dirname(os.path.abspath(__file__))


@app.post("/query/")
async def query(query: Query):
    answer = es_client.search(text=query.text)
    final_ans = answer["hits"]["hits"]
    print()
    # groq_text_models()
    return {"answer": len(final_ans)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    fsuffix = "".join(file.filename.partition(".")[1:])
    tmp_dir = os.path.join(WORK_DIR, 'tmp')
    tmp_dir = "tmp"
    with NamedTemporaryFile(mode="wb",
                            suffix=fsuffix,
                            dir=tmp_dir,
                            delete=False) as tmp_file:
        contents = file.file.read()
        base_name = os.path.basename(tmp_file.name)
        logging.info(f'File saved:  {base_name}')
        tmp_file.write(contents)

        pdf_file = fitz.open(tmp_file.name)
        
        # STEP 3
        # iterate over PDF pages
        for page_index in range(len(pdf_file)):

            # get the page itself
            page = pdf_file.load_page(page_index)  # load the page
            image_list = page.get_images()
            page_text = page.get_text()
            chunked_texts = RCTsplitter(page_text)
            text_embeddings = random_emb(chunked_texts)

            data_to_ingest = [{
                "doc_name": file.filename,
                "doc_page": str(page_index),
                "text_vector": chunk_embed,
                "doc_text": chunk_t
            } for chunk_t, chunk_embed in zip(chunked_texts, text_embeddings)]
            
            # data ingestion
            es_client.bulk(data_to_ingest)
            
            if image_list:
                print(f"[+] Found a total of {len(image_list)} images on page {page_index}")

            for image_index, img in enumerate(image_list, start=1):
                # get the XREF of the image
                xref = img[0]
                
                # extract the image bytes
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                
                # image = Image.open(io.BytesIO(image_bytes))

                encoded_string = base64.b64encode(image_bytes).decode('utf-8')
                
                # image to text
                # embedding
                # db ingestion
                
    return {"filename": file.filename}