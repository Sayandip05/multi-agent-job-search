"""
CSV Storage Utility

Handles saving candidate data and search results to CSV files.
"""

import csv
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any

class CandidateStorage:
    def __init__(self, data_dir: str = "data"):
        """Initialize storage with data directory"""
        # Get project root (3 levels up from src/utils/csv_storage.py)
        self.root_dir = Path(__file__).parent.parent.parent
        self.data_dir = self.root_dir / data_dir
        
        # Create data directory if it doesn't exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.candidates_file = self.data_dir / "candidates.csv"
        self.results_file = self.data_dir / "results.csv"
        
        # Initialize files with headers if they don't exist
        self._init_files()

    def _init_files(self):
        """Initialize CSV files with headers"""
        if not self.candidates_file.exists():
            with open(self.candidates_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'full_name', 'experience_level', 
                    'work_preference', 'location', 'country', 
                    'target_role', 'skills_count', 'total_experience_years'
                ])
                
        if not self.results_file.exists():
            with open(self.results_file, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    'timestamp', 'candidate_name', 'job_rank', 'company', 
                    'job_title', 'tier', 'score', 'action', 'rationale'
                ])

    def save_candidate(self, full_name, experience_level, work_preference, 
                      location_preference, country, target_role, 
                      skills_count, total_experience_years):
        """Save candidate profile to CSV"""
        try:
            with open(self.candidates_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    full_name,
                    experience_level,
                    work_preference,
                    location_preference,
                    country,
                    target_role,
                    skills_count,
                    total_experience_years
                ])
        except Exception as e:
            print(f"Error saving candidate: {e}")

    def save_job_results(self, candidate_name: str, ranked_jobs: List[Dict[str, Any]]):
        """Save job search results to CSV"""
        try:
            with open(self.results_file, 'a', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                timestamp = datetime.now().isoformat()
                
                for job in ranked_jobs:
                    writer.writerow([
                        timestamp,
                        candidate_name,
                        job.get('rank'),
                        job.get('company'),
                        job.get('job_title'),
                        job.get('tier'),
                        job.get('final_score'),
                        job.get('action_recommendation'),
                        job.get('ranking_rationale')
                    ])
        except Exception as e:
            print(f"Error saving results: {e}")
