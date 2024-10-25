import streamlit as st

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
