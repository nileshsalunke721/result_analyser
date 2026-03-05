import streamlit as st
import pandas as pd

from parsers.fe_parser import extract_fe
from parsers.se_parser import extract_se
from parsers.te_parser import extract_te
from parsers.be_parser import extract_be, generate_analysis


st.set_page_config(
    page_title="Result Analyzer",
    page_icon="📊",
    layout="centered"
)

# ---------------- SESSION STATE ----------------

if "year" not in st.session_state:
    st.session_state.year = None

if "df" not in st.session_state:
    st.session_state.df = None

if "analysis_df" not in st.session_state:
    st.session_state.analysis_df = None

if "search_result" not in st.session_state:
    st.session_state.search_result = None


# ---------------- TITLE ----------------

st.title("🎓 University Result Analyzer")
st.caption("Upload Result PDF → Generate Excel → Perform Analysis")


# ---------------- YEAR SELECT ----------------

st.subheader("Select Academic Year")

col1, col2, col3, col4 = st.columns(4)

with col1:
    if st.button("🎓 FE"):
        st.session_state.year = "FE"

with col2:
    if st.button("📘 SE"):
        st.session_state.year = "SE"

with col3:
    if st.button("📗 TE"):
        st.session_state.year = "TE"

with col4:
    if st.button("📕 BE"):
        st.session_state.year = "BE"


year = st.session_state.year


# ---------------- EXTRACTION COMPONENT ----------------

if year:

    st.success(f"Selected Year : {year}")

    uploaded_file = st.file_uploader(
        "Upload Result PDF",
        type=["pdf"]
    )

    if uploaded_file:

        if st.button("Extract Result"):

            with st.spinner("Extracting data from PDF..."):

                if year == "FE":
                    df = extract_fe(uploaded_file)

                elif year == "SE":
                    df = extract_se(uploaded_file)

                elif year == "TE":
                    df = extract_te(uploaded_file)

                elif year == "BE":
                    df = extract_be(uploaded_file)

                st.session_state.df = df

            st.toast("Extraction Completed 🎉")


# ---------------- STUDENT DATA ----------------

if st.session_state.df is not None:

    st.divider()
    st.subheader("Student Data")

    st.dataframe(
        st.session_state.df,
        use_container_width=True
    )

    # Excel Download
    st.session_state.df.to_excel("result.xlsx", index=False)

    with open("result.xlsx", "rb") as f:
        st.download_button(
            "⬇ Download Excel",
            f,
            file_name="student_results.xlsx"
        )


# ---------------- ANALYSIS COMPONENT ----------------

if year == "BE" and st.session_state.df is not None:

    st.divider()
    st.subheader("📊 Result Analysis")

    if st.button("Generate Result Analysis"):

        with st.spinner("Generating analysis..."):

            analysis_df = generate_analysis(st.session_state.df)

            st.session_state.analysis_df = analysis_df

    if st.session_state.analysis_df is not None:

        st.dataframe(
            st.session_state.analysis_df,
            use_container_width=True
        )


# ---------------- STUDENT FINDER COMPONENT ----------------

if year == "BE" and st.session_state.df is not None:

    st.divider()
    st.subheader("🔎 Find Students by Subject & Grade")

    df = st.session_state.df

    subject_map = {
        "ISR (414441)": "414441",
        "SPM (414442)": "414442",
        "DL (414443)": "414443",
        "MC (414444A)": "414444A",
        "WC (414445D)": "414445D",
        "LPIII (414446)": "414446",
        "LPIV (414447)": "414447",
        "PS-I (414448)": "414448"
    }

    grades = ["O","A+","A","B+","B","C","P","F","IC"]

    # FORM prevents refresh while selecting
    with st.form("student_search_form"):

        col1, col2 = st.columns(2)

        with col1:
            subject = st.selectbox(
                "Select Subject",
                list(subject_map.keys())
            )

        with col2:
            grade = st.selectbox(
                "Select Grade",
                grades
            )

        submit = st.form_submit_button("Show Students")

    if submit:

        with st.spinner("Finding students..."):

            code = subject_map[subject]

            grade_col = f"{code}_grade"

            filtered = df[df[grade_col] == grade]

            st.session_state.search_result = filtered

    if st.session_state.search_result is not None:

        result = st.session_state.search_result

        if result.empty:

            st.warning("No students found")

        else:

            st.success(f"{len(result)} students found")

            st.dataframe(
                result[["Seat No","Name","PRN"]],
                use_container_width=True
            )