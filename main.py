import streamlit as st # type: ignore
import json
import requests # type: ignore
from PIL import Image # type: ignore
import io

import os
import wave
from vosk import Model, KaldiRecognizer # type: ignore
from pydub import AudioSegment # type: ignore
import speech_recognition as sr # type: ignore


# Example sign dictionary for testing
sign_dict = {"hello": "hello.gif", "thank you": "thank_you.gif"}

# Function for Voice to Text (for placeholder use)
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

# Image Recognition API Credentials
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

        st.error(f"Error: Status code {response.status_code}")
        st.error("Response text: " + response.text)
        return []
    
    try:
        result = response.json()
        ingredients = [tag['tag']['en'] for tag in result.get("result", {}).get("tags", []) if tag['confidence'] > 50]
        return ingredients
    except json.JSONDecodeError as e:
        st.error("Failed to parse JSON response.")
        st.write(response.text)
        st.error(str(e))
        return []

# Vosk Transcription Setup and Integration
def transcribe_audio(audio_file_path, model_path="vosk-model-small-en-us-0.15"):
    # Ensure model is downloaded
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at {model_path}. Download it from the Vosk website.")
    model = Model(model_path)
    wf = wave.open(audio_file_path, "rb")
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        raise ValueError("Audio file must be WAV format, mono PCM.")
    recognizer = KaldiRecognizer(model, wf.getframerate())
    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if recognizer.AcceptWaveform(data):
            result = recognizer.Result()
            result_text += json.loads(result).get('text', '') + " "
    wf.close()
    return result_text.strip()

def get_recipes(ingredients):
    api_url = "https://api.spoonacular.com/recipes/findByIngredients"
    api_key = "f51f1696cfdf434f9b5081e01e534ea0"  # Replace with your actual API key

    params = {
        'ingredients': ','.join(ingredients),
        'apiKey': api_key,
        'number': 5,  # Number of recipes to return
    }
    
    response = requests.get(api_url, params=params)
    
    if response.status_code == 200:
        return response.json()  # Return the JSON response containing recipes
    else:
        st.error(f"Error fetching recipes: {response.status_code}")
        return []

# Custom CSS
st.markdown(
    """
    <style>

    .stApp { background-color: #3CB371; }
    .main-title { color: white; text-align: center; font-size: 3rem; margin-bottom: 20px; }
    .center-container { display: flex; justify-content: center; margin-top: 20px; }
    button { padding: 10px 20px; font-size: 16px; }

    </style>
    """,
    unsafe_allow_html=True
)


# Initialize page state
if 'page' not in st.session_state:
    st.session_state.page = 1

# Page navigation functions
def next_page():
    st.session_state.page += 1



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
        if st.button("Take a Picture of What you got"):
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

    # Display the current ingredients in a text input
    ingredients_input = st.text_input("Ingredients:", value=st.session_state.ingredients, key="ingredients_input")

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
                st.write("Transcribed Text:")
                st.write(transcription)  # Display the transcription

                # Update ingredients in session state
                st.session_state.ingredients = transcription  # Save transcription to session state

            except sr.WaitTimeoutError:
                st.error("Listening timed out. Please try again.")
            except sr.UnknownValueError:
                st.error("Sorry, I could not understand the audio.")
            except sr.RequestError as e:
                st.error(f"Could not request results from Google Speech Recognition service; {e}")

    # Show updated ingredients in the text input
    st.text_input("Ingredients:", value=st.session_state.ingredients, key="updated_ingredients_input", disabled=False)

    if st.button("Cook"):
        # Get the ingredients from session state
        ingredient_list = st.session_state.ingredients.split(',') if st.session_state.ingredients else []
        
        if ingredient_list:
            ingredient_list = [ingredient.strip() for ingredient in ingredient_list]  # Clean up whitespace
            recipes = get_recipes(ingredient_list)  # Fetch recipes based on ingredients

            # Display the recipes
            if recipes:
                st.write("Here are some recipes you can try:")
                for recipe in recipes:
                    st.write(f"- **{recipe['title']}**")
            else:
                st.write("No recipes found for the given ingredients.")
        else:
            st.warning("Please enter some ingredients or use the microphone to speak.")

    if st.button("⬅️ Back"):
        prev_page()
    

# Page 5: Image Recognition
elif st.session_state.page == 4:  # Update the page number to match the new logic
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
        
        if ingredients:
            st.write("Ingredients detected:", ingredients)
        else:
            st.write("No recognizable ingredients detected.")

    if st.button("⬅️ Back"):
        prev_page()



