"""
PII (Personally Identifiable Information) masking service.
"""
import re
from typing import Any, Dict, List, Optional


class PIIMaskingService:
    """Service for masking PII data in text content."""
    
    # Common PII patterns
    EMAIL_PATTERN = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    PHONE_PATTERN = r'(\+?7|8)?[\s\-]?\(?[0-9]{3}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}'
    PASSPORT_PATTERN = r'\b\d{4}\s?\d{6}\b'
    SNILS_PATTERN = r'\b\d{3}-\d{3}-\d{3}\s\d{2}\b'
    CARD_PATTERN = r'\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b'
    
    # Russian names patterns (common first/last names)
    RUSSIAN_NAMES = [
        'Александр', 'Алексей', 'Андрей', 'Анна', 'Владимир', 'Дмитрий', 'Елена', 'Иван',
        'Ирина', 'Мария', 'Михаил', 'Наталья', 'Николай', 'Ольга', 'Павел', 'Сергей',
        'Татьяна', 'Юрий', 'Екатерина', 'Александрова', 'Алексеева', 'Андреева', 'Владимирова',
        'Дмитриева', 'Иванова', 'Иванов', 'Петров', 'Сидоров', 'Козлов', 'Морозов', 'Новиков'
    ]
    
    @classmethod
    def mask_email(cls, text: str) -> str:
        """Mask email addresses in text."""
        def replace_email(match):
            email = match.group(0)
            local, domain = email.split('@')
            masked_local = local[:2] + '*' * (len(local) - 2) if len(local) > 2 else local[0] + '*'
            return f"{masked_local}@{domain}"
        
        return re.sub(cls.EMAIL_PATTERN, replace_email, text, flags=re.IGNORECASE)
    
    @classmethod
    def mask_phone(cls, text: str) -> str:
        """Mask phone numbers in text."""
        def replace_phone(match):
            phone = match.group(0)
            # Keep first 3 and last 2 digits, mask the rest
            if len(phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')) >= 10:
                return phone[:3] + '***' + phone[-2:]
            return '***'
        
        return re.sub(cls.PHONE_PATTERN, replace_phone, text)
    
    @classmethod
    def mask_passport(cls, text: str) -> str:
        """Mask passport numbers in text."""
        def replace_passport(match):
            passport = match.group(0)
            return passport[:4] + ' ******'
        
        return re.sub(cls.PASSPORT_PATTERN, replace_passport, text)
    
    @classmethod
    def mask_snils(cls, text: str) -> str:
        """Mask SNILS numbers in text."""
        def replace_snils(match):
            snils = match.group(0)
            return '***-***-*** **'
        
        return re.sub(cls.SNILS_PATTERN, replace_snils, text)
    
    @classmethod
    def mask_card(cls, text: str) -> str:
        """Mask credit card numbers in text."""
        def replace_card(match):
            card = match.group(0)
            return '**** **** **** ' + card[-4:]
        
        return re.sub(cls.CARD_PATTERN, replace_card, text)
    
    @classmethod
    def mask_names(cls, text: str) -> str:
        """Mask Russian names in text."""
        masked_text = text
        for name in cls.RUSSIAN_NAMES:
            # Case-insensitive replacement
            pattern = re.escape(name)
            masked_text = re.sub(
                pattern, 
                lambda m: m.group(0)[0] + '*' * (len(m.group(0)) - 1),
                masked_text, 
                flags=re.IGNORECASE
            )
        return masked_text
    
    @classmethod
    def mask_pii(cls, text: str, mask_names: bool = True) -> str:
        """
        Mask all PII in text content.
        
        Args:
            text: Text content to mask
            mask_names: Whether to mask names (default: True)
            
        Returns:
            Text with PII masked
        """
        if not text or not isinstance(text, str):
            return text
        
        masked_text = text
        
        # Apply all masking functions
        masked_text = cls.mask_email(masked_text)
        masked_text = cls.mask_phone(masked_text)
        masked_text = cls.mask_passport(masked_text)
        masked_text = cls.mask_snils(masked_text)
        masked_text = cls.mask_card(masked_text)
        
        if mask_names:
            masked_text = cls.mask_names(masked_text)
        
        return masked_text
    
    @classmethod
    def mask_application_data(cls, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mask PII in application data dictionary.
        
        Args:
            application_data: Application data dictionary
            
        Returns:
            Application data with PII masked
        """
        if not isinstance(application_data, dict):
            return application_data
        
        masked_data = application_data.copy()
        
        # Fields that commonly contain PII
        pii_fields = [
            'cover_letter', 'additional_answers', 'cv_summary', 
            'chat_summary', 'interview_prompt'
        ]
        
        for field in pii_fields:
            if field in masked_data and isinstance(masked_data[field], str):
                masked_data[field] = cls.mask_pii(masked_data[field])
        
        # Mask additional_answers if it's a dict
        if 'additional_answers' in masked_data and isinstance(masked_data['additional_answers'], dict):
            for key, value in masked_data['additional_answers'].items():
                if isinstance(value, str):
                    masked_data['additional_answers'][key] = cls.mask_pii(value)
        
        return masked_data
    
    @classmethod
    def is_pii_present(cls, text: str) -> bool:
        """
        Check if text contains PII.
        
        Args:
            text: Text to check
            
        Returns:
            True if PII is detected, False otherwise
        """
        if not text or not isinstance(text, str):
            return False
        
        # Check for various PII patterns
        patterns = [
            cls.EMAIL_PATTERN,
            cls.PHONE_PATTERN,
            cls.PASSPORT_PATTERN,
            cls.SNILS_PATTERN,
            cls.CARD_PATTERN
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        
        # Check for Russian names
        for name in cls.RUSSIAN_NAMES:
            if re.search(re.escape(name), text, re.IGNORECASE):
                return True
        
        return False


# Global instance
pii_masking_service = PIIMaskingService()
