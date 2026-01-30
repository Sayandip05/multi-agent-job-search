"""
Job Search Tool - RapidAPI JSearch Integration

This tool wraps the JSearch API from RapidAPI and makes it available to CrewAI agents.
It demonstrates how to integrate external APIs into the multi-agent system.

Why a Custom Tool?
- Agents can't directly call APIs - they need tools
- Tools provide a standardized interface
- Tools handle error cases and data formatting
- Tools can be reused across multiple agents
"""

import requests
from typing import List, Dict, Any, Optional, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..config.settings import settings
from ..models.domain import JobPosting, ExperienceLevel


class JobSearchToolSchema(BaseModel):
    """Schema for job search tool arguments."""
    query: str = Field(
        ...,
        description="Job title or keywords to search for, e.g., 'Python Developer', 'Data Scientist'"
    )
    num_results: int = Field(
        default=10,
        description="Number of job results to return (max 10)"
    )
    location: Optional[str] = Field(
        default=None,
        description="Optional location filter, e.g., 'Remote', 'New York', 'India'"
    )


class JobSearchTool(BaseTool):
    """
    Custom CrewAI tool for searching jobs using JSearch API.
    
    This tool allows agents to search for real job postings based on:
    - Job title/keywords
    - Location
    - Experience level
    - Number of results
    
    The tool handles API calls, error handling, and data transformation.
    """
    
    name: str = "job_search"
    description: str = (
        "Search for real job postings using JSearch API. "
        "Input should be a job title or keywords (e.g., 'Python Developer', 'Data Scientist'). "
        "Returns a list of relevant job postings with details like title, company, "
        "description, required skills, and location."
    )
    args_schema: Type[BaseModel] = JobSearchToolSchema
    
    def _run(
        self,
        query: str,
        num_results: int = 10,
        location: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Execute the job search.
        
        Args:
            query: Job title or keywords to search for
            num_results: Number of results to return (max 10 for free tier)
            location: Optional location filter (e.g., "Remote", "New York")
        
        Returns:
            List of job postings as dictionaries
        
        API Documentation:
        https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
        """
        try:
            # Construct search query
            search_query = query
            if location:
                search_query = f"{query} {location}"
            
            # API endpoint and headers
            url = f"https://{settings.rapidapi_host}/search"
            headers = {
                "X-RapidAPI-Key": settings.rapidapi_key,
                "X-RapidAPI-Host": settings.rapidapi_host
            }
            
            # Query parameters
            params = {
                "query": search_query,
                "num_pages": "1",  # Free tier limitation
                "page": "1"
            }
            
            # Make API request
            response = requests.get(url, headers=headers, params=params, timeout=10)
            response.raise_for_status()  # Raise exception for bad status codes
            
            data = response.json()
            
            # Extract job listings
            jobs = data.get("data", [])
            
            # Limit results
            jobs = jobs[:num_results]
            
            # Transform to simpler format
            simplified_jobs = []
            for job in jobs:
                simplified_jobs.append({
                    "job_id": job.get("job_id", ""),
                    "title": job.get("job_title", ""),
                    "company": job.get("employer_name", ""),
                    "description": job.get("job_description", "")[:1000],  # Truncate long descriptions
                    "required_skills": self._extract_skills(job.get("job_description", "")),
                    "location": job.get("job_city", "") or job.get("job_country", ""),
                    "employment_type": job.get("job_employment_type", ""),
                    "url": job.get("job_apply_link", ""),
                    "posted_date": job.get("job_posted_at_datetime_utc", "")
                })
            
            return simplified_jobs
            
        except requests.exceptions.RequestException as e:
            return [{"error": f"API request failed: {str(e)}"}]
        except Exception as e:
            return [{"error": f"Unexpected error: {str(e)}"}]
    
    def _extract_skills(self, description: str) -> List[str]:
        """
        Simple skill extraction from job description.
        
        This is a basic implementation - in production, you'd use NLP.
        It looks for common tech keywords in the description.
        
        Args:
            description: Job description text
        
        Returns:
            List of identified skills
        """
        # Common tech skills to look for (can be expanded)
        skill_keywords = [
            "python", "java", "javascript", "typescript", "react", "angular", "vue",
            "node.js", "django", "flask", "fastapi", "spring", "kubernetes", "docker",
            "aws", "azure", "gcp", "sql", "postgresql", "mongodb", "redis",
            "machine learning", "deep learning", "tensorflow", "pytorch",
            "git", "ci/cd", "agile", "scrum", "rest api", "graphql"
        ]
        
        description_lower = description.lower()
        found_skills = []
        
        for skill in skill_keywords:
            if skill in description_lower:
                found_skills.append(skill.title())
        
        return found_skills[:10]  # Limit to top 10 skills


def search_jobs_for_candidate(
    job_title: str,
    skills: List[str],
    location: Optional[str] = None,
    num_results: int = 10
) -> List[JobPosting]:
    """
    Helper function to search jobs and convert to JobPosting objects.
    
    This bridges the tool output to our domain models.
    
    Args:
        job_title: Target job title
        skills: Candidate's skills (for context)
        location: Optional location filter
        num_results: Number of jobs to fetch
    
    Returns:
        List of JobPosting domain objects
    """
    tool = JobSearchTool()
    results = tool._run(query=job_title, num_results=num_results, location=location)
    
    job_postings = []
    
    for job_data in results:
        # Skip error entries
        if "error" in job_data:
            print(f"⚠️  Warning: {job_data['error']}")
            continue
        
        try:
            # Map to JobPosting domain model
            job_posting = JobPosting(
                job_id=job_data.get("job_id", "unknown"),
                title=job_data.get("title", ""),
                company=job_data.get("company", ""),
                description=job_data.get("description", ""),
                required_skills=job_data.get("required_skills", []),
                preferred_skills=[],  # API doesn't distinguish, so empty for now
                experience_level=ExperienceLevel.MID,  # Default, could be enhanced with NLP
                location=job_data.get("location"),
                url=job_data.get("url")
            )
            job_postings.append(job_posting)
        except Exception as e:
            print(f"⚠️  Failed to parse job: {e}")
            continue
    
    return job_postings
