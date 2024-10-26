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

# Initialize session state to track the current page
if 'page' not in st.session_state:
    st.session_state.page = 1

# Function to move to the next page
def next_page():
    st.session_state.page += 1

# Function to move to the previous page
def prev_page():
    st.session_state.page -= 1

# Home Page (Page 1)
if st.session_state.page == 1:
    st.markdown("<h1 class='main-title'>Welcome To You AI Food Recipe Generator</h1>", unsafe_allow_html=True)
    
    st.markdown("""
        <div class='get-started'>
            <button onclick="window.location.href='/'">get started</button>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button('get started'):
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
            st.write("Feature not yet implemented.")
    
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
