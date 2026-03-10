"""
AI Service - GPT-4 powered features
"""
from typing import List, Dict, Optional
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage

from app.core.config import settings


class AIService:
    """AI-powered features using GPT"""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self.temperature = settings.OPENAI_TEMPERATURE
    
    async def chat_response(
        self,
        message: str,
        conversation_history: List[Dict[str, str]] = None,
        context: Optional[str] = None
    ) -> Dict[str, any]:
        """
        Generate chatbot response using GPT
        
        Args:
            message: User's message
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
            context: Additional context (KB articles, ticket info, etc.)
        
        Returns:
            Dict with response and metadata
        """
        try:
            messages = [
                {
                    "role": "system",
                    "content": """You are a helpful and professional customer support AI assistant.
                    
                    Your role:
                    - Provide accurate and helpful answers
                    - Be empathetic and understanding
                    - Offer step-by-step solutions when needed
                    - Escalate to human agent when necessary
                    - Always be polite and professional
                    
                    If you don't know the answer, be honest and suggest contacting a human agent."""
                }
            ]
            
            # Add context if provided
            if context:
                messages.append({
                    "role": "system",
                    "content": f"Relevant information from knowledge base:\n{context}"
                })
            
            # Add conversation history
            if conversation_history:
                messages.extend(conversation_history[-10:])  # Last 10 messages
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Call GPT API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=self.max_tokens,
                temperature=self.temperature
            )
            
            return {
                "response": response.choices[0].message.content,
                "confidence": 85,  # Could implement confidence scoring
                "should_escalate": self._should_escalate(message, response.choices[0].message.content),
                "tokens_used": response.usage.total_tokens
            }
        
        except Exception as e:
            print(f"AI chat error: {str(e)}")
            return {
                "response": "I apologize, but I'm having trouble processing your request. Would you like to speak with a human agent?",
                "confidence": 0,
                "should_escalate": True,
                "error": str(e)
            }
    
    async def suggest_agent_response(
        self,
        ticket_context: str,
        customer_message: str,
        agent_notes: Optional[str] = None
    ) -> str:
        """
        Suggest response for agent to send to customer
        
        Args:
            ticket_context: Context about the ticket
            customer_message: Latest customer message
            agent_notes: Internal agent notes
        
        Returns:
            Suggested response text
        """
        try:
            prompt = f"""As a customer support expert, suggest a professional response to the customer.
            
Ticket Context: {ticket_context}

Customer Message: {customer_message}

{f'Agent Notes: {agent_notes}' if agent_notes else ''}

Generate a helpful, empathetic, and professional response that addresses the customer's concern.
Keep it concise but complete. Use a friendly tone."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            return f"Error generating suggestion: {str(e)}"
    
    async def categorize_ticket(self, subject: str, description: str) -> Dict[str, str]:
        """
        AI-powered ticket categorization
        
        Returns:
            Dict with category, priority, and tags
        """
        try:
            prompt = f"""Analyze this support ticket and categorize it.

Subject: {subject}
Description: {description}

Respond in JSON format:
{{
  "category": "technical|billing|feature_request|bug_report|general|complaint",
  "priority": "low|medium|high|urgent",
  "tags": ["tag1", "tag2", "tag3"],
  "suggested_department": "string"
}}"""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3  # Lower temperature for more consistent categorization
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
        
        except Exception as e:
            # Default fallback
            return {
                "category": "general",
                "priority": "medium",
                "tags": [],
                "suggested_department": "general"
            }
    
    async def extract_intent(self, message: str) -> str:
        """
        Extract customer intent from message
        
        Returns:
            Intent string (refund, help, complaint, inquiry, etc.)
        """
        try:
            prompt = f"""What is the primary intent of this customer message? Choose ONE from:
- refund
- cancellation
- technical_support
- billing_inquiry
- feature_request
- complaint
- general_inquiry
- product_info
- account_help

Message: {message}

Respond with just the intent word, nothing else."""

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=20,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip().lower()
        
        except Exception as e:
            return "general_inquiry"
    
    def _should_escalate(self, user_message: str, ai_response: str) -> bool:
        """
        Determine if conversation should be escalated to human agent
        
        Criteria:
        - User explicitly asks for human
        - AI is unsure
        - Sensitive topics (legal, medical, financial disputes)
        """
        escalation_keywords = [
            "speak to human", "talk to person", "real person",
            "not helpful", "frustrated", "angry", "lawyer",
            "sue", "legal action", "complaint", "manager"
        ]
        
        message_lower = user_message.lower()
        response_lower = ai_response.lower()
        
        # Check for explicit escalation requests
        for keyword in escalation_keywords:
            if keyword in message_lower:
                return True
        
        # Check if AI suggests escalation
        if any(phrase in response_lower for phrase in ["speak with", "contact", "human agent"]):
            return True
        
        return False
    
    async def generate_kb_summary(self, article_content: str) -> str:
        """Generate concise summary of knowledge base article"""
        try:
            prompt = f"Summarize this help article in 2-3 sentences:\n\n{article_content[:2000]}"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=150,
                temperature=0.5
            )
            
            return response.choices[0].message.content
        except:
            return article_content[:200] + "..."


# Global AI service instance
ai_service = AIService()
