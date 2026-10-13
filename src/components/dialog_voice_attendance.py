
import streamlit as st
from datetime import datetime, date
import pandas as pd

from src.Database.config import supabase
from src.Pipeline.voice_pipeline import process_bulk_audio


@st.dialog("Voice Attendance")
def voice_attendance_dialog(selected_subject_id):

    st.write(
        "Record audio of students saying "
        "'I am present'. Then AI will recognize "
        "the voices."
    )

    # --------------------------------------------------
    # Record classroom audio
    # --------------------------------------------------
    audio_data = st.audio_input(
        "Record classroom audio"
    )

    # --------------------------------------------------
    # Analyze Audio
    # --------------------------------------------------
    if st.button(
        "Analyze Audio",
        width="stretch",
        type="primary"
    ):

        if audio_data is None:
            st.warning(
                "Please record audio first."
            )
            return

        with st.spinner(
            "Processing voice data..."
        ):

            # --------------------------------------------------
            # Get enrolled students
            # --------------------------------------------------
            try:

                enrolled_students_res = (
                    supabase
                    .table("subject_students")
                    .select(
                        "student_id, "
                        "students(student_id, name, voice_embedding)"
                    )
                    .eq(
                        "subject_id",
                        selected_subject_id
                    )
                    .execute()
                )

                enrolled_students = (
                    enrolled_students_res.data or []
                )

            except Exception as e:

                st.error(
                    f"Failed to load enrolled students: {e}"
                )
                return

            # --------------------------------------------------
            # Check enrolled students
            # --------------------------------------------------
            if not enrolled_students:

                st.warning(
                    "No enrolled students in this course."
                )
                return

            # --------------------------------------------------
            # Create candidate dictionary
            # --------------------------------------------------
            candidates_dict = {}

            for node in enrolled_students:

                student = node.get("students")

                if not student:
                    continue

                student_id = student.get(
                    "student_id"
                )

                voice_embedding = student.get(
                    "voice_embedding"
                )

                if (
                    student_id is not None
                    and voice_embedding
                ):

                    candidates_dict[
                        int(student_id)
                    ] = voice_embedding

            # --------------------------------------------------
            # Check voice profiles
            # --------------------------------------------------
            if not candidates_dict:

                st.error(
                    "No enrolled students have "
                    "voice profiles registered."
                )
                return

            # --------------------------------------------------
            # Read audio
            # --------------------------------------------------
            audio_bytes = audio_data.read()

            if not audio_bytes:

                st.warning(
                    "Recorded audio is empty."
                )
                return

            # --------------------------------------------------
            # AI Voice Recognition
            # --------------------------------------------------
            all_detected_ids = process_bulk_audio(
                audio_bytes,
                candidates_dict
            )

            if not all_detected_ids:

                st.warning(
                    "No enrolled student voice "
                    "was recognized."
                )
                return

            # --------------------------------------------------
            # Prepare result
            # --------------------------------------------------
            results = []

            recognized_student_ids = set()

            for student_id, score in all_detected_ids.items():

                recognized_student_ids.add(
                    int(student_id)
                )

            # --------------------------------------------------
            # Prepare display result
            # --------------------------------------------------
            for node in enrolled_students:

                student = node.get("students")

                if not student:
                    continue

                student_id = int(
                    student["student_id"]
                )

                score = all_detected_ids.get(
                    student_id,
                    0
                )

                is_present = (
                    student_id
                    in recognized_student_ids
                )

                results.append({

                    "Name": student["name"],

                    "ID": student_id,

                    "Score": round(
                        float(score),
                        3
                    ),

                    "Source": (
                        "Voice"
                        if is_present
                        else "-"
                    ),

                    "Status": (
                        "✅ Present"
                        if is_present
                        else "❌ Absent"
                    )
                })

            # --------------------------------------------------
            # Result DataFrame
            # --------------------------------------------------
            result_df = pd.DataFrame(
                results
            )

            st.session_state[
                "voice_attendance_results"
            ] = result_df

            # --------------------------------------------------
            # Save recognized IDs
            # --------------------------------------------------
            st.session_state[
                "voice_recognized_student_ids"
            ] = list(
                recognized_student_ids
            )

            st.session_state[
                "voice_selected_subject_id"
            ] = selected_subject_id

            # --------------------------------------------------
            # Show result
            # --------------------------------------------------
            st.dataframe(
                result_df,
                hide_index=True,
                width="stretch"
            )

            st.success(
                f"{len(recognized_student_ids)} "
                "student(s) recognized."
            )

    # ==========================================================
    # CONFIRM ATTENDANCE
    # ==========================================================

    if (
        "voice_attendance_results"
        in st.session_state
    ):

        st.divider()

        result_df = st.session_state[
            "voice_attendance_results"
        ]

        recognized_ids = st.session_state.get(
            "voice_recognized_student_ids",
            []
        )

        subject_id = st.session_state.get(
            "voice_selected_subject_id",
            selected_subject_id
        )

        st.subheader(
            "Attendance Result"
        )

        st.dataframe(
            result_df,
            hide_index=True,
            width="stretch"
        )

        col1, col2 = st.columns(2)

        # --------------------------------------------------
        # Confirm
        # --------------------------------------------------
        with col1:

            if st.button(
                "✅ Confirm Attendance",
                width="stretch",
                type="primary"
            ):

                if not recognized_ids:

                    st.warning(
                        "No student is marked present."
                    )
                    return

                try:

                    # --------------------------------------------------
                    # Today's date
                    # --------------------------------------------------
                    today = date.today()

                    current_timestamp = (
                        datetime.now()
                        .strftime(
                            "%Y-%m-%dT%H:%M:%S"
                        )
                    )

                    # --------------------------------------------------
                    # Check today's existing attendance
                    # --------------------------------------------------
                    existing_res = (
                        supabase
                        .table("attendace_logs")
                        .select(
                            "id, student_id, "
                            "subject_id, timestamp, "
                            "is_present"
                        )
                        .eq(
                            "subject_id",
                            subject_id
                        )
                        .gte(
                            "timestamp",
                            f"{today}T00:00:00"
                        )
                        .lt(
                            "timestamp",
                            f"{today}T23:59:59"
                        )
                        .execute()
                    )

                    existing_records = (
                        existing_res.data or []
                    )

                    existing_student_ids = {

                        int(row["student_id"])

                        for row in existing_records

                        if row.get("student_id")
                        is not None
                    }

                    # --------------------------------------------------
                    # Insert only new attendance
                    # --------------------------------------------------
                    new_records = []

                    for student_id in recognized_ids:

                        student_id = int(
                            student_id
                        )

                        # Already marked today
                        if (
                            student_id
                            in existing_student_ids
                        ):
                            continue

                        new_records.append({

                            "timestamp":
                                current_timestamp,

                            "subject_id":
                                subject_id,

                            "student_id":
                                student_id,

                            "is_present":
                                True
                        })

                    # --------------------------------------------------
                    # Nothing new
                    # --------------------------------------------------
                    if not new_records:

                        st.info(
                            "Today's attendance for "
                            "the recognized students "
                            "already exists."
                        )

                    else:

                        # --------------------------------------------------
                        # Insert into Supabase
                        # --------------------------------------------------
                        insert_response = (
                            supabase
                            .table("attendace_logs")
                            .insert(
                                new_records
                            )
                            .execute()
                        )

                        st.success(
                            f"Attendance synced successfully! "
                            f"{len(new_records)} record(s) saved."
                        )

                        # --------------------------------------------------
                        # Clear temporary voice state
                        # --------------------------------------------------
                        st.session_state.pop(
                            "voice_attendance_results",
                            None
                        )

                        st.session_state.pop(
                            "voice_recognized_student_ids",
                            None
                        )

                        st.session_state.pop(
                            "voice_selected_subject_id",
                            None
                        )

                        st.rerun()

                except Exception as e:

                    st.error(
                        f"Attendance sync failed: {e}"
                    )

        # --------------------------------------------------
        # Clear result
        # --------------------------------------------------
        with col2:

            if st.button(
                "🗑️ Clear Result",
                width="stretch"
            ):

                st.session_state.pop(
                    "voice_attendance_results",
                    None
                )

                st.session_state.pop(
                    "voice_recognized_student_ids",
                    None
                )

                st.session_state.pop(
                    "voice_selected_subject_id",
                    None
                )

                st.rerun()

