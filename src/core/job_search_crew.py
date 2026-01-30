"""
Job Search Crew - Main Orchestrator

This is the heart of the multi-agent system. It orchestrates all agents
to work together in a coordinated pipeline:

Resume Upload → Analysis → Job Discovery → Skill Matching → Ranking → Results

This demonstrates the full power of CrewAI's multi-agent architecture.
Each agent focuses on its specialty, and this crew coordinates them all.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime

from ..models.domain import (
    CandidateProfile,
    JobPosting,
    JobMatchResult,
    ExperienceLevel
)
from ..agents.resume_analyst import parse_resume
from ..agents.job_discovery import discover_jobs
from ..agents.skill_matcher import match_candidate_to_job
from ..agents.ranking_agent import rank_job_matches


class JobSearchCrew:
    """
    Main orchestrator for the job search multi-agent system.
    
    This class manages the entire workflow and coordinates all agents.
    It's the "conductor" of the agent orchestra.
    
    Architecture Pattern: Facade Pattern
    - Provides a simple interface to a complex subsystem
    - Hides the complexity of agent coordination
    - Makes the system easy to use from UI layer
    """
    
    def __init__(self):
        """Initialize the job search crew"""
        self.candidate_profile: Optional[CandidateProfile] = None
        self.discovered_jobs: List[JobPosting] = []
        self.job_matches: List[JobMatchResult] = []
        self.ranking: Optional[Dict[str, Any]] = None
        self.execution_log: List[str] = []
    
    def log(self, message: str):
        """Log execution steps for debugging and transparency"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.execution_log.append(log_entry)
        print(f"📝 {log_entry}")
    
    def analyze_resume(self, resume_text: str) -> CandidateProfile:
        """
        Step 1: Analyze the candidate's resume
        
        Args:
            resume_text: Raw text from the resume
        
        Returns:
            CandidateProfile: Structured candidate information
        """
        self.log("Step 1/5: Analyzing resume...")
        
        try:
            self.candidate_profile = parse_resume(resume_text)
            self.log(f"✅ Resume analyzed: {self.candidate_profile.name}")
            self.log(f"   Skills: {len(self.candidate_profile.skills)}")
            self.log(f"   Experience: {self.candidate_profile.experience_level.value if hasattr(self.candidate_profile.experience_level, 'value') else self.candidate_profile.experience_level}")
            return self.candidate_profile
        except Exception as e:
            self.log(f"❌ Resume analysis failed: {e}")
            raise
    
    def find_jobs(
        self,
        target_role: str,
        num_jobs: int = 5
    ) -> List[JobPosting]:
        """
        Step 2: Discover relevant job opportunities
        
        Args:
            target_role: The job title/role to search for
            num_jobs: Number of jobs to find
        
        Returns:
            List of JobPosting objects
        """
        if not self.candidate_profile:
            raise ValueError("Must analyze resume first")
        
        self.log(f"Step 2/5: Searching for '{target_role}' jobs...")
        
        try:
            self.discovered_jobs = discover_jobs(
                candidate=self.candidate_profile,
                target_role=target_role,
                num_jobs=num_jobs
            )
            self.log(f"✅ Found {len(self.discovered_jobs)} job opportunities")
            return self.discovered_jobs
        except Exception as e:
            self.log(f"❌ Job discovery failed: {e}")
            raise
    
    def match_all_jobs(self) -> List[JobMatchResult]:
        """
        Step 3: Match candidate against all discovered jobs
        
        Returns:
            List of JobMatchResult objects
        """
        if not self.candidate_profile:
            raise ValueError("Must analyze resume first")
        if not self.discovered_jobs:
            raise ValueError("Must discover jobs first")
        
        self.log(f"Step 3/5: Matching candidate to {len(self.discovered_jobs)} jobs...")
        
        self.job_matches = []
        
        for i, job in enumerate(self.discovered_jobs, 1):
            try:
                self.log(f"   Matching job {i}/{len(self.discovered_jobs)}: {job.title}")
                
                match_result = match_candidate_to_job(
                    candidate=self.candidate_profile,
                    job=job
                )
                
                self.job_matches.append(match_result)
                self.log(f"   ✅ Score: {match_result.overall_fit_score}/100")
                
            except Exception as e:
                self.log(f"   ⚠️  Failed to match job {i}: {e}")
                continue
        
        self.log(f"✅ Completed {len(self.job_matches)} job matches")
        return self.job_matches
    
    def rank_opportunities(self) -> Dict[str, Any]:
        """
        Step 4: Rank all matched jobs strategically
        
        Returns:
            Dictionary with ranked jobs and recommendations
        """
        if not self.job_matches:
            raise ValueError("Must match jobs first")
        
        self.log(f"Step 4/5: Ranking {len(self.job_matches)} opportunities...")
        
        try:
            self.ranking = rank_job_matches(self.job_matches)
            self.log(f"✅ Jobs ranked and prioritized")
            return self.ranking
        except Exception as e:
            self.log(f"❌ Ranking failed: {e}")
            raise
    
    def generate_report(self) -> Dict[str, Any]:
        """
        Step 5: Generate final comprehensive report
        
        Returns:
            Complete analysis report with all results
        """
        self.log("Step 5/5: Generating final report...")
        
        if not all([self.candidate_profile, self.job_matches, self.ranking]):
            raise ValueError("Must complete all previous steps first")
        
        report = {
            "candidate": {
                "name": self.candidate_profile.name,
                "email": self.candidate_profile.email,
                "experience_level": self.candidate_profile.experience_level.value if hasattr(self.candidate_profile.experience_level, 'value') else str(self.candidate_profile.experience_level),
                "total_years": self.candidate_profile.total_years_experience,
                "skills_count": len(self.candidate_profile.skills),
                "top_skills": [s.name for s in self.candidate_profile.skills[:5]]
            },
            "job_search": {
                "jobs_found": len(self.discovered_jobs),
                "jobs_matched": len(self.job_matches),
                "average_score": sum(m.overall_fit_score for m in self.job_matches) / len(self.job_matches)
            },
            "ranked_opportunities": self.ranking["ranked_jobs"],
            "recommendations": {
                "top_pick": self.ranking["top_recommendation"],
                "strategy": self.ranking["overall_strategy"]
            },
            "execution_log": self.execution_log,
            "generated_at": datetime.now().isoformat()
        }
        
        self.log("✅ Report generated successfully")
        return report
    
    def run_full_pipeline(
        self,
        resume_text: str,
        target_role: str,
        num_jobs: int = 5
    ) -> Dict[str, Any]:
        """
        Execute the complete job search pipeline in one call.
        
        This is the main entry point for the entire system.
        
        Args:
            resume_text: Raw resume text
            target_role: Job title to search for
            num_jobs: Number of jobs to analyze
        
        Returns:
            Complete analysis report
        
        Pipeline:
            1. Analyze Resume → CandidateProfile
            2. Discover Jobs → List[JobPosting]
            3. Match Jobs → List[JobMatchResult]
            4. Rank Results → Ranked recommendations
            5. Generate Report → Final output
        """
        self.log("="*60)
        self.log("🚀 Starting Multi-Agent Job Search Pipeline")
        self.log("="*60)
        
        try:
            # Execute pipeline
            self.analyze_resume(resume_text)
            self.find_jobs(target_role, num_jobs)
            self.match_all_jobs()
            self.rank_opportunities()
            report = self.generate_report()
            
            self.log("="*60)
            self.log("🎉 Pipeline completed successfully!")
            self.log("="*60)
            
            return report
            
        except Exception as e:
            self.log(f"❌ Pipeline failed: {e}")
            raise
    
    def get_execution_summary(self) -> str:
        """
        Get a human-readable summary of the execution.
        
        Returns:
            Formatted summary string
        """
        return "\n".join(self.execution_log)
