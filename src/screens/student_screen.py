import time

import streamlit as st
from PIL import Image
import numpy as np

from src.Database.db import (
    get_all_students,
    create_student,
    get_student_subjects,
    get_student_attendance,
    unenroll_student_to_subject
)

from src.Pipeline.voice_pipeline import get_voice_embedding

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout
)

from src.components.footer import footer_dashboard
from src.components.Header import header_dashboard

from src.Pipeline.face_pipeline import (
    get_face_embedding,
    predict_attendance,
    train_classifier
)

from src.components.dialog_enroll import enroll_dialog
from src.components.subject_card import subject_card


# =========================================================
# STUDENT DASHBOARD
# =========================================================

def student_dashboard():

    student_data = st.session_state.get("student_data")

    if not student_data:
        st.error("Student information not found. Please login again.")

        if st.button("Go to Login", type="primary"):
            st.session_state.clear()
            st.rerun()

        return

    student_id = student_data.get("student_id")

    if not student_id:
        st.error("Student ID not found. Please login again.")

        if st.button("Go to Login", type="primary"):
            st.session_state.clear()
            st.rerun()

        return

    # =====================================================
    # HEADER
    # =====================================================

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    with c1:
        header_dashboard()

    with c2:

        st.subheader(
            f"Welcome, {student_data.get('name', 'Student')}!"
        )

        if st.button(
            "Logout",
            type="secondary",
            key="student_logout_btn",
            shortcut="control+backspace"
        ):
            st.session_state.clear()
            st.rerun()

    st.space()

    # =====================================================
    # ENROLLED SUBJECTS
    # =====================================================

    c1, c2 = st.columns(
        2,
        vertical_alignment="center"
    )

    with c1:
        st.header("Your Enrolled Subjects")

    with c2:

        if st.button(
            "Enroll in Subject",
            type="primary",
            width="stretch",
            key="enroll_subject_btn"
        ):
            enroll_dialog()

    st.divider()

    # =====================================================
    # LOAD DATA
    # =====================================================

    with st.spinner("Loading your enrolled subjects..."):

        try:
            subjects = get_student_subjects(student_id)
            logs = get_student_attendance(student_id)

        except Exception as e:
            st.error("Could not load your subjects or attendance.")
            st.exception(e)
            return

    if subjects is None:
        subjects = []

    if logs is None:
        logs = []

    # =====================================================
    # ATTENDANCE STATS
    # =====================================================

    stats_map = {}

    for log in logs:

        sid = log.get("subject_id")

        if not sid:
            continue

        if sid not in stats_map:
            stats_map[sid] = {
                "total": 0,
                "attended": 0
            }

        stats_map[sid]["total"] += 1

        if log.get("is_present"):
            stats_map[sid]["attended"] += 1

    # =====================================================
    # NO SUBJECTS
    # =====================================================

    if not subjects:

        st.info(
            "You are not enrolled in any subject yet. "
            "Click 'Enroll in Subject' to join a course."
        )

    # =====================================================
    # DISPLAY SUBJECTS
    # =====================================================

    else:

        cols = st.columns(2)

        for i, sub_node in enumerate(subjects):

            # -------------------------------------------------
            # GET SUBJECT DATA
            # -------------------------------------------------

            sub = sub_node.get("subjects")

            if not sub:
                continue

            # subject_students table ka subject_id
            sid = sub_node.get("subject_id")

            # Fallback: subjects table ka id
            if not sid:
                sid = sub.get("id")

            if not sid:
                continue

            # -------------------------------------------------
            # ATTENDANCE STATS
            # -------------------------------------------------

            stats = stats_map.get(
                sid,
                {
                    "total": 0,
                    "attended": 0
                }
            )

            # -------------------------------------------------
            # SUBJECT CARD
            # -------------------------------------------------

            with cols[i % 2]:

                subject_card(
                    name=sub.get(
                        "name",
                        "Unknown Subject"
                    ),
                    code=sub.get(
                        "subject_code",
                        "N/A"
                    ),
                    section=sub.get(
                        "section",
                        "N/A"
                    ),
                    stats=[
                        (
                            "📆",
                            "Total",
                            stats["total"]
                        ),
                        (
                            "✅",
                            "Attended",
                            stats["attended"]
                        )
                    ]
                )

                # -------------------------------------------------
                # UNENROLL BUTTON
                # -------------------------------------------------

                if st.button(
                    "Unenroll from this course",
                    type="tertiary",
                    width="stretch",
                    icon=":material/delete_forever:",
                    key=f"unenroll_{sid}"
                ):

                    try:

                        with st.spinner("Unenrolling..."):

                            unenroll_student_to_subject(
                                student_id,
                                sid
                            )

                        st.success(
                            "You have been unenrolled from this course."
                        )

                        # Refresh dashboard
                        st.rerun()

                    except Exception as e:

                        st.error(
                            "Could not unenroll from this course."
                        )

                        st.exception(e)

    # =====================================================
    # FOOTER
    # =====================================================

    footer_dashboard()


# =========================================================
# STUDENT SCREEN
# =========================================================

