import streamlit as st
import base64
import os

# Ruta al logo
logo_path = os.path.join(os.path.dirname(__file__), "logos", "mdlz.png")

# Usuarios hardcoded
USERS = {
    "danipostigo": "1234",
    "luispostigo": "abcd"
}


def show_login():
    """
    Muestra la pantalla de login con fondo morado y logo centrado.
    Retorna (is_authenticated: bool, username: str)
    """
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = ""

    if st.session_state.logged_in:
        return True, st.session_state.username

    # Fondo morado y logo centrado

    st.markdown("""
        <style>
            .stApp {
                background-color: #6a0dad;  /* morado fuerte, puedes ajustar */
                color: white;
            }

            .centered-logo {
                display: flex;
                justify-content: center;
                margin-bottom: 20px;
            }

            h1, h2, h3, h4, h5, h6, label {
                color: white !important;
            }
            input[type="text"], input[type="password"] {
                background-color: #502171 !important;
                color: white !important;
                border: 1px solid white;
            }
                
            ::placeholder {
                color: #ddd !important;
                opacity: 0.8;
            }

            .stButton button {
                background-color: white;
                color: #6a0dad;
                border: none;
            }

            .stButton button:hover {
                background-color: #ddd;
                color: #6a0dad;
            }
        </style>
    """, unsafe_allow_html=True)

    if os.path.exists(logo_path):
        encoded_logo = base64.b64encode(open(logo_path, "rb").read()).decode()
        st.markdown(
            f"<div class='centered-logo'><img src='data:image/png;base64,{encoded_logo}' width='180'></div>",
            unsafe_allow_html=True
        )

    st.title("Iniciar sesión")
    username = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    if st.button("Login"):
        if username in USERS and USERS[username] == password:
            st.session_state.logged_in = True
            st.session_state.username = username
            st.success(f"Bienvenido/a, {username}")
            st.rerun()
        else:
            st.error("Credenciales incorrectas")

    return False, ""
