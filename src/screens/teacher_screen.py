import streamlit as st
import numpy as np
import pandas as pd
from datetime import datetime

from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout
)

from src.components.footer import footer_dashboard
from src.components.Header import header_dashboard

from src.Database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login,
    get_teacher_subjects, get_attendance_for_teacher
)

from src.components.dialog_create_subjects import (
    create_subject_dialog
)

from src.components.dialog_share_subject import (
    share_subject_dialog
)

from src.components.subject_card import (
    subject_card
)

from src.components.dialog_add_photo import (
    add_photos_dialog
)

from src.Pipeline.face_pipeline import (
    predict_attendance
)

from src.Database.config import supabase

from src.components.dialog_attendance_results import (
    attendance_result_dialog
)

from src.components.dialog_voice_attendance import (
    voice_attendance_dialog
)


# =========================================================
# MAIN TEACHER SCREEN
# =========================================================

def teacher_screen():

    style_background_dashboard()
    style_base_layout()

    # -----------------------------------------------------
    # Already logged in
    # -----------------------------------------------------

    if (
        st.session_state.get(
            "is_logged_in",
            False
        )
        and
        st.session_state.get(
            "user_role"
        ) == "teacher"
    ):

        teacher_dashboard()

        return

    # -----------------------------------------------------
    # Login type
    # -----------------------------------------------------

    if "teacher_login_type" not in st.session_state:

        st.session_state.teacher_login_type = "login"

    # -----------------------------------------------------
    # Login / Register
    # -----------------------------------------------------

    if (
        st.session_state.teacher_login_type
        == "login"
    ):

        teacher_screen_login()

    elif (
        st.session_state.teacher_login_type
        == "register"
    ):

        teacher_screen_register()


# =========================================================
# TEACHER DASHBOARD
# =========================================================

def teacher_dashboard():

    teacher_data = st.session_state.get(
        "teacher_data"
    )

    # -----------------------------------------------------
    # Teacher data check
    # -----------------------------------------------------

    if not teacher_data:

        st.session_state.is_logged_in = False

        st.session_state.pop(
            "user_role",
            None
        )

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

    # -----------------------------------------------------
    # Header logo
    # -----------------------------------------------------

    with c1:

        header_dashboard()

    # -----------------------------------------------------
    # Teacher welcome + logout
    # -----------------------------------------------------

    with c2:

        st.subheader(
            f"Welcome, "
            f"{teacher_data.get('name', 'Teacher')}!"
        )

        if st.button(
            "Logout",
            type="secondary",
            key="logoutbtn",
            shortcut="control+backspace"
        ):

            st.session_state.is_logged_in = False

            st.session_state.pop(
                "user_role",
                None
            )

            st.session_state.pop(
                "teacher_data",
                None
            )

            st.session_state.pop(
                "current_teacher_tab",
                None
            )

            st.session_state.pop(
                "attendance_images",
                None
            )

            st.session_state.pop(
                "voice_attendance_results",
                None
            )

            st.session_state.pop(
                "voice_attendance_logs",
                None
            )

            st.rerun()

    st.space()

    # =====================================================
    # DEFAULT TAB
    # =====================================================

    if (
        "current_teacher_tab"
        not in st.session_state
    ):

        st.session_state.current_teacher_tab = (
            "take_attendance"
        )

    # =====================================================
    # TAB BUTTONS
    # =====================================================

    tab1, tab2, tab3 = st.columns(3)

    # =====================================================
    # TAKE ATTENDANCE TAB
    # =====================================================

    with tab1:

        button_type = (
            "primary"
            if (
                st.session_state.current_teacher_tab
                == "take_attendance"
            )
            else "tertiary"
        )

        if st.button(
            "Take Attendance",
            type=button_type,
            width="stretch",
            icon=":material/how_to_reg:",
            key="take_attendance_tab"
        ):

            st.session_state.current_teacher_tab = (
                "take_attendance"
            )

            st.rerun()

    # =====================================================
    # MANAGE SUBJECTS TAB
    # =====================================================

    with tab2:

        button_type = (
            "primary"
            if (
                st.session_state.current_teacher_tab
                == "manage_subjects"
            )
            else "tertiary"
        )

        if st.button(
            "Manage Subjects",
            type=button_type,
            width="stretch",
            icon=":material/book_ribbon:",
            key="manage_subjects_tab"
        ):

            st.session_state.current_teacher_tab = (
                "manage_subjects"
            )

            st.rerun()

    # =====================================================
    # ATTENDANCE RECORDS TAB
    # =====================================================

    with tab3:

        button_type = (
            "primary"
            if (
                st.session_state.current_teacher_tab
                == "attendance_records"
            )
            else "tertiary"
        )

        if st.button(
            "Attendance Records",
            type=button_type,
            width="stretch",
            icon=":material/cards_stack:",
            key="attendance_records_tab"
        ):

            st.session_state.current_teacher_tab = (
                "attendance_records"
            )

            st.rerun()

    st.space()

    # =====================================================
    # DISPLAY SELECTED TAB
    # =====================================================

    if (
        st.session_state.current_teacher_tab
        == "take_attendance"
    ):

        teacher_tab_take_attendance()

    elif (
        st.session_state.current_teacher_tab
        == "manage_subjects"
    ):

        teacher_tab_manage_subjects()

    elif (
        st.session_state.current_teacher_tab
        == "attendance_records"
    ):

        teacher_tab_attendance_records()

    # -----------------------------------------------------
    # Voice attendance result dialog is handled by
    # voice_attendance_dialog().
    # -----------------------------------------------------

    footer_dashboard()


