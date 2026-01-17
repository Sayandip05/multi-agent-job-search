"""
Job Discovery Agent

This agent searches for relevant job opportunities based on a candidate's profile.
It uses the JSearch API tool to find real job postings that match the candidate's
skills, experience level, and career goals.

Key Responsibilities:
- Understand candidate's target role from their profile
- Use job search tool to find relevant opportunities
- Filter jobs based on skill overlap and experience match
- Return curated list of suitable job postings
"""

from crewai import Agent, Task, Crew, LLM
from typing import List
import json

from ..config.settings import settings
from ..models.domain import CandidateProfile, JobPosting, ExperienceLevel
from ..tools.job_search_tools import JobSearchTool, search_jobs_for_candidate


def create_ollama_llm() -> LLM:
    """Initialize Ollama LLM with proper formatting"""
    model_name = settings.ollama.model
    if not model_name.startswith("ollama/"):
        model_name = f"ollama/{model_name}"
    
    return LLM(
        model=model_name,
        base_url=settings.ollama.base_url,
        temperature=settings.ollama.temperature,
    )


def create_job_discovery_agent(llm: LLM) -> Agent:
    """
    Create the Job Discovery Agent.
    
    This agent acts like a career advisor who understands what jobs
    would be a good fit for a candidate and knows how to search for them.
    
    Key capabilities:
    - Uses JSearch tool to find real job postings
    - Understands job market and role equivalencies
    - Filters irrelevant opportunities
    """
    return Agent(
        role="Job Market Researcher",
        
        goal=(
            "Find the most relevant job opportunities for candidates by searching "
            "real job postings and filtering based on skills, experience level, "
            "and career trajectory. Ensure recommended jobs are realistic matches."
        ),
        
        backstory=(
            "You are a seasoned career advisor and recruiter with deep knowledge "
            "of the job market. You understand how to translate a candidate's "
            "background into effective job searches. You know which job titles "
            "are equivalent (e.g., 'Software Engineer' vs 'Developer'), which "
            "skills are transferable, and what experience levels companies "
            "typically require. You use real-time job search tools to find "
            "current opportunities and can quickly assess if a job is worth "
            "pursuing based on a candidate's profile."
        ),
        
        llm=llm,
        tools=[JobSearchTool()],  # Give the agent access to JSearch
        verbose=settings.agent.verbose,
        allow_delegation=False,
    )


def create_job_discovery_task(
    agent: Agent,
    candidate: CandidateProfile,
    target_role: str,
    num_jobs: int = 5
) -> Task:
    """
    Create a task for discovering relevant jobs.
    
    Args:
        agent: The job discovery agent
        candidate: The candidate's profile
        target_role: The job title/role the candidate is targeting
        num_jobs: Number of jobs to find
    
    Returns:
        Task: Configured job discovery task
    """
    # Extract key info from candidate
    skills_str = ", ".join([skill.name for skill in candidate.skills[:10]])
    experience_str = f"{candidate.experience_level.value} ({candidate.total_years_experience} years)"
    
    return Task(
        description=f"""
        Find {num_jobs} relevant job opportunities for this candidate.
        
        CANDIDATE PROFILE:
        - Target Role: {target_role}
        - Experience Level: {experience_str}
        - Key Skills: {skills_str}
        - Previous Roles: {', '.join(candidate.previous_roles[:3])}
        
        INSTRUCTIONS:
        
        1. USE THE JOB SEARCH TOOL:
           - Search for jobs matching the target role: "{target_role}"
           - The tool will return real job postings from the market
        
        2. EVALUATE EACH JOB:
           For each job returned, assess:
           - Does it match the candidate's experience level?
           - Do the required skills overlap with candidate's skills?
           - Is the job title appropriate for their background?
           - Would this be a realistic opportunity?
        
        3. FILTER AND SELECT:
           - Keep only jobs that are good matches
           - Remove jobs that are too senior or too junior
           - Remove jobs with completely different skill requirements
           - Prioritize jobs where candidate has 60%+ skill overlap
        
        4. RETURN TOP {num_jobs} JOBS:
           - Sort by relevance (best matches first)
           - Include variety (different companies/locations if possible)
        
        OUTPUT FORMAT:
        Return a JSON array of job IDs and brief reasoning:
        {{
            "recommended_jobs": [
                {{
                    "job_id": "job identifier from search results",
                    "title": "job title",
                    "company": "company name",
                    "reason": "1-2 sentences why this is a good match"
                }}
            ],
            "search_summary": "Brief summary of your search strategy and findings"
        }}
        
        IMPORTANT:
        - Actually USE the job_search tool - don't make up jobs
        - Be selective - only recommend truly relevant opportunities
        - Consider both required and preferred skills
        - Output ONLY valid JSON, no additional text
        """,
        
        expected_output=(
            "A JSON object containing recommended job IDs with reasoning "
            "and a search summary"
        ),
        
        agent=agent,
    )


