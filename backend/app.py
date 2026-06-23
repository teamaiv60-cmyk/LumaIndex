from fastapi import FastAPI
from fastapi import UploadFile
from fastapi import File

import os

from rag.loader import load_pdf
from rag.chunker import chunk_text
from rag.embedder import create_embeddings
from rag.retriever import save
from rag.generator import answer
from rag.retriever import retrieve
from sentence_transformers import SentenceTransformer


embed = SentenceTransformer("all-MiniLM-L6-v2")


app=FastAPI()

UPLOAD_DIR="uploads"
DOCUMENT_TEXT=""

os.makedirs(
    UPLOAD_DIR,
    exist_ok=True
)


@app.post("/upload")

async def upload_pdf(
file:UploadFile=File(...)
):

    global DOCUMENT_TEXT

    path=f"uploads/{file.filename}"

    with open(
        path,
        "wb"
    ) as f:

        f.write(
            await file.read()
        )

    text=load_pdf(path)

    DOCUMENT_TEXT=text

    chunks=chunk_text(
        text
    )

    emb=create_embeddings(
        chunks
    )

    save(
        chunks,
        emb
    )

    return {

        "message":"uploaded",

        "chunks":len(chunks)

    }

@app.get("/ask")

def ask(
question:str
):

    q=embed.encode(
        question
    )

    docs=retrieve(q)

    context="\n".join(
        docs["documents"][0]
    )

    print("\nRetrieved:\n")
    print(context)

    result=answer(
        question,
        context
    )

    return {

        "answer":
        result

    }