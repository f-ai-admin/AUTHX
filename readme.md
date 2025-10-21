<div align="center">
  <h1>🔐 f-ai AuthX</h1>
  <p><strong>AI-Powered Identity Verification System with Advanced Duplicate Detection</strong></p>

  <a href="https://opensource.org/licenses/MIT"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python" src="https://img.shields.io/badge/Python-3.9+-blue.svg"></a>
  <a href="https://reactjs.org/"><img alt="React" src="https://img.shields.io/badge/React-18.0+-61DAFB.svg"></a>
  <a href="https://fastapi.tiangolo.com/"><img alt="FastAPI" src="https://img.shields.io/badge/FastAPI-0.104+-009688.svg"></a>
  <a href="https://supabase.com/"><img alt="Supabase" src="https://img.shields.io/badge/Supabase-Powered-3ECF8E.svg"></a>

  <p>Built for IndiaAI CyberGuard AI Hackathon 2025</p>
</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Key Features](#-key-features)
- [Tech Stack](#️-tech-stack)
- [System Architecture](#️-system-architecture)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Project Structure](#-project-structure)
- [How It Works](#-how-it-works)
- [Performance](#-performance)
- [Security](#-security)
- [Contributing](#-contributing)
- [License](#-license)
- [Acknowledgments](#-acknowledgments)
- [Contact](#-contact)

---

## 🎯 Overview

**F-AI AuthX** is a comprehensive AI-powered identity verification system designed to combat fraudulent registrations and prevent multiple account creation by the same individual. Built for the **IndiaAI CyberGuard AI Hackathon**, it combines cutting-edge face recognition, liveness detection, document OCR, and intelligent duplicate detection to ensure secure and reliable user verification.

### Problem Statement

The system addresses the critical challenge of **de-duplication and multi-account detection** by:
- Identifying multiple applications submitted by the same individual
- Preventing synthetic/fake identity fraud
- Detecting face spoofing and presentation attacks
- Verifying identity documents against live biometrics
- Managing incomplete registrations with intelligent expiry

### Novelty & Innovation

- 🌟 **Triple-Layer Duplicate Detection**: Unique 3-stage verification across document face, selfie, and live capture  
- 🕐 **Smart Expiry Management**: Time-based registration cleanup with automatic filtering of stale data  
- 🎭 **Multi-Stage Verification Pipeline**: Liveness detection → Face extraction → Triple comparison → Final decision  
- 🔍 **Self-Exclusion Logic**: Prevents false duplicates by excluding user's own previous uploads  
- 📊 **Comprehensive Audit Trail**: Complete tracking of verification journey with similarity scores  

---

## ✨ Key Features

### Core Capabilities

- ✅ **Triple-Layer Duplicate Detection**
  - Document face comparison (80% similarity threshold)
  - Selfie face comparison (80% similarity threshold)
  - Live capture comparison (80% similarity threshold)
  - 2/3 match rule for duplicate flagging

- ✅ **Advanced Face Recognition**
  - InsightFace Buffalo-L model (99.1% accuracy)
  - 512-dimensional face embeddings
  - Cosine similarity matching
  - 60% threshold for face verification

- ✅ **Liveness Detection**
  - Silent-Face-Anti-Spoofing (98% accuracy)
  - Detects photos, videos, masks, and deepfakes
  - Real-time confidence scoring
  - Presentation attack detection

- ✅ **Document OCR & Verification**
  - PaddleOCR with 80+ language support
  - Fuzzy matching for OCR errors (80% threshold)
  - Supports Aadhaar, PAN, Passport, DL, Voter ID
  - Automatic data extraction and validation

- ✅ **Smart Registration Management**
  - 7-day expiry for incomplete registrations
  - Automatic expiry extension on activity
  - Expired user filtering in duplicate checks
  - Resume verification from any device

### Technical Highlights

- **Fast Performance**: ~1.5s for complete verification  
- **Scalable Architecture**: Stateless API design  
- **Secure Storage**: Supabase with PostgreSQL + File Storage  
- **Real-time Processing**: WebSocket-ready architecture  
- **Comprehensive Logging**: Full audit trail for compliance  

---
### Frontend

## 🛠️ Tech Stack
- React 18.0+ → Dynamic UI framework
- React Webcam → Real-time camera capture
- Axios → HTTP client for API calls
- React Router → Navigation management
- CSS3 → Modern styling

  
### Backend
- FastAPI 0.104+ → High-performance async API
-  Python 3.9+ → Core programming language
-  Uvicorn → ASGI server
-  Supabase Python → Database client
-  python-multipart → File upload handling

### Database & Storage
- Supabase PostgreSQL → Relational database
- Supabase Storage → File storage (documents, selfies, live captures)
- JSONB Indexing → Fast embedding searches


---

## 🚀 Installation

### Prerequisites

- **Node.js** 16.0+ and npm
- **Python** 3.9+
- **Git**
- **Supabase Account** (free tier available)

### Backend Setup

1. **Clone the Repository**

2. **Navigate to Backend Directory**

3. **Create Virtual Environment**
python -m venv venv

Windows
venv\Scripts\activate

Linux/Mac
source venv/bin/activate

4. **Install Python Dependencies**


5. **Create `.env` File**
   
6. **Configure Environment Variables**
Supabase Configuration
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_anon_key

Application Settings
ENVIRONMENT=development
DEBUG=True

8. **Start Backend Server**
Development mode
python main.py

Production mode
uvicorn main:app --host 0.0.0.0 --port 8000

Backend will run at: `http://localhost:8000`

---

### Frontend Setup

1. **Navigate to Frontend Directory**

2. **Install Dependencies**
npm install


3. **Create `.env` File**
Copy example environment file
cp .env.example .env


4. **Configure Environment Variables**
REACT_APP_API_URL=http://localhost:8000


5. **Start Frontend Server**
npm start

Frontend will run at: `http://localhost:3000`

---

### Database Setup (Supabase)

1. **Create Supabase Project**
   - Visit [Supabase](https://supabase.com)
   - Create new project
   - Note your project URL and anon key

2. **Run Database Migrations**


---

## 📖 Usage

### User Journey

#### **Step 1: Personal Information Registration**

#### **Step 2: Document Upload**

#### **Step 3: Selfie Upload**

#### **Step 4: Biometric Upload** (Optional)

#### **Step 5: Live Camera Verification** (Final)

### Resume Verification

Users can resume incomplete registration:

---

## 🔬 How It Works

### Triple-Layer Duplicate Detection

#### **Layer 1: Document Face Check**

#### **Layer 2: Selfie Face Check**

#### **Layer 3: Live Capture Check**

#### **Final Decision Logic**

---

### Smart Expiry Management


**Benefits:**
- Stale incomplete registrations don't slow down checks
- Users have reasonable time (7 days + extensions)
- Database stays clean
- Expired users can re-register without duplicate flag






