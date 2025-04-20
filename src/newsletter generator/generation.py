# app/services/generation.py
import os
from typing import List, Dict, Any
from langchain.llms import HuggingFaceHub
from langchain.chains import LLMChain, MapReduceDocumentsChain, AnalyzeDocumentChain
from langchain.prompts import PromptTemplate

class NewsletterGenerator:
    def __init__(self):
        self.hf_api_key = os.getenv("HUGGINGFACE_API_KEY")
        
        # Initialize text generation model
        self.text_generation_llm = HuggingFaceHub(
            repo_id="mistralai/Mixtral-8x7B-Instruct-v0.1",
            huggingfacehub_api_token=self.hf_api_key,
            model_kwargs={"temperature": 0.7, "max_length": 500}
        )
        
        # Initialize summarization model
        self.summarization_llm = HuggingFaceHub(
            repo_id="facebook/bart-large-cnn",
            huggingfacehub_api_token=self.hf_api_key,
            model_kwargs={"temperature": 0.3, "max_length": 300}
        )
    
    async def generate_newsletter_section(self, topic: str, documents: List[Dict[str, Any]]) -> str:
        """
        Generate a newsletter section for a specific topic
        """
        # Create prompt template
        template = """
        You are a professional newsletter editor. Based on the following extracted content about {topic}, 
        create a concise, engaging newsletter section of 2-3 paragraphs. Include key insights, new developments, 
        and why this matters to readers interested in {topic}.
        
        EXTRACTED CONTENT:
        {content}
        
        NEWSLETTER SECTION:
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["topic", "content"]
        )
        
        # Create LLM chain
        chain = LLMChain(llm=self.text_generation_llm, prompt=prompt)
        
        # Combine content from documents
        content = "\n\n".join([doc.page_content for doc in documents])
        
        # Generate the newsletter section
        result = await chain.arun(topic=topic, content=content)
        
        return result
    
    async def summarize_document(self, document: Dict[str, Any]) -> str:
        """
        Summarize a single document
        """
        template = """
        Please summarize the following text in a concise and informative manner:
        
        {text}
        
        SUMMARY:
        """
        
        prompt = PromptTemplate(
            template=template,
            input_variables=["text"]
        )
        
        chain = LLMChain(llm=self.summarization_llm, prompt=prompt)
        
        analyze_doc_chain = AnalyzeDocumentChain(
            combine_documents_chain=chain
        )
        
        result = await analyze_doc_chain.arun(input_document=document.page_content)
        
        return result
    
    async def generate_complete_newsletter(self, topics: List[str], all_documents: List[Dict[str, Any]], 
                                   title: str, intro: str) -> str:
        """
        Generate a complete newsletter with multiple sections
        """
        newsletter_content = f"# {title}\n\n{intro}\n\n"
        
        for topic in topics:
            # Filter documents by topic
            topic_docs = [doc for doc in all_documents if doc.metadata.get("topic") == topic]
            
            # Generate section content
            section_content = await self.generate_newsletter_section(topic, topic_docs)
            
            # Add section to newsletter
            newsletter_content += f"## {topic}\n\n{section_content}\n\n"
        
        return newsletter_content