def discover_jobs(
    candidate: CandidateProfile,
    target_role: str,
    num_jobs: int = 5
) -> List[JobPosting]:
    """
    Main function: Discover relevant jobs for a candidate.
    
    This orchestrates the job discovery process:
    1. Agent uses JSearch tool to find jobs
    2. Agent evaluates and filters results
    3. We fetch full details for recommended jobs
    
    Args:
        candidate: The candidate's profile
        target_role: Job title/role to search for
        num_jobs: Number of jobs to return
    
    Returns:
        List of JobPosting objects
    
    Raises:
        ValueError: If job discovery fails
    """
    # Create LLM and agent
    llm = create_ollama_llm()
    agent = create_job_discovery_agent(llm)
    
    # Create task
    task = create_job_discovery_task(agent, candidate, target_role, num_jobs)
    
    # Execute
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=settings.agent.verbose,
    )
    
    result = crew.kickoff()
    
    # Parse result
    try:
        import re
        result_str = str(result)
        
        # Extract JSON
        json_match = re.search(r'\{[\s\S]*\}', result_str)
        if json_match:
            json_str = json_match.group()
            parsed_data = json.loads(json_str)
        else:
            raise ValueError("No JSON found in agent output")
        
        # Get recommended job IDs
        recommended = parsed_data.get("recommended_jobs", [])
        
        if not recommended:
            print("⚠️  Agent didn't find any suitable jobs")
            # Fallback: search directly
            return search_jobs_for_candidate(target_role, [], num_results=num_jobs)
        
        # Fetch full job details for recommended jobs
        # Since we already have the job data from the tool, we'll search again
        # In production, you'd cache the results
        all_jobs = search_jobs_for_candidate(target_role, [], num_results=10)
        
        # Filter to only recommended jobs
        recommended_job_ids = [job["job_id"] for job in recommended]
        filtered_jobs = [
            job for job in all_jobs 
            if job.job_id in recommended_job_ids
        ]
        
        # If filtering removed too many, just return the search results
        if len(filtered_jobs) < 3:
            filtered_jobs = all_jobs[:num_jobs]
        
        return filtered_jobs[:num_jobs]
        
    except Exception as e:
        print(f"⚠️  Error parsing agent output: {e}")
        # Fallback: direct search
        return search_jobs_for_candidate(target_role, [], num_results=num_jobs)


# Testing code
if __name__ == "__main__":
    """
    Test the job discovery agent
    
    Run: python -m src.agents.job_discovery
    """
    from ..models.domain import Skill, SkillCategory
    
    print("🚀 Testing Job Discovery Agent...\n")
    print("=" * 60)
    
    # Create sample candidate
    candidate = CandidateProfile(
        name="John Doe",
        email="john@email.com",
        summary="Experienced Python developer with ML expertise",
        skills=[
            Skill(
                name="Python",
                category=SkillCategory.PROGRAMMING_LANGUAGE,
                years_experience=4.0,
                proficiency="advanced"
            ),
            Skill(
                name="Machine Learning",
                category=SkillCategory.DOMAIN_KNOWLEDGE,
                years_experience=2.0,
                proficiency="intermediate"
            ),
            Skill(
                name="FastAPI",
                category=SkillCategory.FRAMEWORK,
                years_experience=2.0,
                proficiency="intermediate"
            ),
        ],
        total_years_experience=4.0,
        experience_level=ExperienceLevel.MID,
        previous_roles=["Software Engineer", "ML Engineer"],
        previous_companies=["TechCorp"],
        education=["B.S. Computer Science"],
        raw_resume_text="Sample resume"
    )
    
    try:
        print("\n🔍 Searching for 'Python Developer' jobs...\n")
        
        jobs = discover_jobs(
            candidate=candidate,
            target_role="Python Developer",
            num_jobs=5
        )
        
        print(f"\n✅ Found {len(jobs)} relevant job opportunities!\n")
        
        for i, job in enumerate(jobs, 1):
            print(f"Job {i}: {job.title}")
            print(f"  Company: {job.company}")
            print(f"  Location: {job.location}")
            print(f"  Skills: {', '.join(job.required_skills[:5])}")
            print(f"  URL: {job.url[:50] if job.url else 'N/A'}...")
            print()
        
        print("=" * 60)
        print("🎉 Job Discovery Agent is working!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()