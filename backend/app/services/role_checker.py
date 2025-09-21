"""
Role-based access control service.
"""
from typing import Any, Optional
from sqlalchemy.orm import Session
from ..models.models import User
from ..database import execute_raw_query


class RoleChecker:
    """Service for checking user roles and permissions."""
    
    @classmethod
    def is_hr_user(cls, user: User) -> bool:
        """
        Check if user has HR privileges.
        
        Args:
            user: User object to check
            
        Returns:
            True if user is HR, False otherwise
        """
        if not user:
            return False
        
        return getattr(user, 'is_hr', False)
    
    @classmethod
    def can_execute_sql(cls, user: User) -> bool:
        """
        Check if user can execute SQL queries.
        
        Args:
            user: User object to check
            
        Returns:
            True if user can execute SQL, False otherwise
        """
        return cls.is_hr_user(user)
    
    @classmethod
    def can_access_hr_panel(cls, user: User) -> bool:
        """
        Check if user can access HR panel.
        
        Args:
            user: User object to check
            
        Returns:
            True if user can access HR panel, False otherwise
        """
        return cls.is_hr_user(user)
    
    @classmethod
    def can_view_applications(cls, user: User, application_user_id: Optional[int] = None) -> bool:
        """
        Check if user can view applications.
        HR users can view all applications, regular users can only view their own.
        
        Args:
            user: User object to check
            application_user_id: ID of the user who created the application
            
        Returns:
            True if user can view the application, False otherwise
        """
        if not user:
            return False
        
        # HR users can view all applications
        if cls.is_hr_user(user):
            return True
        
        # Regular users can only view their own applications
        return application_user_id is None or user.id == application_user_id
    
    @classmethod
    def can_modify_application(cls, user: User, application_user_id: Optional[int] = None) -> bool:
        """
        Check if user can modify applications.
        HR users can modify all applications, regular users can only modify their own.
        
        Args:
            user: User object to check
            application_user_id: ID of the user who created the application
            
        Returns:
            True if user can modify the application, False otherwise
        """
        if not user:
            return False
        
        # HR users can modify all applications
        if cls.is_hr_user(user):
            return True
        
        # Regular users can only modify their own applications
        return application_user_id is None or user.id == application_user_id
    
    @classmethod
    def execute_safe_sql(cls, user: User, sql_query: str, db: Session) -> Any:
        """
        Execute SQL query only if user has proper permissions.
        
        Args:
            user: User object to check
            sql_query: SQL query to execute
            db: Database session
            
        Returns:
            Query result if user has permissions
            
        Raises:
            PermissionError: If user doesn't have SQL execution permissions
        """
        if not cls.can_execute_sql(user):
            raise PermissionError("User does not have permission to execute SQL queries")
        
        return execute_raw_query(sql_query)


# Global instance
role_checker = RoleChecker()