# =========================================================
# TAKE ATTENDANCE
# =========================================================

def teacher_tab_take_attendance():

    # =====================================================
    # TEACHER ID
    # =====================================================

    teacher_id = st.session_state.teacher_data[
        "teacher_id"
    ]

    # =====================================================
    # HEADER
    # =====================================================

    st.header(
        "Take AI Attendance"
    )

    # =====================================================
    # INITIALIZE PHOTO SESSION STATE
    # =====================================================

    if (
        "attendance_images"
        not in st.session_state
    ):

        st.session_state.attendance_images = []

    # =====================================================
    # GET TEACHER SUBJECTS
    # =====================================================

    subjects = get_teacher_subjects(
        teacher_id
    )

    # -----------------------------------------------------
    # No subjects
    # -----------------------------------------------------

    if not subjects:

        st.warning(
            "You haven't created any subjects yet! "
            "Please create one to begin!"
        )

        return

    # =====================================================
    # SUBJECT OPTIONS
    # =====================================================

    subject_options = {

        f"{s['name']} - {s['subject_code']}":
        s["subject_id"]

        for s in subjects
    }

    # =====================================================
    # SELECT SUBJECT
    # =====================================================

    selected_subject_label = st.selectbox(
        "Select Subject",
        options=list(
            subject_options.keys()
        ),
        key="attendance_subject_select"
    )

    selected_subject_id = (
        subject_options[
            selected_subject_label
        ]
    )

    st.divider()

    # =====================================================
    # FACE ATTENDANCE
    # =====================================================

    st.subheader(
        "📷 Face Attendance"
    )

    st.write(
        "Add classroom photos and use AI face "
        "recognition to mark attendance."
    )

    # =====================================================
    # ADD PHOTOS BUTTON
    # =====================================================

    if st.button(
        "Add Photos",
        type="primary",
        icon=":material/photo_prints:",
        width="stretch",
        key="add_attendance_photos"
    ):

        add_photos_dialog()

    # =====================================================
    # PHOTO SECTION
    # =====================================================

    if st.session_state.attendance_images:

        st.write(
            f"**"
            f"{len(st.session_state.attendance_images)}"
            f" photo(s) added"
            f"**"
        )

        # =================================================
        # PHOTO GALLERY
        # =================================================

        gallery_cols = st.columns(4)

        for idx, img in enumerate(
            st.session_state.attendance_images
        ):

            with gallery_cols[
                idx % 4
            ]:

                st.image(
                    img,
                    width="stretch",
                    caption=(
                        f"Photo {idx + 1}"
                    )
                )

        st.divider()

        # =================================================
        # PHOTO ACTION BUTTONS
        # =================================================

        c1, c2 = st.columns(2)

        # =================================================
        # CLEAR ALL PHOTOS
        # =================================================

        with c1:

            if st.button(
                "Clear All Photos",
                width="stretch",
                type="tertiary",
                icon=":material/delete:",
                key="clear_all_attendance_photos"
            ):

                st.session_state.attendance_images = []

                st.rerun()

        # =================================================
        # RUN FACE ANALYSIS
        # =================================================

        with c2:

            if st.button(
                "Run Face Analysis",
                width="stretch",
                type="secondary",
                icon=":material/analytics:",
                key="run_face_analysis"
            ):

                with st.spinner(
                    "Deep scanning classroom photos..."
                ):

                    all_detected_ids = {}

                    # =====================================
                    # ANALYZE EVERY PHOTO
                    # =====================================

                    for idx, img in enumerate(
                        st.session_state.attendance_images
                    ):

                        try:

                            img_np = np.array(
                                img.convert(
                                    "RGB"
                                )
                            )

                            detected, _, _ = (
                                predict_attendance(
                                    img_np
                                )
                            )

                            if detected:

                                for sid in (
                                    detected.keys()
                                ):

                                    student_id = int(
                                        sid
                                    )

                                    if (
                                        student_id
                                        not in
                                        all_detected_ids
                                    ):

                                        all_detected_ids[
                                            student_id
                                        ] = []

                                    all_detected_ids[
                                        student_id
                                    ].append(
                                        f"Photo {idx + 1}"
                                    )

                        except Exception as e:

                            st.error(
                                f"Error analyzing "
                                f"Photo {idx + 1}: "
                                f"{e}"
                            )

                    # =====================================
                    # NO STUDENT FOUND
                    # =====================================

                    if not all_detected_ids:

                        st.warning(
                            "No registered student was "
                            "recognized in the photos."
                        )

                    else:

                        recognized_ids = list(
                            all_detected_ids.keys()
                        )

                        # =================================
                        # GET STUDENT DETAILS
                        # =================================

                        try:

                            students_res = (
                                supabase
                                .table(
                                    "students"
                                )
                                .select(
                                    "student_id, name"
                                )
                                .in_(
                                    "student_id",
                                    recognized_ids
                                )
                                .execute()
                            )

                            recognized_students = (
                                students_res.data
                                or []
                            )

                        except Exception as e:

                            st.error(
                                "Unable to fetch "
                                "recognized students "
                                "from database."
                            )

                            st.exception(e)

                            return

                        # =================================
                        # ATTENDANCE RESULT
                        # =================================

                        results = []

                        attendance_to_log = []

                        for student in (
                            recognized_students
                        ):

                            student_id = int(
                                student[
                                    "student_id"
                                ]
                            )

                            sources = (
                                all_detected_ids.get(
                                    student_id,
                                    []
                                )
                            )

                            results.append({

                                "Name":
                                    student[
                                        "name"
                                    ],

                                "ID":
                                    student_id,

                                "Source":
                                    ", ".join(
                                        sources
                                    ),

                                "Status":
                                    "✅ Present"
                            })

                            attendance_to_log.append({

                                "student_id":
                                    student_id,

                                "subject_id":
                                    selected_subject_id,

                                "is_present":
                                    True
                            })

                        # =================================
                        # SHOW RESULT DIALOG
                        # =================================

                        if results:

                            result_df = (
                                pd.DataFrame(
                                    results
                                )
                            )

                            attendance_result_dialog(
                                result_df,
                                attendance_to_log
                            )

                        else:

                            st.warning(
                                "No student details "
                                "were found."
                            )

    # =====================================================
    # VOICE ATTENDANCE
    # =====================================================

    st.divider()

    st.subheader(
        "🎤 Voice Attendance"
    )

    st.write(
        "Record classroom audio and let AI recognize "
        "students using their registered voice profiles."
    )

    if st.button(
        "Use Voice Attendance",
        type="primary",
        width="stretch",
        icon=":material/mic:",
        key="use_voice_attendance"
    ):

        voice_attendance_dialog(
            selected_subject_id
        )


