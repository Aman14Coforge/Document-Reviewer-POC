"""
Chatbot Module - Handles conversational Q&A with extracted documents
"""

import logging
from typing import List, Tuple
import re

from advanced_features import AdvancedChatbot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentChatbot:
    """
    Chatbot that answers questions based on extracted document text
    """
    
    def __init__(self, document_text: str, max_context_length: int = 2000, openai_api_key: str = ""):
        """
        Initialize chatbot with document text
        
        Args:
            document_text: The extracted document text
            max_context_length: Maximum length of context to consider
            openai_api_key: Optional OpenAI API key for enhanced responses
        """
        self.document_text = document_text
        self.max_context_length = max_context_length
        self.logger = logger
        self.conversation_history: List[Tuple[str, str]] = []
        self.advanced_bot = AdvancedChatbot(document_text, openai_api_key) if openai_api_key else None
    
    def preprocess_text(self, text: str) -> str:
        """
        Preprocess text for better matching
        
        Args:
            text: Text to preprocess
            
        Returns:
            Preprocessed text
        """
        # Remove extra whitespace
        text = ' '.join(text.split())
        # Convert to lowercase for matching
        return text.lower()
    
    def find_relevant_passages(self, query: str, num_passages: int = 3) -> List[str]:
        """
        Find relevant passages in the document related to the query
        
        Args:
            query: User's question
            num_passages: Number of passages to retrieve
            
        Returns:
            List of relevant passages
        """
        query_lower = self.preprocess_text(query)
        query_words = set(query_lower.split())
        
        # Split document into sentences
        sentences = self.document_text.split('.')
        
        # Score sentences based on query word matches
        scored_sentences = []
        for sentence in sentences:
            sentence_words = set(self.preprocess_text(sentence).split())
            # Calculate relevance score
            common_words = query_words.intersection(sentence_words)
            score = len(common_words)
            
            if score > 0:
                scored_sentences.append((sentence.strip(), score))
        
        # Sort by score and get top passages
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        relevant_passages = [s[0] for s in scored_sentences[:num_passages]]
        
        return relevant_passages
    
    def generate_response(self, query: str) -> str:
        """
        Generate a response to the user's query
        
        Args:
            query: User's question
            
        Returns:
            Response text
        """
        try:
            # Check if document is empty
            if not self.document_text or len(self.document_text.strip()) < 10:
                return "No document text available. Please upload a document first."
            
            # Find relevant passages
            relevant_passages = self.find_relevant_passages(query)
            
            if not relevant_passages:
                return "I couldn't find relevant information in the document to answer your question. Try asking something different."
            
            # Combine relevant passages
            context = ". ".join(relevant_passages)
            
            # Use OpenAI LLM if configured, otherwise return a local response
            if self.advanced_bot and self.advanced_bot.llm_available:
                response = self.advanced_bot.generate_advanced_response(query, context)
            else:
                response = self._build_response(query, context)
            
            # Store in conversation history
            self.conversation_history.append((query, response))
            
            return response
        
        except Exception as e:
            self.logger.error(f"Error generating response: {str(e)}")
            return f"An error occurred while processing your question: {str(e)}"
    
    def _build_response(self, query: str, context: str) -> str:
        """
        Build a response based on query and context
        
        Args:
            query: User's question
            context: Relevant context from document
            
        Returns:
            Generated response
        """
        query_lower = query.lower()
        
        # Check for specific question types
        if any(word in query_lower for word in ['who', 'which person', 'which company']):
            response = f"Based on the document: {context[:500]}..."
        elif any(word in query_lower for word in ['what', 'define', 'explain']):
            response = f"According to the document: {context[:500]}..."
        elif any(word in query_lower for word in ['when', 'date', 'time']):
            response = f"The document mentions: {context[:500]}..."
        elif any(word in query_lower for word in ['where', 'location', 'address']):
            response = f"Regarding location: {context[:500]}..."
        elif any(word in query_lower for word in ['how', 'process', 'method']):
            response = f"The process is described as: {context[:500]}..."
        else:
            response = f"Based on the document content: {context[:500]}..."
        
        return response + "\n\n*Source: Extracted from uploaded document*"
    
    def get_summary(self, num_sentences: int = 3) -> str:
        """
        Generate a summary of the document
        
        Args:
            num_sentences: Number of summary sentences
            
        Returns:
            Document summary
        """
        try:
            sentences = self.document_text.split('.')
            # Get first few meaningful sentences
            summary_sentences = []
            for sentence in sentences[:num_sentences]:
                clean_sentence = sentence.strip()
                if len(clean_sentence) > 20:
                    summary_sentences.append(clean_sentence)
            
            summary = ". ".join(summary_sentences[:num_sentences]) + "."
            return summary if summary.strip() else "Unable to generate summary."
        
        except Exception as e:
            self.logger.error(f"Error generating summary: {str(e)}")
            return "Unable to generate summary."
    
    def get_key_terms(self, num_terms: int = 10) -> List[str]:
        """
        Extract key terms from the document
        
        Args:
            num_terms: Number of key terms to extract
            
        Returns:
            List of key terms
        """
        try:
            # Simple keyword extraction - get longest words that appear frequently
            words = self.document_text.split()
            
            # Filter out common stop words and short words
            stop_words = {
                'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
                'of', 'is', 'was', 'are', 'been', 'be', 'have', 'has', 'do', 'does',
                'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can'
            }
            
            filtered_words = [w.lower() for w in words if len(w) > 4 and w.lower() not in stop_words]
            
            # Get frequency count
            word_freq = {}
            for word in filtered_words:
                clean_word = re.sub(r'[^a-zA-Z0-9]', '', word)
                if clean_word:
                    word_freq[clean_word] = word_freq.get(clean_word, 0) + 1
            
            # Sort by frequency and get top terms
            key_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:num_terms]
            return [term[0] for term in key_terms]
        
        except Exception as e:
            self.logger.error(f"Error extracting key terms: {str(e)}")
            return []
    
    def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []
    
    def get_history(self) -> List[Tuple[str, str]]:
        """Get conversation history"""
        return self.conversation_history
