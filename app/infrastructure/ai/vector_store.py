from typing import List

from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

_EMBEDDINGS_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def create_pdf_retriever(
    pdf_paths: List[str], chunk_size: int = 1000, chunk_overlap: int = 100, k: int = 2
) -> VectorStoreRetriever:
    documents = sum((PyPDFLoader(path).load() for path in pdf_paths), [])
    chunks = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size, chunk_overlap=chunk_overlap
    ).split_documents(documents)
    embeddings = HuggingFaceEmbeddings(model_name=_EMBEDDINGS_MODEL)
    return FAISS.from_documents(chunks, embeddings).as_retriever(search_kwargs={"k": k})