def student_screen():

    style_background_dashboard()
    style_base_layout()

    # =====================================================
    # ALREADY LOGGED IN
    # =====================================================

    if (
        st.session_state.get("is_logged_in", False)
        and st.session_state.get("user_role") == "student"
        and "student_data" in st.session_state
    ):

        student_dashboard()
        return

    # =====================================================
    # HEADER
    # =====================================================

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    with c1:
        header_dashboard()

    with c2:

        if st.button(
            "Go back to Home",
            type="secondary",
            key="loginbackbtn",
            shortcut="control+backspace"
        ):
            st.session_state.clear()
            st.rerun()

    # =====================================================
    # LOGIN
    # =====================================================

    st.header(
        "Login using FaceId",
        text_alignment="center"
    )

    st.space()
    st.space()

    # =====================================================
    # CAMERA
    # =====================================================

    photo_source = st.camera_input(
        "Position yourself in front of the camera"
    )

    # =====================================================
    # FACE LOGIN
    # =====================================================

    if photo_source:

        img = np.array(
            Image.open(photo_source).convert("RGB"),
            dtype=np.uint8
        )

        with st.spinner("AI is Scanning..."):

            try:

                detected, all_ids, num_faces = predict_attendance(img)

            except Exception as e:

                st.error("Face recognition failed.")
                st.exception(e)
                return

        if num_faces == 0:

            st.warning("Face not found.")

        elif num_faces > 1:

            st.warning(
                "Multiple faces detected. "
                "Please keep only one person in front of the camera."
            )

        else:

            if detected:

                student_id = list(detected.keys())[0]

                all_students = get_all_students()

                student = next(
                    (
                        s
                        for s in all_students
                        if s.get("student_id") == student_id
                    ),
                    None
                )

                if student:

                    st.session_state.is_logged_in = True
                    st.session_state.user_role = "student"
                    st.session_state.student_data = student

                    student_name = student.get(
                        "name",
                        "Student"
                    )

                    st.toast(
                        f"Welcome back, {student_name}!"
                    )

                    time.sleep(1)
                    st.rerun()

                else:

                    st.error(
                        "Student record not found in database."
                    )

            else:

                st.info(
                    "Face not recognized. "
                    "You might be a new student."
                )

    # =====================================================
    # NEW STUDENT REGISTRATION
    # =====================================================

    with st.container(border=True):

        st.header(
            "Register as a New Profile"
        )

        new_name = st.text_input(
            "Enter your name",
            placeholder="E.g. Varun Yadav"
        )

        st.subheader(
            "Optional: Voice Enrollment"
        )

        st.info(
            "Enroll your voice for voice-based attendance."
        )

        # =================================================
        # VOICE INPUT
        # =================================================

        audio_data = None

        try:

            audio_data = st.audio_input(
                "Record a short phrase like: "
                "I am present, My name is Varun."
            )

        except Exception:

            st.warning(
                "Audio input is not supported by your browser."
            )

        # =================================================
        # CREATE ACCOUNT
        # =================================================

        if st.button(
            "Create Account",
            type="primary",
            key="create_student_account"
        ):

            if not new_name.strip():

                st.warning(
                    "Please enter your name!"
                )

            elif photo_source is None:

                st.warning(
                    "Please capture your face using the camera first."
                )

            else:

                with st.spinner("Creating profile..."):

                    try:

                        img = np.array(
                            Image.open(photo_source).convert("RGB"),
                            dtype=np.uint8
                        )

                        # =================================
                        # FACE EMBEDDING
                        # =================================

                        encodings = get_face_embedding(img)

                        if not encodings:

                            st.error(
                                "Could not capture your facial recognition. "
                                "Please make sure your face is clearly visible."
                            )

                        else:

                            face_emb = encodings[0].tolist()

                            # =============================
                            # VOICE EMBEDDING
                            # =============================

                            voice_emb = None

                            if audio_data:

                                try:

                                    voice_emb = get_voice_embedding(
                                        audio_data.read()
                                    )

                                except Exception:

                                    st.warning(
                                        "Voice enrollment failed. "
                                        "Your account will be created "
                                        "without voice enrollment."
                                    )

                            # =============================
                            # CREATE STUDENT
                            # =============================

                            response_data = create_student(
                                new_name.strip(),
                                face_embedding=face_emb,
                                voice_embedding=voice_emb
                            )

                            if response_data:

                                # =============================
                                # TRAIN CLASSIFIER
                                # =============================

                                try:

                                    train_classifier()

                                except Exception as e:

                                    st.warning(
                                        "Profile created, but "
                                        "face classifier training failed."
                                    )

                                    st.exception(e)

                                # =============================
                                # LOGIN
                                # =============================

                                st.session_state.is_logged_in = True
                                st.session_state.user_role = "student"
                                st.session_state.student_data = response_data[0]

                                st.toast(
                                    f"Profile created! "
                                    f"Hi {new_name.strip()}!"
                                )

                                # time.sleep(1)
                                st.rerun()

                            else:

                                st.error(
                                    "Could not create student profile."
                                )

                    except Exception as e:

                        st.error(
                            "Something went wrong while creating your profile."
                        )

                        st.exception(e)

    # =====================================================
    # FOOTER
    # =====================================================

    footer_dashboard()