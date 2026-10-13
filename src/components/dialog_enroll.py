
import time
import streamlit as st

from src.Database.db import enroll_student_to_subject
from src.Database.config import supabase


@st.dialog("Enroll in Subject")
def enroll_dialog():

    # =====================================================
    # SUBJECT CODE INPUT
    # =====================================================

    st.write(
        "Enter the subject code provided by your teacher "
        "to enroll."
    )

    join_code = st.text_input(
        "Subject Code",
        placeholder="Eg. CS101"
    )

    # =====================================================
    # ENROLL
    # =====================================================

    if st.button(
        "Enroll now",
        type="primary",
        width="stretch"
    ):

        if not join_code.strip():

            st.warning(
                "Please enter a subject code."
            )

            return

        # Remove accidental spaces
        join_code = join_code.strip()

        # =================================================
        # FIND SUBJECT
        # =================================================

        try:

            res = (
                supabase
                .table("subjects")
                .select(
                    "subject_id, name, subject_code"
                )
                .eq(
                    "subject_code",
                    join_code
                )
                .execute()
            )

        except Exception as e:

            st.error(
                "Could not find the subject."
            )

            st.exception(e)

            return

        # =================================================
        # SUBJECT NOT FOUND
        # =================================================

        if not res.data:

            st.error(
                f"No subject found with code "
                f"'{join_code}'."
            )

            return

        subject = res.data[0]

        # =================================================
        # STUDENT
        # =================================================

        student_data = st.session_state.get(
            "student_data"
        )

        if not student_data:

            st.error(
                "Student information not found. "
                "Please login again."
            )

            return

        student_id = student_data.get(
            "student_id"
        )

        if not student_id:

            st.error(
                "Student ID not found."
            )

            return

        # =================================================
        # CHECK EXISTING ENROLLMENT
        # =================================================

        try:

            check = (
                supabase
                .table("subject_students")
                .select("*")
                .eq(
                    "subject_id",
                    subject["subject_id"]
                )
                .eq(
                    "student_id",
                    student_id
                )
                .execute()
            )

        except Exception as e:

            st.error(
                "Could not check your enrollment."
            )

            st.exception(e)

            return

        # =================================================
        # ALREADY ENROLLED
        # =================================================

        if check.data:

            st.warning(
                "You are already enrolled in this subject."
            )

            return

        # =================================================
        # ENROLL
        # =================================================

        try:

            enroll_student_to_subject(
                student_id,
                subject["subject_id"]
            )

            st.success(
                f"Successfully enrolled in "
                f"{subject['name']}!"
            )

            time.sleep(1)

            st.rerun()

        except Exception as e:

            st.error(
                "Could not enroll in this subject."
            )

            st.exception(e)

