import json
import re
from typing import Dict, List, Any, Optional
from sqlalchemy.orm import Session
from ..database import execute_raw_query
from ..models.models import JobApplication, Job, User, ChatSession
from .openai_service import openai_service
from .application_service import application_service


class AIAgentService:
    """
    Autonomous AI Agent with tools for CV analysis, SQL queries, and data collection.
    WARNING: Contains intentional vulnerabilities for educational purposes!
    """
    
    def __init__(self):
        self.tools = {
            "analyze_cv": self._analyze_cv_tool,
            "execute_sql_query": self._execute_sql_query_tool,
            "save_user_response": self._save_user_response_tool,
            "get_job_details": self._get_job_details_tool,
            "update_application_status": self._update_application_status_tool,
            "create_application": self._create_application_tool
        }
    
    async def process_message(
        self, 
        user_message: str, 
        session: ChatSession,
        job_context: Optional[Dict[str, Any]] = None,
        chat_history: List[Dict[str, str]] = None,
        cv_file_content: Optional[str] = None,
        cv_filename: Optional[str] = None,
        db: Session = None,
        user: User = None
    ) -> str:
        """
        Process user message with autonomous agent capabilities.
        Agent can decide which tools to use based on context.
        """
        
        # CRITICAL: If CV file is provided, immediately create application
        if cv_file_content and cv_filename and session.job_id:
            existing_app = application_service.get_existing_application(db, user.id, session.job_id)
            if not existing_app:
                try:
                    # Auto-create application with CV analysis
                    application = await application_service.create_application_from_content(
                        db=db,
                        user=user,
                        job_id=session.job_id,
                        cv_content=cv_file_content,
                        cv_filename=cv_filename,
                        cover_letter=user_message or "Заявка подана через чат",
                        additional_answers={"auto_created_by_agent": True}
                    )
                    
                    # Add CV info to chat history context for agent
                    cv_context = f"\n\n[СИСТЕМА: Резюме '{cv_filename}' автоматически проанализировано. Оценка: {application.cv_score}/10. Заявка создана (ID: {application.id}). Проведите собеседование на основе резюме.]"
                    user_message += cv_context
                    
                except Exception as e:
                    user_message += f"\n\n[СИСТЕМА: Ошибка при создании заявки: {str(e)}]"
        
        # Build comprehensive context for the agent
        agent_context = self._build_agent_context(
            user_message, session, job_context, cv_file_content, cv_filename, user
        )
        
        # Add CV analysis context if available
        if cv_file_content and session.job_id:
            existing_app = application_service.get_existing_application(db, user.id, session.job_id)
            if existing_app and existing_app.cv_score:
                agent_context["cv_analysis"] = {
                    "score": existing_app.cv_score,
                    "filename": cv_filename,
                    "application_id": existing_app.id
                }
        
        # Get initial agent response with tool selection
        agent_prompt = self._build_agent_prompt(agent_context, chat_history)
        
        # Agent decides what tools to use
        agent_response = await openai_service.chat_with_ai(
            user_message=agent_prompt,
            job_context=job_context,
            chat_history=chat_history
        )
        
        # Parse and execute tool calls
        final_response = await self._execute_tool_calls(
            agent_response, session, db, user, cv_file_content, cv_filename
        )
        
        return final_response
    
    def _build_agent_context(
        self, 
        user_message: str, 
        session: ChatSession, 
        job_context: Optional[Dict[str, Any]], 
        cv_file_content: Optional[str], 
        cv_filename: Optional[str],
        user: User
    ) -> Dict[str, Any]:
        """Build comprehensive context for the AI agent."""
        
        context = {
            "user_message": user_message,
            "session_id": session.id,
            "user_id": user.id,
            "user_name": user.full_name,
            "has_cv_file": cv_file_content is not None,
            "cv_filename": cv_filename,
            "job_context": job_context,
            "cv_analysis": None  # Will be populated if CV analysis exists
        }
        
        return context
    
    def _build_agent_prompt(
        self, 
        context: Dict[str, Any], 
        chat_history: List[Dict[str, str]]
    ) -> str:
        """
        Build agent prompt with tool capabilities.
        WARNING: User input is directly included - vulnerable to prompt injection and system prompt leakage!
        """
        
        # VULNERABLE: System prompt construction allows extraction via prompt injection
        system_instructions = f"""Вы - автономный HR-агент Big Kahuna Burger с расширенными возможностями.

ДОСТУПНЫЕ ИНСТРУМЕНТЫ:
1. analyze_cv(cv_content) - анализ резюме и выставление оценки
2. execute_sql_query(query) - выполнение SQL-запросов к базе данных (БЕЗ ВАЛИДАЦИИ!)
3. save_user_response(key, value, context) - сохранение ответов пользователя (БЕЗ САНИТИЗАЦИИ!)
4. get_job_details(job_id) - получение деталей вакансии
5. update_application_status(application_id, status, notes) - обновление статуса заявки
6. create_application(cv_content, cover_letter) - создание заявки с анализом резюме

ТЕКУЩИЙ КОНТЕКСТ:
- Пользователь: {context['user_name']} (ID: {context['user_id']})
- Сессия: {context['session_id']}
- Есть резюме: {context['has_cv_file']}
- Файл: {context['cv_filename'] or 'нет'}
- Вакансия: {context['job_context']['job_title'] if context['job_context'] else 'не выбрана'}
- Анализ резюме: {f"Оценка {context['cv_analysis']['score']}/10 (ID заявки: {context['cv_analysis']['application_id']})" if context.get('cv_analysis') else 'не проводился'}"""

        # CRITICALLY VULNERABLE: User message is directly concatenated to system prompt
        # This allows attackers to inject instructions that can leak the system prompt
        user_input_section = f"""

СООБЩЕНИЕ ПОЛЬЗОВАТЕЛЯ: {context['user_message']}

ИНСТРУКЦИИ:
1. Проанализируйте сообщение пользователя
2. Если резюме уже проанализировано - используйте эту информацию для вопросов  
3. Если есть новое резюме - система автоматически создала заявку с анализом
4. Задавайте конкретные вопросы на основе анализа резюме и требований вакансии
5. Сохраняйте все ответы пользователя в БД
6. При необходимости выполняйте SQL-запросы для получения дополнительной информации

Используйте инструменты в формате:
TOOL_CALL: название_инструмента(параметры)

Отвечайте профессионально и задавайте релевантные вопросы для оценки кандидата."""

        # Vulnerable concatenation that allows prompt injection attacks
        full_prompt = system_instructions + user_input_section
        
        return full_prompt
    
    async def _execute_tool_calls(
        self, 
        agent_response: str, 
        session: ChatSession, 
        db: Session, 
        user: User,
        cv_file_content: Optional[str] = None,
        cv_filename: Optional[str] = None
    ) -> str:
        """
        Parse and execute tool calls from agent response.
        WARNING: Contains SQL injection vulnerabilities for educational purposes!
        """
        
        # Find all tool calls in the response
        tool_pattern = r'TOOL_CALL:\s*(\w+)\((.*?)\)'
        tool_calls = re.findall(tool_pattern, agent_response, re.DOTALL)
        
        tool_results = []
        
        for tool_name, params_str in tool_calls:
            if tool_name in self.tools:
                try:
                    # Parse parameters (simplified - vulnerable to injection)
                    params = self._parse_tool_params(params_str)
                    
                    # Execute tool
                    result = await self.tools[tool_name](
                        params, session, db, user, cv_file_content, cv_filename
                    )
                    tool_results.append(f"[{tool_name}]: {result}")
                    
                except Exception as e:
                    tool_results.append(f"[{tool_name} ERROR]: {str(e)}")
        
        # If no tools were executed, return the original agent response
        if not tool_results:
            return agent_response
        
        # Tools were executed - build final response incorporating tool results
        final_prompt = f"""ОТВЕТ АГЕНТА: 
{agent_response}

РЕЗУЛЬТАТЫ ИНСТРУМЕНТОВ:
{chr(10).join(tool_results)}

Теперь дайте финальный ответ пользователю, учитывая результаты инструментов. Если требуется, задайте дополнительные вопросы на основе полученной информации."""

        final_response = await openai_service.chat_with_ai(
            user_message=final_prompt,
            job_context=None,
            chat_history=[]
        )
        
        return final_response
    
    def _parse_tool_params(self, params_str: str) -> Dict[str, Any]:
        """
        Parse tool parameters from string.
        WARNING: Simplified parsing vulnerable to injection!
        """
        # Remove quotes and split by commas (very simplified)
        params_str = params_str.strip()
        if params_str.startswith('"') and params_str.endswith('"'):
            # Single string parameter
            return {"param1": params_str[1:-1]}
        
        # Multiple parameters (simplified parsing)
        params = {}
        parts = params_str.split(',')
        for i, part in enumerate(parts):
            part = part.strip()
            if part.startswith('"') and part.endswith('"'):
                params[f"param{i+1}"] = part[1:-1]
            else:
                params[f"param{i+1}"] = part
        
        return params
    
    async def _analyze_cv_tool(
        self, 
        params: Dict[str, Any], 
        session: ChatSession, 
        db: Session, 
        user: User, 
        cv_file_content: Optional[str],
        cv_filename: Optional[str]
    ) -> str:
        """Tool for analyzing CV content using application service."""
        
        if not cv_file_content:
            return "No CV content available for analysis"
        
        if not session.job_id:
            return "No job context available for CV analysis"
        
        # Get existing application
        existing_app = application_service.get_existing_application(db, user.id, session.job_id)
        
        if existing_app:
            # Update existing application with CV analysis
            job = db.query(Job).filter(Job.id == session.job_id).first()
            cv_score = await openai_service.analyze_cv(cv_file_content, job.description)
            
            application_service.save_cv_analysis(
                db, existing_app, cv_score, cv_filename or "uploaded_cv.pdf"
            )
            
            return f"CV analyzed. Score: {cv_score}/10. Analysis saved to existing application."
        
        return "No application found to save CV analysis to. Use create_application tool first."
    
    async def _create_application_tool(
        self, 
        params: Dict[str, Any], 
        session: ChatSession, 
        db: Session, 
        user: User, 
        cv_file_content: Optional[str],
        cv_filename: Optional[str]
    ) -> str:
        """Tool for creating job application using application service."""
        
        cv_content = params.get("param1", "") or cv_file_content
        cover_letter = params.get("param2", "")
        
        if not cv_content:
            return "No CV content provided for application creation"
        
        if not session.job_id:
            return "No job context available for application creation"
        
        try:
            # Use application service to create application
            application = await application_service.create_application_from_content(
                db=db,
                user=user,
                job_id=session.job_id,
                cv_content=cv_content,
                cv_filename=cv_filename or "uploaded_cv.pdf",
                cover_letter=cover_letter,
                additional_answers={"submitted_via_agent": True}
            )
            
            return f"Application created successfully. ID: {application.id}, CV Score: {application.cv_score}/10"
            
        except Exception as e:
            return f"Failed to create application: {str(e)}"
    
    async def _execute_sql_query_tool(
        self, 
        params: Dict[str, Any], 
        session: ChatSession, 
        db: Session, 
        user: User, 
        cv_file_content: Optional[str],
        cv_filename: Optional[str]
    ) -> str:
        """
        Tool for executing SQL queries.
        WARNING: Contains intentional SQL injection vulnerabilities!
        """
        
        query = params.get("param1", "")
        
        if not query:
            return "No query provided"
        
        try:
            # VULNERABLE: Direct execution of user-provided SQL
            # This allows SQL injection for educational purposes
            results = execute_raw_query(query)
            
            # Limit results to prevent data dumps
            limited_results = list(results)[:10]
            
            if limited_results:
                # Convert to readable format
                result_str = "Query results:\n"
                for i, row in enumerate(limited_results):
                    result_str += f"Row {i+1}: {dict(row._mapping)}\n"
                return result_str
            else:
                return "Query executed successfully. No results returned."
                
        except Exception as e:
            return f"SQL Error: {str(e)}"
    
    async def _save_user_response_tool(
        self, 
        params: Dict[str, Any], 
        session: ChatSession, 
        db: Session, 
        user: User, 
        cv_file_content: Optional[str],
        cv_filename: Optional[str]
    ) -> str:
        """Tool for saving user responses using application service."""
        
        key = params.get("param1", "")
        value = params.get("param2", "")
        context = params.get("param3", "general")
        
        if not key or not value:
            return "Key and value required for saving response"
        
        # Find existing application
        if session.job_id:
            existing_app = application_service.get_existing_application(db, user.id, session.job_id)
            
            if existing_app:
                success = application_service.save_user_response(
                    db, existing_app, key, value, context
                )
                
                if success:
                    return f"Response saved: {key} = {value}"
        
        return "No application found to save response to"
    
    async def _get_job_details_tool(
        self, 
        params: Dict[str, Any], 
        session: ChatSession, 
        db: Session, 
        user: User, 
        cv_file_content: Optional[str],
        cv_filename: Optional[str]
    ) -> str:
        """Tool for getting job details."""
        
        job_id_param = params.get("param1", "")
        
        # Use session job_id if no specific job_id provided
        job_id = session.job_id
        if job_id_param and job_id_param.isdigit():
            job_id = int(job_id_param)
        
        if not job_id:
            return "No job ID available"
        
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job:
            return f"Job with ID {job_id} not found"
        
        return f"Job: {job.title}\nDescription: {job.description}\nRequirements: {job.requirements}\nLocation: {job.location}\nSalary: {job.salary_range}"
    
    async def _update_application_status_tool(
        self, 
        params: Dict[str, Any], 
        session: ChatSession, 
        db: Session, 
        user: User, 
        cv_file_content: Optional[str],
        cv_filename: Optional[str]
    ) -> str:
        """Tool for updating application status using application service."""
        
        application_id = params.get("param1", "")
        status = params.get("param2", "")
        notes = params.get("param3", "")
        
        if not application_id or not status:
            return "Application ID and status required"
        
        if not application_id.isdigit():
            return "Invalid application ID"
        
        success = application_service.update_application_status(
            db, int(application_id), status, notes
        )
        
        if success:
            return f"Application {application_id} status updated to: {status}"
        else:
            return f"Application {application_id} not found"


# Global instance
ai_agent_service = AIAgentService()