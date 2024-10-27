import streamlit as st
import json
import requests
from PIL import Image
import io
import os
import wave
from vosk import Model, KaldiRecognizer
from pydub import AudioSegment
import speech_recognition as sr

# Configuration
TASTY_API_CONFIG = {
    "url": "https://tasty.p.rapidapi.com/recipes/list",
    "headers": {
        "X-RapidAPI-Key": "3fbf67f012mshe98341a8fff273bp1d6aedjsn010aaef24072",
        "X-RapidAPI-Host": "tasty.p.rapidapi.com"
    }
}

IMAGGA_CONFIG = {
    "api_key": "acc_3dbc34a6200e1d8",
    "api_secret": "bd700ca01192e873a808bc3d39cfb4e3",
    "endpoint": "https://api.imagga.com/v2/tags"
}

# Page Configuration
st.set_page_config(
    page_title="Pantry Pal",
    page_icon="🥘",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #43a047 0%, #1b5e20 100%);
        }
        .main-title {
            color: white;
            text-align: center;
            font-size: 3.5rem;
            margin-bottom: 1.5rem;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
        }
        .subtitle {
            color: white;
            text-align: center;
            font-size: 1.2rem;
            margin-bottom: 2rem;
            opacity: 0.9;
        }
        .stButton > button {
            width: 100%;
            border-radius: 10px;
            padding: 0.75rem 1.5rem;
            background: white;
            color: #2e7d32;
            border: none;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 8px rgba(0,0,0,0.15);
        }
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 15px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin-bottom: 1rem;
        }
        .recipe-card {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 0.5rem;
            transition: all 0.3s ease;
        }
        .recipe-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .ingredient-tag {
            display: inline-block;
            background: #e8f5e9;
            color: #2e7d32;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            margin: 0.25rem;
            font-size: 0.9rem;
        }
        div[data-testid="stToolbar"] {
            display: none;
        }
        .stTextInput > div > div > input {
            border-radius: 10px;
        }
        .success-message {
            padding: 1rem;
            background: #e8f5e9;
            color: #2e7d32;
            border-radius: 10px;
            margin: 1rem 0;
        }
        .error-message {
            padding: 1rem;
            background: #ffebee;
            color: #c62828;
            border-radius: 10px;
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Utility Functions
def get_tasty_recipes(ingredients):
    """Fetch recipes from Tasty API."""
    params = {
        "from": 0,
        "size": 5,
        "tags": ",".join(ingredients),
    }
    
    try:
        response = requests.get(
            TASTY_API_CONFIG["url"],
            headers=TASTY_API_CONFIG["headers"],
            params=params
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        st.error(f"Error fetching recipes: {str(e)}")
        return None

def detect_ingredients(image_content):
    """Detect ingredients in image using Imagga API."""
    try:
        response = requests.post(
            IMAGGA_CONFIG["endpoint"],
            auth=(IMAGGA_CONFIG["api_key"], IMAGGA_CONFIG["api_secret"]),
            files={"image": image_content}
        )
        response.raise_for_status()
        result = response.json()
        return [
            tag['tag']['en'] 
            for tag in result.get("result", {}).get("tags", []) 
            if tag['confidence'] > 50
        ]
    except requests.RequestException as e:
        st.error(f"Error detecting ingredients: {str(e)}")
        return []

def transcribe_audio(recognizer, audio):
    """Transcribe audio using Google Speech Recognition."""
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        st.error("Could not understand audio")
        return None
    except sr.RequestError as e:
        st.error(f"Error with speech recognition service: {str(e)}")
        return None

def display_recipe_card(recipe):
    """Display a recipe in a card format."""
    with st.container():
        st.markdown(f"""
            <div class="recipe-card">
                <h3>{recipe['name']}</h3>
                <p style="color: #666;">
                    {recipe.get('total_time_minutes', 'N/A')} mins | 
                    {recipe.get('num_servings', 'N/A')} servings
                </p>
                <a href="{recipe.get('video_url', '#')}" target="_blank">View Recipe</a>
            </div>
        """, unsafe_allow_html=True)

# Initialize Session State
if 'page' not in st.session_state:
    st.session_state.page = 1
if 'ingredients' not in st.session_state:
    st.session_state.ingredients = []

# Main App Logic
def main():
    if st.session_state.page == 1:
        # Home Page
        st.markdown('<h1 class="main-title">🥘 Pantry Pal</h1>', unsafe_allow_html=True)
        st.markdown('<p class="subtitle">Turn your ingredients into delicious recipes</p>', unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            if st.button("Get Started", key="start"):
                st.session_state.page = 2



def prev_page():
    st.session_state.page -= 1

# Page 1: Home
if st.session_state.page == 1:
    st.markdown("<h1 class='main-title'>Pantry Pal</h1>", unsafe_allow_html=True)

    if st.button('Get Started'):
        next_page()

# Page 2: Input Method
elif st.session_state.page == 2:
    st.markdown("<h3>How would you like to input your ingredients?</h3>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Tell us with your voice"):
            st.session_state.page = 4


    with col2:
        if st.button("Type in Manually"):
            next_page()

    if st.button("⬅️ Back"):
        prev_page()

# Page 3: Manual Input
elif st.session_state.page == 3:
    st.markdown("<h3>Tell us what you got... (e.g., tomatoes, beans...)</h3>", unsafe_allow_html=True)

    # Initialize ingredients session state if it doesn't exist
    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = ""

    # Display a single text input that shows either typed or transcribed ingredients
    ingredients = st.text_input("Ingredients:", value=st.session_state.ingredients, key="ingredients_input")

    # Update session state when the user types manually
    st.session_state.ingredients = ingredients

    # Button to start live transcription
    if st.button("🎤 Start Speaking"):
        st.session_state.is_recording = True
        st.markdown("**Listening...**")

        # Function to transcribe audio live
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            try:
                audio = recognizer.listen(source, timeout=5)  # Listen for the audio
                transcription = recognizer.recognize_google(audio)  # Recognize the audio using Google Speech Recognition
                st.session_state.is_recording = False
                st.success("Transcription completed!")

                # Update the ingredients session state with the transcribed text
                st.session_state.ingredients = transcription

                # Manually update the text input to reflect new ingredients
                st.text_input("Ingredients:", value=st.session_state.ingredients, key="ingredients_input_updated")

            except sr.WaitTimeoutError:
                st.error("Listening timed out. Please try again.")
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Speech Recognition service; {e}")

    # Button to generate recipes using the current ingredients in session state
    if st.button("Cook"):
        # Get the ingredients list from session state
        ingredient_list = st.session_state.ingredients.split(',') if st.session_state.ingredients else []
        
        if ingredient_list:
            ingredient_list = [ingredient.strip() for ingredient in ingredient_list]  # Clean up whitespace
            recipes = get_tasty_recipes(ingredient_list)  # Fetch recipes based on ingredients

            # Display the recipes with clickable links
            if recipes:
                st.write("Here are some recipes you can try:")
                for recipe in recipes['results']:
                    recipe_title = recipe['name']
                    recipe_url = recipe['original_video_url'] or recipe['video_url']  # Use video link if available
                    st.markdown(f"- **[{recipe_title}]({recipe_url})**", unsafe_allow_html=True)
            else:
                st.write("No recipes found for the given ingredients.")
        else:
            st.warning("Please enter some ingredients or use the microphone to speak.")

    # Button to go back to the previous page
    if st.button("⬅️ Back"):
        prev_page()    

# Page 5: Voice recognition
elif st.session_state.page == 5:  # Update the page number to match the new logic
    st.markdown("<h3>Take a picture or upload an image of your ingredients</h3>", unsafe_allow_html=True)
    camera_input = st.camera_input("Take a picture") or st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])


    if camera_input:
        image = Image.open(camera_input)
        st.image(image, caption="Uploaded Image", use_column_width=True)


        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes = image_bytes.getvalue()


        st.write("Analyzing the image...")
        ingredients = detect_ingredients(image_bytes)
        
        if st.button("← Back", key="back3"):
            st.session_state.page = 2

    if st.button("⬅️ Back"):
        prev_page()
        prev_page()

# Page 4: Manual Input
elif st.session_state.page == 4:
    st.markdown("<h3>Tell us what you got... (e.g., tomatoes, beans...)</h3>", unsafe_allow_html=True)

    # Initialize ingredients session state if it doesn't exist
    if 'ingredients' not in st.session_state:
        st.session_state.ingredients = ""

    # Display a single text input that shows either typed or transcribed ingredients
    ingredients = st.text_input("Ingredients:", value=st.session_state.ingredients, key="ingredients_input")

    # Update session state when the user types manually
    st.session_state.ingredients = ingredients

    # Button to start live transcription
    if st.button("🎤 Start Speaking"):
        st.session_state.is_recording = True
        st.markdown("**Listening...**")

        # Function to transcribe audio live
        recognizer = sr.Recognizer()
        mic = sr.Microphone()

        with mic as source:
            recognizer.adjust_for_ambient_noise(source)  # Adjust for ambient noise
            try:
                audio = recognizer.listen(source, timeout=5)  # Listen for the audio
                transcription = recognizer.recognize_google(audio)  # Recognize the audio using Google Speech Recognition
                st.session_state.is_recording = False
                st.success("Transcription completed!")

                # Update the ingredients session state with the transcribed text
                st.session_state.ingredients = transcription

                # Manually update the text input to reflect new ingredients
                st.text_input("Ingredients:", value=st.session_state.ingredients, key="ingredients_input_updated")

            except sr.WaitTimeoutError:
                st.error("Listening timed out. Please try again.")
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Speech Recognition service; {e}")

    # Button to generate recipes using the current ingredients in session state
    if st.button("Cook"):
        # Get the ingredients list from session state
        ingredient_list = st.session_state.ingredients.split(',') if st.session_state.ingredients else []
        
        if st.button("🎤 Start Recording", key="record"):
            with st.spinner("Listening..."):
                recognizer = sr.Recognizer()
                with sr.Microphone() as source:
                    st.info("Listening... Speak your ingredients!")
                    recognizer.adjust_for_ambient_noise(source)
                    audio = recognizer.listen(source, timeout=5)
                    
                text = transcribe_audio(recognizer, audio)
                if text:
                    st.session_state.ingredients = [i.strip() for i in text.split(",")]
                    st.success("Transcription successful!")
                    st.write("Detected ingredients:")
                    for ingredient in st.session_state.ingredients:
                        st.markdown(f'<span class="ingredient-tag">{ingredient}</span>', unsafe_allow_html=True)
        
        if st.session_state.ingredients:
            if st.button("🔍 Find Recipes", key="find_voice"):
                with st.spinner("Searching for recipes..."):
                    recipes = get_tasty_recipes(st.session_state.ingredients)
                    if recipes and recipes.get('results'):
                        for recipe in recipes['results']:
                            display_recipe_card(recipe)
                    else:
                        st.warning("No recipes found. Try different ingredients!")
        
        if st.button("← Back", key="back4"):
            st.session_state.page = 2

    elif st.session_state.page == 5:
        # Photo Input Page
        st.markdown('<h1 class="main-title">Photo Input</h1>', unsafe_allow_html=True)
        
        img_file = st.camera_input("Take a picture of your ingredients")
        if img_file:
            image = Image.open(img_file)
            
            # Convert image for API
            img_byte_arr = io.BytesIO()
            image.save(img_byte_arr, format=image.format)
            img_byte_arr = img_byte_arr.getvalue()
            
            with st.spinner("Analyzing image..."):
                detected_ingredients = detect_ingredients(img_byte_arr)
                if detected_ingredients:
                    st.success("Ingredients detected!")
                    st.session_state.ingredients = detected_ingredients
                    for ingredient in detected_ingredients:
                        st.markdown(f'<span class="ingredient-tag">{ingredient}</span>', unsafe_allow_html=True)
                    
                    if st.button("🔍 Find Recipes", key="find_photo"):
                        recipes = get_tasty_recipes(detected_ingredients)
                        if recipes and recipes.get('results'):
                            for recipe in recipes['results']:
                                display_recipe_card(recipe)
                        else:
                            st.warning("No recipes found. Try taking another photo!")
                else:
                    st.warning("No ingredients detected. Try taking another photo!")
        
        if st.button("← Back", key="back5"):
            st.session_state.page = 2

    # Button to go back to the previous page
    if st.button("⬅️ Back"):
        prev_page()    
