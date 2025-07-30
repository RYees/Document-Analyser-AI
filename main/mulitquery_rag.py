import os
from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from operator import itemgetter
from langchain_openai import ChatOpenAI
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_openai import ChatOpenAI
from langchain.load import dumps, loads
from ragbackend.utils import chroma
from ragbackend.utils.chunking import ChunkingApproaches
from ragbackend.utils.file import FileReader
from flask import request, jsonify
from dotenv import dotenv_values
env_vars = dotenv_values('.env')

from ragbackend.main.base import (
    BaseResource
)

class MultiQueryRag(BaseResource):
    def post(self):
        try:
            value = request.get_json()
            file_path = value.get('file_path')
            question = value.get('question')
            print("#####")
            print(value)
            documents = FileReader.pdf_reader_to_document_format(file_path)
            embed = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=env_vars.get('OPENAI_API_KEY'))
            # chunk_list = ChunkingApproaches.chunking_RecursiveCharacterTextSplitter(documents) 
            vectorstore = FAISS.from_documents(documents, embed)
            retriever = vectorstore.as_retriever()
            retrieval_chain = self.generate_queries(retriever)
          
            template = """
                Provide an answer to the following question based on the given legal contract context. Be sure to include the relevant section number(s) in your response. If there are multiple possible answers, list them all.

                Context: {context}

                Question: {question}
            """

            prompt = ChatPromptTemplate.from_template(template)

            llm = ChatOpenAI(temperature=0)

            final_rag_chain = (
                {"context": retrieval_chain, 
                "question": itemgetter("question")} 
                | prompt
                | llm
                | StrOutputParser()
            )
            llm_response = final_rag_chain.invoke({"question": question})
          
            return  {"response": llm_response}, 200
       
        except Exception as e:
            return f'Error: {str(e)}'   

    def get_unique_union(self, documents: list[list]):
        try:
            """ Unique union of retrieved docs """
            flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]
            unique_docs = list(set(flattened_docs))
            return [loads(doc) for doc in unique_docs], 200
        except Exception as e:
            return f'Error: {str(e)}'   
    
    def generate_queries(self, retriever):
        try:
            template = """You are an AI language model assistant. Your task is to generate five 
            different versions of the given user question to retrieve relevant documents from a vector 
            database. By generating multiple perspectives on the user question, your goal is to help
            the user overcome some of the limitations of the distance-based similarity search. 
            Provide these alternative questions separated by newlines. Original question: {question}"""
            prompt_perspectives = ChatPromptTemplate.from_template(template)

            generate_queries = (
                prompt_perspectives 
                | ChatOpenAI(temperature=0) 
                | StrOutputParser() 
                | (lambda x: x.split("\n"))
            )
            retrieval_chain = generate_queries | retriever.map() | self.get_unique_union
            return retrieval_chain
        except Exception as e:
            return f'Error: {str(e)}'   

 