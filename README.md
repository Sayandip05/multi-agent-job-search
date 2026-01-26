# 🎯 Multi-Agent Job Search System

> An AI-powered job search assistant using a multi-agent architecture with CrewAI, Ollama, and Streamlit.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![CrewAI](https://img.shields.io/badge/CrewAI-0.86.0-green.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.41-red.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 🎯 Overview

This project implements an intelligent job search assistant using a **multi-agent AI system**. Upload your resume, specify your target role, and let AI agents analyze, search, match, and rank job opportunities for you.

### ✨ Features

- 📄 **Resume Analysis** - AI extracts skills, experience, and qualifications from your resume
- 🔍 **Job Discovery** - Searches real job postings using JSearch API
- 🎯 **Skill Matching** - Compares your profile against job requirements with detailed scoring
- 🏆 **Smart Ranking** - Strategically ranks opportunities based on fit and career goals
- 💾 **Data Storage** - Saves candidate profiles and results to CSV

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Streamlit UI (app.py)                       │
├─────────────────────────────────────────────────────────────────┤
│                    JobSearchCrew Orchestrator                    │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   Resume     │     Job      │    Skill     │      Ranking       │
│   Analyst    │  Discovery   │   Matcher    │       Agent        │
│    Agent     │    Agent     │    Agent     │                    │
├──────────────┴──────────────┴──────────────┴────────────────────┤
│                    CrewAI + LangChain-Ollama                     │
├─────────────────────────────────────────────────────────────────┤
│                      Ollama (llama3)                             │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Tech Stack

| Category | Technology |
|----------|------------|
| **AI Framework** | CrewAI 0.86.0 |
| **LLM Provider** | Ollama (local) |
| **LLM Model** | llama3 |
| **Frontend** | Streamlit |
| **Data Validation** | Pydantic 2.10 |
| **Job API** | RapidAPI JSearch |
| **File Parsing** | pypdf, python-docx |

## 📦 Installation

### Prerequisites

- Python 3.10+
- [Ollama](https://ollama.ai/) installed and running
- RapidAPI key for JSearch (free tier available)

### Setup

```bash
# Clone the repository
git clone https://github.com/Sayandip05/multi-agent-job-search.git
cd multi-agent-job-search

# Create virtual environment
python -m venv venv

# Activate venv
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy environment template and configure
cp .env.example .env
# Edit .env and add your RAPIDAPI_KEY

# Pull the Ollama model
ollama pull llama3

# Start Ollama server (in a separate terminal)
ollama serve
```

## 🚀 Usage

### Run the Streamlit UI

```bash
streamlit run src/ui/app.py
```

Then open http://localhost:8501 in your browser.

### How to Use

1. **Enter your name** - Personalize your job search
2. **Select experience level** - Recent Graduate to Lead/Principal
3. **Choose work preference** - Remote, Hybrid, or On-Site
4. **Specify target role** - e.g., "Senior Python Developer"
5. **Upload your resume** - PDF or DOCX format
6. **Get AI-powered results** - Ranked job matches with recommendations

## 📁 Project Structure

```
multi-agent-job-search/
├── src/
│   ├── agents/              # AI Agents
│   │   ├── resume_analyst.py    # Parses resumes
│   │   ├── job_discovery.py     # Finds job postings
│   │   ├── skill_matcher.py     # Matches skills to jobs
│   │   └── ranking_agent.py     # Ranks opportunities
│   ├── core/
│   │   └── job_search_crew.py   # Main orchestrator
│   ├── models/
│   │   └── domain.py            # Pydantic data models
│   ├── config/
│   │   └── settings.py          # Configuration management
│   ├── tools/
│   │   └── job_search_tools.py  # JSearch API integration
│   ├── utils/
│   │   ├── file_parser.py       # PDF/DOCX parsing
│   │   └── csv_storage.py       # Data persistence
│   └── ui/
│       └── app.py               # Streamlit interface
├── data/                    # Stored candidate data (auto-generated)
├── requirements.txt         # Python dependencies
├── .env.example            # Environment template
└── README.md               # This file
```

## ⚙️ Configuration

Copy `.env.example` to `.env` and configure:

```env
# Ollama Settings
OLLAMA__MODEL=llama3
OLLAMA__BASE_URL=http://localhost:11434

# Agent Settings
AGENT__VERBOSE=true

# RapidAPI JSearch (required for job search)
RAPIDAPI_KEY=your_api_key_here
RAPIDAPI_HOST=jsearch.p.rapidapi.com
```

### Getting a RapidAPI Key

1. Go to [RapidAPI JSearch](https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch)
2. Sign up for a free account
3. Subscribe to the JSearch API (free tier: 100 requests/month)
4. Copy your API key to `.env`

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👨‍💻 Author

**Sayandip** - [GitHub](https://github.com/Sayandip05)

---

⭐ Star this repo if you find it useful!
