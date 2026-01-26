"""
Resume Analysis Agent

This agent is responsible for parsing resumes and extracting structured data.
It transforms unstructured text into a validated CandidateProfile.

CrewAI Concepts Used:
- Agent: The autonomous entity with a role and capabilities
- LLM: The language model that powers the agent's reasoning
- Task: The specific job the agent needs to complete
"""

from crewai import Agent, Task, LLM
from typing import Dict, Any
import json

from ..config.settings import settings
from ..models.domain import CandidateProfile, Skill, SkillCategory, ExperienceLevel


def create_ollama_llm() -> LLM:
    """
    Initialize the Ollama LLM using CrewAI's native LLM class
    
    This is our "brain" - the language model that powers agent reasoning.
    We configure it using our settings system.
    
    Returns:
        LLM: Configured language model instance
    
    Why CrewAI LLM class?
    - CrewAI uses LiteLLM under the hood
    - Requires model name in format "ollama/model_name"
    - Properly routes to local Ollama server
    """
    # Format model name for LiteLLM: "ollama/model_name"
    model_name = settings.ollama.model
    if not model_name.startswith("ollama/"):
        model_name = f"ollama/{model_name}"
    
    return LLM(
        model=model_name,
        base_url=settings.ollama.base_url,
        temperature=settings.ollama.temperature,
    )


def create_resume_analyst_agent(llm: LLM) -> Agent:
    """
    Create the Resume Analysis Agent
    
    Agent Design Philosophy:
    - Role: Who the agent is (its persona)
    - Goal: What it's trying to achieve
    - Backstory: Context that shapes its behavior
    - Verbose: Whether to show reasoning steps
    - Allow delegation: Whether it can ask other agents for help
    
    Args:
        llm: The language model to use for reasoning
    
    Returns:
        Agent: Configured resume analyst agent
    """
    return Agent(
        # Identity
        role="Senior Resume Analyst",
        
        # Objective
        goal=(
            "Extract structured, accurate information from resumes including "
            "skills, experience level, years of experience, previous roles, "
            "and education. Ensure all extracted data is precise and complete."
        ),
        
        # Context that shapes behavior
        backstory=(
            "You are an expert recruiter with 15 years of experience analyzing "
            "resumes across various industries. You have a keen eye for detail "
            "and can identify both explicit and implicit skills. You understand "
            "how to map job titles to experience levels and can accurately "
            "estimate years of experience from work history. You always extract "
            "information in a structured, consistent format."
        ),
        
        # Configuration
        llm=llm,
        verbose=settings.agent.verbose,
        allow_delegation=False,  # This agent works independently
    )


def create_resume_analysis_task(
    agent: Agent,
    resume_text: str
) -> Task:
    """
    Create a task for analyzing a resume
    
    This is where the LOGIC lives!
    The task contains:
    - What to do (description)
    - How to think about it (detailed instructions)
    - What format to output (expected_output)
    
    Args:
        agent: The agent that will perform this task
        resume_text: The raw resume text to analyze
    
    Returns:
        Task: Configured analysis task
    """
    return Task(
        description=f"""
        Analyze the following resume and extract structured information.
        
        RESUME TEXT:
        {resume_text}
        
        EXTRACTION REQUIREMENTS:
        
        1. SKILLS EXTRACTION:
           - Identify all technical skills (programming languages, frameworks, tools)
           - Identify soft skills (leadership, communication, etc.)
           - Categorize each skill appropriately
           - Estimate years of experience for each skill if mentioned
           
        2. EXPERIENCE LEVEL DETERMINATION:
           - Calculate total years of professional experience
           - Determine experience level based on:
             * 0-2 years: ENTRY or JUNIOR
             * 2-5 years: MID
             * 5-10 years: SENIOR
             * 10+ years: LEAD or PRINCIPAL
           
        3. WORK HISTORY:
           - Extract all previous job titles
           - Extract all company names
           
        4. EDUCATION:
           - Extract all degrees, certifications, and educational qualifications
           
        5. PROFESSIONAL SUMMARY:
           - Create a concise professional summary (2-3 sentences)
           - Capture the candidate's core expertise and value proposition
        
        OUTPUT FORMAT:
        You must output a valid JSON object matching this structure:
        {{
            "name": "string or null",
            "email": "string or null",
            "summary": "professional summary string",
            "skills": [
                {{
                    "name": "skill name",
                    "category": "programming_language|framework|tool|soft_skill|domain_knowledge",
                    "years_experience": number or null,
                    "proficiency": "beginner|intermediate|advanced|expert or null"
                }}
            ],
            "total_years_experience": number,
            "experience_level": "entry|junior|mid|senior|lead|principal",
            "previous_roles": ["role1", "role2"],
            "previous_companies": ["company1", "company2"],
            "education": ["degree1", "degree2"],
            "raw_resume_text": "original resume text"
        }}
        
        IMPORTANT:
        - Output ONLY valid JSON, no additional text
        - Ensure all skills have at least a name and category
        - Be thorough but accurate - don't invent information
        - If information is not available, use null or empty arrays
        """,
        
        expected_output=(
            "A valid JSON object representing the candidate profile with all "
            "extracted information structured according to the CandidateProfile schema"
        ),
        
        agent=agent,
    )


def parse_resume(resume_text: str) -> CandidateProfile:
    """
    Main function: Parse a resume into a structured CandidateProfile
    
    This orchestrates the entire resume analysis process:
    1. Create the LLM
    2. Create the agent
    3. Create the task
    4. Execute the task
    5. Parse the result into a CandidateProfile
    
    Args:
        resume_text: Raw text from the resume
    
    Returns:
        CandidateProfile: Validated, structured candidate profile
    
    Raises:
        ValueError: If the agent's output cannot be parsed
        ValidationError: If the output doesn't match CandidateProfile schema
    """
    # Step 1: Initialize the LLM
    llm = create_ollama_llm()
    
    # Step 2: Create the specialized agent
    agent = create_resume_analyst_agent(llm)
    
    # Step 3: Create the task with the resume text
    task = create_resume_analysis_task(agent, resume_text)
    
    # Step 4: Execute the task
    # Note: In CrewAI, we need a Crew to execute tasks
    # For now, we'll create a simple crew with just this agent
    from crewai import Crew
    
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=settings.agent.verbose,
    )
    
    # Execute and get result
    result = crew.kickoff()
    
    # Step 5: Parse the JSON result
    try:
        # CrewAI returns a CrewOutput object, convert to string first
        result_str = str(result)
        
        # Try to extract JSON from the result string
        # Sometimes the LLM adds extra text before/after JSON
        import re
        json_match = re.search(r'\{[\s\S]*\}', result_str)
        if json_match:
            json_str = json_match.group()
            parsed_data = json.loads(json_str)
        else:
            raise ValueError("No JSON object found in agent output")
        
        # Step 6: Create and validate the CandidateProfile
        # This is where our Pydantic models shine - automatic validation!
        candidate_profile = CandidateProfile(**parsed_data)
        
        return candidate_profile
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Agent output was not valid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Failed to create CandidateProfile from agent output: {e}")

