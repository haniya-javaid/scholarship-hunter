import streamlit as st
from main import find_scholarships, find_scholarships_by_cv

st.set_page_config(
    page_title="Scholarship Hunter",
    page_icon="🎓",
    layout="centered"
)

st.title("🎓 Scholarship Hunter")
st.caption("Find scholarships from around the world — powered by AI")

st.divider()

# Tabs
tab1, tab2 = st.tabs(["🔎 Search Scholarships", "📄 Upload CV"])

# ─── TAB 1: Manual Search ───
with tab1:
    st.write("**Quick Searches:**")
    col1, col2, col3 = st.columns(3)

    if col1.button("🇺🇸 USA"):
        st.session_state.query = "fully funded scholarships in USA for Pakistani students 2025"
    if col2.button("🇬🇧 UK"):
        st.session_state.query = "fully funded scholarships in UK for Pakistani students 2025"
    if col3.button("🇩🇪 Germany"):
        st.session_state.query = "fully funded scholarships in Germany for Pakistani students 2025"

    query = st.text_input(
        "Search Scholarships",
        value=st.session_state.get("query", ""),
        placeholder="e.g. fully funded MS scholarships for Pakistani students"
    )

    if st.button("Find Scholarships 🚀", type="primary", use_container_width=True):
        if not query.strip():
            st.error("Please enter a search query!")
        else:
            with st.spinner("🔍 Searching the web..."):
                try:
                    results = find_scholarships(query)
                    st.session_state.results = results
                    st.session_state.last_query = query
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

    if "results" in st.session_state and st.session_state.results:
        st.divider()
        st.subheader(f"📋 Results for: _{st.session_state.get('last_query', '')}_")
        st.markdown(st.session_state.results)
        if st.button("🔄 New Search"):
            del st.session_state.results
            st.rerun()

# ─── TAB 2: CV Upload ───
with tab2:
    st.subheader("📄 Upload Your CV")
    st.caption("Upload your CV and we'll find scholarships that match your profile!")

    uploaded_file = st.file_uploader(
        "Upload CV (PDF or DOCX)",
        type=["pdf", "docx"]
    )

    if uploaded_file:
        if st.button("Find Matching Scholarships 🎯", type="primary", use_container_width=True):
            with st.spinner("📖 Reading your CV..."):
                try:
                    cv_info, results = find_scholarships_by_cv(uploaded_file)
                    st.session_state.cv_info = cv_info
                    st.session_state.cv_results = results
                except Exception as e:
                    st.error(f"Something went wrong: {str(e)}")

    if "cv_info" in st.session_state:
        st.divider()
        
        # CV Summary
        st.subheader("👤 Your Profile")
        info = st.session_state.cv_info
        col1, col2 = st.columns(2)
        with col1:
            st.write(f"**Name:** {info.get('name', 'N/A')}")
            st.write(f"**Field:** {info.get('field', 'N/A')}")
            st.write(f"**Level:** {info.get('education_level', 'N/A')}")
        with col2:
            st.write(f"**GPA:** {info.get('gpa', 'N/A')}")
            skills = info.get('skills', [])
            st.write(f"**Skills:** {', '.join(skills) if skills else 'N/A'}")

        st.divider()
        st.subheader("🎓 Recommended Scholarships")
        st.markdown(st.session_state.cv_results)

        if st.button("🔄 Try Another CV"):
            del st.session_state.cv_info
            del st.session_state.cv_results
            st.rerun()