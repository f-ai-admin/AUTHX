# F-AI AuthX: Technical Documentation
## Architecture, Implementation & Integration Guide

---

## 📋 Table of Contents
1. [System Architecture](#system-architecture)
2. [Technology Stack](#technology-stack)
3. [Database Schema](#database-schema)
4. [API Documentation](#api-documentation)
5. [Security Architecture](#security-architecture)
6. [Development Setup](#development-setup)
7. [Deployment Guide](#deployment-guide)
8. [Testing Strategy](#testing-strategy)
9. [Performance Optimization](#performance-optimization)
10. [Monitoring & Logging](#monitoring--logging)

---

## 🏗️ System Architecture

### High-Level Architecture Overview

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Application<br/>React.js]
        B[Mobile App<br/>React Native]
    end

    subgraph "API Gateway"
        C[API Gateway<br/>FastAPI]
        D[Load Balancer]
    end

    subgraph "Service Layer"
        E[Document Service<br/>OCR Processing]
        F[Face Recognition Service<br/>AI/ML Models]
        G[Biometric Service<br/>Verification]
        H[Auth Service<br/>JWT Management]
    end

    subgraph "Data Layer"
        I[Supabase PostgreSQL<br/>Primary Database]
        J[Redis Cache<br/>Session Store]
        K[Object Storage<br/>File Management]
    end

    subgraph "External Services"
        L[Aadhar Verification API]
        M[PAN Validation Service]
        N[SMS Gateway]
        O[Email Service]
    end

    A --> C
    B --> C
    C --> D
    D --> E
    D --> F
    D --> G
    D --> H
    E --> I
    F --> I
    G --> I
    H --> J
    E --> K
    F --> K
    E --> L
    E --> M
    H --> N
    H --> O
```

### Microservices Architecture

The system follows a microservices architecture with the following core services:

#### 1. Document Verification Service
- **Responsibility**: Document processing, OCR, and validation
- **Technology**: Python, OpenCV, Tesseract OCR
- **Key Features**:
  - Multi-format document parsing
  - Real-time OCR processing
  - Document authenticity verification
  - Data extraction and validation

#### 2. Face Recognition Service
- **Responsibility**: Face detection, matching, and liveness detection
- **Technology**: Python, Buffalo-L model (InsightFace), OpenCV
- **Key Features**:
  - 3D face mapping
  - Anti-spoofing algorithms
  - Liveness detection
  - Face embedding generation

#### 3. Biometric Service
- **Responsibility**: Fingerprint and iris verification
- **Technology**: Python, Biometric SDKs
- **Key Features**:
  - Fingerprint pattern matching
  - Iris recognition
  - Biometric template generation
  - Secure biometric storage

#### 4. Authentication Service
- **Responsibility**: User authentication and session management
- **Technology**: Python, JWT, OAuth 2.0
- **Key Features**:
  - Multi-factor authentication
  - JWT token management
  - Session handling
  - Password policies

#### 5. Notification Service
- **Responsibility**: SMS, email, and push notifications
- **Technology**: Python, Twilio, SendGrid
- **Key Features**:
  - Multi-channel notifications
  - Template management
  - Delivery tracking
  - Scheduling capabilities

---

## 🛠️ Technology Stack

### Backend Technologies

#### Core Framework
- **FastAPI**: High-performance async web framework
  - Version: 0.104.1+
  - Features: Auto-documentation, type hints, dependency injection
  - Advantages: High performance, modern Python features

#### Database & Storage
- **Supabase**: Backend-as-a-Service with PostgreSQL
  - PostgreSQL 15+ for primary data storage
  - Real-time subscriptions
  - Built-in authentication
  - Row-level security

#### AI/ML Libraries
- **InsightFace**: Face recognition and analysis
  - Buffalo-L model for face detection
  - Face embedding generation
  - Anti-spoofing capabilities

- **OpenCV**: Computer vision operations
  - Image preprocessing
  - Face detection
  - Image enhancement

- **Tesseract OCR**: Text extraction from images
  - Multi-language support
  - High accuracy text recognition
  - Custom training capabilities

#### Security Libraries
- **Cryptography**: Encryption and hashing
- **PyJWT**: JWT token handling
- **Passlib**: Password hashing
- **Python-multipart**: File upload security

### Frontend Technologies

#### Core Framework
- **React.js 18+**: Modern JavaScript library
  - Component-based architecture
  - Virtual DOM for performance
  - Rich ecosystem

#### State Management
- **Context API**: Global state management
- **React Query**: Server state management
- **Local Storage**: Client-side persistence

#### UI/UX Libraries
- **Material-UI**: Component library
- **React Webcam**: Camera integration
- **React Router**: Navigation
- **Axios**: HTTP client

### Development Tools

#### Build & Deployment
- **Docker**: Containerization
- **GitHub Actions**: CI/CD pipeline
- **Nginx**: Reverse proxy
- **Uvicorn**: ASGI server

#### Code Quality
- **Black**: Code formatting
- **Flake8**: Linting
- **MyPy**: Type checking
- **Pytest**: Testing framework

---

## 🗄️ Database Schema

### Entity Relationship Diagram

```mermaid
erDiagram
    USERS ||--o{ DOCUMENTS : uploads
    USERS ||--o{ VERIFICATIONS : undergoes
    DOCUMENTS ||--o{ VERIFICATIONS : used_in
    USERS ||--o{ BIOMETRICS : provides
    VERIFICATIONS ||--o{ BIOMETRICS : includes

    USERS {
        uuid id PK
        string name
        string email UK
        string phone UK
        date dob
        string address
        string created_at
        string updated_at
        string last_login
        boolean email_verified
        boolean phone_verified
    }

    DOCUMENTS {
        uuid id PK
        uuid user_id FK
        string document_type
        string document_number
        string front_image_url
        string back_image_url
        json ocr_data
        boolean is_verified
        string verification_status
        date issued_date
        date expiry_date
        string created_at
        string updated_at
    }

    VERIFICATIONS {
        uuid id PK
        uuid user_id FK
        uuid document_id FK
        string verification_type
        json verification_data
        string status
        float confidence_score
        json face_embeddings
        string rejection_reason
        string created_at
        string completed_at
        string verified_by
    }

    BIOMETRICS {
        uuid id PK
        uuid user_id FK
        uuid verification_id FK
        string biometric_type
        string biometric_data
        json template_data
        float quality_score
        boolean is_verified
        string created_at
        string updated_at
    }

    AUDIT_LOGS {
        uuid id PK
        uuid user_id FK
        string action
        json details
        string ip_address
        string user_agent
        string created_at
    }
```

### Table Definitions

#### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) UNIQUE,
    dob DATE,
    address TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_login TIMESTAMP WITH TIME ZONE,
    email_verified BOOLEAN DEFAULT FALSE,
    phone_verified BOOLEAN DEFAULT FALSE
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_phone ON users(phone);
```

#### Documents Table
```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_type VARCHAR(50) NOT NULL,
    document_number VARCHAR(100),
    front_image_url TEXT NOT NULL,
    back_image_url TEXT,
    ocr_data JSONB,
    is_verified BOOLEAN DEFAULT FALSE,
    verification_status VARCHAR(50) DEFAULT 'pending',
    issued_date DATE,
    expiry_date DATE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_documents_user_id ON documents(user_id);
CREATE INDEX idx_documents_type ON documents(document_type);
CREATE INDEX idx_documents_number ON documents(document_number);
```

#### Verifications Table
```sql
CREATE TABLE verifications (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    document_id UUID REFERENCES documents(id) ON DELETE CASCADE,
    verification_type VARCHAR(50) NOT NULL,
    verification_data JSONB,
    status VARCHAR(50) DEFAULT 'pending',
    confidence_score DECIMAL(5,4),
    face_embeddings JSONB,
    rejection_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE,
    verified_by VARCHAR(255)
);

CREATE INDEX idx_verifications_user_id ON verifications(user_id);
CREATE INDEX idx_verifications_status ON verifications(status);
CREATE INDEX idx_verifications_type ON verifications(verification_type);
```

#### Biometrics Table
```sql
CREATE TABLE biometrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    verification_id UUID REFERENCES verifications(id) ON DELETE CASCADE,
    biometric_type VARCHAR(50) NOT NULL,
    biometric_data TEXT,
    template_data JSONB,
    quality_score DECIMAL(5,4),
    is_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_biometrics_user_id ON biometrics(user_id);
CREATE INDEX idx_biometrics_type ON biometrics(biometric_type);
```

#### Audit Logs Table
```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_created_at ON audit_logs(created_at);
```

---

## 📡 API Documentation

### RESTful API Design

#### Base URL
```
Production: https://api.fai-authx.com/v1
Development: http://localhost:8000/v1
```

#### Authentication
All API requests require JWT authentication:
```http
Authorization: Bearer <jwt_token>
```

### API Endpoints

#### Authentication Endpoints

##### POST /auth/register
Register a new user account.

**Request:**
```json
{
  "name": "John Doe",
  "email": "john.doe@example.com",
  "phone": "+919876543210",
  "dob": "1990-01-01",
  "address": "123 Main St, Mumbai, India"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "user_id": "uuid",
    "message": "User registered successfully",
    "verification_required": true
  }
}
```

##### POST /auth/login
Authenticate user and return JWT token.

**Request:**
```json
{
  "email": "john.doe@example.com",
  "password": "secure_password"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "access_token": "jwt_token",
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
      "id": "uuid",
      "name": "John Doe",
      "email": "john.doe@example.com"
    }
  }
}
```

#### Document Management Endpoints

##### POST /documents/upload
Upload and process identity documents.

**Request (multipart/form-data):**
```
document_type: "aadhar"
front_image: [file]
back_image: [file]
```

**Response:**
```json
{
  "success": true,
  "data": {
    "document_id": "uuid",
    "ocr_data": {
      "name": "John Doe",
      "document_number": "123456789012",
      "dob": "1990-01-01",
      "address": "123 Main St, Mumbai, India"
    },
    "verification_status": "processing",
    "confidence_score": 0.95
  }
}
```

##### GET /documents/{document_id}
Retrieve document details.

**Response:**
```json
{
  "success": true,
  "data": {
    "id": "uuid",
    "document_type": "aadhar",
    "document_number": "123456789012",
    "is_verified": true,
    "verification_status": "approved",
    "ocr_data": {...},
    "created_at": "2024-01-01T10:00:00Z"
  }
}
```

#### Face Recognition Endpoints

##### POST /face/capture
Capture and process face image.

**Request (multipart/form-data):**
```
face_image: [file]
live_video: [file]  // For liveness detection
```

**Response:**
```json
{
  "success": true,
  "data": {
    "face_id": "uuid",
    "face_embeddings": [0.1, 0.2, ...],
    "liveness_score": 0.98,
    "quality_score": 0.95,
    "verification_status": "processing"
  }
}
```

##### POST /face/verify
Verify face against document photo.

**Request:**
```json
{
  "document_id": "uuid",
  "face_image": "base64_encoded_image"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "match_score": 0.92,
    "verification_status": "approved",
    "confidence_level": "high",
    "processing_time_ms": 1500
  }
}
```

#### Biometric Endpoints

##### POST /biometrics/capture
Capture biometric data.

**Request:**
```json
{
  "biometric_type": "fingerprint",
  "biometric_data": "base64_encoded_data",
  "quality_threshold": 0.8
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "biometric_id": "uuid",
    "quality_score": 0.92,
    "template_data": {...},
    "verification_status": "processing"
  }
}
```

#### Verification Endpoints

##### POST /verification/start
Initiate comprehensive verification process.

**Request:**
```json
{
  "verification_type": "comprehensive",
  "document_ids": ["uuid1", "uuid2"],
  "include_biometrics": true,
  "biometric_types": ["fingerprint", "iris"]
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "verification_id": "uuid",
    "status": "initiated",
    "estimated_duration_minutes": 10,
    "steps": [
      {
        "name": "document_verification",
        "status": "pending",
        "estimated_time": 3
      },
      {
        "name": "face_matching",
        "status": "pending",
        "estimated_time": 2
      },
      {
        "name": "biometric_verification",
        "status": "pending",
        "estimated_time": 5
      }
    ]
  }
}
```

##### GET /verification/{verification_id}/status
Check verification status.

**Response:**
```json
{
  "success": true,
  "data": {
    "verification_id": "uuid",
    "status": "in_progress",
    "current_step": "face_matching",
    "progress_percentage": 60,
    "estimated_completion": "2024-01-01T10:15:00Z",
    "steps": [...]
  }
}
```

### Error Handling

#### Standard Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid document format",
    "details": {
      "field": "document_image",
      "reason": "Unsupported file format"
    },
    "timestamp": "2024-01-01T10:00:00Z",
    "request_id": "req_uuid"
  }
}
```

#### HTTP Status Codes
- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid request parameters
- `401 Unauthorized`: Authentication required
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `429 Too Many Requests`: Rate limit exceeded
- `500 Internal Server Error`: Server error

---

## 🔒 Security Architecture

### Multi-Layer Security Model

#### 1. Network Security
```mermaid
graph TB
    subgraph "Network Security Layer"
        A[WAF - Web Application Firewall]
        B[DDoS Protection]
        C[SSL/TLS Encryption]
        D[API Gateway Security]
    end

    subgraph "Application Security"
        E[JWT Authentication]
        F[Rate Limiting]
        G[Input Validation]
        H[CSRF Protection]
    end

    subgraph "Data Security"
        I[AES-256 Encryption]
        J[Database Encryption]
        K[Secure Storage]
        L[Data Masking]
    end

    A --> E
    B --> F
    C --> I
    D --> J
```

#### 2. Authentication & Authorization

##### JWT Token Structure
```json
{
  "header": {
    "alg": "HS256",
    "typ": "JWT"
  },
  "payload": {
    "sub": "user_uuid",
    "email": "user@example.com",
    "role": "user",
    "permissions": ["verify_documents", "view_dashboard"],
    "iat": 1640995200,
    "exp": 1640998800
  }
}
```

##### Role-Based Access Control (RBAC)
- **Admin**: Full system access
- **Verifier**: Document and face verification
- **User**: Personal verification only
- **Auditor**: Read-only audit access

#### 3. Data Encryption

##### Encryption at Rest
- **Database**: AES-256 encryption for sensitive fields
- **File Storage**: Server-side encryption for uploaded files
- **Backup**: Encrypted backups with key rotation

##### Encryption in Transit
- **TLS 1.3**: End-to-end encryption
- **Certificate Pinning**: Prevent MITM attacks
- **HSTS**: Enforce secure connections

#### 4. Biometric Security

##### Template Protection
```python
# Example: Biometric template encryption
import hashlib
from cryptography.fernet import Fernet

class BiometricSecurity:
    def __init__(self):
        self.encryption_key = Fernet.generate_key()
        self.cipher = Fernet(self.encryption_key)

    def create_template(self, biometric_data):
        # Convert biometric data to template
        template = self.extract_features(biometric_data)

        # Encrypt template
        encrypted_template = self.cipher.encrypt(
            json.dumps(template).encode()
        )

        # Create hash for verification
        template_hash = hashlib.sha256(encrypted_template).hexdigest()

        return {
            'encrypted_template': encrypted_template,
            'template_hash': template_hash
        }

    def verify_template(self, stored_template, new_data):
        # Create template from new data
        new_template = self.extract_features(new_data)
        encrypted_new = self.cipher.encrypt(
            json.dumps(new_template).encode()
        )

        # Compare hashes
        new_hash = hashlib.sha256(encrypted_new).hexdigest()

        return new_hash == stored_template['template_hash']
```

#### 5. Audit & Compliance

##### Audit Trail Implementation
```python
class AuditLogger:
    def log_action(self, user_id, action, details, request):
        audit_entry = {
            'user_id': user_id,
            'action': action,
            'details': details,
            'ip_address': request.client.host,
            'user_agent': request.headers.get('user-agent'),
            'timestamp': datetime.utcnow().isoformat()
        }

        # Store in audit logs table
        supabase.table('audit_logs').insert(audit_entry).execute()

        # Also log to security monitoring system
        self.security_monitor.log_security_event(audit_entry)
```

---

## 💻 Development Setup

### Prerequisites

- Python 3.9+
- Node.js 16+
- Docker & Docker Compose
- Git
- Supabase CLI (optional)

### Local Development Environment

#### 1. Clone Repository
```bash
git clone https://github.com/your-org/fai-authx.git
cd fai-authx
```

#### 2. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python scripts/init_database.py

# Run development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

#### 3. Frontend Setup
```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Set environment variables
cp .env.example .env.local
# Edit .env.local with your configuration

# Run development server
npm start
```

#### 4. Docker Setup
```bash
# Run all services with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Environment Configuration

#### Backend (.env)
```bash
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/authx_db
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Security
SECRET_KEY=your_super_secret_key_here
JWT_SECRET_KEY=your_jwt_secret_key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60

# File Storage
UPLOAD_DIR=./uploads
MAX_FILE_SIZE=10485760  # 10MB

# External APIs
SENDGRID_API_KEY=your_sendgrid_key
TWILIO_ACCOUNT_SID=your_twilio_sid
TWILIO_AUTH_TOKEN=your_twilio_token

# AI/ML Models
FACE_MODEL_PATH=./models/face_recognition_model.pth
OCR_LANGUAGE=eng

# Monitoring
SENTRY_DSN=your_sentry_dsn
LOG_LEVEL=INFO
```

#### Frontend (.env.local)
```bash
# API Configuration
REACT_APP_API_URL=http://localhost:8000/v1
REACT_APP_WS_URL=ws://localhost:8000/ws

# Authentication
REACT_APP_JWT_SECRET=your_jwt_secret

# Features
REACT_APP_ENABLE_BIOMETRICS=true
REACT_APP_ENABLE_LIVENESS_DETECTION=true

# Analytics
REACT_APP_GA_TRACKING_ID=your_ga_id
REACT_APP_SENTRY_DSN=your_sentry_dsn
```

### Development Tools Setup

#### VS Code Extensions
```
# Python
Python
Python Docstring Generator
Pylance

# JavaScript/React
ES7+ React/Redux/React-Native snippets
Prettier - Code formatter
ESLint

# General
GitLens
Docker
Thunder Client (API testing)
```

#### Pre-commit Hooks
```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 22.3.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/flake8
    rev: 4.0.1
    hooks:
      - id: flake8

  - repo: https://github.com/pre-commit/mirrors-eslint
    rev: v8.10.0
    hooks:
      - id: eslint
        additional_dependencies:
          - eslint@8.10.0
          - eslint-config-react-app@7.0.0
```

---

## 🚀 Deployment Guide

### Production Architecture

```mermaid
graph TB
    subgraph "CDN"
        A[CloudFlare CDN]
    end

    subgraph "Load Balancer"
        B[Nginx Load Balancer]
    end

    subgraph "Application Servers"
        C[FastAPI Server 1]
        D[FastAPI Server 2]
        E[FastAPI Server 3]
    end

    subgraph "Database Cluster"
        F[PostgreSQL Primary]
        G[PostgreSQL Replica]
        H[Redis Cache]
    end

    subgraph "File Storage"
        I[Supabase Storage]
        J[CDN for Static Files]
    end

    subgraph "Monitoring"
        K[Prometheus]
        L[Grafana]
        M[ELK Stack]
    end

    A --> B
    B --> C
    B --> D
    B --> E
    C --> F
    D --> F
    E --> F
    F --> G
    C --> H
    D --> H
    E --> H
    C --> I
    D --> I
    E --> I
    C --> K
    D --> K
    E --> K
    K --> L
    C --> M
    D --> M
    E --> M
```

### Docker Configuration

#### Dockerfile (Backend)
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libopencv-dev \
    tesseract-ocr \
    tesseract-ocr-eng \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd --create-home --shell /bin/bash app
USER app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Dockerfile (Frontend)
```dockerfile
# Build stage
FROM node:16-alpine as build

WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=build /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=${DATABASE_URL}
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=${POSTGRES_DB}
      - POSTGRES_USER=${POSTGRES_USER}
      - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend

volumes:
  postgres_data:
  redis_data:
```

### CI/CD Pipeline

#### GitHub Actions Workflow
```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.9'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt

      - name: Run tests
        run: |
          cd backend
          pytest tests/ -v --cov=.

      - name: Set up Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '16'

      - name: Install frontend dependencies
        run: |
          cd frontend
          npm ci

      - name: Run frontend tests
        run: |
          cd frontend
          npm test -- --coverage --watchAll=false

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'

    steps:
      - uses: actions/checkout@v3

      - name: Deploy to production
        run: |
          # Add your deployment script here
          echo "Deploying to production..."
```

### Production Configuration

#### Nginx Configuration
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server backend:8000;
    }

    upstream frontend {
        server frontend:80;
    }

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=upload:10m rate=1r/s;

    server {
        listen 80;
        server_name api.fai-authx.com;

        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";

        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://backend/v1/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # File upload routes
        location /upload {
            limit_req zone=upload burst=5 nodelay;
            client_max_body_size 10M;
            proxy_pass http://backend/upload;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }

        # Frontend routes
        location / {
            proxy_pass http://frontend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
```

---

## 🧪 Testing Strategy

### Testing Pyramid

```mermaid
graph TB
    subgraph "Testing Pyramid"
        A[End-to-End Tests<br/>10%]
        B[Integration Tests<br/>20%]
        C[Unit Tests<br/>70%]
    end

    A --> B
    B --> C
```

### Unit Testing

#### Backend Tests
```python
# tests/test_face_recognition.py
import pytest
from services.face_recognition import FaceRecognitionService

class TestFaceRecognition:
    @pytest.fixture
    def face_service(self):
        return FaceRecognitionService()

    def test_face_detection(self, face_service):
        # Test with valid face image
        result = face_service.detect_face("test_face.jpg")
        assert result.success is True
        assert result.confidence > 0.8
        assert len(result.landmarks) == 68

    def test_face_matching(self, face_service):
        # Test face matching
        result = face_service.compare_faces(
            face1_path="test_face1.jpg",
            face2_path="test_face2.jpg"
        )
        assert result.similarity_score > 0.7
        assert result.is_match is True

    def test_liveness_detection(self, face_service):
        # Test liveness detection
        result = face_service.check_liveness("test_video.mp4")
        assert result.is_live is True
        assert result.confidence > 0.9
```

#### Frontend Tests
```javascript
// src/components/__tests__/FaceCapture.test.js
import { render, screen, fireEvent } from '@testing-library/react';
import FaceCapture from '../FaceCapture';

describe('FaceCapture Component', () => {
  test('renders camera interface', () => {
    render(<FaceCapture />);
    expect(screen.getByTestId('camera-element')).toBeInTheDocument();
    expect(screen.getByText('Position your face in the frame')).toBeInTheDocument();
  });

  test('captures image on button click', () => {
    render(<FaceCapture />);
    const captureButton = screen.getByText('Capture');

    fireEvent.click(captureButton);

    // Mock camera capture
    expect(screen.getByText('Processing...')).toBeInTheDocument();
  });

  test('handles camera errors gracefully', () => {
    render(<FaceCapture />);

    // Mock camera error
    navigator.mediaDevices.getUserMedia = jest
      .fn()
      .mockRejectedValue(new Error('Camera not found'));

    expect(screen.getByText('Camera access denied')).toBeInTheDocument();
  });
});
```

### Integration Testing

#### API Integration Tests
```python
# tests/test_api_integration.py
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

class TestDocumentVerification:
    def test_document_upload_flow(self):
        # Register user
        register_response = client.post("/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "secure_password"
        })
        assert register_response.status_code == 201

        # Login
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "secure_password"
        })
        token = login_response.json()["data"]["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # Upload document
        with open("test_documents/aadhar.jpg", "rb") as f:
            upload_response = client.post(
                "/documents/upload",
                files={"front_image": f},
                data={"document_type": "aadhar"},
                headers=headers
            )
        assert upload_response.status_code == 200

        document_id = upload_response.json()["data"]["document_id"]

        # Check verification status
        status_response = client.get(
            f"/documents/{document_id}",
            headers=headers
        )
        assert status_response.status_code == 200
        assert status_response.json()["data"]["verification_status"] in [
            "processing", "approved", "rejected"
        ]
```

### End-to-End Testing

#### Selenium E2E Tests
```python
# tests/e2e/test_verification_flow.py
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class TestVerificationFlow:
    def test_complete_verification_process(self):
        driver = webdriver.Chrome()

        try:
            # Navigate to application
            driver.get("http://localhost:3000")

            # Register new user
            driver.find_element(By.ID, "name").send_keys("Test User")
            driver.find_element(By.ID, "email").send_keys("test@example.com")
            driver.find_element(By.ID, "password").send_keys("secure_password")
            driver.find_element(By.ID, "register-button").click()

            # Wait for registration to complete
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "verification-wizard"))
            )

            # Upload document
            driver.find_element(By.ID, "document-upload").send_keys(
                "/path/to/test_document.jpg"
            )
            driver.find_element(By.ID, "upload-button").click()

            # Capture face
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "face-capture"))
            )
            driver.find_element(By.ID, "capture-face").click()

            # Complete verification
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "verification-complete"))
            )

            # Verify success message
            success_message = driver.find_element(By.ID, "success-message")
            assert "Verification completed successfully" in success_message.text

        finally:
            driver.quit()
```

### Performance Testing

#### Load Testing with Locust
```python
# tests/performance/locustfile.py
from locust import HttpUser, task, between

class AuthXUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Login and get auth token"""
        response = self.client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "secure_password"
        })
        self.token = response.json()["data"]["access_token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}

    @task(3)
    def upload_document(self):
        """Test document upload endpoint"""
        with open("test_document.jpg", "rb") as f:
            self.client.post(
                "/documents/upload",
                files={"front_image": f},
                data={"document_type": "aadhar"},
                headers=self.headers
            )

    @task(2)
    def check_verification_status(self):
        """Test status checking endpoint"""
        self.client.get("/verification/test_id/status", headers=self.headers)

    @task(1)
    def capture_face(self):
        """Test face capture endpoint"""
        with open("test_face.jpg", "rb") as f:
            self.client.post(
                "/face/capture",
                files={"face_image": f},
                headers=self.headers
            )
```

### Test Coverage

#### Coverage Configuration
```ini
# .coveragerc
[run]
source = .
omit =
    venv/*
    tests/*
    migrations/*
    */__pycache__/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = htmlcov
```

#### Running Tests with Coverage
```bash
# Run tests with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Generate coverage badge
coverage-badge -o docs/coverage.svg
```

---

## ⚡ Performance Optimization

### Caching Strategy

#### Redis Caching Implementation
```python
# services/cache_service.py
import redis
import json
from typing import Optional, Any
from datetime import timedelta

class CacheService:
    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        value = self.redis_client.get(key)
        if value:
            return json.loads(value)
        return None

    def set(self, key: str, value: Any, ttl: int = 3600):
        """Set value in cache with TTL"""
        self.redis_client.setex(
            key,
            timedelta(seconds=ttl),
            json.dumps(value)
        )

    def delete(self, key: str):
        """Delete key from cache"""
        self.redis_client.delete(key)

    def cache_face_embeddings(self, user_id: str, embeddings: list):
        """Cache face embeddings for fast retrieval"""
        self.set(f"face_embeddings:{user_id}", embeddings, ttl=86400)

    def get_face_embeddings(self, user_id: str) -> Optional[list]:
        """Get cached face embeddings"""
        return self.get(f"face_embeddings:{user_id}")
```

### Database Optimization

#### Query Optimization
```python
# models/optimized_queries.py
from sqlalchemy.orm import selectinload, joinedload
from sqlalchemy import func

class OptimizedQueries:
    @staticmethod
    def get_user_with_documents(session, user_id: str):
        """Get user with all documents in single query"""
        return session.query(User)\
            .options(selectinload(User.documents))\
            .filter(User.id == user_id)\
            .first()

    @staticmethod
    def get_verification_stats(session):
        """Get verification statistics with optimized queries"""
        return session.query(
            Verification.status,
            func.count(Verification.id).label('count')
        ).group_by(Verification.status).all()

    @staticmethod
    def search_documents(session, filters: dict):
        """Search documents with indexed fields"""
        query = session.query(Document)

        if 'document_type' in filters:
            query = query.filter(Document.document_type == filters['document_type'])

        if 'is_verified' in filters:
            query = query.filter(Document.is_verified == filters['is_verified'])

        # Use pagination for large result sets
        return query.offset(filters.get('offset', 0))\
                   .limit(filters.get('limit', 50))\
                   .all()
```

#### Database Indexing
```sql
-- Optimized indexes for performance
CREATE INDEX CONCURRENTLY idx_documents_composite
ON documents(user_id, document_type, is_verified);

CREATE INDEX CONCURRENTLY idx_verifications_status_created
ON verifications(status, created_at);

CREATE INDEX CONCURRENTLY idx_audit_logs_user_created
ON audit_logs(user_id, created_at);

-- Partial indexes for better performance
CREATE INDEX CONCURRENTLY idx_documents_pending
ON documents(id) WHERE verification_status = 'pending';

CREATE INDEX CONCURRENTLY idx_verifications_active
ON verifications(id) WHERE status IN ('pending', 'in_progress');
```

### Image Processing Optimization

#### Efficient Image Handling
```python
# services/image_optimizer.py
import cv2
import numpy as np
from PIL import Image
import io

class ImageOptimizer:
    @staticmethod
    def resize_image(image_data: bytes, max_size: tuple = (800, 600)) -> bytes:
        """Resize image to reduce file size while maintaining quality"""
        img = Image.open(io.BytesIO(image_data))
        img.thumbnail(max_size, Image.Resampling.LANCZOS)

        # Convert to RGB if necessary
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # Save with optimal quality
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=85, optimize=True)
        return output.getvalue()

    @staticmethod
    def enhance_image_for_ocr(image_data: bytes) -> bytes:
        """Enhance image for better OCR results"""
        # Convert to numpy array
        img_array = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )

        # Noise reduction
        denoised = cv2.fastNlMeansDenoising(thresh)

        # Convert back to bytes
        _, buffer = cv2.imencode('.jpg', denoised)
        return buffer.tobytes()

    @staticmethod
    def extract_face_region(image_data: bytes, face_bbox: tuple) -> bytes:
        """Extract face region for processing"""
        img_array = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        x, y, w, h = face_bbox
        face_region = img[y:y+h, x:x+w]

        # Standardize face size for recognition
        face_resized = cv2.resize(face_region, (112, 112))

        _, buffer = cv2.imencode('.jpg', face_resized)
        return buffer.tobytes()
```

### Asynchronous Processing

#### Background Task Processing
```python
# services/task_queue.py
import asyncio
from celery import Celery
from typing import Dict, Any

# Celery configuration
celery_app = Celery(
    'authx_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/1'
)

class AsyncTaskProcessor:
    @staticmethod
    @celery_app.task(bind=True)
    def process_document_ocr(self, document_id: str, image_path: str):
        """Process OCR in background"""
        try:
            from services.document_processor import DocumentProcessor

            processor = DocumentProcessor()
            result = processor.extract_text(image_path)

            # Update document with OCR results
            # ... database update logic

            return {
                'status': 'success',
                'document_id': document_id,
                'ocr_data': result
            }
        except Exception as exc:
            self.retry(exc=exc, countdown=60, max_retries=3)

    @staticmethod
    @celery_app.task
    def perform_face_matching(verification_id: str, face_image_path: str, document_id: str):
        """Perform face matching in background"""
        try:
            from services.face_recognition import FaceRecognitionService

            face_service = FaceRecognitionService()
            result = face_service.compare_with_document(
                face_image_path, document_id
            )

            # Update verification results
            # ... database update logic

            return {
                'status': 'success',
                'verification_id': verification_id,
                'match_score': result.similarity_score,
                'is_match': result.is_match
            }
        except Exception as exc:
            return {
                'status': 'error',
                'verification_id': verification_id,
                'error': str(exc)
            }
```

### Performance Monitoring

#### Application Metrics
```python
# services/metrics.py
from prometheus_client import Counter, Histogram, Gauge
import time

# Define metrics
REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint', 'status'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')
ACTIVE_VERIFICATIONS = Gauge('active_verifications_count', 'Number of active verifications')
FACE_RECOGNITION_DURATION = Histogram('face_recognition_duration_seconds', 'Face recognition processing time')

class MetricsMiddleware:
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        start_time = time.time()

        def custom_start_response(status, headers, exc_info=None):
            REQUEST_COUNT.labels(
                method=environ['REQUEST_METHOD'],
                endpoint=environ['PATH_INFO'],
                status=status.split()[0]
            ).inc()

            REQUEST_DURATION.observe(time.time() - start_time)
            return start_response(status, headers, exc_info)

        return self.app(environ, custom_start_response)
```

---

## 📊 Monitoring & Logging

### Logging Architecture

#### Structured Logging
```python
# services/logger.py
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # Create structured formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)

        # File handler for JSON logs
        file_handler = logging.FileHandler('logs/application.log')
        json_formatter = JsonFormatter()
        file_handler.setFormatter(json_formatter)
        self.logger.addHandler(file_handler)

    def log_api_request(self, request_id: str, method: str, path: str,
                       user_id: str = None, ip: str = None):
        """Log API request"""
        self.logger.info("API Request", extra={
            'event_type': 'api_request',
            'request_id': request_id,
            'method': method,
            'path': path,
            'user_id': user_id,
            'ip_address': ip,
            'timestamp': datetime.utcnow().isoformat()
        })

    def log_verification_attempt(self, user_id: str, verification_type: str,
                               document_type: str, confidence: float):
        """Log verification attempt"""
        self.logger.info("Verification Attempt", extra={
            'event_type': 'verification_attempt',
            'user_id': user_id,
            'verification_type': verification_type,
            'document_type': document_type,
            'confidence_score': confidence,
            'timestamp': datetime.utcnow().isoformat()
        })

    def log_security_event(self, event_type: str, user_id: str, details: Dict[str, Any]):
        """Log security-related events"""
        self.logger.warning("Security Event", extra={
            'event_type': 'security_event',
            'security_event_type': event_type,
            'user_id': user_id,
            'details': details,
            'timestamp': datetime.utcnow().isoformat(),
            'severity': 'high'
        })

class JsonFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
        }

        # Add extra fields if present
        if hasattr(record, 'event_type'):
            log_entry.update(record.__dict__)

        return json.dumps(log_entry)
```

### Health Checks

#### Comprehensive Health Monitoring
```python
# routes/health.py
from fastapi import APIRouter, HTTPException
from services.database import DatabaseService
from services.redis_client import RedisService
from services.face_recognition import FaceRecognitionService
import psutil

router = APIRouter()

@router.get("/health")
async def health_check():
    """Comprehensive health check"""
    health_status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {}
    }

    # Check database connection
    try:
        db_service = DatabaseService()
        db_service.execute_query("SELECT 1")
        health_status["services"]["database"] = "healthy"
    except Exception as e:
        health_status["services"]["database"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check Redis connection
    try:
        redis_service = RedisService()
        redis_service.ping()
        health_status["services"]["redis"] = "healthy"
    except Exception as e:
        health_status["services"]["redis"] = f"unhealthy: {str(e)}"
        health_status["status"] = "unhealthy"

    # Check AI model availability
    try:
        face_service = FaceRecognitionService()
        face_service.load_model()
        health_status["services"]["ai_models"] = "healthy"
    except Exception as e:
        health_status["services"]["ai_models"] = f"unhealthy: {str(e)}"
        health_status["status"] = "degraded"

    # System metrics
    health_status["system"] = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent
    }

    status_code = 200 if health_status["status"] == "healthy" else 503
    return JSONResponse(content=health_status, status_code=status_code)

@router.get("/health/ready")
async def readiness_check():
    """Readiness probe for Kubernetes"""
    # Check critical dependencies
    checks = [
        check_database_connection(),
        check_redis_connection(),
        check_model_availability()
    ]

    if all(checks):
        return {"status": "ready"}
    else:
        raise HTTPException(status_code=503, detail="Service not ready")

@router.get("/health/live")
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return {"status": "alive", "timestamp": datetime.utcnow().isoformat()}
```

### Error Tracking

#### Sentry Integration
```python
# services/error_tracking.py
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration

class ErrorTracker:
    def __init__(self, dsn: str):
        sentry_sdk.init(
            dsn=dsn,
            integrations=[
                FastApiIntegration(auto_enabling_integrations=False),
                SqlalchemyIntegration(),
            ],
            traces_sample_rate=0.1,
            environment="production"
        )

    def track_verification_error(self, user_id: str, error_type: str,
                                context: dict):
        """Track verification-related errors"""
        sentry_sdk.set_user({"id": user_id})
        sentry_sdk.set_tag("error_type", error_type)
        sentry_sdk.set_context("verification", context)
        sentry_sdk.capture_message(f"Verification error: {error_type}", level="error")

    def track_performance_issue(self, operation: str, duration: float,
                              threshold: float):
        """Track performance issues"""
        if duration > threshold:
            sentry_sdk.set_tag("operation", operation)
            sentry_sdk.set_measurement("duration", duration, "second")
            sentry_sdk.capture_message(
                f"Performance issue: {operation} took {duration}s",
                level="warning"
            )
```

### Analytics Dashboard

#### Real-time Metrics
```python
# services/analytics.py
from collections import defaultdict
import asyncio
from datetime import datetime, timedelta

class AnalyticsService:
    def __init__(self):
        self.metrics = defaultdict(int)
        self.real_time_data = {}

    async def track_verification_event(self, event_type: str, user_id: str,
                                     metadata: dict):
        """Track verification events in real-time"""
        timestamp = datetime.utcnow()

        # Update counters
        self.metrics[f"{event_type}_total"] += 1

        # Store real-time data
        event_key = f"{event_type}_{timestamp.strftime('%Y%m%d%H%M')}"
        if event_key not in self.real_time_data:
            self.real_time_data[event_key] = []

        self.real_time_data[event_key].append({
            'timestamp': timestamp,
            'user_id': user_id,
            'metadata': metadata
        })

        # Clean up old data (keep only last hour)
        cutoff_time = timestamp - timedelta(hours=1)
        self.real_time_data = {
            k: v for k, v in self.real_time_data.items()
            if datetime.strptime(k.split('_')[1], '%Y%m%d%H%M') > cutoff_time
        }

    def get_dashboard_metrics(self):
        """Get metrics for dashboard"""
        now = datetime.utcnow()
        last_hour = now - timedelta(hours=1)

        # Calculate hourly metrics
        hourly_stats = defaultdict(int)
        for key, events in self.real_time_data.items():
            event_time = datetime.strptime(key.split('_')[1], '%Y%m%d%H%M')
            if event_time > last_hour:
                event_type = key.split('_')[0]
                hourly_stats[f"{event_type}_hourly"] += len(events)

        return {
            'total_metrics': dict(self.metrics),
            'hourly_metrics': dict(hourly_stats),
            'active_verifications': self.metrics['verification_started'] - self.metrics['verification_completed'],
            'success_rate': self.calculate_success_rate(),
            'average_processing_time': self.calculate_avg_processing_time(),
            'last_updated': now.isoformat()
        }

    def calculate_success_rate(self):
        """Calculate verification success rate"""
        total = self.metrics['verification_completed']
        successful = self.metrics['verification_successful']

        if total == 0:
            return 0.0

        return (successful / total) * 100

    def calculate_avg_processing_time(self):
        """Calculate average processing time"""
        total_time = self.metrics['total_processing_time']
        count = self.metrics['verification_completed']

        if count == 0:
            return 0.0

        return total_time / count
```

### Alerting Configuration

#### Prometheus Alert Rules
```yaml
# prometheus-alerts.yml
groups:
  - name: authx-alerts
    rules:
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.1
        for: 2m
        labels:
          severity: critical
        annotations:
          summary: "High error rate detected"
          description: "Error rate is {{ $value }} errors per second"

      - alert: HighResponseTime
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "High response time detected"
          description: "95th percentile response time is {{ $value }} seconds"

      - alert: DatabaseConnectionFailure
        expr: up{job="database"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Database connection failed"
          description: "Database has been down for more than 1 minute"

      - alert: RedisConnectionFailure
        expr: up{job="redis"} == 0
        for: 1m
        labels:
          severity: critical
        annotations:
          summary: "Redis connection failed"
          description: "Redis has been down for more than 1 minute"

      - alert: MemoryUsageHigh
        expr: (node_memory_MemTotal_bytes - node_memory_MemAvailable_bytes) / node_memory_MemTotal_bytes > 0.9
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: "Memory usage is high"
          description: "Memory usage is above 90%"
```

---

*Last Updated: October 2024*
*Document Version: 1.0*
*Next Review: January 2025*