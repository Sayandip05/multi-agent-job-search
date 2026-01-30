# 🎯 Multi-Agent Job Search System

> An AI-powered job search assistant using a multi-agent architecture with CrewAI, Ollama, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-0.86.0-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red.svg)
![Ollama](https://img.shields.io/badge/Ollama-Local%20LLM-purple.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#️-architecture)
- [Tech Stack](#️-tech-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [Project Structure](#-project-structure)
- [Configuration](#️-configuration)
- [AI Agents](#-ai-agents)
- [API Reference](#-api-reference)
- [Testing](#-testing)
- [Contributing](#-contributing)
- [License](#-license)

---

## 🎯 Overview

This project implements an intelligent job search assistant using a **multi-agent AI system**. Upload your resume, specify your target role, and let specialized AI agents analyze your profile, search for job opportunities, match your skills, and rank the best opportunities for you.

### Why Multi-Agent?

Traditional job search tools use simple keyword matching. Our system uses **four specialized AI agents** that work together like a team of career advisors:

1. **Resume Analyst** - Understands your experience and skills
2. **Job Scout** - Finds relevant opportunities from real job boards
3. **Skill Matcher** - Evaluates how well you fit each role
4. **Career Strategist** - Ranks opportunities and provides actionable recommendations

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 📄 **Smart Resume Parsing** | AI extracts skills, experience, education, and qualifications from PDF/DOCX resumes |
| 🔍 **Real Job Discovery** | Searches live job postings using JSearch API with intelligent query building |
| 🎯 **Deep Skill Matching** | Compares your profile against job requirements with detailed gap analysis |
| 🏆 **Strategic Ranking** | Ranks opportunities based on fit score, growth potential, and career alignment |
| 💾 **Data Persistence** | Saves candidate profiles and search results to CSV for future reference |
| 🖥️ **Beautiful UI** | Modern, responsive Streamlit interface with step-by-step workflow |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        STREAMLIT UI (app.py)                         │
│              Multi-step form • Progress tracking • Results           │
├─────────────────────────────────────────────────────────────────────┤
│                    JOB SEARCH CREW (Orchestrator)                    │
│         Coordinates agents • Manages pipeline • Generates report     │
├────────────────┬────────────────┬────────────────┬──────────────────┤
│    RESUME      │      JOB       │     SKILL      │     RANKING      │
│    ANALYST     │   DISCOVERY    │    MATCHER     │      AGENT       │
│                │                │                │                  │
│  • Extract     │  • Build query │  • Compare     │  • Apply weights │
│    skills      │  • Call API    │    skills      │  • Calculate     │
│  • Parse       │  • Parse       │  • Gap         │    final score   │
│    experience  │    listings    │    analysis    │  • Strategic     │
│  • Identify    │  • Normalize   │  • Fit score   │    ranking       │
│    education   │    data        │    (0-100)     │  • Action plan   │
├────────────────┴────────────────┴────────────────┴──────────────────┤
│                      CREWAI + LANGCHAIN-OLLAMA                       │
│              Agent framework • Task definitions • Memory             │
├─────────────────────────────────────────────────────────────────────┤
│                         OLLAMA (llama3.2)                            │
│                    Local LLM inference • Privacy                     │
└─────────────────────────────────────────────────────────────────────┘
```

### Data Flow

```
Resume (PDF/DOCX) ──► Resume Analyst ──► CandidateProfile
                                              │
                                              ▼
Target Role ──────────► Job Discovery ──► List[JobPosting]
                                              │
                                              ▼
CandidateProfile + Jobs ──► Skill Matcher ──► List[JobMatchResult]
                                              │
                                              ▼
                      Ranking Agent ──► JobRanking (Sorted, with recommendations)
                                              │
                                              ▼
                              Final Report ──► UI Display + CSV Storage
```

---

## 🛠️ Tech Stack

| Category | Technology | Version | Purpose |
|----------|------------|---------|---------|
| **AI Framework** | CrewAI | 0.86.0 | Multi-agent orchestration |
| **LLM Provider** | Ollama | 0.4.4 | Local LLM inference |
| **LLM Model** | Llama 3.2 | latest | Language understanding |
| **LLM Integration** | LangChain-Ollama | 0.2.2 | Agent-LLM bridge |
| **Frontend** | Streamlit | 1.41.1 | Interactive web UI |
| **Data Validation** | Pydantic | 2.10.5 | Type-safe models |
| **Job API** | RapidAPI JSearch | - | Real job postings |
| **PDF Parsing** | pypdf | 3.17.4 | Resume text extraction |
| **DOCX Parsing** | python-docx | 1.1.0 | Word doc processing |
| **Logging** | Loguru | 0.7.3 | Advanced logging |

---

## 📦 Installation

### Prerequisites

- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Ollama** - [Install Ollama](https://ollama.ai/)
- **RapidAPI Account** - Free tier available (100 requests/month)

### Step-by-Step Setup

```bash
# 1. Clone the repository
git clone https://github.com/Sayandip05/multi-agent-job-search.git
cd multi-agent-job-search

# 2. Create and activate virtual environment
python -m venv venv

# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure environment variables
cp .env.example .env
# Edit .env and add your RAPIDAPI_KEY

# 5. Pull the Ollama model (requires ~2GB download)
ollama pull llama3.2:latest

# 6. Start Ollama server (keep this terminal open)
ollama serve
```

### Verify Installation

```bash
# Check Ollama is running
ollama list

# Should show: llama3.2:latest
```

---

## 🚀 Usage

### Quick Start

```bash
# Make sure Ollama is running in a separate terminal
ollama serve

# Start the Streamlit application
streamlit run src/ui/app.py
```

Open your browser at **http://localhost:8501**

### Step-by-Step Workflow

| Step | Action | Description |
|------|--------|-------------|
| 1️⃣ | **Enter Name** | Personalize your job search experience |
| 2️⃣ | **Experience Level** | Select from Recent Graduate to Lead/Principal |
| 3️⃣ | **Work Preference** | Choose Remote, Hybrid, or On-Site |
| 4️⃣ | **Target Role** | Specify the job title you're seeking |
| 5️⃣ | **Upload Resume** | PDF or DOCX format supported |
| 6️⃣ | **AI Analysis** | Watch agents process your application |
| 7️⃣ | **View Results** | See ranked job matches with recommendations |

### Example Target Roles

- ✅ "Senior Python Developer"
- ✅ "Data Scientist - Machine Learning"
- ✅ "Full-Stack JavaScript Developer"
- ✅ "Product Manager - SaaS"
- ❌ "Developer" (too generic)
- ❌ "Job" (not specific)

---

## 📁 Project Structure

```
multi-agent-job-search/
├── 📂 src/
│   ├── 📂 agents/                  # AI Agent implementations
│   │   ├── __init__.py
│   │   ├── resume_analyst.py       # Parses and analyzes resumes
│   │   ├── job_discovery.py        # Searches for job postings
│   │   ├── skill_matcher.py        # Matches candidate to jobs
│   │   └── ranking_agent.py        # Ranks opportunities strategically
│   │
│   ├── 📂 core/                    # Core orchestration
│   │   ├── __init__.py
│   │   └── job_search_crew.py      # Main pipeline orchestrator
│   │
│   ├── 📂 models/                  # Data models
│   │   ├── __init__.py
│   │   └── domain.py               # Pydantic models (CandidateProfile, etc.)
│   │
│   ├── 📂 config/                  # Configuration management
│   │   ├── __init__.py
│   │   └── settings.py             # Environment-based settings
│   │
│   ├── 📂 tools/                   # External tool integrations
│   │   ├── __init__.py
│   │   └── job_search_tools.py     # JSearch API wrapper
│   │
│   ├── 📂 utils/                   # Utility functions
│   │   ├── __init__.py
│   │   ├── file_parser.py          # PDF/DOCX text extraction
│   │   └── csv_storage.py          # Data persistence layer
│   │
│   └── 📂 ui/                      # User interface
│       ├── __init__.py
│       └── app.py                  # Streamlit application
│
├── 📂 data/                        # Generated data (auto-created)
│   ├── candidates.csv              # Saved candidate profiles
│   └── results.csv                 # Job search results
│
├── 📂 tests/                       # Test suite
│   └── ...
│
├── 📄 .env.example                 # Environment template
├── 📄 .gitignore                   # Git ignore rules
├── 📄 requirements.txt             # Python dependencies
└── 📄 README.md                    # This file
```

---

## ⚙️ Configuration

### Environment Variables

Copy `.env.example` to `.env` and configure:

```env
# Ollama Settings
OLLAMA__MODEL=llama3.2:latest
OLLAMA__BASE_URL=http://localhost:11434

# Agent Settings
AGENT__VERBOSE=true
LOG_LEVEL=INFO

# RapidAPI JSearch (REQUIRED for job search)
RAPIDAPI_KEY=your_api_key_here
RAPIDAPI_HOST=jsearch.p.rapidapi.com
```

### Getting a RapidAPI Key

1. Visit [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
2. Sign up for a **free account**
3. Subscribe to JSearch API (**Free tier: 100 requests/month**)
4. Copy your **X-RapidAPI-Key** to `.env`

### Configuration Options

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA__MODEL` | llama3.2:latest | Ollama model to use |
| `OLLAMA__BASE_URL` | http://localhost:11434 | Ollama server URL |
| `AGENT__VERBOSE` | true | Show agent reasoning in console |
| `LOG_LEVEL` | INFO | Logging verbosity |

---

## 🤖 AI Agents

### 1. Resume Analyst Agent

**Role:** Extract structured information from unstructured resume text

**Capabilities:**
- Identify technical and soft skills
- Parse work experience with years calculation
- Extract education and certifications
- Determine experience level (junior/mid/senior/lead)

**Output:** `CandidateProfile` with skills, experience, and education

---

### 2. Job Discovery Agent

**Role:** Find relevant job opportunities from real job boards

**Capabilities:**
- Build optimized search queries
- Call JSearch API with proper parameters
- Parse and normalize job listings
- Handle API errors gracefully

**Output:** List of `JobPosting` objects with full details

---

### 3. Skill Matcher Agent

**Role:** Deep analysis of candidate-job fit

**Capabilities:**
- Match required vs. candidate skills
- Identify skill gaps and potential
- Calculate weighted fit score (0-100)
- Assess experience alignment

**Output:** `JobMatchResult` with scores and gap analysis

---

### 4. Ranking Agent

**Role:** Strategic ranking and recommendations

**Capabilities:**
- Apply weighted scoring (skills, experience, growth)
- Tier classification (Tier 1-4)
- Action recommendations (Apply Immediately, Strong Candidate, etc.)
- Career strategy insights

**Output:** `JobRanking` with sorted opportunities and recommendations

---

## 📡 API Reference

### JSearch API (RapidAPI)

The job discovery agent uses the JSearch API to fetch real job postings.

**Endpoint:** `https://jsearch.p.rapidapi.com/search`

**Parameters:**
| Parameter | Type | Description |
|-----------|------|-------------|
| `query` | string | Job search query |
| `num_pages` | int | Number of result pages |
| `page` | int | Page number |
| `date_posted` | string | Filter (all, today, 3days, week, month) |

**Rate Limits:**
- Free tier: 100 requests/month
- Basic: 10,000 requests/month

---

## 🧪 Testing

```bash
# Install dev dependencies (included in requirements.txt)
pip install pytest pytest-asyncio

# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src --cov-report=html
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

### Development Setup

```bash
# Fork and clone
git clone https://github.com/YOUR_USERNAME/multi-agent-job-search.git
cd multi-agent-job-search

# Install dev dependencies
pip install -r requirements.txt

# Create feature branch
git checkout -b feature/your-amazing-feature
```

### Contribution Guidelines

1. **Fork** the repository
2. **Create** your feature branch (`git checkout -b feature/amazing-feature`)
3. **Write tests** for new functionality
4. **Format code** with Black (`black src/`)
5. **Lint** with Ruff (`ruff check src/`)
6. **Commit** your changes (`git commit -m 'Add amazing feature'`)
7. **Push** to the branch (`git push origin feature/amazing-feature`)
8. **Open** a Pull Request

### Code Style

- Use **Black** for formatting
- Use **Ruff** for linting
- Follow **PEP 8** conventions
- Add **docstrings** to all functions

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 👨‍💻 Author

**Sayandip** - AI/ML Developer

- GitHub: [@Sayandip05](https://github.com/Sayandip05)

---

## 🙏 Acknowledgments

- [CrewAI](https://github.com/joaomdmoura/crewAI) - Multi-agent framework
- [Ollama](https://ollama.ai/) - Local LLM inference
- [Streamlit](https://streamlit.io/) - Web UI framework
- [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch) - Job search API

---

<div align="center">

⭐ **Star this repo if you find it useful!** ⭐

Made with ❤️ using CrewAI & Streamlit

</div>
