# Big Kahuna Burger HR Platform

A comprehensive HR platform for Big Kahuna Burger featuring AI-powered candidate interactions, job management, and application processing.

## 🚀 Features

### Core Functionality
- **Employee Data Management**: Centralized repository for HR staff information
- **Job Openings Management**: Create, update, and manage job postings
- **Applicant Processing**: Handle candidate applications with AI-powered resume analysis
- **AI-Powered Chatbot**: Interactive assistant for candidates to learn about positions and company culture

### Two-Interface Design
1. **Candidate Interface**: 
   - Browse available job openings
   - Chat with AI assistant about jobs and company
   - Submit applications with resume analysis
   
2. **HR Interface**: 
   - Personal dashboard with metrics and analytics
   - Manage job postings and applications
   - Review candidate applications with AI insights

### AI Capabilities
- **Resume Analysis**: Automatic matching of resumes to job requirements with scoring
- **Conversational AI**: Interactive chatbot for candidate support
- **Additional Information Collection**: AI-generated screening questions

## 🛠 Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: Database ORM
- **PostgreSQL**: Primary database
- **OpenAI API**: AI-powered features
- **JWT Authentication**: Secure token-based auth
- **Redis**: Caching and session storage (optional)

### Frontend
- **Vue.js 3**: Progressive JavaScript framework
- **Bootstrap 5**: UI component library
- **Vuex**: State management
- **Vue Router**: Client-side routing
- **Axios**: HTTP client

### Infrastructure
- **Docker & Docker Compose**: Containerized deployment
- **Nginx**: Reverse proxy and load balancer
- **PostgreSQL**: Database service
- **Redis**: Caching service

## 🔒 Security Features

- **Environment Variables**: Secure configuration management with python-dotenv
- **Rate Limiting**: API protection against abuse
- **CORS Protection**: Configurable cross-origin resource sharing
- **Security Headers**: XSS, CSRF, and clickjacking protection
- **SSL/TLS**: HTTPS encryption in production
- **Input Validation**: Comprehensive data validation
- **Authentication**: JWT-based secure authentication

## 📦 Project Structure

```
big-kahuna-burger-hr-platform/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Database models
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── schemas/        # Pydantic schemas
│   │   └── main.py         # FastAPI app
│   ├── tests/              # Unit tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # Vue.js frontend
│   ├── src/
│   │   ├── components/     # Vue components
│   │   ├── views/          # Page components
│   │   ├── router/         # Route configuration
│   │   └── store/          # Vuex store
│   ├── package.json        # Node dependencies
│   └── Dockerfile
├── nginx/                  # Nginx configuration
│   └── nginx.conf         # Production proxy config
├── scripts/               # Utility scripts
│   ├── generate-secrets.py # Security secret generator
│   └── init-db.sh         # Database initialization
├── docker-compose.yml     # Multi-service setup
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
└── README.md
```

## 🚀 Quick Start

### Prerequisites
- Docker and Docker Compose
- OpenAI API key
- Python 3.11+ (for local development)
- Node.js 18+ (for local development)

### 🔐 Security Setup (IMPORTANT!)

1. **Generate Secure Secrets**:
   ```bash
   python scripts/generate-secrets.py
   ```

2. **Create Environment File**:
   ```bash
   cp .env.example .env
   ```

3. **Configure Your Secrets**:
   Edit `.env` and add your secrets (use output from step 1):
   ```env
   # Required secrets
   SECRET_KEY=your-generated-secret-key-here
   OPENAI_API_KEY=sk-your-openai-api-key-here
   POSTGRES_PASSWORD=your-secure-db-password
   
   # Optional but recommended
   REDIS_PASSWORD=your-redis-password
   ```

   ⚠️ **SECURITY WARNING**: Never commit your `.env` file to version control!

### Running with Docker Compose

1. **Development Mode**:
   ```bash
   docker-compose up -d
   ```

2. **Production Mode**:
   ```bash
   docker-compose --profile production up -d
   ```

3. **Access the application**:
   - **Frontend**: http://localhost:3000
   - **Backend API**: http://localhost:8000
   - **API Documentation**: http://localhost:8000/docs
   - **Database**: PostgreSQL on port 5432

### Manual Setup (Development)

#### Backend Setup
```bash
cd backend
pip install -r requirements.txt

# Create .env file with required variables
cp ../.env.example .env
# Edit .env with your configuration

# Run the application
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend
npm install

# Set environment variables
echo "VUE_APP_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run serve
```

#### Database Setup
```bash
# Using Docker
docker run -d \
  --name bigkahuna-postgres \
  -e POSTGRES_DB=bigkahuna_hr \
  -e POSTGRES_USER=user \
  -e POSTGRES_PASSWORD=your-secure-password \
  -p 5432:5432 \
  postgres:15
```

## 🧪 Testing

### Backend Tests (TDD)
```bash
cd backend
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_models.py -v
```

### Test Coverage
```bash
cd backend
pytest --cov=app --cov-report=term-missing
```

## 🔧 Configuration

### Environment Variables

