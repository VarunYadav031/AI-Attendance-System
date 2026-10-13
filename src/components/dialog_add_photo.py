import streamlit as st
from PIL import Image

@st.dialog("Capture or upload photos")
def add_photos_dialog():

    st.write("Add classroom photos to scan for attendance")

    if "photo_tab" not in st.session_state:
        st.session_state.photo_tab = "camera"

    # Make sure attendance_images exists
    if "attendance_images" not in st.session_state:
        st.session_state.attendance_images = []

    t1, t2 = st.columns(2)

    with t1:
        type_camera = (
            "primary"
            if st.session_state.photo_tab == "camera"
            else "tertiary"
        )

        if st.button(
            "Camera",
            type=type_camera,
            width="stretch"
        ):
            st.session_state.photo_tab = "camera"
            st.rerun()

    with t2:
        type_upload = (
            "primary"
            if st.session_state.photo_tab == "upload"
            else "tertiary"
        )

        if st.button(
            "Upload photos",
            type=type_upload,
            width="stretch"
        ):
            st.session_state.photo_tab = "upload"
            st.rerun()

    # Camera tab
    if st.session_state.photo_tab == "camera":

        cam_photo = st.camera_input(
            "Take Snapshot",
            key="upload_cam"
        )

        if cam_photo:
            image = Image.open(cam_photo)

            st.session_state.attendance_images.append(image)

            st.toast("Photo Captured Successfully")

    # Upload tab
    if st.session_state.photo_tab == "upload":

        uploaded_files = st.file_uploader(
            "Choose image files",
            type=["jpg", "png", "jpeg"],
            accept_multiple_files=True,
            key="upload_files"
        )

        if uploaded_files:

            for f in uploaded_files:
                image = Image.open(f)

                st.session_state.attendance_images.append(image)

            st.toast("Photos Uploaded Successfully")

        st.divider()

        if st.button(
            "Done",
            type="primary",
            width="stretch"
        ):
            st.rerun()