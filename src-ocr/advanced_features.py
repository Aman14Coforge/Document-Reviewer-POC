"""
Advanced Features Module - Optional enhancements for the chatbot
This module provides advanced capabilities like LLM integration and advanced NLP
"""

import logging
from typing import Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AdvancedChatbot:
    """
    Enhanced chatbot with OpenAI LLM integration
    """
    
    def __init__(self, document_text: str, api_key: Optional[str] = None):
        """
        Initialize advanced chatbot
        
        Args:
            document_text: Extracted document text
            api_key: OpenAI API key
        """
        self.document_text = document_text
        self.api_key = api_key
        self.llm_available = False
        self.openai = None
        
        if api_key:
            try:
                import openai
                self.openai = openai
                self.openai.api_key = api_key
                self.llm_available = True
                logger.info("LLM service initialized successfully")
            except ImportError:
                logger.warning("OpenAI library not installed. LLM features disabled.")
            except Exception as e:
                logger.error(f"Failed to initialize LLM: {str(e)}")
    
    def _build_prompt(self, query: str, context: str) -> str:
        """
        Build the prompt for the OpenAI API call.
        """
        return (
            "You are a helpful assistant that answers questions using only the provided document context. "
            "If the answer is not available in the context, say you cannot find it. "
            "Keep the answer concise and factual.\n\n"
            "Document context:\n" + context + "\n\n"
            "Question:\n" + query
        )
    
    def _truncate_context(self, context: str, max_chars: int = 4000) -> str:
        """
        Truncate context if it is too large for the model.
        """
        if len(context) <= max_chars:
            return context
        return context[:max_chars] + "..."
    
    def generate_advanced_response(self, query: str, context: str = "") -> str:
        """
        Generate a response using OpenAI based on the document context.
        
        Args:
            query: User's question
            context: Relevant document passages
            
        Returns:
            Generated response from OpenAI or fallback text
        """
        if not self.llm_available:
            logger.warning("LLM not available. Using basic response generation.")
            return "LLM service is not configured. Using basic Q&A mode."
        
        try:
            truncated_context = self._truncate_context(context)
            prompt = self._build_prompt(query, truncated_context)
            
            response = self.openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant. Answer questions using only the given context."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,
                max_tokens=300,
                top_p=1.0
            )
            
            answer = response["choices"][0]["message"]["content"].strip()
            return answer + "\n\n*Source: OpenAI assisted response based on extracted document content*"
        except Exception as e:
            logger.error(f"Error generating LLM response: {str(e)}")
            return f"Error generating response: {str(e)}"
    
    def extract_entities(self) -> dict:
        """
        Extract named entities from document
        Requires spaCy: pip install spacy
        
        Returns:
            Dictionary of extracted entities
        """
        try:
            import spacy
            nlp = spacy.load("en_core_web_sm")
            doc = nlp(self.document_text[:5000])  # Limit to first 5000 chars
            
            entities = {}
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)
            
            return entities
        except ImportError:
            logger.warning("spaCy not installed. Cannot extract entities.")
            return {}
        except Exception as e:
            logger.error(f"Error extracting entities: {str(e)}")
            return {}
    
    def generate_qa_pairs(self, num_pairs: int = 5) -> list:
        """
        Automatically generate Q&A pairs from document
        
        Args:
            num_pairs: Number of Q&A pairs to generate
            
        Returns:
            List of (question, answer) tuples
        """
        try:
            # This would ideally use an LLM or QA model
            # For now, return empty list as placeholder
            logger.info(f"Generating {num_pairs} Q&A pairs...")
            
            # Placeholder implementation
            qa_pairs = []
            
            # In a real implementation, you would use a model like:
            # - transformers for seq2seq models
            # - question generation models
            # - LLM API calls
            
            return qa_pairs
        
        except Exception as e:
            logger.error(f"Error generating Q&A pairs: {str(e)}")
            return []
    
    def translate_text(self, target_language: str = "es") -> str:
        """
        Translate extracted text to another language
        Requires Google Translate API or similar
        
        Args:
            target_language: Target language code (e.g., 'es', 'fr', 'de')
            
        Returns:
            Translated text
        """
        try:
            from google.cloud import translate_v2
            # This is a template - requires Google Cloud credentials
            # client = translate_v2.Client()
            # result = client.translate_text(
            #     self.document_text[:1000],
            #     target_language=target_language
            # )
            # return result['translatedText']
            
            logger.warning("Translation service not configured")
            return "Translation service not available"
        
        except ImportError:
            logger.warning("Google Cloud Translation library not installed.")
            return "Translation library not available"
        except Exception as e:
            logger.error(f"Error translating text: {str(e)}")
            return f"Translation error: {str(e)}"
    
    def summarize_with_transformers(self, max_length: int = 150) -> str:
        """
        Generate summary using transformer models
        Requires: pip install transformers torch
        
        Args:
            max_length: Maximum length of summary
            
        Returns:
            Generated summary
        """
        try:
            from transformers import pipeline
            
            summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            
            # Split text into chunks if needed (model has token limits)
            text = self.document_text[:1024]
            
            summary = summarizer(text, max_length=max_length, min_length=50, do_sample=False)
            return summary[0]['summary_text']
        
        except ImportError:
            logger.warning("Transformers library not installed.")
            return "Transformer models not available"
        except Exception as e:
            logger.error(f"Error generating transformer summary: {str(e)}")
            return f"Summary generation error: {str(e)}"
    
    def detect_language(self) -> str:
        """
        Detect language of the document
        Requires: pip install textblob
        
        Returns:
            Detected language code
        """
        try:
            from textblob import TextBlob
            
            blob = TextBlob(self.document_text[:500])
            language = blob.detect_language()
            
            logger.info(f"Detected language: {language}")
            return language
        
        except ImportError:
            logger.warning("TextBlob not installed.")
            return "unknown"
        except Exception as e:
            logger.error(f"Error detecting language: {str(e)}")
            return "unknown"
    
    def sentiment_analysis(self) -> dict:
        """
        Analyze sentiment of the document
        
        Returns:
            Dictionary with sentiment scores
        """
        try:
            from textblob import TextBlob
            
            blob = TextBlob(self.document_text)
            sentiment = blob.sentiment
            
            return {
                "polarity": sentiment.polarity,  # -1 (negative) to 1 (positive)
                "subjectivity": sentiment.subjectivity,  # 0 (objective) to 1 (subjective)
                "classification": "positive" if sentiment.polarity > 0 else "negative" if sentiment.polarity < 0 else "neutral"
            }
        
        except ImportError:
            logger.warning("TextBlob not installed.")
            return {"error": "TextBlob not available"}
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {str(e)}")
            return {"error": str(e)}


# Usage examples for advanced features

def example_advanced_usage():
    """
    Example of using advanced features
    """
    
    # Basic setup
    sample_text = "Your extracted document text here..."
    
    # Initialize advanced chatbot (without LLM for this example)
    advanced_bot = AdvancedChatbot(sample_text)
    
    # Example 1: Sentiment Analysis
    sentiment = advanced_bot.sentiment_analysis()
    print(f"Sentiment: {sentiment}")
    
    # Example 2: Language Detection
    language = advanced_bot.detect_language()
    print(f"Language: {language}")
    
    # Example 3: Entity Extraction
    entities = advanced_bot.extract_entities()
    print(f"Entities: {entities}")
    
    # Example 4: With LLM (requires API key)
    import os
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        llm_bot = AdvancedChatbot(sample_text, api_key=api_key)
        response = llm_bot.generate_advanced_response(
            "What is the main topic of the document?",
            context="This is a sample document text with important information about the topic."
        )
        print(f"LLM Response: {response}")
    else:
        print("OpenAI API key not found. Set OPENAI_API_KEY to enable LLM mode.")


if __name__ == "__main__":
    # This file is meant to be imported, not run directly
    logger.info("Advanced features module loaded")
