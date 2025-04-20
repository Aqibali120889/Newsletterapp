# Updated content for app/routes/newsletter.py using DuckDuckGo

import os
from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel
import logging
from dotenv import load_dotenv

# Langchain and HuggingFace imports
from langchain_huggingface import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate
from langchain_community.tools import DuckDuckGoSearchRun # Import DuckDuckGo Search
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Load environment variables
load_dotenv()

# Initialize router
router = APIRouter(
    prefix="/newsletter",
    tags=["newsletter"],
)

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Globals for Langchain components ---
search_tool = None
chain = None
initialization_error = None

# --- Initialize AI Components ---
try:
    # Model Configuration (API Key no longer needed for search)
    HUGGINGFACE_MODEL_NAME = os.getenv("HUGGINGFACE_MODEL_NAME", "distilgpt2")
    logger.info(f"Using Hugging Face model: {HUGGINGFACE_MODEL_NAME}")

    # 1. Initialize Search Tool (Using DuckDuckGo)
    try:
        search_tool = DuckDuckGoSearchRun()
        logger.info("DuckDuckGoSearchRun initialized.")
    except ImportError as ie:
         logger.error(f"DuckDuckGoSearchRun import failed. Please install 'duckduckgo-search'. Error: {ie}")
         initialization_error = "Search tool dependency missing. Install 'duckduckgo-search'."
         search_tool = None # Ensure search_tool is None if import fails
    except Exception as e:
         logger.error(f"Error initializing DuckDuckGoSearchRun: {e}", exc_info=True)
         initialization_error = f"Failed to initialize search tool: {e}"
         search_tool = None # Ensure search_tool is None if init fails

    # Only proceed if search tool didn't cause a fatal error
    if initialization_error is None:
        # 2. Initialize HuggingFace Pipeline LLM
        tokenizer = AutoTokenizer.from_pretrained(HUGGINGFACE_MODEL_NAME)
        model = AutoModelForCausalLM.from_pretrained(HUGGINGFACE_MODEL_NAME)
        pipe = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=300)
        llm = HuggingFacePipeline(pipeline=pipe)
        logger.info("HuggingFacePipeline initialized.")

        # 3. Initialize Prompt Template
        template = """
Instructions:
You are an AI assistant writing a newsletter section.
Your goal is to generate a single, concise paragraph about the specific topic provided, using the background information given.
The tone should be informative and engaging for a general audience.
Do NOT include any introductory phrases like "Here is the newsletter section..." or any sign-offs.
Do NOT repeat these instructions in your output.

Context:
Topic: {topic}
Background Information: {information}

Newsletter Paragraph:
"""
        prompt = PromptTemplate(template=template, input_variables=["topic", "information"])

        # 4. Initialize Chain using LCEL
        chain = prompt | llm
        logger.info("LCEL Chain initialized.")

except ImportError as ie:
    # Catch potential import errors for HuggingFace/transformers if they occur
    logger.error(f"ImportError during AI component initialization: {ie}. Make sure all dependencies are installed.", exc_info=True)
    initialization_error = f"ImportError: {ie}. Check dependencies."
    # Ensure chain is None if LLM part fails
    chain = None
except Exception as e:
    logger.error(f"Error initializing AI components: {e}", exc_info=True)
    initialization_error = f"Error initializing AI components: {e}"
    # Ensure chain is None if LLM part fails
    chain = None

# --- Request Body Model ---
class NewsletterRequest(BaseModel):
    topic: str

# --- API Endpoint ---
@router.post("/generate")
async def generate_newsletter_endpoint(request: NewsletterRequest = Body(...)):
    logger.info(f"Received request for topic: {request.topic}")

    if initialization_error:
        logger.error(f"Initialization error: {initialization_error}")
        raise HTTPException(status_code=500, detail=f"Server setup error: {initialization_error}")

    # Check specifically if the chain failed to initialize
    if not chain:
         logger.error("LLM Chain component not available.")
         raise HTTPException(status_code=500, detail="AI Text Generation component not initialized.")

    search_results = "No search information available (search tool not initialized)."
    if not search_tool:
         logger.warning("DuckDuckGoSearch tool not available. Proceeding without search.")
    else:
        try:
            logger.info(f"Performing DuckDuckGo search for: '{request.topic}'") # Updated log
            # DDGRun takes the query directly
            search_results = search_tool.run(request.topic)
            logger.info("Search completed.")
            if not search_results:
                 search_results = "No results found by DuckDuckGo."
                 logger.warning(f"Empty search results for topic: {request.topic}")
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}", exc_info=True) # Updated log
            search_results = f"Error during search: {e}"

    try:
        logger.info("Generating content with LCEL chain...")
        generation_input = {"topic": request.topic, "information": search_results}
        generated_content = await chain.ainvoke(generation_input)
        logger.info(f"Successfully generated content for topic: {request.topic}")

        return {"topic": request.topic, "newsletter_content": generated_content.strip()}

    except Exception as e:
        logger.error(f"LLM generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate newsletter content: {e}")

# --- Optional Status Endpoint ---
@router.get("/status")
async def get_status():
    if initialization_error:
        return {"status": "error", "message": initialization_error}
    return {
        "status": "running",
        "search_tool_initialized": bool(search_tool),
        "llm_chain_initialized": bool(chain),
        "model_used": os.getenv("HUGGINGFACE_MODEL_NAME", "distilgpt2")
        }
