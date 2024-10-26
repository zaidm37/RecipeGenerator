import streamlit as st
from PIL import Image
import os
import google.cloud
from google.cloud import aiplatform
import speech_recognition as sr

# Set up your Google Cloud API key environment variable
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'path/to/your-google-cloud-service-account.json'

# Set up Google Cloud Vertex AI configuration
project_id = "YOUR_PROJECT_ID"
location = "YOUR_LOCATION"
model_id = "YOUR_MODEL_ID"  # Replace with the ID of your language model in Google Cloud

aiplatform.init(project=project_id, location=location)

# Custom CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #83C983;
    }
    .main-title {
        text-align: center;
        font-size: 32px;
        color: black;
    }
    .get-started, .learn-more {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    .get-started button, .learn-more button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 18px;
        cursor: pointer;
        border-radius: 25px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for page tracking
if 'page' not in st.session_state:
    st.session_state.page = 1

# Page navigation functions
def next_page():
    st.session_state.page += 1

def prev_page():
    st.session_state.page -= 1

# Function to upload an image
def upload_image():
    uploaded_file = st.file_uploader("Upload an image of your ingredients", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        return True
    return False

# Function to recognize voice input
def recognize_voice():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Please speak your ingredients...")
        audio = recognizer.listen(source)
        try:
            text = recognizer.recognize_google(audio)
            st.write(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            st.write("Could not request results from Google Speech Recognition service.")
            return None

# Function to generate recipes using Google Cloud Vertex AI
def generate_recipes(ingredients):
    client = aiplatform.gapic.PredictionServiceClient()
    model_name = f"projects/{project_id}/locations/{location}/models/{model_id}"

    prompt = f"Generate a recipe based on these ingredients: {ingredients}"
    instances = [{"content": prompt}]
    parameters = {}

    try:
        response = client.predict(
            endpoint=model_name,
            instances=instances,
            parameters=parameters
        )
        recipe = response.predictions[0]["content"] if response.predictions else "No recipe generated."
        return recipe
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return "Error generating recipe."

# Home Page (Page 1)
if st.session_state.page == 1:
    st.markdown("<h1 class='main-title'>Welcome To Your AI Food Recipe Generator</h1>", unsafe_allow_html=True)
    if st.button('Get Started'):
        next_page()

# Input Method Selection Page (Page 2)
elif st.session_state.page == 2:
    st.markdown("<h3>How would you like to input your ingredients?</h3>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        if st.button("Take a Picture of What you got"):
            if upload_image():
                st.success("Image uploaded successfully!")
                next_page()

    with col2:
        if st.button("Type in Manually"):
            next_page()
    
    if st.button("⬅️ Back"):
        prev_page()

# Manual Input Page (Page 3)
elif st.session_state.page == 3:
    st.markdown("<h3>Tell us what you got... (e.g., tomatoes, beans)</h3>", unsafe_allow_html=True)
    ingredients = st.text_input("Input Ingredients", key="ingredients")

    if st.button("Cook"):
        st.write(f"Generating a recipe based on: {ingredients}")
        recipe = generate_recipes(ingredients)
        st.write(recipe)
    
    if st.button("Start Voice Recognition"):
        ingredients_from_voice = recognize_voice()
        if ingredients_from_voice:
            recipe = generate_recipes(ingredients_from_voice)
            st.write(recipe)

    if st.button("⬅️ Back"):
        prev_page()
