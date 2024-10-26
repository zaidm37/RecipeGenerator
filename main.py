import streamlit as st
import json
import requests
from PIL import Image
import io

# Example sign dictionary for testing
sign_dict = {"hello": "hello.gif", "thank you": "thank_you.gif"}

def voice_to_text(audio_file):
    return "hello thank you"  # Dummy response

def display_signs(text):
    words = text.lower().split()
    for word in words:
        if word in sign_dict:
            st.image(sign_dict[word], caption=word)

def save_favorite(text):
    with open("favorites.json", "a") as file:
        json.dump({"text": text}, file)

# Apply custom CSS for bluish-green background color, centered title, and better buttons layout
st.markdown(
    """
    <style>
    .stApp {
        background-color: #3CB371;  /* Bluish Evergreen Tint */
    }
    .main-title {
        color: white;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 20px;
    }
    .center-container {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    button {
        padding: 10px 20px;
        font-size: 16px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

if 'page' not in st.session_state:
    st.session_state.page = 1

def next_page():
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1

# Home Page (Page 1)
if st.session_state.page == 1:
    st.markdown("<h1 class='main-title'>Pantry Pal</h1>", unsafe_allow_html=True)

    if st.button('Get Started'):
        next_page()

# Input Method Selection Page (Page 2)
elif st.session_state.page == 2:
    st.markdown("<h3>How would you like to input your ingredients?</h3>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Take a Picture of What you got"):
            st.session_state.page = 4
    
    with col2:
        if st.button("Type in Manually"):
            next_page()
    
    if st.button("⬅️ Back"):
        prev_page()

# Manual Input Page (Page 3)
elif st.session_state.page == 3:
    st.markdown("<h3>Tell us what you got... (tomatoes, beans...)</h3>", unsafe_allow_html=True)
    ingredients = st.text_input("", key="ingredients")
    
    if st.button("Cook"):
        st.write(f"Generating a recipe based on: {ingredients}")
    
    if st.button("⬅️ Back"):
        prev_page()

# Take a Picture or Upload Image Page (Page 4)
elif st.session_state.page == 4:
    st.markdown("<h3>Take a picture or upload an image of your ingredients</h3>", unsafe_allow_html=True)
    
    # Initialize camera_input as None
    camera_input = None
    
    if st.session_state.get('camera_input_enabled', False) or st.button("Take a Picture"):
        st.session_state['camera_input_enabled'] = True
        # Capture camera input
        camera_input = st.camera_input("Take a picture")
    
    # File uploader input (this remains visible all the time)
    uploaded_file = st.file_uploader("Or upload an image", type=["jpg", "jpeg", "png"])
    
    # Handle both camera input or file upload
    if camera_input is not None or uploaded_file is not None:
        image = Image.open(camera_input or uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        st.write("Analyzing the image...")

        # Convert image to bytes for API processing
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes = image_bytes.getvalue()

        # Detect ingredients
        ingredients = detect_ingredients(image_bytes)
        if ingredients:
            st.write("Ingredients detected:", ingredients)
        else:
            st.write("No recognizable ingredients detected.")
    
    if st.button("⬅️ Back"):
        prev_page()

# Image recognition API creds
IMAGGA_API_KEY = "acc_3dbc34a6200e1d8"
IMAGGA_API_SECRET = "bd700ca01192e873a808bc3d39cfb4e3"
IMAGGA_ENDPOINT = "https://api.imagga.com/v2/tags"

def detect_ingredients(image_content):
    response = requests.post(
        IMAGGA_ENDPOINT,
        auth=(IMAGGA_API_KEY, IMAGGA_API_SECRET),
        files={"image": image_content}
    )
    if response.status_code != 200:
        st.error(f"Error: Received status code {response.status_code}")
        st.error("Response text: " + response.text)
        return []
    
    try:
        result = response.json()
        ingredients = [tag['tag']['en'] for tag in result.get("result", {}).get("tags", []) if tag['confidence'] > 50]
        return ingredients
    except json.JSONDecodeError as e:
        st.error("Failed to parse JSON response. Response text was:")
        st.write(response.text)
        st.error(str(e))
        return []
