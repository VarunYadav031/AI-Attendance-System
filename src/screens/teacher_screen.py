import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
# Footer component import
from src.components.footer import footer_dashboard

# Header component import
from src.components.Header import header_dashboard

# Base UI styling import
from src.ui.base_layout import (
    style_background_dashboard,
    style_base_layout
)

# Database functions import
from src.Database.db import (
    check_teacher_exists,
    create_teacher,
    teacher_login
)


# ======================================================
# Main Teacher Screen Function
# Purpose:
# - Apply UI styles
# - Check login state
# - Open dashboard after login
# - Show login/register screen
# ======================================================
def teacher_screen():

    # Apply dashboard background style
    style_background_dashboard()

    # Apply base layout style
    style_base_layout()

    # If teacher already logged in then open dashboard
    if (
        st.session_state.get("is_logged_in")
        and st.session_state.get("user_role") == "teacher"
    ):
        teacher_dashboard()
        return

    # Default screen is login
    if 'teacher_login_type' not in st.session_state:
        st.session_state.teacher_login_type = 'login'

    # Open login screen
    if st.session_state.teacher_login_type == 'login':
        teacher_screen_login()

    # Open register screen
    elif st.session_state.teacher_login_type == 'register':
        teacher_screen_register()


# ======================================================
# Teacher Dashboard
# Purpose:
# - Open after successful login
# - Show welcome message
# ======================================================
def teacher_dashboard():

    # Get teacher data from session
    teacher_data = st.session_state.teacher_data

    # Welcome message
    st.header(f"Welcome, {teacher_data['name']}!")

    # Logout button
    if st.button("Logout"):
        st.session_state.clear()
        st.rerun()


# ======================================================
# Login Authentication Function
# Purpose:
# - Validate login inputs
# - Check teacher credentials from database
# - Store login session
# ======================================================
def login_teacher(username, password):

    # Check empty fields
    if not username or not password:
        return False

    # Verify login from database
    teacher = teacher_login(username, password)

    # If teacher exists
    if teacher:

        # Store session data
        st.session_state.user_role = 'teacher'
        st.session_state.teacher_data = teacher
        st.session_state.is_logged_in = True

        return True

    return False


# ======================================================
# Teacher Login Screen
# Purpose:
# - Show login form
# - Handle login process
# - Redirect to register screen
# ======================================================
def teacher_screen_login():

    # Create two columns
    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap="xxlarge"
    )

    # Left side header
    with c1:
        header_dashboard()

    # Right side back button
    with c2:
        if st.button(
            'Go back to Home',
            type="secondary",
            key='loginbackbtn',
            shortcut='control+backspace'
        ):
            st.session_state.clear()
            st.rerun()

    # Login title
    st.header(
        "Login using password",
        text_alignment="center"
    )

    st.space()
    st.space()

    # Username input
    teacher_username = st.text_input(
        "Enter username",
        placeholder="varunyadav"
    )

    # Password input
    teacher_pass = st.text_input(
        "Enter password",
        type='password',
        placeholder='Enter password'
    )

    st.divider()

    # Login/Register buttons
    btnc1, btnc2 = st.columns(2)

    # Login button
    with btnc1:

        if st.button(
            "Login",
            icon=":material/passkey:",
            shortcut="control+enter",
            width="stretch"
        ):

            # Verify login
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

                # Reload app
                st.rerun()

            else:
                st.error(
                    "Invalid username or password"
                )

    # Register screen button
    with btnc2:

        if st.button(
            "Register Instead",
            type="primary",
            icon=":material/passkey:",
            width="stretch"
        ):

            st.session_state.teacher_login_type = 'register'
            st.rerun()

    # Footer section
    footer_dashboard()


# ======================================================
# Teacher Registration Logic
# Purpose:
# - Validate registration form
# - Check username availability
# - Create new teacher account
# ======================================================
def register_teacher(
    teacher_username,
    teacher_pass,
    teacher_pass_confirm,
    teacher_name
):

    # Check empty fields
    if (
        not teacher_username
        or not teacher_name
        or not teacher_pass
    ):
        return False, "Please fill all the fields!"

    # Check username already exists
    if check_teacher_exists(teacher_username):
        return (
            False,
            "Username already taken, please choose another one."
        )

    # Password match validation
    if teacher_pass != teacher_pass_confirm:
        return (
            False,
            "Passwords do not match, please try again."
        )

    try:

        # Create teacher in database
        create_teacher(
            teacher_username,
            teacher_pass,
            teacher_name
        )

        return (
            True,
            "Teacher registered successfully! Please login now."
        )

    except Exception as e:

        return False, "Unexpected error!"


# ======================================================
# Teacher Register Screen
# Purpose:
# - Show teacher registration form
# - Create new account
# - Redirect to login screen
# ======================================================
def teacher_screen_register():

    # Create two columns
    c1, c2 = st.columns(
        2,
        vertical_alignment='center',
        gap="xxlarge"
    )

    # Left side header
    with c1:
        header_dashboard()

    # Right side back button
    with c2:

        if st.button(
            'Go back to Home',
            type="secondary",
            key='registerbackbtn',
            shortcut='control+backspace'
        ):

            st.session_state.clear()
            st.rerun()

    # Register title
    st.header("Register Your Teacher Profile")

    st.space()
    st.space()

    # Username input
    teacher_username = st.text_input(
        "Enter username",
        placeholder="varunyadav"
    )

    # Teacher name input
    teacher_name = st.text_input(
        "Enter name",
        placeholder="varun yadav"
    )

    # Password input
    teacher_pass = st.text_input(
        "Enter password",
        type='password',
        placeholder='Enter password'
    )

    # Confirm password input
    teacher_pass_confirm = st.text_input(
        "Confirm password",
        type='password',
        placeholder='Enter password'
    )

    st.divider()

    # Buttons section
    btnc1, btnc2 = st.columns(2)

    # Register button
    with btnc1:

        if st.button(
            "Register now",
            icon=":material/passkey:",
            shortcut="control+enter",
            width="stretch"
        ):

            # Register validation
            success, message = register_teacher(
                teacher_username,
                teacher_pass,
                teacher_pass_confirm,
                teacher_name
            )

            # Registration success
            if success:

                st.success(message)

                import time
                time.sleep(2)

                # Redirect to login
                st.session_state.teacher_login_type = 'login'
                st.rerun()

            else:
                st.error(message)

    # Login screen button
    with btnc2:

        if st.button(
            "Login Instead",
            type="primary",
            icon=":material/passkey:",
            width="stretch"
        ):

            st.session_state.teacher_login_type = 'login'

    # Footer section
    footer_dashboard()