#### Required Variables
- `SECRET_KEY`: JWT signing secret (generate with provided script)
- `OPENAI_API_KEY`: Your OpenAI API key
- `DATABASE_URL`: PostgreSQL connection string
- `POSTGRES_PASSWORD`: Database password

#### Optional Variables
- `ENVIRONMENT`: development/staging/production
- `DEBUG`: Enable debug mode (true/false)
- `CORS_ORIGINS`: Allowed CORS origins (comma-separated)
- `RATE_LIMIT_PER_MINUTE`: API rate limiting
- `REDIS_URL`: Redis connection string
- `LOG_LEVEL`: Logging level (DEBUG/INFO/WARNING/ERROR)

See `.env.example` for complete configuration options.

### Database Models
- **Employee**: HR staff users with role-based access
- **Job**: Job postings with AI-generated questions
- **Applicant**: Candidate profiles with resume storage
- **Application**: Job applications with AI analysis
- **ChatSession**: AI conversation history

## 📚 API Documentation

The API documentation is automatically generated and available at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Authentication
- `POST /auth/login` - HR staff login
- `POST /auth/register` - HR staff registration
- `GET /auth/me` - Get current user info

#### Jobs Management
- `GET /jobs/` - List all jobs (public)
- `POST /jobs/` - Create new job (HR only)
- `GET /jobs/{id}` - Get job details
- `PUT /jobs/{id}` - Update job (HR only)

#### Applicants & Applications
- `POST /applicants/` - Create applicant profile
- `POST /applicants/{id}/apply` - Submit job application
- `GET /applications/` - List applications (HR only)

#### AI Features
- `POST /chat/` - Chat with AI assistant
- `GET /chat/history` - Get chat history

## 🎯 Usage Guide

### For Candidates
1. **Browse Jobs**: Visit the homepage or jobs page to see available positions
2. **Chat with AI**: Use the candidate portal to ask questions about jobs, benefits, and company culture
3. **Apply**: Submit applications directly through the platform with resume text
4. **Get AI Analysis**: Resumes are automatically analyzed for job fit

### For HR Staff
1. **Login**: Access the HR portal with your credentials
2. **Dashboard**: View application metrics and recent activity
3. **Manage Jobs**: Create, edit, and manage job postings
4. **Review Applications**: Access candidate applications with AI insights
5. **Analyze Fit**: Use AI-generated match scores to evaluate candidates

## 🚢 Deployment

### Production Deployment

1. **Prepare Environment**:
   ```bash
   # Generate production secrets
   python scripts/generate-secrets.py
   
   # Create production .env
   cp .env.example .env
   # Configure with production values
   ```

2. **Deploy with Docker**:
   ```bash
   # Build and deploy
   docker-compose --profile production up -d
   
   # View logs
   docker-compose logs -f
   ```

3. **SSL Certificate Setup**:
   ```bash
   # Place SSL certificates in nginx/ssl/
   # - fullchain.pem
   # - privkey.pem
   ```

### Database Migrations
```bash
cd backend
# Install alembic
pip install alembic

# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

### Production Checklist
- [ ] Generate secure secrets
- [ ] Configure SSL certificates
- [ ] Set up database backups
- [ ] Configure monitoring
- [ ] Set up log rotation
- [ ] Configure firewall rules
- [ ] Test disaster recovery

## 🔐 Security Best Practices

### Development
- Never commit `.env` files
- Use the secret generator script
- Rotate secrets regularly
- Enable rate limiting
- Validate all inputs

### Production
- Use HTTPS everywhere
- Configure proper CORS origins
- Set up monitoring and alerting
- Regular security updates
- Database encryption at rest
- Network security groups
- Regular backups

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Write tests for new features
4. Ensure all tests pass
5. Follow security guidelines
6. Submit a pull request

### Development Guidelines
- Follow TDD principles
- Write comprehensive tests
- Use meaningful commit messages
- Document new features
- Follow security best practices

## 📊 Monitoring & Maintenance

### Health Checks
- Backend: `GET /health`
- Database: Built-in PostgreSQL health checks
- Frontend: HTTP response monitoring

### Logging
- Application logs: `/app/logs/`
- Nginx logs: `/var/log/nginx/`
- Database logs: PostgreSQL standard logging

### Backup Strategy
- Database: Automated PostgreSQL backups
- Files: Regular volume backups
- Configuration: Version-controlled infrastructure

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support and questions:
- Check the API documentation at `/docs`
- Review the test files for usage examples
- Check environment variable configuration
- Verify Docker container health
- Create an issue in the repository

## 🔧 Troubleshooting

### Common Issues

1. **OpenAI API Errors**:
   - Verify your API key is correct
   - Check API usage limits
   - Ensure sufficient credits

2. **Database Connection Issues**:
   - Check database container is running
   - Verify connection string
   - Check database credentials

3. **Frontend Build Issues**:
   - Clear node_modules and reinstall
   - Check Node.js version compatibility
   - Verify environment variables

4. **Docker Issues**:
   - Check Docker daemon is running
   - Verify sufficient disk space
   - Check port conflicts

---

**Built with ❤️ and 🔒 Security for Big Kahuna Burger** 