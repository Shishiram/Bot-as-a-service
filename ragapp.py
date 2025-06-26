import json
import os
import sys
import boto3
import streamlit as st

## We will be suing Titan Embeddings Model To generate Embedding

from langchain_community.embeddings import BedrockEmbeddings
from langchain.llms.bedrock import Bedrock
from langchain_community.chat_models import BedrockChat

## Data Ingestion

import numpy as np
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import PyPDFDirectoryLoader

# Vector Embedding And Vector Store

from langchain.vectorstores import FAISS

## LLm Models
from langchain.prompts import PromptTemplate
from langchain.chains import RetrievalQA

## Bedrock Clients
bedrock=boto3.client(service_name="bedrock-runtime")
bedrock_embeddings=BedrockEmbeddings(model_id="amazon.titan-embed-image-v1",client=bedrock)


## Data ingestion
def data_ingestion():
    loader=PyPDFDirectoryLoader("data")
    documents=loader.load()

    # - in our testing Character split works better with this PDF data set
    text_splitter=RecursiveCharacterTextSplitter(chunk_size=10000,
                                                 chunk_overlap=1000)
    
    docs=text_splitter.split_documents(documents)
    return docs

## Vector Embedding and vector store

def get_vector_store(docs):
    vectorstore_faiss=FAISS.from_documents(
        docs,
        bedrock_embeddings
    )
    vectorstore_faiss.save_local("faiss_index")

def get_claude_llm():
    ##create the Anthropic Model
    llm = BedrockChat(  
        model_id="anthropic.claude-3-haiku-20240307-v1:0",  
        client=bedrock,  
        model_kwargs={"max_tokens": 512}  # Use `max_tokens` instead of `model_kwargs`  
    )  
    return llm

def get_llama2_llm():
    ##create the Anthropic Model
    llm=Bedrock(model_id="meta.llama3-70b-instruct-v1:0",client=bedrock,
                model_kwargs={'max_gen_len':512})
    
    return llm

prompt_template = """

Human: Use the following pieces of context to provide a 
concise answer to the question at the end but usse atleast summarize with 
250 words with detailed explaantions. If you don't know the answer, 
just say that you don't know, don't try to make up an answer.
<context>
{context}
</context

Question: {question}

Assistant:"""

PROMPT = PromptTemplate(
    template=prompt_template, input_variables=["context", "question"]
)

def get_response_llm(llm,vectorstore_faiss,query):
    qa = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=vectorstore_faiss.as_retriever(
        search_type="similarity", search_kwargs={"k": 3}
    ),
    return_source_documents=True,
    chain_type_kwargs={"prompt": PROMPT}
)
    answer=qa({"query":query})
    return answer['result']


def main():
    st.set_page_config("Chat PDF")
    
    st.header("Chat with PDF using AWS Bedrock💁")

    user_question = st.text_input("Ask a Question from the PDF Files")

    with st.sidebar:
        st.title("Update Or Create Vector Store:")
        
        if st.button("Vectors Update"):
            with st.spinner("Processing..."):
                docs = data_ingestion()
                get_vector_store(docs)
                st.success("Done")

    if st.button("Claude Output"):
        with st.spinner("Processing..."):
            faiss_index = FAISS.load_local("faiss_index", bedrock_embeddings, allow_dangerous_deserialization=True)
            llm=get_claude_llm()
            
            #faiss_index = get_vector_store(docs)
            st.write(get_response_llm(llm,faiss_index,user_question))
            st.success("Done")

    if st.button("Llama2 Output"):
        with st.spinner("Processing..."):
            faiss_index = FAISS.load_local("faiss_index", bedrock_embeddings, allow_dangerous_deserialization=True)
            llm=get_llama2_llm()
            
            #faiss_index = get_vector_store(docs)
            st.write(get_response_llm(llm,faiss_index,user_question))
            st.success("Done")
import requests
import json

# --- CONFIGURATION ---
SOURCEGRAPH_URL = "https://<your-sourcegraph-instance>"  # e.g., https://sourcegraph.example.com
ACCESS_TOKEN = "your_token_here"

# --- HEADERS ---
HEADERS = {
    "Authorization": f"token {ACCESS_TOKEN}",
    "Content-Type": "application/json"
}

def build_binary_file_query(file_extensions):
    """
    Constructs a Sourcegraph search query to find binary files based on extensions.

    Args:
        file_extensions (list of str): List of extensions (e.g., ['exe', 'bin'])

    Returns:
        str: Search query string
    """
    pattern = '|'.join(file_extensions)
    return f'count:1000 type:file file:\\.({pattern})$'

def fetch_repos_with_binary_files(search_query):
    """
    Fetch repositories containing binary files using Sourcegraph's GraphQL API.

    Args:
        search_query (str): Sourcegraph search query string

    Returns:
        list of tuples: List of (repository_name, file_path) containing binary files
    """
    graphql_payload = {
        "query": """
        query($searchQuery: String!) {
          search(query: $searchQuery) {
            results {
              results {
                ... on FileMatch {
                  repository {
                    name
                  }
                  file {
                    path
                  }
                }
              }
            }
          }
        }
        """,
        "variables": {
            "searchQuery": search_query
        }
    }

    response = requests.post(
        f"{SOURCEGRAPH_URL}/.api/graphql",
        headers=HEADERS,
        data=json.dumps(graphql_payload)
    )

    if response.status_code != 200:
        raise Exception(f"API Error {response.status_code}: {response.text}")

    results = response.json().get("data", {}).get("search", {}).get("results", {}).get("results", [])
    return [(res["repository"]["name"], res["file"]["path"]) for res in results]

# --- USAGE EXAMPLE ---
if __name__ == "__main__":
    binary_extensions = ['exe', 'dll', 'bin', 'so', 'zip', 'jpg', 'png']  # customize
    query = build_binary_file_query(binary_extensions)
    matches = fetch_repos_with_binary_files(query)

    print("Repositories with binary-like files:")
    for repo, path in matches:
        print(f"- {repo} :: {path}")

if __name__ == "__main__":
    main()
