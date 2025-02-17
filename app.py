import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
import PIL.Image
import random
import asyncio

load_dotenv()

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)

# Safety settings to block harmful content (all categories set to BLOCK_NONE for demonstration, adjust as needed)
safety_settings = [
    {"category": cat, "threshold": "BLOCK_NONE"} for cat in [
        "HARM_CATEGORY_DANGEROUS", "HARM_CATEGORY_HARASSMENT", "HARM_CATEGORY_HATE_SPEECH",
        "HARM_CATEGORY_SEXUALLY_EXPLICIT", "HARM_CATEGORY_DANGEROUS_CONTENT"
    ]
]

st.set_page_config(page_title="ISITADINOSAUR", layout="centered")

st.image('static/dino-logo.png', width=100)
st.header("ISITADINOSAUR", divider='rainbow')
st.markdown('_Is it Jurassic or just a pic? Let our image checker decide!_')

# --- Prompt Generation Function (Asynchronous and Cached) ---

@st.cache_data
async def generate_prompts(num_prompts=5):
    """Generates new prompts using Gemini (asynchronously)."""

    model = genai.GenerativeModel('gemini-2.0-flash-lite-preview-02-05')

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

    response = await model.generate_content_async(meta_prompt) # Use generate_content_async
    prompts = response.text.strip().split("\n")
    prompts = [p.strip('*- ') for p in prompts if p.strip()]
    return prompts

# --- Dinosaur Personalities ---
personalities = {
    "Grumpy T-Rex (Rex)": "Analyze this image as if you are Rex, a perpetually grumpy Tyrannosaurus Rex. You're easily annoyed, find everything inconvenient, and have a very short temper. Complain about everything you see, use short, sharp sentences, and be as sarcastic as possible. Nothing pleases you.",
    "Silly Stegosaurus (Stella)": "Describe this image from the perspective of Stella, a Stegosaurus who is incredibly silly and easily distracted. Use lots of made-up words, giggle frequently (write out 'hehe' or 'teehee'), and get sidetracked by shiny things. Your thoughts should be a jumbled, playful mess.",
    "Philosophical Triceratops (Terry)": "Analyze this image as if you are Terry, a Triceratops who loves to ponder the deeper meaning of everything.  Be thoughtful and introspective. Use metaphors and analogies.  Ask existential questions about the image, even if it's just a picture of a rock. Wonder about the nature of existence.",
    "Excited Velociraptor (Valerie)": "Describe this image as if Valerie, a hyperactive Velociraptor, just spotted it.  You're incredibly enthusiastic and easily excited. Use lots of exclamation points!!! Talk very fast, jump from one idea to the next, and imagine all the exciting (and possibly dangerous) things that *could* be happening in the image.",
    "Sleepy Brontosaurus (Barry)": "Analyze this image as if you are Barry, a Brontosaurus who is perpetually sleepy.  Speak... very... slowly... Use... lots... of... ellipses...  Describe things in a drawn-out, languid way.  Mention how tired you are and how much you'd like to take a nap.",
    "Professor Pterodactyl (Percy)": "Analyze the image as Professor Percy Pterodactyl, a very knowledgeable but slightly pompous paleontologist. Use precise, scientific-sounding language (even if it's humorous), correct any perceived inaccuracies, and offer long-winded explanations. Be a bit of a know-it-all.",
    "Anxious Ankylosaurus (Andy)": "Describe this image from the perspective of Andy, an Ankylosaurus who is constantly worried about everything. Be extremely cautious, point out all the potential dangers, and express your anxieties about what might happen. Overthink everything.",
    "Diva Diplodocus (Diana)": "Analyze the image as Diana, a Diplodocus who is a complete diva. You're obsessed with your appearance, very dramatic, and consider yourself incredibly important. Comment on the image's aesthetic qualities (or lack thereof) and relate everything back to yourself."
}

# --- Fact Loading Function (Cached) ---
@st.cache_data
def load_dino_facts(filename="dino_facts.txt"):
    """Loads dinosaur facts from a text file, handling potential errors."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        st.error(f"Error: Could not find the fact file: {filename}")
        return []

# --- Scene Analysis Function (Asynchronous and Cached) ---
@st.cache_data
async def analyze_scene(image):
    """Analyzes the image to extract keywords describing the scene."""
    model = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety_settings)
    prompt = "Briefly describe the main elements of this scene (e.g., forest, beach, room). Keep it short, 5-10 words."
    response = await model.generate_content_async([prompt, image])
    return response.text

# --- Keyword Extraction Function ---
def extract_keywords(scene_description):
    """Extracts up to 3 relevant keywords from a scene description."""
    keywords = scene_description.lower().split()
    stop_words = {"the", "a", "an", "in", "on", "at", "of", "is", "it", "and", "this", "that", "with", "to"}
    return [word for word in keywords if word not in stop_words and len(word) > 3][:3]

# --- Main App Logic (Asynchronous) ---
async def run_app():
    generated_prompts = await generate_prompts()
    dino_facts = load_dino_facts()

    serious_mode = st.checkbox("Serious Mode (Detect Objects)")
    selected_personality = st.selectbox("Choose a dinosaur personality:", list(personalities.keys())) if not serious_mode else None

    file = st.file_uploader("Upload an image to check for dinosaurs.", type=["jpg", "jpeg", "png", "webp"])
    play_sound = st.checkbox("Play sound effect", value=True)
    user_captions = []

    img, result_col = st.columns(2) # Consistent variable naming

    with img:
        st.info('Uploaded Image', icon="ℹ️")
        if file is not None:
            image = PIL.Image.open(file)
            st.image(image, width=350)  # Pass the PIL Image object

    with result_col:
        st.info('Dinosaur Detection Results', icon="ℹ️")

        if file is not None:
            if serious_mode:
                model = genai.GenerativeModel('gemini-2.0-flash', safety_settings=safety_settings)
                response = await model.generate_content_async(["Identify the main objects visible in this image.", image], stream=True)
                st.write("Detected Objects:")
                async for chunk in response:
                    st.write(chunk.text)

            else:
                scene_description = await analyze_scene(image)
                keywords = extract_keywords(scene_description)
                keyword_phrase = ", ".join(keywords)

                chosen_base_prompt = random.choice(generated_prompts)
                prompt_choice = (
                    f"{personalities[selected_personality]} {chosen_base_prompt.replace('image', f'image showing {keyword_phrase}')}"
                    if keywords else f"{personalities[selected_personality]} {chosen_base_prompt}"
                )

                st.write(f"Using prompt: *{prompt_choice}*")

                model = genai.GenerativeModel('gemini-2.0-flash', safety_settings=safety_settings)
                response = await model.generate_content_async([prompt_choice, image], stream=True)

                async for chunk in response:
                    st.write(chunk.text)

                if play_sound:
                    st.audio("static/sounds/roar.mp3")

                if dino_facts:
                    st.write("---")
                    st.info(f"Dinosaur Fact: {random.choice(dino_facts)}", icon="🦖")

            if not serious_mode:
                user_caption = st.text_area("Enter your own funny caption:", key="user_caption")
                if user_caption:
                    user_captions.append(user_caption)
                    st.write("Your caption has been added!")

                if user_captions:
                    st.subheader("User-Submitted Captions:")
                    for caption in user_captions:
                        st.write(f"- {caption}")

if __name__ == "__main__":
    asyncio.run(run_app())