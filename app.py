from fastapi import FastAPI

app=FastAPI()

@app.get("/")
def home():
    return {"message":"Local RAG Running"}


@app.post("/ask")
def ask():
    return {'message': 'asking a questions'}