# =========================================================
# MANAGE SUBJECTS
# =========================================================

def teacher_tab_manage_subjects():

    teacher_data = st.session_state.get(
        "teacher_data"
    )

    if not teacher_data:

        st.error(
            "Teacher information not found. "
            "Please login again."
        )

        return

    teacher_id = teacher_data.get(
        "teacher_id"
    )

    if teacher_id is None:

        st.error(
            "Teacher ID not found."
        )

        return

    # =====================================================
    # HEADER
    # =====================================================

    col1, col2 = st.columns(
        [2, 1],
        vertical_alignment="center"
    )

    with col1:

        st.header(
            "Manage Subjects"
        )

    with col2:

        if st.button(
            "Create New Subject",
            width="stretch",
            icon=":material/add:",
            key="create_subject_button"
        ):

            create_subject_dialog(
                teacher_id
            )

    st.divider()

    # =====================================================
    # GET SUBJECTS
    # =====================================================

    try:

        subjects = get_teacher_subjects(
            teacher_id
        )

    except Exception as e:

        st.error(
            "Unable to load subjects."
        )

        st.exception(e)

        return

    # =====================================================
    # NO SUBJECTS
    # =====================================================

    if not subjects:

        st.info(
            "No subjects found. "
            "Please create a new subject."
        )

        return

    # =====================================================
    # DISPLAY SUBJECTS
    # =====================================================

    for index, sub in enumerate(
        subjects
    ):

        subject_name = sub.get(
            "name",
            "Unknown Subject"
        )

        subject_code = sub.get(
            "subject_code",
            "N/A"
        )

        section = sub.get(
            "section",
            "N/A"
        )

        total_students = sub.get(
            "total_students",
            0
        )

        total_classes = sub.get(
            "total_classes",
            0
        )

        # =================================================
        # SUBJECT STATS
        # =================================================

        stats = [

            (
                "👥",
                "Students",
                total_students
            ),

            (
                "📅",
                "Classes",
                total_classes
            )
        ]

        # =================================================
        # SHARE BUTTON
        # =================================================

        def share_btn(
            subject=sub,
            subject_index=index
        ):

            if st.button(
                "Share Code",
                key=(
                    f"share_subject_"
                    f"{subject_index}"
                ),
                icon=":material/share:"
            ):

                share_subject_dialog(

                    subject.get(
                        "name",
                        "Subject"
                    ),

                    subject.get(
                        "subject_code",
                        "N/A"
                    )
                )

        # =================================================
        # SUBJECT CARD
        # =================================================

        subject_card(

            name=subject_name,

            code=subject_code,

            section=section,

            stats=stats,

            footer_callback=share_btn
        )

        st.space()


