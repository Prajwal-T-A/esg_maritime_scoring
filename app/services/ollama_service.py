"""
Ollama Service Layer for AI chatbot functionality.
Handles interaction with locally running Ollama LLM for ESG-related queries.
"""

import logging
from typing import List, Dict, Optional
import ollama
from datetime import datetime

from app.config import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OllamaService:
    """Service class for interacting with Ollama LLM."""
    
    def __init__(self):
        """Initialize Ollama service."""
        self.model_name = settings.OLLAMA_MODEL
        self.host = settings.OLLAMA_HOST
        logger.info(f"Ollama service initialized with model: {self.model_name}")
        
    def _create_system_prompt(self) -> str:
        """Create a system prompt for ESG-focused conversations.
        
        Returns:
            System prompt string
        """
        return """You are an AI assistant specialized in Environmental, Social, and Governance (ESG) 
metrics for maritime vessels. You help users understand:

- ESG scoring methodologies for ships
- Carbon emissions calculations and factors
- AIS (Automatic Identification System) data interpretation
- Vessel performance metrics
- Environmental compliance and regulations
- Fuel consumption patterns
- Speed optimization for emissions reduction

Be concise, accurate, and focus on maritime ESG topics. If asked about topics outside 
this domain, politely redirect to ESG-related questions. Use technical terminology 
appropriately but explain complex concepts clearly."""

    async def chat(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict[str, str]]] = None,
        use_system_prompt: bool = True
    ) -> Dict[str, any]:
        """
        Send a message to Ollama and get a response.
        
        Args:
            message: User's message
            conversation_history: Optional list of previous messages
            use_system_prompt: Whether to include the system prompt (default: True)
            
        Returns:
            Dictionary with response and metadata
        """
        try:
            # Build messages array
            messages = []
            
            # Add system prompt only if requested
            if use_system_prompt:
                messages.append({
                    'role': 'system',
                    'content': self._create_system_prompt()
                })
            
            # Add conversation history if provided
            if conversation_history:
                messages.extend(conversation_history)
            
            # Add current user message
            messages.append({
                'role': 'user',
                'content': message
            })
            
            # Make request to Ollama
            logger.info(f"Sending message to Ollama model: {self.model_name}")
            
            response = ollama.chat(
                model=self.model_name,
                messages=messages,
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                }
            )
            
            # Extract response content
            assistant_message = response['message']['content']
            
            return {
                'message': assistant_message,
                'model': self.model_name,
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'success': True
            }
            
        except Exception as e:
            logger.error(f"Error communicating with Ollama: {str(e)}")
            return {
                'message': f"I'm having trouble connecting to the AI model. Please ensure Ollama is running with the '{self.model_name}' model. Error: {str(e)}",
                'model': self.model_name,
                'timestamp': datetime.utcnow().isoformat() + "Z",
                'success': False,
                'error': str(e)
            }
    
    async def get_available_models(self) -> List[str]:
        """
        Get list of available Ollama models.
        
        Returns:
            List of model names
        """
        try:
            models = ollama.list()
            model_names = [model['name'] for model in models.get('models', [])]
            logger.info(f"Available models: {model_names}")
            return model_names
        except Exception as e:
            logger.error(f"Error fetching available models: {str(e)}")
            return []
    
    async def check_health(self) -> Dict[str, any]:
        """
        Check if Ollama is running and accessible.
        
        Returns:
            Health status dictionary
        """
        try:
            models = ollama.list()
            available_models = [model['name'] for model in models.get('models', [])]
            
            return {
                'status': 'healthy',
                'available': True,
                'models': available_models,
                'configured_model': self.model_name,
                'model_available': self.model_name in available_models
            }
        except Exception as e:
            logger.error(f"Ollama health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'available': False,
                'error': str(e),
                'configured_model': self.model_name
            }


# Create a global instance
ollama_service = OllamaService()
