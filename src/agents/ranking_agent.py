"""
Ranking Agent

This agent takes multiple job match results and ranks them to help candidates
prioritize which opportunities to pursue first.

While we could just sort by score, this agent adds strategic intelligence:
- Considers score, but also growth potential, remote options, company reputation
- Identifies "stretch" opportunities vs "safe bets"
- Groups similar opportunities
- Provides actionable prioritization advice

This is Option B (Intelligent Ranker) - more impressive for resume purposes.
"""

from crewai import Agent, Task, Crew, LLM
from typing import List, Dict, Any
import json
import re

from ..config.settings import settings
from ..models.domain import JobMatchResult


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


def create_ranking_agent(llm: LLM) -> Agent:
    """
    Create the Job Ranking Agent.
    
    This agent acts as a strategic career advisor who understands not just
    "which job scores highest" but "which job should the candidate pursue first"
    considering multiple factors.
    """
    return Agent(
        role="Strategic Career Advisor",
        
        goal=(
            "Rank job opportunities strategically to help candidates make the best "
            "career decisions. Consider not just match scores, but also career growth "
            "potential, company trajectory, work-life balance, and candidate's goals."
        ),
        
        backstory=(
            "You are a senior career strategist with 20 years of experience advising "
            "professionals on job selection. You understand that the 'best' job isn't "
            "always the highest scoring one. You consider factors like: Is this a "
            "growing company? Does it offer learning opportunities? Is the commute "
            "reasonable? Will this advance their career 5 years from now? You provide "
            "nuanced, strategic advice that goes beyond simple numerical rankings. "
            "You can identify 'hidden gems' - jobs that might score slightly lower "
            "but offer better long-term value."
        ),
        
        llm=llm,
        verbose=settings.agent.verbose,
        allow_delegation=False,
    )


def create_ranking_task(
    agent: Agent,
    match_results: List[JobMatchResult]
) -> Task:
    """
    Create a task for ranking job opportunities.
    
    Args:
        agent: The ranking agent
        match_results: List of job match results to rank
    
    Returns:
        Task: Configured ranking task
    """
    # Format match results for the prompt
    jobs_summary = []
    for i, match in enumerate(match_results, 1):
        jobs_summary.append(f"""
Job {i}:
  Title: {match.job_posting.title}
  Company: {match.job_posting.company}
  Location: {match.job_posting.location or 'Not specified'}
  Overall Score: {match.overall_fit_score}/100
  Skill Match: {match.skill_match_score}/60
  Experience Match: {match.experience_match_score}/30
  
  Strengths: {', '.join(match.strengths[:3])}
  Gaps: {', '.join(match.gaps[:2]) if match.gaps else 'None'}
  Recommendation: {match.recommendation}
  
  Remote Policy: {match.job_posting.remote_policy or 'Unknown'}
  Salary: {match.job_posting.salary_range or 'Not disclosed'}
        """)
    
    jobs_text = "\n".join(jobs_summary)
    
    return Task(
        description=f"""
        Rank these {len(match_results)} job opportunities strategically for the candidate.
        
        JOB OPPORTUNITIES TO RANK:
        {jobs_text}
        
        RANKING METHODOLOGY:
        
        Your ranking should consider multiple factors, not just the overall_fit_score:
        
        1. BASE SCORE (40% weight):
           - Use the overall_fit_score as foundation
           - Higher scores indicate better technical fit
        
        2. CAREER GROWTH POTENTIAL (25% weight):
           - Is this a senior role offering advancement?
           - Does the company appear to be growing?
           - Will this add valuable experience to resume?
        
        3. PRACTICAL FACTORS (20% weight):
           - Remote vs on-site vs hybrid
           - Location/commute if on-site
           - Work-life balance indicators
           - Salary competitiveness (if disclosed)
        
        4. STRATEGIC VALUE (15% weight):
           - Does this fill skill gaps?
           - Is this a "stretch" opportunity for growth?
           - Company reputation and stability
           - Industry trends (growing vs declining sectors)
        
        CATEGORIZATION:
        
        Classify each job into one of these tiers:
        
        - TIER 1 "Top Priority": Apply immediately, excellent fit
        - TIER 2 "Strong Contender": Definitely apply, very good fit  
        - TIER 3 "Worth Considering": Apply if time permits, decent fit
        - TIER 4 "Backup Option": Keep on radar, apply if nothing better
        
        OUTPUT FORMAT:
        
        Return a JSON object with this structure:
        {{
            "ranked_jobs": [
                {{
                    "rank": 1,
                    "job_title": "title",
                    "company": "company name",
                    "tier": "TIER 1|TIER 2|TIER 3|TIER 4",
                    "final_score": 0-100,
                    "ranking_rationale": "2-3 sentences explaining why this rank",
                    "action_recommendation": "Apply immediately|Apply this week|Consider applying|Keep as backup"
                }}
            ],
            "overall_strategy": "2-3 sentences of strategic advice for the candidate's job search",
            "top_recommendation": "Which single job to prioritize and why (1-2 sentences)"
        }}
        
        IMPORTANT:
        - Be strategic, not just mathematical
        - Consider the candidate's career trajectory
        - Identify both safe bets and growth opportunities
        - Be realistic about pros and cons
        - Output ONLY valid JSON, no additional text
        """,
        
        expected_output=(
            "A JSON object containing strategically ranked jobs with tiers, "
            "rationale, and actionable recommendations"
        ),
        
        agent=agent,
    )


