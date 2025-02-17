# ISITADINOSAUR

_Is it Jurassic or just a pic? Let our image checker decide!_

## What's this?!

This app takes an image as input and uses AI (Google's Gemini Vision Pro) to determine if a dinosaur is present, providing a humorous response.  It's built with Python and Streamlit.

## Features

*   **Dinosaur Detection (Humorous):**  The app analyzes your image and generates a funny response about whether a dinosaur appears to be present.
*   **Multiple Prompt Styles:**  Choose from several different prompt styles to get a variety of humorous responses.
*   **User-Submitted Captions:**  Add your own funny caption to the image!  User captions are displayed alongside the AI-generated response.
*   **Sound Effects (Optional):**  A fun sound effect plays after the AI response (can be muted).
*   **WebP Support:** Supports JPG, JPEG, PNG, and WebP image formats.

## Tech Stack

*   Python
*   Streamlit
*   Gemini Vision Pro

## How to Run (Locally)

1.  **Clone the repository:**
    ```bash
    git clone <your_repository_url>
    cd ISITADINOSAUR
    ```
    (Replace `<your_repository_url>` with the actual URL of your GitHub repository.)

2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Create a `.env` file:**
    *   Create a file named `.env` in the project's root directory.
    *   Add your Google Gemini API key to the `.env` file:
        ```
        GOOGLE_API_KEY=your_actual_api_key_here
        ```
        (Replace `your_actual_api_key_here` with your key.)

4.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

## Roadmap

*   [ ] Add "Serious Mode" for actual object detection.
*   [ ] Implement caching to improve performance.
*   [ ] Explore LangChain integration.
