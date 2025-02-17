import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import PIL.Image
import random

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
    page_title="ISITADINOSAUR",
    layout="centered"
)

st.image('static/dino-logo.png', width=100)
st.header("ISITADINOSAUR", divider='rainbow')
st.markdown('_Is it Jurassic or just a pic?  Let our image checker decide!_')

# --- Prompt Generation Function ---
@st.cache_data
def generate_prompts(num_prompts=5):
    """Generates new prompts using Gemini."""

    model = genai.GenerativeModel('gemini-pro')

    meta_prompt = """
    You are a creative prompt generator for an image analysis app called "ISITADINOSAUR".
    This app takes an image as input and uses AI to determine if a dinosaur is present,
    providing a *humorous* response.

    Your task is to generate prompts that will be used to analyze the images. The prompts should:
    1. Be funny and creative.
    2. Encourage imaginative responses related to dinosaurs (or their absence).
    3. Focus on visual elements of the image.
    4. Be relatively short (around 20-40 words).

    Here are a few examples of good prompts:

    * "Analyze the image and provide a humorous response about whether a dinosaur appears to be present. Be creative, but focus on the visual elements."
    * "Describe this image as if a confused time-traveling dinosaur wrote a postcard about it."
    * "Write a short, silly news report about the (non)discovery of a dinosaur in this image."

    Now, generate {} new, distinct prompts for the ISITADINOSAUR app.
    """.format(num_prompts)

    response = model.generate_content(meta_prompt)
    prompts = response.text.strip().split("\n")
    prompts = [p.strip('*- ') for p in prompts if p.strip()]
    return prompts

# --- Dinosaur Personalities ---
personalities = {
    "Grumpy T-Rex": "Analyze the image as if a grumpy T-Rex were commenting on it. Be sarcastic and unimpressed.",
    "Silly Stegosaurus": "Describe the image from the perspective of a very silly Stegosaurus. Be playful and nonsensical.",
    "Philosophical Triceratops": "Analyze the image as if a philosophical Triceratops were pondering its meaning. Be thoughtful and introspective.",
    "Excited Velociraptor": "Describe the image as if a very excited Velociraptor just saw it. Be energetic and enthusiastic.",
    "Sleepy Brontosaurus": "Analyze this image like a sleepy Brontosaurus, be slow and descriptive."
}

# --- UI Elements ---
generated_prompts = generate_prompts()  # Get dynamically generated prompts

# User selects personality
selected_personality = st.selectbox("Choose a dinosaur personality:", list(personalities.keys()))

# Combine personality with a random prompt
chosen_base_prompt = random.choice(generated_prompts)
prompt_choice = f"{personalities[selected_personality]} {chosen_base_prompt}"


file = st.file_uploader("Upload an image to check for dinosaurs.", type=["jpg", "jpeg", "png", "webp"])
play_sound = st.checkbox("Play sound effect", value=True)
user_captions = []

img, result = st.columns(2)

with img:
    st.info('Uploaded Image', icon="ℹ️")
    if file is not None:
        image = PIL.Image.open(file)
        st.image(file, width=350)

with result:
    st.info('Dinosaur Detection Results', icon="ℹ️")
    st.write(f"Using prompt: *{prompt_choice}*")  # Show the combined prompt

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