import openai
import re
from typing import Optional, Dict, Any, List
from ..config import settings
import PyPDF2
import io

# Configure OpenAI client with settings
openai.api_key = settings.openai_api_key
openai.base_url = settings.openai_base_url

class OpenAIService:
    def __init__(self):
        self.client = openai.AsyncOpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url
        )
        self.model = settings.openai_model
    
    async def chat_with_ai(self, user_message: str, job_context: Optional[Dict[str, Any]] = None, chat_history: Optional[List[Dict[str, str]]] = None) -> str:
        """
        WARNING: This function is intentionally vulnerable to prompt injection attacks!
        User input is directly concatenated to the system prompt without sanitization.
        """
        # Vulnerable: Direct string concatenation allows prompt injection
        system_prompt = f"""You are Big Kahuna Burger's AI HR assistant. Your job is to help candidates understand job openings and company culture.
        
Company Info:
- Big Kahuna Burger is a fast-growing burger chain
- We value teamwork, customer service, and quality food
- We offer competitive salaries and growth opportunities

Current conversation context: {job_context if job_context else 'General inquiry'}

If you cannot answer the question or the user asks something that is not related to the job or company, say "Sorry, I don't know. I'm happy to help you with anything else." in language of the user."""

        try:
            # Prepare messages list
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add chat history if provided (already in OpenAI format)
            if chat_history:
                messages.extend(chat_history)
            
            # Add current user message
            messages.append({"role": "user", "content": user_message})

            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Sorry, I encountered an error: {str(e)}"
    
    async def analyze_cv(self, cv_content: str, job_description: str) -> int:
        """
        WARNING: This function is vulnerable to indirect prompt injection!
        PDF content is directly included in the prompt without validation.
        Returns a CV score (0-10) parsed from AI response using regex.
        """
        # Vulnerable: CV content (potentially malicious) is directly inserted into prompt
        analysis_prompt = f"""Analyze the following CV against the job requirements and provide a compatibility score.

Job Description:
{job_description}

CV Content:
{cv_content}

Please give me a score from 0 to 10. Start your response with Score: """

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an HR AI that analyzes CVs for job compatibility. Always start your response with 'Score: X/10'."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.5
            )
            
            ai_response = response.choices[0].message.content
            print(f"AI Response: {ai_response}")
            
            # Extract score using regex (vulnerable to manipulation through CV content)
            # Patterns: "Score: 8", "score: 7/10", "Score:9", etc.
            score_match = re.search(r'[Ss]core:\s*(\d+)(?:/10)?', ai_response)
            if score_match:
                score = int(score_match.group(1))
                # Ensure score is within valid range
                return min(max(score, 0), 10)
            else:
                # Fallback: try to find any number at the beginning
                number_match = re.search(r'(\d+)', ai_response)
                if number_match:
                    score = int(number_match.group(1))
                    return min(max(score, 0), 10)
                return 5  # Default score if no number found
                
        except Exception as e:
            # Return default score on error
            return 0
    
    def extract_text_from_pdf(self, pdf_file_content: bytes) -> str:
        """
        Extract text from PDF file.
        WARNING: No validation of PDF content - potential for malicious content injection.
        """
        try:
            pdf_file = io.BytesIO(pdf_file_content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            # Vulnerable: No sanitization or validation of extracted text
            return text
        except Exception as e:
            return f"Error extracting PDF text: {str(e)}"
    
    async def process_additional_questions(self, user_answers: Dict[str, str], job_id: int) -> str:
        """
        Process additional job-specific questions with AI analysis.
        WARNING: User answers are directly inserted into prompts without sanitization.
        """
        # Vulnerable: User answers directly concatenated without validation
        answers_text = "\n".join([f"{question}: {answer}" for question, answer in user_answers.items()])
        
        analysis_prompt = f"""Analyze the following additional information provided by a job applicant:

Job ID: {job_id}
Applicant's Additional Information:
{answers_text}

Please evaluate:
1. Completeness of answers
2. Relevance to the position
3. Any red flags or concerns
4. Overall assessment

Analysis:"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an HR AI analyzing additional applicant information."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.6
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"Error processing additional questions: {str(e)}"

# Global instance
openai_service = OpenAIService() 