def rank_job_matches(match_results: List[JobMatchResult]) -> Dict[str, Any]:
    """
    Main function: Rank job match results strategically.
    
    Args:
        match_results: List of JobMatchResult objects to rank
    
    Returns:
        Dictionary containing ranked jobs with strategic advice
    
    Raises:
        ValueError: If ranking fails
    """
    if not match_results:
        return {
            "ranked_jobs": [],
            "overall_strategy": "No jobs to rank",
            "top_recommendation": "Search for more opportunities"
        }
    
    # If only one job, no need for complex ranking
    if len(match_results) == 1:
        job = match_results[0]
        return {
            "ranked_jobs": [{
                "rank": 1,
                "job_title": job.job_posting.title,
                "company": job.job_posting.company,
                "tier": "TIER 1" if job.overall_fit_score >= 70 else "TIER 2",
                "final_score": job.overall_fit_score,
                "ranking_rationale": f"Only opportunity available. Score: {job.overall_fit_score}/100",
                "action_recommendation": "Apply immediately"
            }],
            "overall_strategy": "This is your primary opportunity - focus on a strong application",
            "top_recommendation": f"Apply to {job.job_posting.title} at {job.job_posting.company}"
        }
    
    # Create LLM and agent
    llm = create_ollama_llm()
    agent = create_ranking_agent(llm)
    
    # Create task
    task = create_ranking_task(agent, match_results)
    
    # Execute
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=settings.agent.verbose,
    )
    
    result = crew.kickoff()
    
    # Parse result
    try:
        result_str = str(result)
        
        # Extract JSON
        json_match = re.search(r'\{[\s\S]*\}', result_str)
        if json_match:
            json_str = json_match.group()
            parsed_data = json.loads(json_str)
            return parsed_data
        else:
            raise ValueError("No JSON found in agent output")
            
    except Exception as e:
        print(f"⚠️  Error parsing ranking output: {e}")
        # Fallback: simple score-based ranking
        return _fallback_ranking(match_results)


def _fallback_ranking(match_results: List[JobMatchResult]) -> Dict[str, Any]:
    """
    Fallback ranking if agent fails - simple score-based sort.
    
    This ensures the system always works even if the LLM fails.
    """
    # Sort by overall_fit_score
    sorted_results = sorted(
        match_results,
        key=lambda x: x.overall_fit_score,
        reverse=True
    )
    
    ranked_jobs = []
    for i, match in enumerate(sorted_results, 1):
        # Determine tier based on score
        if match.overall_fit_score >= 75:
            tier = "TIER 1"
            action = "Apply immediately"
        elif match.overall_fit_score >= 60:
            tier = "TIER 2"
            action = "Apply this week"
        elif match.overall_fit_score >= 50:
            tier = "TIER 3"
            action = "Consider applying"
        else:
            tier = "TIER 4"
            action = "Keep as backup"
        
        ranked_jobs.append({
            "rank": i,
            "job_title": match.job_posting.title,
            "company": match.job_posting.company,
            "tier": tier,
            "final_score": match.overall_fit_score,
            "ranking_rationale": f"Ranked by match score ({match.overall_fit_score}/100)",
            "action_recommendation": action
        })
    
    return {
        "ranked_jobs": ranked_jobs,
        "overall_strategy": "Jobs ranked by match score. Focus on highest scoring opportunities first.",
        "top_recommendation": f"Start with {ranked_jobs[0]['job_title']} at {ranked_jobs[0]['company']}"
    }


