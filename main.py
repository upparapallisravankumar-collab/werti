import streamlit as st
import os
import io
import json
import hashlib
from PIL import Image

# ========== USER DATABASE ==========
USER_DB_FILE = "users.json"

def load_users():
    if os.path.exists(USER_DB_FILE):
        with open(USER_DB_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USER_DB_FILE, 'w') as f:
        json.dump(users, f, indent=4)

def hash_password(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

def register_user(email, password):
    users = load_users()
    if email in users:
        return False, "User already exists"
    users[email] = {"password_hash": hash_password(password)}
    save_users(users)
    return True, "Registration successful!"

def login_user(email, password):
    users = load_users()
    if email not in users:
        return False, "User not found"
    if users[email]["password_hash"] == hash_password(password):
        return True, "Login successful!"
    return False, "Invalid password"


# ========== LOGIN / REGISTER ==========
def show_auth_page():
    st.title("🔐 AI Image Generator - Login")
    if "show_register" not in st.session_state:
        st.session_state.show_register = False
    if "auth_message" not in st.session_state:
        st.session_state.auth_message = ""

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login", use_container_width=True):
            st.session_state.show_register = False
            st.rerun()
    with col2:
        if st.button("Register", use_container_width=True):
            st.session_state.show_register = True
            st.rerun()

    if st.session_state.show_register:
        show_register_form()
    else:
        show_login_form()

    if st.session_state.auth_message:
        msg = st.session_state.auth_message
        st.success(msg) if "success" in msg.lower() else st.error(msg)


def show_login_form():
    st.subheader("Login")
    with st.form("login_form"):
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        if st.form_submit_button("Login"):
            if not email or not password:
                st.session_state.auth_message = "Please fill in all fields"
            else:
                success, msg = login_user(email, password)
                st.session_state.auth_message = msg
                if success:
                    st.session_state.logged_in = True
                    st.session_state.user_email = email
                    st.rerun()


def show_register_form():
    st.subheader("Register")
    with st.form("register_form"):
        email = st.text_input("📧 Email")
        password = st.text_input("🔒 Password", type="password")
        confirm = st.text_input("Confirm Password", type="password")
        if st.form_submit_button("Register"):
            if not all([email, password, confirm]):
                st.session_state.auth_message = "Fill all fields"
            elif password != confirm:
                st.session_state.auth_message = "Passwords do not match"
            elif len(password) < 6:
                st.session_state.auth_message = "Password must be at least 6 characters"
            else:
                success, msg = register_user(email, password)
                st.session_state.auth_message = msg
                if success:
                    st.session_state.show_register = False
                    st.rerun()


# ========== IMAGE GENERATOR ==========
def main_app():
    import torch
    from diffusers import StableDiffusionPipeline

    device = "cuda" if torch.cuda.is_available() else "cpu"

    @st.cache_resource
    def load_model():  
        model_id = "runwayml/stable-diffusion-v1-5"
        pipe = StableDiffusionPipeline.from_pretrained(
            model_id,
            torch_dtype=torch.float32,
            use_safetensors=True,
            safety_checker=None,
            requires_safety_checker=False
        ).to(device)
        return pipe

    st.set_page_config(page_title="AI Image Generator", page_icon="🎨", layout="wide")
    st.title("🎨 AI Image Generator")
    st.markdown(f"Welcome, **{st.session_state.user_email}**!")

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.logged_in = False
        st.rerun()

    # Sidebar now shows History instead of sliders
    with st.sidebar:
        st.header("📚 History")
        if "history" in st.session_state and st.session_state.history:
            for i, item in enumerate(reversed(st.session_state.history)):
                st.write(f"**{item['prompt'][:50]}...**")
                st.image(item['image'], use_column_width=True)
                buf = io.BytesIO()
                item['image'].save(buf, format="PNG")
                st.download_button(
                    label="📥 Download",
                    data=buf.getvalue(),
                    file_name=f"generated_image_{i+1}.png",
                    mime="image/png",
                    key=f"download_{i}"
                )
        else:
            st.info("No history yet. Generate an image to see it here!")

    # Text input for prompt
    prompt = st.text_area("✨ Describe your image:", height=120)

    with st.spinner("🔄 Loading model..."):
        pipe = load_model()

    # Generate image button
    if st.button("🚀 Generate Image", use_container_width=True):
        if not prompt.strip():
            st.warning("Please enter a prompt first!")
        else:
            with st.spinner("🎨 Generating image..."):
                result = pipe(prompt)
                image = result.images[0]
                if "history" not in st.session_state:
                    st.session_state.history = []
                st.session_state.history.append({"prompt": prompt, "image": image})
                st.image(image, use_column_width=True)


# ========== MAIN ==========
def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if not st.session_state.logged_in:
        show_auth_page()
    else:
        main_app()


if __name__ == "__main__":
    main()
