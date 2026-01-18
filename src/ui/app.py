"""
AI-Powered Job Search Assistant - Streamlit UI

Multi-step form interface for job seekers to find personalized job matches.
"""

import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.file_parser import extract_resume_text
from src.utils.csv_storage import CandidateStorage
from src.core.job_search_crew import JobSearchCrew


# Page configuration
st.set_page_config(
    page_title="AI Job Search Assistant",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        text-align: center;
        color: #666;
        margin-bottom: 3rem;
    }
    .step-indicator {
        text-align: center;
        font-size: 1rem;
        color: #888;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem;
        border-radius: 8px;
    }
    .job-card {
        border: 2px solid #e0e0e0;
        border-radius: 10px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background-color: #f9f9f9;
    }
    .tier-1 { border-left: 5px solid #28a745; }
    .tier-2 { border-left: 5px solid #17a2b8; }
    .tier-3 { border-left: 5px solid #ffc107; }
    .tier-4 { border-left: 5px solid #6c757d; }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'step' not in st.session_state:
    st.session_state.step = 1
if 'form_data' not in st.session_state:
    st.session_state.form_data = {}
if 'results' not in st.session_state:
    st.session_state.results = None


def next_step():
    """Move to next step in the form"""
    st.session_state.step += 1


def prev_step():
    """Move to previous step in the form"""
    if st.session_state.step > 1:
        st.session_state.step -= 1


def reset_form():
    """Reset the entire form"""
    st.session_state.step = 1
    st.session_state.form_data = {}
    st.session_state.results = None


# Header
st.markdown('<div class="main-header">🎯 AI Job Search Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Find your perfect job match with AI-powered analysis</div>', unsafe_allow_html=True)


# Step indicator
total_steps = 5
st.markdown(
    f'<div class="step-indicator">Step {st.session_state.step} of {total_steps}</div>',
    unsafe_allow_html=True
)

# Progress bar
progress = (st.session_state.step - 1) / total_steps
st.progress(progress)

st.markdown("---")


# ========== STEP 1: Personal Information ==========
if st.session_state.step == 1:
    st.header("👤 Personal Information")
    
    full_name = st.text_input(
        "Full Name *",
        value=st.session_state.form_data.get('full_name', ''),
        placeholder="Enter your full name",
        help="This will be used to personalize your job recommendations"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col2:
        if st.button("Next →", key="step1_next"):
            if full_name.strip():
                st.session_state.form_data['full_name'] = full_name
                next_step()
                st.rerun()
            else:
                st.error("⚠️ Please enter your full name")


# ========== STEP 2: Experience Level ==========
elif st.session_state.step == 2:
    st.header("💼 Experience Level")
    
    experience_level = st.radio(
        "What's your current experience level? *",
        options=[
            "Recent Graduate (0-1 years)",
            "Entry Level (1-2 years)",
            "Mid Level (2-5 years)",
            "Senior (5-10 years)",
            "Lead/Principal (10+ years)"
        ],
        index=0 if 'experience_level' not in st.session_state.form_data else
              ["Recent Graduate (0-1 years)", "Entry Level (1-2 years)", "Mid Level (2-5 years)", 
               "Senior (5-10 years)", "Lead/Principal (10+ years)"].index(st.session_state.form_data.get('experience_level')),
        help="Select the option that best describes your professional experience"
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", key="step2_back"):
            prev_step()
            st.rerun()
    
    with col3:
        if st.button("Next →", key="step2_next"):
            st.session_state.form_data['experience_level'] = experience_level
            next_step()
            st.rerun()


# ========== STEP 3: Work Preferences ==========
elif st.session_state.step == 3:
    st.header("🏢 Work Preferences")
    
    work_preference = st.radio(
        "What's your preferred work arrangement? *",
        options=["Remote", "Hybrid", "On-Site"],
        index=0 if 'work_preference' not in st.session_state.form_data else
              ["Remote", "Hybrid", "On-Site"].index(st.session_state.form_data.get('work_preference')),
        help="Select your preferred work location type"
    )
    
    # Show location fields only if On-Site is selected
    location_preference = None
    country = None
    
    if work_preference == "On-Site":
        st.markdown("---")
        
        location_preference = st.radio(
            "Location Preference *",
            options=["Only my country", "Open to relocation"],
            index=0 if 'location_preference' not in st.session_state.form_data else
                  ["Only my country", "Open to relocation"].index(st.session_state.form_data.get('location_preference', "Only my country"))
        )
        
        country = st.text_input(
            "Country *",
            value=st.session_state.form_data.get('country', ''),
            placeholder="e.g., United States, India, United Kingdom",
            help="Enter the country where you want to work"
        )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", key="step3_back"):
            prev_step()
            st.rerun()
    
    with col3:
        if st.button("Next →", key="step3_next"):
            # Validation
            if work_preference == "On-Site" and not country:
                st.error("⚠️ Please enter your country")
            else:
                st.session_state.form_data['work_preference'] = work_preference
                st.session_state.form_data['location_preference'] = location_preference or "N/A"
                st.session_state.form_data['country'] = country or "N/A"
                next_step()
                st.rerun()


# ========== STEP 4: Target Role ==========
elif st.session_state.step == 4:
    st.header("🎯 Target Job Role")
    
    target_role = st.text_input(
        "What job role are you looking for? *",
        value=st.session_state.form_data.get('target_role', ''),
        placeholder="e.g., Python Developer, Data Scientist, Product Manager",
        help="Be specific about the role you want to apply for"
    )
    
    st.info("💡 **Tip:** Be specific! Instead of 'Developer', try 'Senior Python Developer' or 'Full-Stack JavaScript Developer'")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", key="step4_back"):
            prev_step()
            st.rerun()
    
    with col3:
        if st.button("Next →", key="step4_next"):
            if target_role.strip():
                st.session_state.form_data['target_role'] = target_role
                next_step()
                st.rerun()
            else:
                st.error("⚠️ Please enter your target job role")


# ========== STEP 5: Resume Upload ==========
elif st.session_state.step == 5:
    st.header("📄 Upload Your Resume")
    
    uploaded_file = st.file_uploader(
        "Upload your resume *",
        type=['pdf', 'docx'],
        help="Supported formats: PDF (.pdf) and Word (.docx)",
        accept_multiple_files=False
    )
    
    if uploaded_file:
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        # Show file details
        file_size = uploaded_file.size / 1024  # Convert to KB
        st.info(f"📊 File size: {file_size:.2f} KB")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("← Back", key="step5_back"):
            prev_step()
            st.rerun()
    
    with col3:
        if st.button("🚀 Analyze & Find Jobs", key="step5_submit", type="primary"):
            if not uploaded_file:
                st.error("⚠️ Please upload your resume")
            else:
                # Extract resume text
                with st.spinner("📄 Extracting text from resume..."):
                    try:
                        resume_text = extract_resume_text(uploaded_file, uploaded_file.name)
                        st.session_state.form_data['resume_text'] = resume_text
                        
                        # Show processing and run the pipeline
                        st.session_state.step = 6
                        st.rerun()
                    
                    except Exception as e:
                        st.error(f"❌ Failed to process resume: {str(e)}")


# ========== STEP 6: Processing ==========
elif st.session_state.step == 6:
    st.header("⚙️ Processing Your Application")
    
    # Create progress placeholders
    progress_text = st.empty()
    progress_bar = st.empty()
    status_text = st.empty()
    
    try:
        # Initialize storage
        storage = CandidateStorage()
        
        # Step 1: Analyze Resume
        progress_text.markdown("### 📝 Step 1/4: Analyzing Resume...")
        progress_bar.progress(0.25)
        
        crew = JobSearchCrew()
        candidate_profile = crew.analyze_resume(st.session_state.form_data['resume_text'])
        status_text.success("✅ Resume analyzed successfully")
        
        # Step 2: Search Jobs
        progress_text.markdown("### 🔍 Step 2/4: Searching Job Opportunities...")
        progress_bar.progress(0.50)
        
        jobs = crew.find_jobs(
            target_role=st.session_state.form_data['target_role'],
            num_jobs=5
        )
        status_text.success(f"✅ Found {len(jobs)} job opportunities")
        
        # Step 3: Match Skills
        progress_text.markdown("### 🎯 Step 3/4: Matching Skills & Analyzing Fit...")
        progress_bar.progress(0.75)
        
        matches = crew.match_all_jobs()
        status_text.success(f"✅ Analyzed {len(matches)} job matches")
        
        # Step 4: Rank Jobs
        progress_text.markdown("### 🏆 Step 4/4: Ranking Opportunities...")
        progress_bar.progress(0.90)
        
        ranking = crew.rank_opportunities()
        report = crew.generate_report()
        
        progress_bar.progress(1.0)
        status_text.success("✅ Analysis complete!")
        
        # Save to CSV
        storage.save_candidate(
            full_name=st.session_state.form_data['full_name'],
            experience_level=st.session_state.form_data['experience_level'],
            work_preference=st.session_state.form_data['work_preference'],
            location_preference=st.session_state.form_data['location_preference'],
            country=st.session_state.form_data['country'],
            target_role=st.session_state.form_data['target_role'],
            skills_count=report['candidate']['skills_count'],
            total_experience_years=report['candidate']['total_years']
        )
        
        storage.save_job_results(
            candidate_name=st.session_state.form_data['full_name'],
            ranked_jobs=ranking['ranked_jobs']
        )
        
        # Store results
        st.session_state.results = report
        
        # Move to results
        st.session_state.step = 7
        st.rerun()
    
    except Exception as e:
        st.error(f"❌ An error occurred: {str(e)}")
        st.info("💡 Please try again or contact support if the issue persists")
        
        if st.button("🔄 Try Again"):
            st.session_state.step = 5
            st.rerun()


# ========== STEP 7: Results ==========
elif st.session_state.step == 7:
    st.header("🎉 Your Personalized Job Recommendations")
    
    report = st.session_state.results
    
    # Candidate Summary
    st.markdown("### 👤 Your Profile")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Name", report['candidate']['name'])
    with col2:
        st.metric("Experience", report['candidate']['experience_level'].title())
    with col3:
        st.metric("Total Years", f"{report['candidate']['total_years']} years")
    with col4:
        st.metric("Skills", report['candidate']['skills_count'])
    
    st.markdown("**Top Skills:** " + ", ".join(report['candidate']['top_skills']))
    
    st.markdown("---")
    
    # Job Search Summary
    st.markdown("### 📊 Search Summary")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Jobs Found", report['job_search']['jobs_found'])
    with col2:
        st.metric("Jobs Analyzed", report['job_search']['jobs_matched'])
    with col3:
        st.metric("Avg Match Score", f"{report['job_search']['average_score']:.1f}/100")
    
    st.markdown("---")
    
    # Top Recommendation
    st.markdown("### 🏆 Top Recommendation")
    st.info(f"**{report['recommendations']['top_pick']}**")
    st.markdown(f"**Strategy:** {report['recommendations']['strategy']}")
    
    st.markdown("---")
    
    # Ranked Jobs
    st.markdown("### 📋 Ranked Job Opportunities")
    
    for job in report['ranked_opportunities']:
        tier_class = f"tier-{job['tier'].split()[1]}"
        
        with st.container():
            st.markdown(f'<div class="job-card {tier_class}">', unsafe_allow_html=True)
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.markdown(f"### #{job['rank']} - {job['job_title']}")
                st.markdown(f"**Company:** {job['company']}")
                st.markdown(f"**{job['tier']}** | Score: **{job['final_score']}/100**")
            
            with col2:
                st.markdown(f"**Action:**")
                st.markdown(f"{job['action_recommendation']}")
            
            with st.expander("📝 View Details"):
                st.markdown(f"**Why this rank:**")
                st.write(job['ranking_rationale'])
            
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Actions
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🔄 Start New Search", key="new_search"):
            reset_form()
            st.rerun()
    
    with col2:
        if st.button("📥 Download Report (Coming Soon)", disabled=True):
            pass


# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>"
    "Made with ❤️ using CrewAI & Streamlit | © 2025 AI Job Search Assistant"
    "</div>",
    unsafe_allow_html=True
)