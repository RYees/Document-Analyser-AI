import psycopg2 as ps
import openai
from langchain_community.embeddings.openai import OpenAIEmbeddings
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.documents import Document
from supabase.client import create_client
from dotenv import dotenv_values

env_vars = dotenv_values('./.env')
supabase_url = env_vars.get('SUPABASE_URL')
supabase_key = env_vars.get('SUPABASE_KEY')
openai.api_key = env_vars.get('OPENAI_API_KEY')
openai_client = openai.OpenAI(api_key=openai.api_key)


class SupabaseResource:
    def store_to_supabase(docs: list):
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai.api_key)
        supabase_client = create_client(supabase_url, supabase_key)
        vector_store = SupabaseVectorStore.from_documents(
            docs,
            embeddings,
            client=supabase_client,
            table_name="documents",
            query_name="match_documents",
            chunk_size=500,
        )
        return vector_store
    
    def fetch_stored_embedding():
        embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai.api_key)
        supabase_client = create_client(supabase_url, supabase_key)
        vector_store = SupabaseVectorStore(
            client=supabase_client,
            embedding=embeddings,
            table_name="documents",
            query_name="match_documents",
        )
        return vector_store

    def db_connection_psycopg(self):
        try:
            pgconn = ps.connect(
                dbname="postgres",
                user="postgres.oilbyyqcgttqjfqsusst",
                password="neA7c4AusMeEKyWz",
                host="aws-0-eu-central-1.pooler.supabase.com",
                port="6543"
            )
            self.db_insert_data_psycopg(pgconn)
            return "Connection successful!"
        except Exception as e:
            return f'Error: {str(e)}'

    def db_insert_data_psycopg(pgconn, table):
        try:
            cur = pgconn.cursor()
            sql = f"""
                CREATE TABLE IF NOT EXISTS {table} (
                    id UUID PRIMARY KEY,
                    content TEXT,
                    embedding VECTOR,
                    metadata JSONB,
                    created_at TIMESTAMPTZ
                );
            """
            cur.execute(sql)
            sql = f"""
                ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;
                CREATE POLICY "Allow access to all users" ON {table}
                FOR ALL
                TO PUBLIC
                USING (true);;
            """
            cur.execute(sql)
            pgconn.commit()
            return "Table created and RLS policy enabled successfully!"
        except Exception as e:
            pgconn.rollback()
            return f'Error: {str(e)}'

# from sentence_transformers import CrossEncoder
# import numpy as np
# def cross_encoder_reranker(query, retrieved_documents):
#     try:
#         cross_encoder = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
#         query_text = query
#         pairs = [[query_text, doc.page_content] for doc in retrieved_documents]
        
#         scores = cross_encoder.predict(pairs)
#         ordered_indices = np.argsort(scores)[::-1]
#         top_scored_docs = [retrieved_documents[i] for i in ordered_indices[:15]]

#         return top_scored_docs
#     except Exception as e:
#         return f'Error: {str(e)}'
           
# def fetch_stored_embedding(question):
#     embeddings = OpenAIEmbeddings(model="text-embedding-3-small", openai_api_key=openai.api_key)
#     supabase_client = create_client(supabase_url, supabase_key)
#     vector_store = SupabaseVectorStore(
#         client=supabase_client,
#         embedding=embeddings,
#         table_name="documents",
#         query_name="match_documents",
#     )
  
#     vector_store = SupabaseResource.fetch_stored_embedding()     
#     context = vector_store.similarity_search(question)
#     ranked_docs = cross_encoder_reranker(question, context)
#     print(ranked_docs)

# question = "Who are the parties to the Agreement and what are their defined names?"

# fetch_stored_embedding(question)