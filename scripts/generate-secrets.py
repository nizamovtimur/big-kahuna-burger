#!/usr/bin/env python3
"""
Security Secret Generator for Big Kahuna Burger HR Platform

This script generates secure secrets for production deployment.
Run this script and copy the output to your .env file.
"""

import secrets
import string
import uuid
from typing import Dict


def generate_secret_key(length: int = 32) -> str:
    """Generate a secure secret key for JWT signing"""
    return secrets.token_urlsafe(length)


def generate_password(length: int = 16) -> str:
    """Generate a secure password"""
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    password = ''.join(secrets.choice(alphabet) for _ in range(length))
    return password


def generate_uuid() -> str:
    """Generate a UUID4"""
    return str(uuid.uuid4())


def generate_api_key(length: int = 24) -> str:
    """Generate an API key"""
    return secrets.token_hex(length)


def main():
    """Generate all required secrets"""
    print("=" * 70)
    print("🔐 BIG KAHUNA BURGER HR PLATFORM - SECURITY SECRETS GENERATOR")
    print("=" * 70)
    print()
    print("⚠️  IMPORTANT SECURITY NOTES:")
    print("   • Store these secrets securely in your .env file")
    print("   • Never commit secrets to version control")
    print("   • Use different secrets for each environment")
    print("   • Rotate secrets regularly in production")
    print()
    print("=" * 70)
    print()
    
    secrets_config: Dict[str, str] = {
        "# JWT Secret Key (32+ characters)": "",
        "SECRET_KEY": generate_secret_key(32),
        "": "",
        "# Database Password": "",
        "POSTGRES_PASSWORD": generate_password(16),
        "": "",
        "# Redis Password (if using Redis)": "",
        "REDIS_PASSWORD": generate_password(12),
        "": "",
        "# Application Instance ID": "",
        "APP_INSTANCE_ID": generate_uuid(),
        "": "",
        "# API Keys for external services": "",
        "INTERNAL_API_KEY": generate_api_key(),
        "": "",
        "# Session Secret": "",
        "SESSION_SECRET": generate_secret_key(24),
    }
    
    for key, value in secrets_config.items():
        if key.startswith("#") or key == "":
            print(key)
        else:
            print(f"{key}={value}")
    
    print()
    print("=" * 70)
    print("🔐 NEXT STEPS:")
    print("   1. Copy the secrets above to your .env file")
    print("   2. Add your OPENAI_API_KEY, OPENAI_BASE_URL, OPENAI_MODEL")
    print("   3. Configure other environment-specific variables")
    print("   4. Ensure .env is in your .gitignore file")
    print("   5. Back up your .env file securely")
    print("=" * 70)


if __name__ == "__main__":
    main() 