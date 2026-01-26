"""
Skill Matching Agent

This agent compares a candidate's profile against job requirements and produces
a detailed match analysis with explicit scoring logic.

This demonstrates Option B: Explicit, auditable scoring rules.
"""

from crewai import Agent, Task, Crew, LLM
from typing import List, Optional
from pydantic import BaseModel, Field
import json
import re

from ..config.settings import settings
from ..models.domain import (
    CandidateProfile,
    JobPosting,
    JobMatchResult,
    SkillMatch,
    ExperienceLevel
)


# Pydantic model for structured LLM output
class SkillMatchItem(BaseModel):
    """Individual skill match result"""
    skill_name: str
    candidate_has: bool
    candidate_years: Optional[float] = None
    required_years: Optional[float] = None
    match_strength: float = Field(ge=0.0, le=1.0)
    is_required: bool = True


class SkillMatchOutput(BaseModel):
    """Structured output from the skill matching agent"""
    skill_matches: List[SkillMatchItem]
    overall_fit_score: float = Field(ge=0.0, le=100.0)
    skill_match_score: float = Field(ge=0.0, le=60.0)
    experience_match_score: float = Field(ge=0.0, le=30.0)
    strengths: List[str]
    gaps: List[str]
    recommendation: str
    explanation: str


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


def create_skill_matcher_agent(llm: LLM) -> Agent:
    """
    Create the Skill Matching Agent
    
    This agent specializes in comparing candidate skills against job requirements.
    It follows explicit scoring rules to ensure consistency and explainability.
    """
    return Agent(
        role="Technical Skill Matcher",
        
        goal=(
            "Accurately compare candidate skills against job requirements using "
            "explicit scoring rules. Identify matches, gaps, and provide detailed "
            "explanations with precise score calculations."
        ),
        
        backstory=(
            "You are a meticulous technical recruiter with expertise in skill "
            "assessment. You have a mathematical approach to candidate evaluation, "
            "always following consistent scoring criteria. You can identify skill "
            "equivalents (e.g., Flask and FastAPI are similar frameworks) and "
            "understand what 'years of experience' truly means for different "
            "technologies. Your analyses are always backed by clear reasoning "
            "and numerical breakdowns."
        ),
        
        llm=llm,
        verbose=settings.agent.verbose,
        allow_delegation=False,
    )


def create_skill_matching_task(
    agent: Agent,
    candidate: CandidateProfile,
    job: JobPosting
) -> Task:
    """
    Create a task for matching candidate skills to job requirements.
    
    This task contains EXPLICIT SCORING LOGIC (Option B approach).
    The agent must follow these rules precisely.
    """
    
    # Format candidate skills for the prompt
    candidate_skills_str = "\n".join([
        f"  - {skill.name} ({skill.category.value}): "
        f"{skill.years_experience or 'unspecified'} years, "
        f"{skill.proficiency or 'unspecified'} proficiency"
        for skill in candidate.skills
    ])
    
    return Task(
        description=f"""
        Perform a detailed skill match analysis between the candidate and job posting.
        
        CANDIDATE INFORMATION:
        - Name: {candidate.name}
        - Experience Level: {candidate.experience_level.value}
        - Total Years: {candidate.total_years_experience}
        - Skills:
{candidate_skills_str}
        
        JOB POSTING INFORMATION:
        - Title: {job.title}
        - Company: {job.company}
        - Required Experience Level: {job.experience_level.value}
        - Required Skills: {', '.join(job.required_skills)}
        - Preferred Skills: {', '.join(job.preferred_skills)}
        
        EXPLICIT SCORING RULES (Total: 100 points):
        
        1. SKILL MATCHING (60 points max):
           For each REQUIRED skill:
           - Exact match + sufficient experience: +20 points
           - Exact match + insufficient experience: +10 points
           - Similar/equivalent skill: +15 points
           - Missing: 0 points
           
           For each PREFERRED skill:
           - Has skill: +5 points
           - Missing: 0 points
           
           Cap at 60 points total for this section.
        
        2. EXPERIENCE LEVEL MATCHING (30 points max):
           - Exact match: +30 points
           - One level above: +20 points
           - One level below: +15 points
           - Two+ levels different: +5 points
           
           Experience hierarchy: entry < junior < mid < senior < lead < principal
        
        3. OVERALL PROFILE STRENGTH (10 points max):
           - Strong overall fit with job domain: +10 points
           - Moderate fit: +5 points
           - Weak fit: 0 points
        
        ANALYSIS REQUIREMENTS:
        
        1. Create a SkillMatch object for EACH required skill:
           - skill_name: name of the required skill
           - candidate_has: true if candidate has this skill (or equivalent)
           - candidate_years: candidate's years with this skill
           - required_years: if mentioned in job description
           - match_strength: 0.0 to 1.0 (0=no match, 1=perfect match)
           - is_required: true
        
        2. Calculate scores using the rules above:
           - skill_match_score: 0-60 based on skill matching rules
           - experience_match_score: 0-30 based on experience level rules
           - overall_fit_score: Sum of all scores (0-100)
        
        3. Identify STRENGTHS (what makes this candidate good):
           - List specific skills they excel at
           - Highlight relevant experience
           - Note transferable skills
        
        4. Identify GAPS (what's missing):
           - List required skills they lack
           - Note experience level mismatches
           - Mention significant weaknesses
        
        5. Provide RECOMMENDATION:
           - "Strong Match - Recommend Interview" (score >= 75)
           - "Good Match - Consider for Interview" (score 60-74)
           - "Moderate Match - Review Carefully" (score 50-59)
           - "Weak Match - Likely Not Suitable" (score < 50)
        
        6. Write EXPLANATION (2-3 paragraphs):
           - Paragraph 1: Overall assessment and score breakdown
           - Paragraph 2: Key strengths and why they're valuable
           - Paragraph 3: Gaps and whether they're dealbreakers
        
        OUTPUT FORMAT:
        You must output ONLY valid JSON matching this structure:
        {{
            "skill_matches": [
                {{
                    "skill_name": "skill name",
                    "candidate_has": true/false,
                    "candidate_years": number or null,
                    "required_years": number or null,
                    "match_strength": 0.0-1.0,
                    "is_required": true/false
                }}
            ],
            "overall_fit_score": 0-100,
            "skill_match_score": 0-60,
            "experience_match_score": 0-30,
            "strengths": ["strength 1", "strength 2", ...],
            "gaps": ["gap 1", "gap 2", ...],
            "recommendation": "recommendation string",
            "explanation": "detailed explanation paragraphs"
        }}
        
        IMPORTANT:
        - Follow the scoring rules EXACTLY
        - Show your score calculations in the explanation
        - Be thorough but fair in your assessment
        - Output ONLY the JSON, no additional text
        """,
        
        expected_output=(
            "A valid JSON object containing detailed skill match analysis, "
            "explicit scores, strengths, gaps, recommendation, and explanation"
        ),
        
        agent=agent,
        output_pydantic=SkillMatchOutput,  # Force structured output
    )


