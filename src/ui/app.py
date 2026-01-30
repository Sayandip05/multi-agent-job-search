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
    /* Add horizontal padding to main content area */
    .block-container {
        padding-left: 5rem !important;
        padding-right: 5rem !important;
        max-width: 1200px;
        margin: 0 auto;
    }
    
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


# Step indicator (7 total steps: 5 form + processing + results)
total_steps = 7
display_step = min(st.session_state.step, 5)  # Show max "Step 5 of 5" for user-facing steps
st.markdown(
    f'<div class="step-indicator">Step {display_step} of 5</div>',
    unsafe_allow_html=True
)

# Progress bar
if st.session_state.step == 7:
    progress = 1.0
else:
    progress = min((st.session_state.step - 1) / 5, 0.95)  # Scale to 5 form steps
    
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
                # Store the uploaded file object for later processing
                st.session_state.form_data['resume_file'] = uploaded_file
                st.session_state.step = 6
                st.rerun()
                    
                    
# ========== STEP 6: AI Analysis ==========
elif st.session_state.step == 6:
    st.header("🤖 AI Analysis in Progress")
    st.info("Our team of AI agents is analyzing your profile and searching for jobs...")
    
    # Progress bar for analysis steps
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Get uploaded resume file
        resume_file = st.session_state.form_data['resume_file']
        
        # Read file content
        if resume_file.name.endswith('.pdf'):
            from pypdf import PdfReader
            pdf = PdfReader(resume_file)
            resume_text = ""
            for page in pdf.pages:
                resume_text += page.extract_text() + "\n"
        else:
            # DOCX
            import docx
            doc = docx.Document(resume_file)
            resume_text = "\n".join([para.text for para in doc.paragraphs])
            
        # Log to debug
        print(f"📄 Resume text length: {len(resume_text)} chars")
        
        with st.spinner('Agents are working... please wait'):
            # Initialize Crew
            crew = JobSearchCrew()
            
            # Step 1: Analyze Resume
            status_text.text("Step 1/5: Analyzing resume...")
            progress_bar.progress(0.2)
            candidate_profile = crew.analyze_resume(resume_text)
            
            # Step 2: Find Jobs
            status_text.text(f"Step 2/5: Searching for '{st.session_state.form_data['target_role']}' jobs...")
            progress_bar.progress(0.4)
            found_jobs = crew.find_jobs(
                target_role=st.session_state.form_data['target_role'],
                num_jobs=5
            )
            
            # Step 3: Match Skills
            status_text.text(f"Step 3/5: Matching candidate to {len(found_jobs)} jobs...")
            progress_bar.progress(0.6)
            crew.match_skills()
            
            # Step 4: Rank Jobs
            status_text.text("Step 4/5: Ranking opportunities...")
            progress_bar.progress(0.8)
            ranking = crew.rank_opportunities()
            
            # Step 5: Report
            status_text.text("Step 5/5: Generating final report...")
            progress_bar.progress(0.9)
            report = crew.generate_report()
            
        progress_bar.progress(1.0)
        status_text.success("✅ Analysis complete!")
        
        # Initialize storage
        storage = CandidateStorage()

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
        tier = job['tier'].split()[1] if ' ' in job['tier'] else '2'
        
        # Use colored border based on tier
        border_colors = {'1': '#28a745', '2': '#17a2b8', '3': '#ffc107', '4': '#6c757d'}
        border_color = border_colors.get(tier, '#17a2b8')
        
        # Create job card with inline styling
        st.markdown(
            f"""
            <div style="
                border: 2px solid #333;
                border-left: 5px solid {border_color};
                border-radius: 10px;
                padding: 1.5rem;
                margin-bottom: 1rem;
                background-color: rgba(255,255,255,0.05);
            ">
                <div style="display: flex; justify-content: space-between; align-items: start;">
                    <div>
                        <h3 style="margin: 0;">#{job['rank']} - {job['job_title']}</h3>
                        <p><strong>Company:</strong> {job['company']}</p>
                        <p><strong>{job['tier']}</strong> | Score: <strong>{job['final_score']}/100</strong></p>
                    </div>
                    <div style="text-align: right;">
                        <p><strong>Action:</strong></p>
                        <p style="color: {border_color}; font-weight: bold;">{job['action_recommendation']}</p>
                    </div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        with st.expander(f"📝 View Details - {job['job_title']}"):
            st.markdown(f"**Why this rank:**")
            st.write(job['ranking_rationale'])
    
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