# =========================================================
# ATTENDANCE RECORDS
# =========================================================

def teacher_tab_attendance_records():

    st.header("Attendance Records")

    teacher_id = st.session_state.teacher_data["teacher_id"]

    try:
        records = get_attendance_for_teacher(teacher_id)

    except Exception as e:
        st.error("Unable to load attendance records.")
        st.exception(e)
        return

    if not records:
        st.info("No attendance records found.")
        return

    data = []

    for r in records:

        ts = r.get("timestamp")

        # Parse timestamp safely
        try:
            dt = (
                datetime.fromisoformat(
                    ts.replace("Z", "+00:00")
                )
                if ts
                else None
            )
        except (ValueError, AttributeError):
            dt = None

        subject = r.get("subjects") or {}

        data.append({
            "ts_group": dt.isoformat() if dt else "Unknown",

            "Time": (
                dt.strftime("%Y-%m-%d %I:%M %p")
                if dt
                else "Unknown"
            ),

            "Subject": subject.get(
                "name",
                "Unknown Subject"
            ),

            "Subject Code": subject.get(
                "subject_code",
                "N/A"
            ),

            "is_present": bool(
                r.get("is_present", False)
            )
        })

    df = pd.DataFrame(data)

    # Group attendance records
    summary = (
        df.groupby(
            [
                "ts_group",
                "Time",
                "Subject",
                "Subject Code"
            ],
            dropna=False
        )
        .agg(
            Present_Count=("is_present", "sum"),
            Total_Count=("is_present", "count")
        )
        .reset_index()
    )

    # Format attendance statistics
    summary["Attendance Stats"] = (
        summary["Present_Count"].astype(str)
        + " / "
        + summary["Total_Count"].astype(str)
        + " Students"
    )

    # Sort and prepare the final table
    display_df = (
        summary.sort_values(
            by="ts_group",
            ascending=False
        )
        [
            [
                "Time",
                "Subject",
                "Subject Code",
                "Attendance Stats"
            ]
        ]
    )

    st.dataframe(
        display_df,
        width="stretch",
        hide_index=True
    )


