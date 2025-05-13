import streamlit as st
from urllib.parse import urlencode

def set_view(view_name: str):
    """
    Sets the current view in session and removes URL query parameters.
    """
    st.session_state.view = view_name
    st.experimental_set_query_params()  # Clears ?action=... from URL

def get_current_view():
    """
    Returns the current active view from session_state or URL query.
    """
    query_params = st.experimental_get_query_params()
    if 'action' in query_params:
        return query_params['action'][0]
    return st.session_state.get("view", None)

def render_button(label: str, action: str, css_class: str = ""):
    """
    Renders a full-width HTML button styled with a custom CSS class,
    using an HTML <form> that sets ?action=...
    """
    html = f"""
    <form action="?{urlencode({'action': action})}" method="get" style="margin: 0.5rem auto; text-align: center;">
        <button type="submit" class="custom-button {css_class}">{label}</button>
    </form>
    """
    st.markdown(html, unsafe_allow_html=True)

def render_logo(logo_path: str, width: int = 150):
    """
    Shows a centered logo from the given path.
    """
    import base64
    import os

    if os.path.exists(logo_path):
        encoded = base64.b64encode(open(logo_path, "rb").read()).decode()
        st.markdown(
            f"<div style='display: flex; justify-content: center;'>"
            f"<img src='data:image/png;base64,{encoded}' width='{width}'></div>",
            unsafe_allow_html=True
        )

def inject_base_css():
    """
    Injects base CSS classes for buttons.
    """
    st.markdown("""
        <style>
            .custom-button {
                width: 60%;
                padding: 0.9em 1.5em;
                font-size: 18px;
                font-weight: bold;
                border-radius: 8px;
                text-align: center;
                cursor: pointer;
                text-decoration: none;
                display: inline-block;
            }
            .btn-nueva {
                background-color: #502171;
                color: white;
            }
            .btn-nueva:hover {
                background-color: #67428a;
            }
            .btn-modificar {
                background-color: #cccccc;
                color: #222;
            }
            .btn-modificar:hover {
                background-color: #bbbbbb;
            }
            .btn-logout {
                background-color: white;
                color: #502171;
                border: 2px solid #502171;
            }
            .btn-logout:hover {
                background-color: #f2f2f2;
            }
        </style>
    """, unsafe_allow_html=True)