# Testing code
if __name__ == "__main__":
    """
    Test the ranking agent
    
    Run: python -m src.agents.ranking_agent
    """
    from ..models.domain import (
        CandidateProfile, JobPosting, Skill, SkillCategory,
        ExperienceLevel, SkillMatch
    )
    
    print("🚀 Testing Ranking Agent...\n")
    print("=" * 60)
    
    # Create sample candidate
    candidate = CandidateProfile(
        name="Jane Smith",
        summary="Python developer",
        skills=[
            Skill(name="Python", category=SkillCategory.PROGRAMMING_LANGUAGE,
                  years_experience=3.0, proficiency="advanced")
        ],
        total_years_experience=3.0,
        experience_level=ExperienceLevel.MID,
        previous_roles=["Developer"],
        raw_resume_text="test"
    )
    
    # Create sample job matches (3 jobs with different scores)
    job1 = JobPosting(
        job_id="1",
        title="Senior Python Developer",
        company="Tech Giant Inc",
        description="...",
        required_skills=["Python", "Django"],
        experience_level=ExperienceLevel.SENIOR,
        location="San Francisco",
        salary_range="$150k-$180k",
        remote_policy="Hybrid"
    )
    
    job2 = JobPosting(
        job_id="2",
        title="Python Engineer",
        company="Startup XYZ",
        description="...",
        required_skills=["Python", "FastAPI"],
        experience_level=ExperienceLevel.MID,
        location="Remote",
        salary_range="$120k-$140k",
        remote_policy="Fully Remote"
    )
    
    job3 = JobPosting(
        job_id="3",
        title="Backend Developer",
        company="Medium Corp",
        description="...",
        required_skills=["Python", "PostgreSQL"],
        experience_level=ExperienceLevel.MID,
        location="New York",
        salary_range="$110k-$130k",
        remote_policy="On-site"
    )
    
    # Create match results with different scores
    match1 = JobMatchResult(
        candidate_profile=candidate,
        job_posting=job1,
        skill_matches=[],
        overall_fit_score=72.0,
        skill_match_score=45.0,
        experience_match_score=15.0,
        strengths=["Strong Python skills", "Good experience"],
        gaps=["Experience level one below required"],
        recommendation="Good Match - Consider for Interview",
        explanation="Decent fit but slightly junior"
    )
    
    match2 = JobMatchResult(
        candidate_profile=candidate,
        job_posting=job2,
        skill_matches=[],
        overall_fit_score=85.0,
        skill_match_score=55.0,
        experience_match_score=30.0,
        strengths=["Perfect experience match", "Remote work", "Modern stack"],
        gaps=[],
        recommendation="Strong Match - Recommend Interview",
        explanation="Excellent fit, fully remote, growing startup"
    )
    
    match3 = JobMatchResult(
        candidate_profile=candidate,
        job_posting=job3,
        skill_matches=[],
        overall_fit_score=68.0,
        skill_match_score=40.0,
        experience_match_score=20.0,
        strengths=["Experience match", "Stable company"],
        gaps=["Requires on-site", "Limited remote options"],
        recommendation="Moderate Match - Review Carefully",
        explanation="Good fit but location may be challenging"
    )
    
    try:
        print("\n📊 Ranking 3 job opportunities...\n")
        
        ranking = rank_job_matches([match1, match2, match3])
        
        print("✅ Ranking Complete!\n")
        print("=" * 60)
        print("RANKED JOB OPPORTUNITIES:\n")
        
        for job in ranking["ranked_jobs"]:
            print(f"#{job['rank']} - {job['tier']}")
            print(f"   {job['job_title']} at {job['company']}")
            print(f"   Score: {job['final_score']}/100")
            print(f"   Action: {job['action_recommendation']}")
            print(f"   Why: {job['ranking_rationale']}")
            print()
        
        print("=" * 60)
        print(f"\n💡 STRATEGY: {ranking['overall_strategy']}")
        print(f"\n🎯 TOP PICK: {ranking['top_recommendation']}")
        
        print("\n" + "=" * 60)
        print("🎉 Ranking Agent is working correctly!")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()



