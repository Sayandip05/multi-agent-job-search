"""
Domain Models - Core Business Entities

This module defines the data structures that represent our business domain.
Following Domain-Driven Design (DDD) principles:
- Models are independent of infrastructure (databases, APIs)
- Models enforce business rules through validation
- Models are immutable where possible (Pydantic frozen)

Why this matters for resume-quality:
- Shows understanding of clean architecture
- Separates business logic from technical concerns
- Makes testing easier (no database needed)
"""

from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator


class ExperienceLevel(str, Enum):
    """
    Standardized experience levels for job matching
    Using Enum ensures only valid values can be used
    """
    ENTRY = "entry"
    JUNIOR = "junior"
    MID = "mid"
    SENIOR = "senior"
    LEAD = "lead"
    PRINCIPAL = "principal"


class SkillCategory(str, Enum):
    """Categories for organizing skills"""
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    TOOL = "tool"
    SOFT_SKILL = "soft_skill"
    DOMAIN_KNOWLEDGE = "domain_knowledge"
    DATABASE = "database"
    CLOUD = "cloud"
    DEVOPS = "devops"


class Skill(BaseModel):
    """
    Represents a single skill with proficiency level
    
    Example: Skill(name="Python", category="programming_language", years=3)
    """
    name: str = Field(description="Skill name (e.g., 'Python', 'Leadership')")
    category: SkillCategory = Field(description="Type of skill")
    years_experience: Optional[float] = Field(
        default=None,
        ge=0,
        description="Years of experience with this skill"
    )
    proficiency: Optional[str] = Field(
        default=None,
        description="Self-assessed level: beginner, intermediate, advanced, expert"
    )
    
    class Config:
        # Makes model immutable - professional practice for value objects
        frozen = True


class CandidateProfile(BaseModel):
    """
    Structured representation of a candidate's resume
    
    This is what the Resume Analysis Agent produces.
    It's the "canonical" representation of the candidate.
    """
    # Basic information
    name: Optional[str] = Field(default=None, description="Candidate name")
    email: Optional[str] = Field(default=None, description="Contact email")
    
    # Professional summary
    summary: str = Field(description="Professional summary or objective")
    
    # Experience and skills
    skills: List[Skill] = Field(
        default_factory=list,
        description="List of candidate skills"
    )
    total_years_experience: float = Field(
        ge=0,
        description="Total years of professional experience"
    )
    experience_level: ExperienceLevel = Field(
        description="Overall seniority level"
    )
    
    # Work history (simplified - can be expanded)
    previous_roles: List[str] = Field(
        default_factory=list,
        description="List of previous job titles"
    )
    previous_companies: List[str] = Field(
        default_factory=list,
        description="List of previous employers"
    )
    
    # Education
    education: List[str] = Field(
        default_factory=list,
        description="Educational qualifications"
    )
    
    # Metadata
    raw_resume_text: str = Field(description="Original resume text")
    analyzed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this profile was created"
    )
    
    @field_validator('skills')
    @classmethod
    def validate_skills_not_empty(cls, v: List[Skill]) -> List[Skill]:
        """Business rule: A candidate must have at least one skill"""
        if not v:
            raise ValueError("Candidate must have at least one skill")
        return v


class JobPosting(BaseModel):
    """
    Represents a job opportunity
    
    This is what the Job Discovery Agent finds/creates.
    """
    # Job identifiers
    job_id: str = Field(description="Unique job identifier")
    title: str = Field(description="Job title")
    company: str = Field(description="Company name")
    
    # Job details
    description: str = Field(description="Full job description")
    required_skills: List[str] = Field(
        default_factory=list,
        description="Hard requirements"
    )
    preferred_skills: List[str] = Field(
        default_factory=list,
        description="Nice-to-have skills"
    )
    experience_level: ExperienceLevel = Field(
        description="Required seniority level"
    )
    
    # Additional info
    location: Optional[str] = Field(default=None, description="Job location")
    salary_range: Optional[str] = Field(default=None, description="Salary info")
    remote_policy: Optional[str] = Field(
        default=None,
        description="Remote/hybrid/onsite"
    )
    
    # Metadata
    posted_date: Optional[datetime] = Field(
        default=None,
        description="When job was posted"
    )
    url: Optional[str] = Field(default=None, description="Application link")


class SkillMatch(BaseModel):
    """
    Represents how well a candidate's skill matches a job requirement
    
    This is what the Skill Matching Agent produces.
    """
    skill_name: str = Field(description="Name of the skill being matched")
    candidate_has: bool = Field(description="Does candidate have this skill?")
    candidate_years: Optional[float] = Field(
        default=None,
        description="Candidate's years of experience"
    )
    required_years: Optional[float] = Field(
        default=None,
        description="Job's required years"
    )
    match_strength: float = Field(
        ge=0.0,
        le=1.0,
        description="Match score: 0=no match, 1=perfect match"
    )
    is_required: bool = Field(
        default=True,
        description="Is this a hard requirement or preferred?"
    )


class JobMatchResult(BaseModel):
    """
    Complete evaluation of how well a candidate fits a job
    
    This is the final output combining all agent analyses.
    """
    # References
    candidate_profile: CandidateProfile
    job_posting: JobPosting
    
    # Matching analysis
    skill_matches: List[SkillMatch] = Field(
        description="Detailed skill-by-skill comparison"
    )
    
    # Scores (0-100)
    overall_fit_score: float = Field(
        ge=0.0,
        le=100.0,
        description="Overall match score"
    )
    skill_match_score: float = Field(
        ge=0.0,
        le=60.0,
        description="How well skills align (max 60)"
    )
    experience_match_score: float = Field(
        ge=0.0,
        le=30.0,
        description="How well experience level aligns (max 30)"
    )
    
    # Analysis
    strengths: List[str] = Field(
        description="Why candidate is a good fit"
    )
    gaps: List[str] = Field(
        description="What candidate is missing"
    )
    recommendation: str = Field(
        description="Apply/Skip/Stretch and reasoning"
    )
    
    # Explanation (human-readable)
    explanation: str = Field(
        description="Natural language explanation of the match"
    )
    
    # Metadata
    evaluated_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When this evaluation was performed"
    )


# Example usage for testing
if __name__ == "__main__":
    """
    This demonstrates how to create and validate domain models.
    Run: python src/models/domain.py
    """
    
    # Create a sample skill
    python_skill = Skill(
        name="Python",
        category=SkillCategory.PROGRAMMING_LANGUAGE,
        years_experience=3.5,
        proficiency="advanced"
    )
    
    print("✅ Created skill:", python_skill)
    print(f"   Immutable: {python_skill.model_config.get('frozen')}")
    
    # Create a candidate profile
    candidate = CandidateProfile(
        name="John Doe",
        summary="Experienced Python developer specializing in AI/ML",
        skills=[python_skill],
        total_years_experience=3.5,
        experience_level=ExperienceLevel.MID,
        previous_roles=["Software Engineer", "Data Analyst"],
        raw_resume_text="Sample resume text..."
    )
    
    print("\n✅ Created candidate profile:")
    print(f"   Name: {candidate.name}")
    print(f"   Experience: {candidate.experience_level.value}")
    print(f"   Skills: {len(candidate.skills)}")
    
    # Demonstrate validation
    try:
        invalid_candidate = CandidateProfile(
            summary="No skills!",
            skills=[],  # This will fail validation
            total_years_experience=0,
            experience_level=ExperienceLevel.ENTRY,
            raw_resume_text="text"
        )
    except ValueError as e:
        print(f"\n✅ Validation working: {e}")
    
    print("\n🎉 All domain models are valid!")