# app/routes/newsletter.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Dict, Any
from pydantic import BaseModel

from app.services.search import SearchService
from app.services.extraction import ExtractionService
from app.services.generation import NewsletterGenerator
from app.services.firebase import FirebaseService

# Data models
class NewsletterRequest(BaseModel):
    title: str
    intro: str
    topics: List[str]
    results_per_topic: int = 3

class NewsletterResponse(BaseModel):
    newsletter_id: str
    title: str
    content: str

# Create router
router = APIRouter(prefix="/newsletters", tags=["newsletters"])

# Dependency injection
def get_search_service():
    return SearchService()

def get_extraction_service():
    return ExtractionService()

def get_generator_service():
    return NewsletterGenerator()

def get_firebase_service():
    return FirebaseService()

@router.post("/generate", response_model=NewsletterResponse)
async def generate_newsletter(
    request: NewsletterRequest,
    search_service: SearchService = Depends(get_search_service),
    extraction_service: ExtractionService = Depends(get_extraction_service),
    generator_service: NewsletterGenerator = Depends(get_generator_service),
    firebase_service: FirebaseService = Depends(get_firebase_service)
):
    """
    Generate a newsletter from specified topics
    """
    try:
        all_documents = []
        
        # For each topic, search and extract content
        for topic in request.topics:
            # Search using SERP API
            search_results = await search_service.search_with_serpapi(
                query=topic, 
                num_results=request.results_per_topic
            )
            
            # Get URLs from search results
            urls = await search_service.get_urls_from_results(search_results)
            
            # Extract content from URLs
            documents = await extraction_service.extract_from_multiple_urls(urls)
            
            # Add topic metadata
            topic_documents = await extraction_service.add_topic_metadata(documents, topic)
            
            all_documents.extend(topic_documents)
        
        # Generate the newsletter
        newsletter_content = await generator_service.generate_complete_newsletter(
            topics=request.topics,
            all_documents=all_documents,
            title=request.title,
            intro=request.intro
        )
        
        # Save to Firebase (assuming user authentication is handled elsewhere)
        user_id = "example_user_id"  # This would come from auth middleware
        newsletter_id = await firebase_service.save_newsletter(
            user_id=user_id,
            title=request.title,
            content=newsletter_content,
            topics=request.topics
        )
        
        return {
            "newsletter_id": newsletter_id,
            "title": request.title,
            "content": newsletter_content
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating newsletter: {str(e)}"
        )