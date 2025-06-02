import os
import boto3
from langchain_community.embeddings import BedrockEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader
from langchain.llms.bedrock import Bedrock
from langchain_community.chat_models import BedrockChat
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

bedrock = boto3.client(service_name="bedrock-runtime")
bedrock_embeddings = BedrockEmbeddings(model_id="amazon.titan-embed-image-v1", client=bedrock)

PROMPT = PromptTemplate(
    template="""
Human: Use the following pieces of context to provide a 
concise answer to the question at the end but use at least summarize with 
250 words with detailed explanations. If you don't know the answer, 
just say that you don't know, don't try to make up an answer.
<context>
{context}
</context>

Question: {question}

Assistant:""",
    input_variables=["context", "question"]
)

def data_ingestion(kb_id):
    loader = PyPDFDirectoryLoader(f"data/{kb_id}")
    documents = loader.load()
    splitter = RecursiveCharacterTextSplitter(chunk_size=10000, chunk_overlap=1000)
    return splitter.split_documents(documents)

def calculate_embedding_cost(docs):
    total_tokens = sum(len(doc.page_content.split()) for doc in docs)
    cost_per_token = 0.0001  # Change as per model pricing
    return round(total_tokens * cost_per_token, 4)

def create_vector_store(docs, kb_id):
    faiss_store = FAISS.from_documents(docs, bedrock_embeddings)
    faiss_store.save_local(f"faiss_index_{kb_id}")

def load_vector_store(kb_id):
    return FAISS.load_local(
        f"faiss_index_{kb_id}",
        bedrock_embeddings,
        allow_dangerous_deserialization=True
    )

def get_claude_llm():
    return BedrockChat(
        model_id="anthropic.claude-3-haiku-20240307-v1:0",
        client=bedrock,
        model_kwargs={"max_tokens": 512}
    )

def get_llama2_llm():
    return Bedrock(
        model_id="meta.llama3-70b-instruct-v1:0",
        client=bedrock,
        model_kwargs={"max_gen_len": 512}
    )

def get_response_llm(llm, vectorstore, query):
    qa = RetrievalQA.from_chain_type(
        llm=llm,
        chain_type="stuff",
        retriever=vectorstore.as_retriever(search_type="similarity", search_kwargs={"k": 3}),
        return_source_documents=True,
        chain_type_kwargs={"prompt": PROMPT}
    )
    return qa({"query": query})["result"]