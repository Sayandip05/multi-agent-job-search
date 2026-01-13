# Multi-Agent Job Search System

> A multi-agent AI system for intelligent job search and candidate-job matching, powered by CrewAI, Ollama, and FastAPI.

## 🎯 Project Overview

This project implements an intelligent job search assistant using a multi-agent architecture. The system analyzes resumes, extracts skills, and matches candidates to job postings with detailed scoring and recommendations.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Multi-Agent System                        │
├─────────────────────┬───────────────────────────────────────┤
│  Resume Analyst     │  Skill Matcher                        │
│  Agent              │  Agent                                │
│  ✅ Working         │  ✅ Working                           │
├─────────────────────┴───────────────────────────────────────┤
│                    CrewAI + LiteLLM                         │
├─────────────────────────────────────────────────────────────┤
│                    Ollama (llama3)                          │
└─────────────────────────────────────────────────────────────┘
```

## ✅ Progress Tracker

### Phase 1: Core Agent Development
- [x] Project structure setup
- [x] Configuration system with Pydantic
- [x] Domain models (CandidateProfile, JobPosting, SkillMatch, JobMatchResult)
- [x] Resume Analyst Agent - Extracts structured data from resumes
- [x] Skill Matcher Agent - Matches candidates to jobs with scoring

### Phase 2: API Development (Planned)
- [ ] FastAPI backend
- [ ] REST endpoints for resume upload
- [ ] Job matching API
- [ ] Async task processing

### Phase 3: Containerization (Planned)
- [ ] Docker configuration
- [ ] Docker Compose for multi-service setup
- [ ] Ollama container integration

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **AI Framework** | CrewAI 0.86.0 |
| **LLM Provider** | Ollama + LiteLLM |
| **Local Model** | llama3:latest |
| **Data Validation** | Pydantic 2.10 |
| **Backend** | FastAPI (planned) |
| **Containerization** | Docker (planned) |

## 📦 Installation

```bash
# Clone the repository
cd agentic-job-search

# Create virtual environment
python -m venv venv

# Activate venv (Windows)
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Ensure Ollama is running
ollama serve

# Pull the model
ollama pull llama3
```

## 🚀 Usage

### Test Resume Analyst Agent
```bash
python -m src.agents.resume_analyst
```

**Expected Output:**
```
🚀 Testing Resume Analysis Agent...
============================================================
✅ Resume Analysis Complete!

Name: John Doe
Email: john.doe@email.com
Experience Level: senior
Total Years: 4.0
Skills Extracted: 13
```

### Test Skill Matcher Agent (In Progress)
```bash
python -m src.agents.skill_matcher
```

## 📁 Project Structure

```
agentic-job-search/
├── src/
│   ├── agents/
│   │   ├── resume_analyst.py    # ✅ Resume parsing agent
│   │   └── skill_matcher.py     # 🔧 Job matching agent
│   ├── config/
│   │   └── settings.py          # ✅ Configuration management
│   └── models/
│       └── domain.py            # ✅ Pydantic domain models
├── tests/                       # Test suite
├── requirements.txt             # Dependencies
├── .env.example                 # Environment template
├── .gitignore                   # Git ignore rules
└── README.md                    # This file
```

## ⚙️ Configuration

The system uses environment variables for configuration. Copy `.env.example` to `.env` and customize:

```env
ENVIRONMENT=development
OLLAMA__MODEL=llama3:latest
OLLAMA__BASE_URL=http://localhost:11434
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## 📄 License

MIT License
