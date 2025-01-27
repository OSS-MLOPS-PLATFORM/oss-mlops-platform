
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings

def langchain_create_code_chunks(
    language: any,
    chunk_size: int,
    chunk_overlap: int,
    code: any
) -> any:
    splitter = RecursiveCharacterTextSplitter.from_language(
        language = language,
        chunk_size = chunk_size, 
        chunk_overlap = chunk_overlap
    )

    code_chunks = splitter.create_documents([code])
    code_chunks = [doc.page_content for doc in code_chunks]
    return code_chunks

def langchain_create_text_chunks(
    chunk_size: int,
    chunk_overlap: int,
    text: any
) -> any:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size = chunk_size, 
        chunk_overlap = chunk_overlap,
        length_function = len,
        is_separator_regex = False
    )

    text_chunks = splitter.create_documents([text])
    text_chunks = [doc.page_content for doc in text_chunks]
    return text_chunks
