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

# --- Prompt Generation Function (Now Asynchronous) ---
@st.cache_data
async def generate_prompts(num_prompts=5):
    """Generates new prompts using Gemini (asynchronously)."""

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

# --- Fact Loading Function --- (No Changes)
@st.cache_data
def load_dino_facts(filename="dino_facts.txt"):
    """Loads dinosaur facts from a text file."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            facts = [line.strip() for line in f if line.strip()]
        return facts
    except FileNotFoundError:
        st.error(f"Error: Could not find the fact file: {filename}")
        return []

# --- Scene Analysis Function (Now Asynchronous) ---
@st.cache_data
async def analyze_scene(image):
    """Analyzes the scene to extract keywords (asynchronously)."""
    model = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety_settings)
    prompt = "Briefly describe the main elements of this scene..."
    response = await model.generate_content_async([prompt, image]) # Use generate_content_async
    return response.text

# --- Keyword Extraction Function --- (No Changes)
def extract_keywords(scene_description):
    """Extracts keywords from the scene description."""
    keywords = scene_description.lower().split()
    stop_words = {"the", "a", "an", "in", "on", "at", "of", "is", "it", "and", "this", "that", "with", "to"}
    keywords = [word for word in keywords if word not in stop_words and len(word) > 3]
    return keywords[:3]

# --- Main App Logic (Now Asynchronous) ---
async def run_app():  # Wrap the main logic in an async function
    generated_prompts = await generate_prompts() #await
    dino_facts = load_dino_facts()

    serious_mode = st.checkbox("Serious Mode (Detect Objects)")

    if not serious_mode:
        selected_personality = st.selectbox("Choose a dinosaur personality:", list(personalities.keys()))

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

        if file is not None:
            if serious_mode:
                model = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety_settings)
                response = await model.generate_content_async(["Identify the main objects visible in this image.", image], stream=True) # Use generate_content_async
                st.write("Detected Objects:")

                async for chunk in response: #async for loop
                    st.write(chunk.text)

            else:
                scene_description = await analyze_scene(image) #await
                keywords = extract_keywords(scene_description)
                keyword_phrase = ", ".join(keywords)

                chosen_base_prompt = random.choice(generated_prompts)
                if keywords:
                    prompt_choice = f"{personalities[selected_personality]} {chosen_base_prompt.replace('image', f'image showing {keyword_phrase}')}"
                else:
                    prompt_choice = f"{personalities[selected_personality]} {chosen_base_prompt}"

                st.write(f"Using prompt: *{prompt_choice}*")

                model = genai.GenerativeModel('gemini-pro-vision', safety_settings=safety_settings)
                response = await model.generate_content_async([prompt_choice, image], stream=True) # Use generate_content_async

                async for chunk in response: #async for loop
                    st.write(chunk.text)

                if play_sound:
                    st.audio("static/sounds/roar.mp3")

                if dino_facts:
                    random_fact = random.choice(dino_facts)
                    st.write("---")
                    st.info(f"Dinosaur Fact: {random_fact}", icon="🦖")
        if not serious_mode:
            user_caption = st.text_area("Enter your own funny caption:", key="user_caption")
            if user_caption:
                user_captions.append(user_caption)
                st.write("Your caption has been added!")

            if user_captions:
                st.subheader("User-Submitted Captions:")
                for caption in user_captions:
                    st.write(f"- {caption}")

# --- Run the App (Using asyncio.run) ---
if __name__ == "__main__":
    asyncio.run(run_app()) #changed