import streamlit as st
def header_home():
    logo_url = "https://i.ibb.co/YTYGn5qV/logo.png"
    st.markdown(f"""
        <div style="text-align:center; padding-top:20px;">
            <img src="{logo_url}" style="height:80px;">
            <h1 style="text-align:center; color:#E0E3FF;">SNAP</br> CLASS</h1>
        </div>
                    """, unsafe_allow_html=True)