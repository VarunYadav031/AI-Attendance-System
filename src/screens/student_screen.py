import streamlit as st
from src.ui.base_layout import style_background_dashboard, style_base_layout
# Footer component import
from src.components.footer import footer_dashboard
from PIL import Image
import numpy as np
# Header component import
from src.components.Header import header_dashboard
def student_screen():
    style_background_dashboard,
    style_base_layout
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
    st.header('Login using FaceId', text_alignment='center')   
    st.space()
    st.space()
    
    photo_source=st.camera_input("Position yourself in front of the camera")
    if photo_source:
        np.array(Image.open(photo_source))
        
    footer_dashboard()
    