def match_candidate_to_job(
    candidate: CandidateProfile,
    job: JobPosting
) -> JobMatchResult:
    """
    Main function: Match a candidate to a job posting.
    
    Args:
        candidate: The candidate's profile
        job: The job posting requirements
    
    Returns:
        JobMatchResult: Complete match analysis with scores and recommendations
    
    Raises:
        ValueError: If agent output cannot be parsed
    """
    # Step 1: Create LLM and agent
    llm = create_ollama_llm()
    agent = create_skill_matcher_agent(llm)
    
    # Step 2: Create the matching task
    task = create_skill_matching_task(agent, candidate, job)
    
    # Step 3: Execute
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=settings.agent.verbose,
    )
    
    result = crew.kickoff()
    
    # Step 4: Parse result
    try:
        # Check if CrewAI returned a pydantic model directly
        if hasattr(result, 'pydantic') and result.pydantic is not None:
            output = result.pydantic
        elif isinstance(result, SkillMatchOutput):
            output = result
        else:
            # Fall back to JSON parsing from raw output
            result_str = result.raw if hasattr(result, 'raw') else str(result)
            
            # Try to parse as SkillMatchOutput
            import re
            
            # Remove markdown code blocks
            result_str = re.sub(r'```json\s*', '', result_str)
            result_str = re.sub(r'```\s*', '', result_str)
            
            # Find JSON object
            start_idx = result_str.find('{')
            if start_idx == -1:
                raise ValueError("No JSON object found in agent output")
            
            # Find matching closing brace
            depth = 0
            in_string = False
            escape_next = False
            end_idx = -1
            
            for i, char in enumerate(result_str[start_idx:], start_idx):
                if escape_next:
                    escape_next = False
                    continue
                if char == '\\':
                    escape_next = True
                    continue
                if char == '"' and not escape_next:
                    in_string = not in_string
                    continue
                if in_string:
                    continue
                if char == '{':
                    depth += 1
                elif char == '}':
                    depth -= 1
                    if depth == 0:
                        end_idx = i
                        break
            
            if end_idx == -1:
                raise ValueError("Malformed JSON in agent output")
            
            json_str = result_str[start_idx:end_idx+1]
            
            # Fix common issues
            json_str = re.sub(r',\s*}', '}', json_str)
            json_str = re.sub(r',\s*]', ']', json_str)
            
            parsed_data = json.loads(json_str)
            output = SkillMatchOutput(**parsed_data)
        
        # Create SkillMatch objects from the output
        skill_matches = [
            SkillMatch(
                skill_name=sm.skill_name,
                candidate_has=sm.candidate_has,
                candidate_years=sm.candidate_years,
                required_years=sm.required_years,
                match_strength=sm.match_strength,
                is_required=sm.is_required
            )
            for sm in output.skill_matches
        ]
        
        # Step 5: Construct JobMatchResult
        match_result = JobMatchResult(
            candidate_profile=candidate,
            job_posting=job,
            skill_matches=skill_matches,
            overall_fit_score=output.overall_fit_score,
            skill_match_score=output.skill_match_score,
            experience_match_score=output.experience_match_score,
            strengths=output.strengths,
            gaps=output.gaps,
            recommendation=output.recommendation,
            explanation=output.explanation,
        )
        
        return match_result
        
    except json.JSONDecodeError as e:
        raise ValueError(f"Agent output was not valid JSON: {e}")
    except Exception as e:
        raise ValueError(f"Failed to create JobMatchResult: {e}")