# =========================================================
# LOGIN TEACHER
# =========================================================

def login_teacher(
    username,
    password
):

    # =====================================================
    # EMPTY CHECK
    # =====================================================

    if not username or not password:

        return False

    # =====================================================
    # LOGIN
    # =====================================================

    try:

        teacher = teacher_login(
            username,
            password
        )

    except Exception as e:

        st.error(
            "Unable to login. "
            "Database error occurred."
        )

        st.exception(e)

        return False

    # =====================================================
    # SUCCESS
    # =====================================================

    if teacher:

        st.session_state.user_role = (
            "teacher"
        )

        st.session_state.teacher_data = (
            teacher
        )

        st.session_state.is_logged_in = True

        return True

    # =====================================================
    # FAILURE
    # =====================================================

    return False


# =========================================================
# TEACHER LOGIN SCREEN
# =========================================================

def teacher_screen_login():

    # =====================================================
    # HEADER
    # =====================================================

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    # -----------------------------------------------------
    # Logo
    # -----------------------------------------------------

    with c1:

        header_dashboard()

    # -----------------------------------------------------
    # Back button
    # -----------------------------------------------------

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
    # LOGIN TITLE
    # =====================================================

    st.header(
        "Login using password",
        text_alignment="center"
    )

    st.space()
    st.space()

    # =====================================================
    # USERNAME
    # =====================================================

    teacher_username = st.text_input(
        "Enter username",
        placeholder="varunyadav",
        key="teacher_login_username"
    )

    # =====================================================
    # PASSWORD
    # =====================================================

    teacher_pass = st.text_input(
        "Enter password",
        type="password",
        placeholder="Enter password",
        key="teacher_login_password"
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    # =====================================================
    # LOGIN BUTTON
    # =====================================================

    with btnc1:

        if st.button(
            "Login",
            icon=":material/passkey:",
            shortcut="control+enter",
            width="stretch",
            key="teacher_login_button"
        ):

            if login_teacher(
                teacher_username,
                teacher_pass
            ):

                st.toast(
                    "Welcome back!",
                    icon="✌️"
                )

                import time

                time.sleep(1)

                st.rerun()

            else:

                st.error(
                    "Invalid username or password"
                )

    # =====================================================
    # REGISTER BUTTON
    # =====================================================

    with btnc2:

        if st.button(
            "Register Instead",
            type="primary",
            icon=":material/person_add:",
            width="stretch",
            key="teacher_register_button"
        ):

            st.session_state.teacher_login_type = (
                "register"
            )

            st.rerun()

    footer_dashboard()


# =========================================================
# REGISTER TEACHER
# =========================================================

def register_teacher(
    teacher_username,
    teacher_pass,
    teacher_pass_confirm,
    teacher_name
):

    # =====================================================
    # CHECK EMPTY FIELDS
    # =====================================================

    if (
        not teacher_username
        or not teacher_name
        or not teacher_pass
        or not teacher_pass_confirm
    ):

        return (
            False,
            "Please fill all the fields!"
        )

    # =====================================================
    # CHECK USERNAME
    # =====================================================

    try:

        if check_teacher_exists(
            teacher_username
        ):

            return (
                False,
                "Username already taken, "
                "please choose another one."
            )

    except Exception as e:

        return (
            False,
            f"Unable to check username: {e}"
        )

    # =====================================================
    # CHECK PASSWORD
    # =====================================================

    if (
        teacher_pass
        != teacher_pass_confirm
    ):

        return (
            False,
            "Passwords do not match, "
            "please try again."
        )

    # =====================================================
    # CREATE TEACHER
    # =====================================================

    try:

        create_teacher(
            teacher_username,
            teacher_pass,
            teacher_name
        )

        return (
            True,
            "Teacher registered successfully! "
            "Please login now."
        )

    except Exception as e:

        return (
            False,
            f"Unable to register teacher: {e}"
        )


# =========================================================
# TEACHER REGISTER SCREEN
# =========================================================

def teacher_screen_register():

    # =====================================================
    # HEADER
    # =====================================================

    c1, c2 = st.columns(
        2,
        vertical_alignment="center",
        gap="xxlarge"
    )

    # -----------------------------------------------------
    # Logo
    # -----------------------------------------------------

    with c1:

        header_dashboard()

    # -----------------------------------------------------
    # Back button
    # -----------------------------------------------------

    with c2:

        if st.button(
            "Go back to Home",
            type="secondary",
            key="registerbackbtn",
            shortcut="control+backspace"
        ):

            st.session_state.clear()

            st.rerun()

    # =====================================================
    # REGISTER TITLE
    # =====================================================

    st.header(
        "Register Your Teacher Profile"
    )

    st.space()
    st.space()

    # =====================================================
    # USERNAME
    # =====================================================

    teacher_username = st.text_input(
        "Enter username",
        placeholder="varunyadav",
        key="teacher_register_username"
    )

    # =====================================================
    # NAME
    # =====================================================

    teacher_name = st.text_input(
        "Enter name",
        placeholder="varun yadav",
        key="teacher_register_name"
    )

    # =====================================================
    # PASSWORD
    # =====================================================

    teacher_pass = st.text_input(
        "Enter password",
        type="password",
        placeholder="Enter password",
        key="teacher_register_password"
    )

    # =====================================================
    # CONFIRM PASSWORD
    # =====================================================

    teacher_pass_confirm = st.text_input(
        "Confirm password",
        type="password",
        placeholder="Enter password",
        key="teacher_register_confirm_password"
    )

    st.divider()

    btnc1, btnc2 = st.columns(2)

    # =====================================================
    # REGISTER NOW
    # =====================================================

    with btnc1:

        if st.button(
            "Register now",
            icon=":material/person_add:",
            shortcut="control+enter",
            width="stretch",
            key="teacher_register_now"
        ):

            success, message = register_teacher(

                teacher_username,

                teacher_pass,

                teacher_pass_confirm,

                teacher_name
            )

            # ---------------------------------------------
            # Registration successful
            # ---------------------------------------------

            if success:

                st.success(
                    message
                )

                import time

                time.sleep(2)

                st.session_state.teacher_login_type = (
                    "login"
                )

                st.rerun()

            # ---------------------------------------------
            # Registration failed
            # ---------------------------------------------

            else:

                st.error(
                    message
                )

    # =====================================================
    # LOGIN INSTEAD
    # =====================================================

    with btnc2:

        if st.button(
            "Login Instead",
            type="primary",
            icon=":material/login:",
            width="stretch",
            key="teacher_login_instead"
        ):

            st.session_state.teacher_login_type = (
                "login"
            )

            st.rerun()

    footer_dashboard()