import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import PIL.Image

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

safety_settings = [
    {
        "category": "HARM_CATEGORY_DANGEROUS",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

st.set_page_config(
    page_title="ISITADINOSAUR",  # Changed title
    layout="centered"
)

st.image('static/dino-logo.png', width=100)  # Added logo back
st.header("ISITADINOSAUR", divider='rainbow') # Changed the header
st.markdown('_Is it Jurassic or just a pic?  Let our image checker decide!_')

# --- Prompts ---
prompts = [
    "Analyze the image and provide a humorous response about whether a dinosaur appears to be present. Be creative, but focus on the visual elements.",
    "Describe this image as if a confused time-traveling dinosaur wrote a postcard about it.",
    "Write a short, silly news report about the (non)discovery of a dinosaur in this image.",
    "If this image *were* a scene from a dinosaur movie, what would the title be?",
    "Generate a funny caption for this image, assuming there's a hidden dinosaur *somewhere*.",
    "Pretend to be a paleontologist providing a humorous analysis, looking for dinosaurs."
]

# --- UI Elements ---
prompt_choice = st.selectbox("Choose a prompt style:", prompts, index=0)
file = st.file_uploader("Upload an image to check for dinosaurs.", type=["jpg", "jpeg", "png", "webp"])
play_sound = st.checkbox("Play sound effect", value=True)
user_captions = []  # Store user captions

img, result = st.columns(2)

with img:
    st.info('Uploaded Image', icon="ℹ️")
    if file is not None:
        image = PIL.Image.open(file)
        st.image(file, width=350)

with result:
    st.info('Dinosaur Detection Results', icon="ℹ️")
    if file is not None:
        model = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety_settings)
        response = model.generate_content([prompt_choice, image], stream=True)
        response.resolve()

        for chunk in response:
            st.write(chunk.text)

        if play_sound:
            st.audio("static/sounds/roar.mp3")

    # --- User Caption Input ---
    user_caption = st.text_area("Enter your own funny caption:", key="user_caption")
    if user_caption:
        user_captions.append(user_caption)
        st.write("Your caption has been added!")

    if user_captions:
        st.subheader("User-Submitted Captions:")
        for caption in user_captions:
            st.write(f"- {caption}")