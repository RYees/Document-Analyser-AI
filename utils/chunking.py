from langchain.text_splitter import CharacterTextSplitter
from langchain.text_splitter import RecursiveCharacterTextSplitter
from ..utils import chroma
from langchain_core.documents import Document
from collections import namedtuple

Chunk = namedtuple("Chunk", ["id", "text", "metadata"])

class ChunkingApproaches:
    @staticmethod
    def chunking_CharacterTextSplitter(pdf_doc):
        text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
            separator="\n\n",
            chunk_size=100,
            chunk_overlap=100,
            is_separator_regex=False,
            model_name='text-embedding-3-small',
            encoding_name='text-embedding-3-small'
        )
        character_split_texts = text_splitter.split_text('\n\n'.join(pdf_doc))
        token_split_texts = chroma.sentence_transfomer_textsplitter(character_split_texts)
        return token_split_texts
    
    def chunking_RecursiveCharacterTextSplitter(pdf_doc):
        text = '\n\n'.join([page.page_content for page in pdf_doc])
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " "],
            chunk_size=200,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False
        )
        chunk_list = text_splitter.create_documents([text])
        return chunk_list

    def chunking_RecursiveCharacter(pdf_doc):
        text = '\n\n'.join([page.page_content for page in pdf_doc])
        text_splitter = RecursiveCharacterTextSplitter(
            separators=["\n\n", "\n", " "],
            chunk_size=200,
            chunk_overlap=100,
            length_function=len,
            is_separator_regex=False
        )

        chunk_list = []
        for i, chunk in enumerate(text_splitter.create_documents([text])):
            metadata = {"page_number": [page.metadata["page_number"] for page in pdf_doc if page.page_content in chunk.page_content]}
            chunk_list.append(Document(id=i, page_content=chunk.page_content, metadata=metadata))

        return chunk_list