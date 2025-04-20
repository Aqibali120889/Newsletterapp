# app/services/extraction.py
from typing import List, Dict, Any
from langchain.document_loaders import WebBaseLoader, AsyncHtmlLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

class ExtractionService:
    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=100
        )
    
    async def extract_from_url(self, url: str) -> List[Dict[str, Any]]:
        """
        Extract content from a single URL
        """
        loader = WebBaseLoader(url)
        docs = loader.load()
        
        # Split documents into manageable chunks
        split_docs = self.text_splitter.split_documents(docs)
        return split_docs
    
    async def extract_from_multiple_urls(self, urls: List[str]) -> List[Dict[str, Any]]:
        """
        Extract content from multiple URLs
        """
        loader = AsyncHtmlLoader(urls)
        docs = await loader.aload()
        
        # Split documents into manageable chunks
        split_docs = self.text_splitter.split_documents(docs)
        return split_docs
    
    async def add_topic_metadata(self, docs: List[Dict[str, Any]], topic: str) -> List[Dict[str, Any]]:
        """
        Add topic metadata to documents
        """
        for doc in docs:
            doc.metadata["topic"] = topic
        
        return docs