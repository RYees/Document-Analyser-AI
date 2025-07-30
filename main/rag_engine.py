import pandas as pd
import uuid
from ragbackend.utils import chroma
from ragbackend.utils.chunking import ChunkingApproaches
from ragbackend.utils.reranking import CrossEncoderReranker
from ragbackend.utils.file import FileReader
from ragbackend.utils.supabase_db import SupabaseResource
import chromadb
import textwrap
from IPython.display import display, clear_output, HTML
from flask import request, jsonify
from ragbackend.main.base import (
    BaseResource
)
from dotenv import dotenv_values
import openai

env_vars = dotenv_values('./.env')
openai.api_key = env_vars.get('OPENAI_API_KEY')
openai_client = openai.OpenAI(api_key=openai.api_key)


class TestViewResource(BaseResource):
    def get(self):
        return "selam, it is working"

class RagEngineUploadDocument(BaseResource):
    def post(self):
        try:
            value = request.get_json()
            file_path = value.get('file_path')
            documents = FileReader.pdf_reader_to_document_format(file_path)
            token_split_texts = ChunkingApproaches.chunking_RecursiveCharacterTextSplitter(documents)  
            stored = SupabaseResource.store_to_supabase(token_split_texts)
            return "Saved to Vector Database Successfully!"
        except Exception as e:
            return f'Error: {str(e)}'   
        
class RagEngineResource(BaseResource):
    def post(self):
        try:
            value = request.get_json()
            question = value.get('question')
            vector_store = SupabaseResource.fetch_stored_embedding()     
            context = vector_store.similarity_search(question)
            ranked_docs = CrossEncoderReranker.cross_encoder_reranker(question, context)
            # output_answer = self.generate_llm_response(question, ranked_docs)           
            output_answer = self.main(question, ranked_docs)
            return output_answer
        except Exception as e:           
            return f'Error: {str(e)}'   
        
    def generate_llm_response(self, question, ranked_docs):
        try:
            #information = "\n\n".join([doc.page_content for doc in ranked_docs])

            messages = [
                {"role": "system", "content": "You are an AI assistant that provides answers to questions based on the given information."},
                {"role": "user", "content": f"Question: {question}. Information: {ranked_docs}"}
            ]

            response = openai_client.chat.completions.create(
                model="gpt-4",
                messages=messages,
            )

            return response.choices[0].message.content.strip()
        except Exception as e:
            return f'Error: {str(e)}'  
        
        # llm response with stream 
    def get_response_stream(self, question, ranked_docs):
        try:
            response_stream = openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": f"Question: {question}. Information: {ranked_docs}"}],
                temperature=0,
                max_tokens=729,
                top_p=1,
                stream=True,
            )
            return response_stream
        except Exception as e:
            return f'Error: {str(e)}'  

    def main(self, query, ranked_docs):
        try:
            stream = self.get_response_stream(query, ranked_docs)
            response_text = self.process_streamed_responses(stream)
            return response_text
        except Exception as e:
            return f'Error: {str(e)}'  

    def process_streamed_responses(self, response_stream):
        try:
            response_text = ""
            for chunk in response_stream:
                chunk_message = chunk.choices[0].delta.content
                if chunk_message is not None:
                    response_text += chunk_message
                is_complete = chunk.choices[0].finish_reason is not None
                wrapped_text = textwrap.fill(response_text, width=80)
                clear_output(wait=True)
                display(HTML(f"<div style='text-align: left;'><pre>{wrapped_text}</pre></div>"))
                if is_complete:
                    break
            return response_text
        except Exception as e:
            return f'Error: {str(e)}'  



        



