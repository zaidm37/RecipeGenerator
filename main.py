import streamlit as st
from PIL import Image
import openai
import speech_recognition as sr

# Set up your OpenAI API key (replace 'your-api-key' with your actual key)
openai.api_key = 'your-api-key'

# Set custom CSS for styling
st.markdown("""
    <style>
    body {
        background-color: #83C983; /* Match the green background */
    }
    .main-title {
        text-align: center;
        font-size: 32px;
        color: black;
    }
    .get-started {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-top: 20px;
    }
    .get-started button {
        background-color: #4CAF50;
        color: white;
        border: none;
        padding: 10px 20px;
        font-size: 18px;
        cursor: pointer;
        border-radius: 25px;
    }
    .learn-more {
        display: flex;
        justify-content: center;
        margin-top: 20px;
    }
    .learn-more button {
        background-color: #87CEEB;
        color: white;
        border: none;
        padding: 8px 16px;
        font-size: 14px;
        cursor: pointer;
        border-radius: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state to track the current page
if 'page' not in st.session_state:
    st.session_state.page = 1

# Function to move to the next page
def next_page():
    st.session_state.page += 1

# Function to move to the previous page
def prev_page():
    st.session_state.page -= 1

# Function to upload an image
def upload_image():
    uploaded_file = st.file_uploader("Upload an image of your ingredients", type=["jpg", "jpeg", "png"])
    if uploaded_file is not None:
        image = Image.open(uploaded_file)
        st.image(image, caption='Uploaded Image.', use_column_width=True)
        return True
    return False

# Function to recognize voice input
def recognize_voice():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("Please speak your ingredients...")
        audio = r.listen(source)

        try:
            text = r.recognize_google(audio)
            st.write(f"You said: {text}")
            return text
        except sr.UnknownValueError:
            st.write("Sorry, I could not understand the audio.")
            return None
        except sr.RequestError:
            st.write("Could not request results from Google Speech Recognition service.")
            return None

# Function to generate recipes using OpenAI
def generate_recipes(ingredients):
    response = openai.Completion.create(
        engine="davinci-codex",  # Choose your preferred model
        prompt=f"Generate a recipe using the following ingredients: {ingredients}",
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.7,
    )
    recipe = response.choices[0].text.strip()
    return recipe

# Home Page (Page 1)
if st.session_state.page == 1:
    st.markdown("<h1 class='main-title'>Welcome To Your AI Food Recipe Generator</h1>", unsafe_allow_html=True)

    st.markdown("""
        <div class='get-started'>
            <button onclick="window.location.href='/'">Get Started</button>
        </div>
    """, unsafe_allow_html=True)

    if st.button('Get Started'):
        next_page()

    st.markdown("""
        <div class='learn-more'>
            <button onclick="window.location.href='/'">Learn More</button>
        </div>
    """, unsafe_allow_html=True)

# Input Method Selection Page (Page 2)
elif st.session_state.page == 2:
    st.markdown("<h3>How would you like to input your ingredients?</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Take a Picture of What you got"):
            if upload_image():
                st.success("Image uploaded successfully!")
                next_page()  # Move to the next page after image upload

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
