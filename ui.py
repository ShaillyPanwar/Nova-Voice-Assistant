import streamlit as st
import os
import subprocess
import base64

# Set page config
st.set_page_config(page_title="Nova - Voice Assistant", layout="centered")

# Inject custom CSS for background color and logo styling
st.markdown("""
    <style>
    body {
        background-color: #000000;
        color: white;
    }
    .logo {
        display: flex;
        justify-content: center;
        margin-bottom: 20px;
    }
    .logo img {
        width: 400px;
    }
    .stButton button {
        background-color: #1f1f1f;
        color: white;
        border: 1px solid white;
    }
    </style>
""", unsafe_allow_html=True)


def show_logo():
    with open("logo.gif", "rb") as image_file:
        encoded = base64.b64encode(image_file.read()).decode()
        st.markdown(
            f"""
            <style>
            .nova-logo {{
                display: flex;
                justify-content: center;
                align-items: center;
                margin-top: -50px;
                margin-bottom: 10px;
            }}
            .nova-logo img {{
                width: 400px;  
            }}
            </style>
            <div class="nova-logo">
                <img src="data:image/gif;base64,{encoded}" />
            </div>
            """,
            unsafe_allow_html=True
        )

show_logo()

# App title and description
st.title("Nova - Voice Assistant")

st.markdown("""
Welcome to Nova, your personal voice assistant. Click below to activate voice commands.
""")

if "activated" not in st.session_state:
    st.session_state.activated = False

# Button to trigger assistant
if st.button("🎙️ Activate Nova"):
    st.session_state.activated = True
    st.write("Listening...")

    # Optional: Run the assistant script via subprocess
    try:
        script_path = r"C:\Users\shail\PycharmProjects\finalAssistant\main.py"  # Update path if needed
        Coutput = subprocess.check_output(["python", script_path], stderr=subprocess.STDOUT, text=True)

        st.success("Nova has responded:")
        st.code(Coutput)
    except subprocess.CalledProcessError as e:
        st.error("Error while running Nova:")
        st.code(e.output)

# Footer
st.markdown("---")
st.caption("Powered by Python, Streamlit, and your creativity 💡")
