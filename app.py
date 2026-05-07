import streamlit as st

from src.screens.home_screen import home_screen
from src.screens.student_screen import student_screen
from src.screens.teacher_screen import teacher_screen
def main():
    if "Login type" not in st.session_state:
        st.session_state["Login type"] = None
    match st.session_state["Login type"]:
    
        case "Student":
            student_screen()
        case "Teacher":
            teacher_screen()
        case None:
            home_screen()

main()
