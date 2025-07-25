import re
from typing import List, Dict, Optional
from openai import OpenAI
from ..config import get_openai_config

# Initialize OpenAI client with configurable settings
openai_config = get_openai_config()
client = OpenAI(
    api_key=openai_config["api_key"],
    base_url=openai_config["base_url"],
    timeout=openai_config["timeout"],
    max_retries=openai_config["max_retries"]
)


class OpenAIService:
    @staticmethod
    def analyze_resume_match(resume_text: str, job_description: str, job_requirements: str) -> Dict:
        """Analyze how well a resume matches a job posting"""
        prompt = f"""
        Analyze how well this resume matches the job posting. Provide a detailed analysis and a score from 0-100.

        JOB POSTING:
        Description: {job_description}
        Requirements: {job_requirements}

        RESUME:
        {resume_text}

        Please provide:
        1. A match score (0-100)
        2. Key strengths that align with the job
        3. Areas where the candidate might need development
        4. Overall recommendation (Strong Match, Good Match, Partial Match, Poor Match)

        Format your response as follows:
        Score: [number]
        Strengths: [list of strengths]
        Areas for Development: [areas needing improvement]
        Recommendation: [your recommendation]
        Summary: [brief overall summary]
        """

        try:
            response = client.chat.completions.create(
                model=openai_config["model"],
                messages=[
                    {"role": "system", "content": "You are an expert HR recruiter analyzing resumes for job matches."},
                    {"role": "user", "content": prompt}
                ],
                temperature=openai_config["temperature"],
                max_tokens=openai_config["max_tokens"]
            )
            
            content = response.choices[0].message.content
            
            # Parse using regex instead of JSON
            score_match = re.search(r'Score:\s*(\d+)', content, re.IGNORECASE)
            score = int(score_match.group(1)) if score_match else 50
            
            strengths_match = re.search(r'Strengths:\s*(.*?)(?=Areas for Development:|Recommendation:|Summary:|$)', content, re.IGNORECASE | re.DOTALL)
            strengths = strengths_match.group(1).strip() if strengths_match else "Analysis provided in summary"
            
            areas_match = re.search(r'Areas for Development:\s*(.*?)(?=Recommendation:|Summary:|$)', content, re.IGNORECASE | re.DOTALL)
            areas_for_development = areas_match.group(1).strip() if areas_match else "See summary for details"
            
            recommendation_match = re.search(r'Recommendation:\s*(.*?)(?=Summary:|$)', content, re.IGNORECASE | re.DOTALL)
            recommendation = recommendation_match.group(1).strip() if recommendation_match else "Manual review recommended"
            
            summary_match = re.search(r'Summary:\s*(.*?)$', content, re.IGNORECASE | re.DOTALL)
            summary = summary_match.group(1).strip() if summary_match else content
            
            analysis = {
                "score": score,
                "summary": summary,
                "strengths": strengths,
                "areas_for_development": areas_for_development,
                "recommendation": recommendation
            }
            
            return analysis
        except Exception as e:
            return {
                "score": 0,
                "summary": f"Error analyzing resume: {str(e)}",
                "strengths": "Unable to analyze",
                "areas_for_development": "Unable to analyze",
                "recommendation": "Manual review required"
            }

    @staticmethod
    def chat_about_job(message: str, job_info: Optional[Dict] = None, chat_history: List[Dict] = None) -> str:
        """Handle chat conversations about jobs and company information"""
        
        system_prompt = """
        You are an AI assistant for Big Kahuna Burger's HR platform. You help job candidates learn about:
        - Available positions at Big Kahuna Burger
        - Company culture and values
        - Application process
        - Job requirements and expectations
        - Benefits and compensation (general information)
        
        Be friendly, helpful, and professional. If you don't know specific information, 
        encourage the candidate to contact HR directly or apply for more details.
        
        Big Kahuna Burger is a fast-casual restaurant chain known for:
        - High-quality, fresh ingredients
        - Exceptional customer service
        - Team-oriented work environment
        - Growth opportunities for dedicated employees
        - Competitive compensation and benefits
        """
        
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add chat history if provided
        if chat_history:
            messages.extend(chat_history[-10:])  # Keep last 10 messages for context
        
        # Add job context if provided
        if job_info:
            job_context = f"""
            Current job being discussed:
            Title: {job_info.get('title', 'N/A')}
            Department: {job_info.get('department', 'N/A')}
            Location: {job_info.get('location', 'N/A')}
            Description: {job_info.get('description', 'N/A')}
            Requirements: {job_info.get('requirements', 'N/A')}
            Salary Range: {f"${job_info.get('salary_min', 0):,} - ${job_info.get('salary_max', 0):,}" if job_info.get('salary_min') and job_info.get('salary_max') else 'Contact HR for details'}
            """
            messages.append({"role": "system", "content": job_context})
        
        messages.append({"role": "user", "content": message})
        
        try:
            response = client.chat.completions.create(
                model=openai_config["model"],
                messages=messages,
                temperature=openai_config["temperature"],
                max_tokens=openai_config["max_tokens"]
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"I'm sorry, I'm having trouble responding right now. Please try again or contact our HR team directly. Error: {str(e)}"

    @staticmethod
    def generate_additional_questions(job_description: str, job_requirements: str) -> List[str]:
        """Generate additional screening questions based on job requirements"""
        
        prompt = f"""
        Based on this job posting, generate 3-5 relevant screening questions that would help 
        HR better evaluate candidates. These should be specific to the role and requirements.

        Job Description: {job_description}
        Requirements: {job_requirements}

        The questions should be:
        - Specific to the role and industry
        - Helpful for screening candidates
        - Professional and clear
        - Designed to assess key qualifications

        Please provide each question on a separate line, numbered (1., 2., etc.) or bulleted (-, *, etc.).
        """
        
        try:
            response = client.chat.completions.create(
                model=openai_config["model"],
                messages=[
                    {"role": "system", "content": "You are an HR expert creating screening questions for job applications."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=300
            )
            
            content = response.choices[0].message.content
            
            # Parse questions using regex
            # Look for numbered lists (1., 2., etc.) or bulleted lists (-, *, •, etc.)
            question_patterns = [
                r'^\d+\.\s*(.+\?).*$',  # Numbered questions: "1. Question?"
                r'^\s*[-*•]\s*(.+\?).*$',  # Bulleted questions: "- Question?"
                r'^(.+\?).*$'  # Any line ending with a question mark
            ]
            
            questions = []
            lines = content.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                
                for pattern in question_patterns:
                    match = re.match(pattern, line, re.MULTILINE)
                    if match:
                        question = match.group(1).strip()
                        if question and len(question) > 10:  # Ensure it's a substantial question
                            questions.append(question)
                        break
            
            # If no questions found using patterns, fallback to finding any line with a question mark
            if not questions:
                questions = [line.strip() for line in lines if '?' in line and len(line.strip()) > 10]
            
            # Limit to 5 questions and ensure we have at least some fallback questions
            questions = questions[:5]
            if not questions:
                questions = [
                    "What interests you most about this position?",
                    "How does your experience align with our requirements?",
                    "What are your salary expectations?",
                    "What questions do you have about our company culture?",
                    "When would you be available to start?"
                ]
            
            return questions
        except Exception as e:
            return [
                "What interests you most about this position?",
                "How does your experience align with our requirements?",
                "What are your salary expectations?",
                "What questions do you have about our company culture?",
                "When would you be available to start?"
            ]

    @staticmethod
    def get_client_info() -> Dict:
        """Get information about the configured OpenAI client"""
        return {
            "base_url": openai_config["base_url"],
            "model": openai_config["model"],
            "max_tokens": openai_config["max_tokens"],
            "temperature": openai_config["temperature"],
            "timeout": openai_config["timeout"],
            "max_retries": openai_config["max_retries"]
        } 