import streamlit as st
import json

# Example sign dictionary for testing
sign_dict = {"hello": "hello.gif", "thank you": "thank_you.gif"}

# Page navigation
st.sidebar.title("Pantry Pal")
page = st.sidebar.selectbox("Choose a page", ["Home", "Translate", "Favorites", "History", "Settings"])

def voice_to_text(audio_file):
    # Placeholder for API call - replace with actual API transcription
    return "hello thank you"  # Dummy response

def display_signs(text):
    words = text.lower().split()
    for word in words:
        if word in sign_dict:
            st.image(sign_dict[word], caption=word)

def save_favorite(text):
    with open("favorites.json", "a") as file:
        json.dump({"text": text}, file)

# Pages
if page == "Home":
    st.title("Welcome to SignSpeak")
    st.write("Type or upload an audio file to translate to sign language.")

elif page == "Translate":
    st.title("Translate to Sign Language")
    audio_file = st.file_uploader("Upload audio file", type=["wav", "mp3"])
    text_input = st.text_input("Or type a phrase to translate")

    transcript = voice_to_text(audio_file) if audio_file else text_input
    if transcript:
        st.write("Transcription:", transcript)
        display_signs(transcript)
        if st.button("Add to Favorites"):
            save_favorite(transcript)

elif page == "Favorites":
    st.title("Your Favorites")
    with open("favorites.json", "r") as file:
        favorites = json.load(file)
    for favorite in favorites:
        st.write(favorite["text"])

elif page == "History":
    st.title("Translation History")
    # Logic for loading and displaying history (similar to Favorites)

elif page == "Settings":
    st.title("Settings")
    if st.button("Clear History"):
        open("history.json", "w").close()  # Clears the file
    st.selectbox("Select Language", ["English", "Spanish", "French"])
