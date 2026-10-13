
import time
import streamlit as st

from src.Database.db import enroll_student_to_subject
from src.Database.config import supabase


@st.dialog("Quick Enrollment")
def auto_enroll_dialog(subject_code):

    # =====================================================
    # CHECK STUDENT LOGIN
    # =====================================================

    student_data = st.session_state.get("student_data")

    if not student_data:

        st.error(
            "Student information not found. "
            "Please login again."
        )

        return

    student_id = student_data.get("student_id")

    if not student_id:

        st.error("Student ID not found.")

        return

    # =====================================================
    # FIND SUBJECT
    # =====================================================

    try:

        res = (
            supabase
            .table("subjects")
            .select("subject_id, name, subject_code")
            .eq("subject_code", subject_code)
            .execute()
        )

    except Exception as e:

        st.error("Could not find the subject.")

        st.exception(e)

        return

    # =====================================================
    # SUBJECT NOT FOUND
    # =====================================================

    if not res.data:

        st.error(
            f"Subject code '{subject_code}' was not found."
        )

        if st.button(
            "Close",
            type="primary",
            width="stretch"
        ):

            st.session_state.pop(
                "pending_join_code",
                None
            )

            st.query_params.clear()

            st.rerun()

        return

    # =====================================================
    # SUBJECT FOUND
    # =====================================================

    subject = res.data[0]

    subject_id = subject["subject_id"]
    subject_name = subject.get(
        "name",
        "this subject"
    )

    # =====================================================
    # CHECK ALREADY ENROLLED
    # =====================================================

    try:

        check = (
            supabase
            .table("subject_students")
            .select("*")
            .eq("subject_id", subject_id)
            .eq("student_id", student_id)
            .execute()
        )

    except Exception as e:

        st.error(
            "Could not check your enrollment."
        )

        st.exception(e)

        return

    # =====================================================
    # ALREADY ENROLLED
    # =====================================================

    if check.data:

        st.info(
            f"You are already enrolled in "
            f"**{subject_name} ({subject_code})**."
        )

        if st.button(
            "Got it!",
            type="primary",
            width="stretch"
        ):

            st.session_state.pop(
                "pending_join_code",
                None
            )

            st.query_params.clear()

            st.rerun()

        return

    # =====================================================
    # JOIN CONFIRMATION
    # =====================================================

    st.markdown(
        f"""
        ### Join Subject

        Would you like to join:

        **{subject_name}**

        Subject Code: **{subject_code}**
        """
    )

    st.write("")

    col1, col2 = st.columns(2)

    # =====================================================
    # NO
    # =====================================================

    with col1:

        if st.button(
            "No",
            width="stretch"
        ):

            st.session_state.pop(
                "pending_join_code",
                None
            )

            st.query_params.clear()

            st.rerun()

    # =====================================================
    # YES
    # =====================================================

    with col2:

        if st.button(
            "Yes, Join",
            type="primary",
            width="stretch"
        ):

            try:

                enroll_student_to_subject(
                    student_id,
                    subject_id
                )

                st.success(
                    f"You have successfully joined "
                    f"{subject_name}!"
                )

                # Remove pending join code
                st.session_state.pop(
                    "pending_join_code",
                    None
                )

                # Remove join_code from URL
                st.query_params.clear()

                time.sleep(1.5)

                st.rerun()

            except Exception as e:

                st.error(
                    "Could not enroll you in this subject."
                )

                st.exception(e)
