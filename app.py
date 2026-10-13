
import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
from src.components.dialog_auto_enroll import auto_enroll_dialog


def main():

    st.set_page_config(
        page_title='SnapClass-Making Attendance faster using AI',
        page_icon='https://i.ibb.co/YTYGn5qV/logo.png'
    )

    # =====================================================
    # DEFAULT LOGIN TYPE
    # =====================================================

    if "Login type" not in st.session_state:
        st.session_state["Login type"] = None

    # =====================================================
    # CHECK JOIN URL
    # =====================================================

    join_code = st.query_params.get("join_code")

    # =====================================================
    # JOIN LINK FLOW
    # =====================================================

    if join_code:

        # Save join code
        st.session_state["pending_join_code"] = join_code

        # Directly open Student screen
        if st.session_state.get("Login type") != "Student":

            st.session_state["Login type"] = "Student"

            st.rerun()

    # =====================================================
    # NORMAL APP FLOW
    # =====================================================

    match st.session_state["Login type"]:

        case "Student":
            student_screen()

        case "Teacher":
            teacher_screen()

        case None:
            home_screen()

    # =====================================================
    # AUTO ENROLL AFTER STUDENT LOGIN
    # =====================================================

    pending_join_code = st.session_state.get(
        "pending_join_code"
    )

    if (
        pending_join_code
        and st.session_state.get("is_logged_in", False)
        and st.session_state.get("user_role") == "student"
    ):

        auto_enroll_dialog(
            pending_join_code
        )


if __name__ == "__main__":
    main()

