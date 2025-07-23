import google.generativeai as genai
import os
import re
from dotenv import load_dotenv
from typing import Dict, Any
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

load_dotenv()

class LLMHelper:
    def __init__(self, model_name: str = "models/gemini-1.5-flash"):
        """
        Initialize the Gemini model with robust error handling
        
        Args:
            model_name: The model to use (e.g., "models/gemini-1.5-flash")
        """
        self.model_name = model_name
        self.model = None
        self.available_models = self._get_available_models()
        
        try:
            api_key = os.getenv('GEMINI_API_KEY')
            if not api_key:
                raise ValueError("GEMINI_API_KEY not found in .env file")
                
            genai.configure(api_key=api_key)
            
            if not self.available_models:
                raise RuntimeError("No available models found")
                
            if model_name not in self.available_models:
                available = "\n".join(self.available_models.keys())
                raise ValueError(
                    f"Model {model_name} not available.\n"
                    f"Available models:\n{available}"
                )
                
            self.model = genai.GenerativeModel(model_name)
            logger.info(f"Successfully initialized model: {model_name}")
            
        except Exception as e:
            logger.error(f"Failed to initialize Gemini: {str(e)}")
            raise RuntimeError(f"LLM initialization failed: {str(e)}")

    def _get_available_models(self) -> Dict[str, Any]:
        """Get all available models that support generateContent"""
        try:
            return {
                m.name: {
                    "name": m.name,
                    "description": m.description,
                    "input_token_limit": m.input_token_limit,
                    "output_token_limit": m.output_token_limit,
                    "supported_methods": m.supported_generation_methods
                }
                for m in genai.list_models() 
                if 'generateContent' in m.supported_generation_methods
            }
        except Exception as e:
            logger.error(f"Error fetching available models: {str(e)}")
            return {}

    def _clean_sql_response(self, sql: str) -> str:
        """
        Clean the SQL response from the model to remove markdown and other artifacts
        
        Args:
            sql: Raw SQL response from the model
            
        Returns:
            Cleaned SQL query ready for execution
        """
        # Remove markdown code blocks
        if sql.startswith("```sql") and sql.endswith("```"):
            sql = sql[6:-3].strip()
        elif sql.startswith("```") and sql.endswith("```"):
            sql = sql[3:-3].strip()
        
        # Remove any remaining line comments
        sql = re.sub(r'--.*$', '', sql, flags=re.MULTILINE)
        
        # Remove excessive whitespace
        sql = ' '.join(sql.split())
        
        # Ensure it ends with semicolon
        if not sql.endswith(';'):
            sql += ';'
            
        return sql.strip()

    def generate_sql_query(self, question: str, schema_info: str) -> str:
        """
        Generate SQL query from natural language question with strict formatting
        
        Args:
            question: Natural language question
            schema_info: Database schema information
            
        Returns:
            Generated SQL query or error message
        """
        prompt = f"""You are an expert SQLite SQL developer. Follow these rules exactly:
        1. Given these tables:
        {schema_info}
        2. Convert this question to SQL: "{question}"
        3. Return ONLY the pure SQL query without:
           - Markdown code blocks
           - Explanations
           - Any text besides the SQL
        4. Use SQLite compatible syntax
        5. Never use backticks or code formatting
        6. Ensure the query ends with a semicolon
        
        SQL Query:"""
        
        try:
            if not self.model:
                raise RuntimeError("Model not initialized")
                
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.1,
                    "max_output_tokens": 1000,
                    "top_p": 0.95
                },
                safety_settings={
                    'HARM_CATEGORY_HARASSMENT': 'BLOCK_NONE',
                    'HARM_CATEGORY_HATE_SPEECH': 'BLOCK_NONE',
                    'HARM_CATEGORY_SEXUALLY_EXPLICIT': 'BLOCK_NONE',
                    'HARM_CATEGORY_DANGEROUS_CONTENT': 'BLOCK_NONE'
                }
            )
            
            if not response.text:
                raise ValueError("Empty response from model")
                
            cleaned_sql = self._clean_sql_response(response.text)
            logger.debug(f"Generated SQL: {cleaned_sql}")
            return cleaned_sql
            
        except Exception as e:
            error_msg = f"Error generating SQL: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def format_response(self, question: str, data: Any) -> str:
        """
        Format raw data into human-readable response with clear structure
        
        Args:
            question: Original question
            data: Data to format (can be list/dict/str)
            
        Returns:
            Formatted response or error message
        """
        prompt = f"""Format this data into a professional business report for: "{question}"
        Data: {data}
        
        Guidelines:
        1. Start with a direct answer to the question
        2. Use bullet points for multiple items
        3. Include specific numbers with proper formatting
        4. Highlight key insights
        5. Keep it concise (1-2 paragraphs max)
        6. Use professional business language
        
        Formatted Answer:"""
        
        try:
            if not self.model:
                raise RuntimeError("Model not initialized")
                
            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.3,
                    "max_output_tokens": 2000,
                    "top_p": 0.95
                }
            )
            
            if not response.text:
                raise ValueError("Empty response from model")
                
            return response.text.strip()
            
        except Exception as e:
            error_msg = f"Error formatting response: {str(e)}"
            logger.error(error_msg)
            return error_msg

    def get_model_info(self) -> Dict[str, Any]:
        """Get detailed information about the current model"""
        if not self.model:
            return {"error": "Model not initialized"}
            
        model_info = self.available_models.get(self.model_name, {})
        return {
            "model_name": self.model_name,
            "description": model_info.get("description", ""),
            "input_token_limit": model_info.get("input_token_limit", 0),
            "output_token_limit": model_info.get("output_token_limit", 0),
            "supported_methods": model_info.get("supported_methods", []),
            "status": "active"
        }

    def test_connection(self) -> Dict[str, Any]:
        """Test the connection to the Gemini API"""
        try:
            test_prompt = "Respond with just the word 'successful'"
            response = self.model.generate_content(test_prompt)
            return {
                "status": "success",
                "response": response.text,
                "model": self.model_name
            }
        except Exception as e:
            return {
                "status": "failed",
                "error": str(e),
                "model": self.model_name
            }