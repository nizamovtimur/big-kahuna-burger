# 🍔 Big Kahuna Burger HR Platform

**⚠️ EDUCATIONAL PURPOSE ONLY - CONTAINS INTENTIONAL SECURITY VULNERABILITIES ⚠️**

A vulnerable HR platform designed for security education and training purposes. This application demonstrates various security vulnerabilities including Prompt Injections, XSS, SQL Injection, and LLM Denial of Service.

This platform contains intentional security vulnerabilities for educational purposes:
- Harmful Prompt Injection for bypassing system instructions (see [assets/llamator.ipynb](assets/llamator.ipynb))
- Indirect Prompt Injection attacks via malicious CV (see [assets/CV](assets/CV))
- Cross-Site Scripting (In Progress)
- SQL Injection (TODO)
- MCP Data Leakage (?)
- System Prompt Leakage (see [assets/llamator.ipynb](assets/llamator.ipynb))
- Denial of Service (see [assets/llamator.ipynb](assets/llamator.ipynb))

## 🏗️ Architecture

- **Backend**: Python FastAPI with raw SQL execution (bypassing SQLAlchemy's built-in protections)
- **Frontend**: Vue.js 3 with unsafe content rendering
- **Database**: PostgreSQL with sample data
- **AI Multiagent**: CrewAI multiagent connected to OpenAI-compatible API
- **Reverse Proxy**: Nginx

> **Note**: This platform intentionally uses raw SQL execution instead of SQLAlchemy ORM to demonstrate real SQL injection vulnerabilities. In production, always use parameterized queries!

## 🎯 Features

### Candidate Interface
- Browse job openings
- AI-powered agentic chat with file upload for CVs

### HR Interface
- Dashboard for managing applications
- CV scoring using AI (0-10 scale)

## 🔧 Setup Instructions

### Prerequisites

- Docker and Docker Compose
- OpenAI API key (for AI features)

### Quick Start

1. **Clone the repository**
```bash
git clone https://github.com/nizamovtimur/big-kahuna-burger.git
cd big-kahuna-burger
```

2. **Set up environment variables in .env file**
```bash
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4.1-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

3. **Start the application**
```bash
docker-compose --env-file .env up -d --build
```

4. **Access the application: http://localhost:8080**

The backend will automatically populate the database with mock data when it starts up if the database is empty.

### Test Accounts

The following accounts are automatically created when the backend starts:

**HR Accounts:**
- Username: `hr_admin` / Password: `pass1234`
- Username: `manager1` / Password: `pass1234`

**Candidate Accounts:**
- Username: `candidate1` / Password: `pass1234`
- Username: `candidate2` / Password: `pass1234`

**Test Account:**
- Username: `testuser` / Password: `pass1234`

## 📄 License

This project is licensed under the Apache 2.0 License - see the LICENSE file for details.

## ⚠️ Disclaimer

This software is provided for educational and research purposes only. The authors are not responsible for any misuse of this software. Do not use this software to attack systems you do not own or have explicit permission to test.
