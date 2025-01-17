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
from modules.image2text import groq_text_models, groq_vision_models
from pydantic import BaseModel


class Query(BaseModel):
    text: str


es_client = ESearchClient()

app = FastAPI()

logger = logging.getLogger(__name__)
WORK_DIR = os.path.dirname(os.path.abspath(__file__))


@app.post("/query/")
async def query(query: Query):
    resp = es_client.search(text=query.text, embedding=random_emb(query.text)[0])
    
    context = "\n".join([f'{chunk.get("_source").get("doc_text")} from {chunk.get("_source").get("doc_name").split("/")[-1]}' for chunk in resp["hits"]["hits"]])
    answer = groq_text_models(context, query.text)
    
    # groq_text_models()
    return {"answer": answer}


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
            
            if image_list:
                print(f"[+] Found a total of {len(image_list)} images on page {page_index}")

            for image_index, img in enumerate(image_list, start=1):
                # get the XREF of the image
                xref = img[0]
                
                # extract the image bytes
                base_image = pdf_file.extract_image(xref)
                image_bytes = base_image["image"]
                
                # image = Image.open(io.BytesIO(image_bytes))

                encoded_string = base64.b64encode(image_bytes)
                
                # image to text
                image_explanation = groq_vision_models(encoded_string)
                print(image_explanation)
                # embedding
                image_embed = random_emb(image_explanation)[0]

                data_to_ingest.append({
                    "doc_name": file.filename,
                    "doc_page": str(page_index),
                    "text_vector": image_embed,
                    "doc_text": image_explanation
                })

            # data ingestion
            es_client.bulk(data_to_ingest)
              
    return {"filename": file.filename}