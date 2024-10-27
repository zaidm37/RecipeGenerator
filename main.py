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

# Keep all original API credentials and configurations
IMAGGA_API_KEY = "acc_3dbc34a6200e1d8"
IMAGGA_API_SECRET = "bd700ca01192e873a808bc3d39cfb4e3"
IMAGGA_ENDPOINT = "https://api.imagga.com/v2/tags"

# Keep all the original functions exactly as they were
def voice_to_text(audio_file):
    return "hello thank you"

def display_signs(text):
    words = text.lower().split()
    for word in words:
        if word in sign_dict:
            st.image(sign_dict[word], caption=word)

def save_favorite(text):
    with open("favorites.json", "a") as file:
        json.dump({"text": text}, file)

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

def transcribe_audio(audio_file_path, model_path="vosk-model-small-en-us-0.15"):
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

def get_tasty_recipes(ingredients):
    api_url = "https://tasty.p.rapidapi.com/recipes/list"
    headers = {
        "X-RapidAPI-Key": "3fbf67f012mshe98341a8fff273bp1d6aedjsn010aaef24072",
        "X-RapidAPI-Host": "tasty.p.rapidapi.com"
    }
    params = {
        "from": 0,
        "size": 5,
        "tags": ",".join(ingredients),
    }

    response = requests.get(api_url, headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        st.error(f"Error fetching recipes: {response.status_code}")
        return []

# Custom styling
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #3CB371 0%, #2E8B57 100%);
        }
        
        .main-title {
            color: white;
            text-align: center;
            font-size: 4rem;
            font-weight: bold;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
            margin-bottom: 2rem;
            padding-top: 2rem;
        }
        
        .subtitle {
            color: white;
            text-align: center;
            font-size: 1.5rem;
            margin-bottom: 2rem;
        }
        
        .stButton>button {
            width: 100%;
            border-radius: 0.5rem;
            padding: 0.75rem 1.5rem;
            font-weight: 500;
            background-color: white;
            color: #2E8B57;
            border: none;
            margin: 0.5rem 0;
        }
        
        .stButton>button:hover {
            background-color: #f0f0f0;
            color: #2E8B57;
        }
        
        .recipe-card {
            background: white;
            color: black;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);

        }
        .recipe-card h3 {
    color: black !important;
}

        
        .input-container {
            background: white;
            padding: 1.5rem;
            border-radius: 0.5rem;
            margin: 1rem 0;
        }
        
        .stTextInput>div>div>input {
            border-radius: 0.5rem;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = 1

if 'ingredients' not in st.session_state:
    st.session_state.ingredients = ""

# Page 1: Home
if st.session_state.page == 1:
    st.markdown("<h1 class='main-title'>Pantry Pal</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitle'>Your Smart Kitchen Assistant</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button('Get Started'):
            st.session_state.page = 2

# Page 2: Input Method
elif st.session_state.page == 2:
    st.markdown("<h2 class='subtitle'>How would you like to input your ingredients?</h2>", unsafe_allow_html=True)



    col1, col2 = st.columns(2)
    with col1:
        if st.button("Tell us with your voice 🎤"):
            st.session_state.page = 4

    with col2:
        if st.button("Type in Manually ⌨️"):
            st.session_state.page = 3

    if st.button("⬅️ Back to Home"):
        st.session_state.page = 1

# Page 3: Manual Input
elif st.session_state.page == 3:
    st.markdown("<h2 class='subtitle'>What ingredients do you have?</h2>", unsafe_allow_html=True)
    
    with st.container():

        #st.markdown("<div class='input-container'>", unsafe_allow_html=True)

        ingredients = st.text_input("", 
                                  value=st.session_state.ingredients,
                                  placeholder="e.g., tomatoes, beans, onions...")
        st.session_state.ingredients = ingredients
        st.markdown("</div>", unsafe_allow_html=True)

        col1, col2 = st.columns([1,1])

        if st.button("Find Recipes 🍳"):
            if ingredients:
                ingredient_list = [i.strip() for i in ingredients.split(',') if i.strip()]
                with st.spinner('Finding recipes...'):
                    recipes = get_tasty_recipes(ingredient_list)

                if recipes and recipes.get('results'):
                    st.success("Found some recipes for you!")
                    for recipe in recipes['results']:
                        thumbnail_url = recipe.get('thumbnail_url')
                        st.markdown(f"""
                                <div class='recipe-card'>
                                    <h3>{recipe['name']}</h3>
                                    {"<img src='" + thumbnail_url + "' width='100%' style='margin-bottom: 1rem;' />" if thumbnail_url else ""}
                                        <a href="{recipe['original_video_url'] or recipe['video_url']}" target="_blank">
                                            View Recipe →
            </a>
        </div>
    """, unsafe_allow_html=True)

                else:
                    st.error("No recipes found. Try different ingredients!")
            else:
                st.warning("Please enter some ingredients first!")
        if st.button("⬅️ Back to Home"):
                st.session_state.page = 1


# Page 4: Voice Input
elif st.session_state.page == 4:
    st.markdown("<h2 class='subtitle'>Speak Your Ingredients</h2>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        if st.button("🎤 Start Speaking"):
            with st.spinner("Listening..."):
                recognizer = sr.Recognizer()
                mic = sr.Microphone()

                with mic as source:
                    try:
                        recognizer.adjust_for_ambient_noise(source)
                        audio = recognizer.listen(source, timeout=5)
                        transcription = recognizer.recognize_google(audio)
                        st.success("Here's what I heard:")
                        st.markdown(f"""
                            <div class='recipe-card'>
                                <p>{transcription}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.session_state.ingredients = transcription
                        ingredient_list = [i.strip() for i in transcription.split(',') if i.strip()]
                        
                        with st.spinner('Finding recipes...'):
                            recipes = get_tasty_recipes(ingredient_list)

                        if recipes and recipes.get('results'):
                            for recipe in recipes['results']:
                                thumbnail_url = recipe.get('thumbnail_url')
                                st.markdown(f"""
                                    <div class='recipe-card'>
                                        <h3>{recipe['name']}</h3>
                                        {"<img src='" + thumbnail_url + "' width='100%' style='margin-bottom: 1rem;' />" if thumbnail_url else ""}
                                        <a href="{recipe['original_video_url'] or recipe['video_url']}" target="_blank">
                                            View Recipe →
                                        </a>
                                    </div>
                                """, unsafe_allow_html=True)
                        else:
                            st.error("No recipes found. Try speaking again!")
                            
                    except sr.WaitTimeoutError:
                        st.error("Listening timed out. Please try again.")
                    except sr.UnknownValueError:
                        st.error("Sorry, I couldn't understand that. Please try again.")
                    except sr.RequestError as e:
                        st.error(f"There was an error with the speech recognition service.")

    if st.button("⬅️ Back to Home"):
        st.session_state.page = 1

