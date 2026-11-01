
import streamlit as st
import fal_client
import os
import base64
import requests

st.set_page_config(
    page_title="Assam Reel AI",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Assam Reel AI")
st.write("Realistic AI Dance & Cinematic Video")

# Secure API key
try:
    os.environ["FAL_KEY"] = st.secrets["FAL_KEY"]
except Exception:
    st.error("API key not found. Check Streamlit Secrets.")
    st.stop()

photo = st.file_uploader(
    "Upload your photo",
    type=["jpg", "jpeg", "png"]
)

song = st.file_uploader(
    "Upload Assamese song",
    type=["mp3", "wav", "m4a"]
)

motion = st.selectbox(
    "Choose Motion Style",
    [
        "Bihu Dance",
        "Kathak Dance",
        "Romantic",
        "Emotional",
        "Happy",
        "Cinematic Only"
    ]
)

camera = st.selectbox(
    "Camera Effect",
    [
        "Smooth cinematic camera movement",
        "Slow zoom in",
        "Slow zoom out",
        "Gentle camera pan"
    ]
)

mood_prompts = {
    "Bihu Dance":
        "Perform a joyful traditional Assamese Bihu dance, "
        "natural graceful movements and festive energy.",

    "Kathak Dance":
        "Perform graceful classical Kathak dance movements "
        "with elegant hand gestures and expressive posture.",

    "Romantic":
        "A gentle cinematic romantic expression, "
        "soft natural movement and graceful gestures.",

    "Emotional":
        "A subtle emotional cinematic performance "
        "with gentle expressive movement.",

    "Happy":
        "A cheerful happy expression with natural "
        "body movement and joyful energy.",

    "Cinematic Only":
        "Remain natural with subtle realistic movement "
        "and cinematic camera motion."
}

if photo:
    st.image(photo, caption="Uploaded Photo",
             use_container_width=True)

if song:
    st.audio(song)

st.info("Test generation: 5 seconds, 720p.")

guardian_ok = st.checkbox(
    "A parent/guardian has approved this paid AI generation."
)

if st.button("GENERATE TEST VIDEO", use_container_width=True):

    if not guardian_ok:
        st.warning("Please get parent/guardian approval first.")
        st.stop()

    if photo is None:
        st.warning("Please upload a photo first.")
        st.stop()

    try:
        with st.spinner("AI is creating your video..."):

            image_data = base64.b64encode(
                photo.getvalue()
            ).decode("utf-8")

            mime = photo.type or "image/jpeg"

            image_url = (
                f"data:{mime};base64,{image_data}"
            )

            prompt = (
                "Create a realistic cinematic video based "
                "on the uploaded person's appearance. "
                + mood_prompts[motion]
                + " "
                + camera
                + ". Preserve the person's facial identity, "
                "clothing and natural proportions. "
                "Smooth realistic motion, detailed background, "
                "professional cinematic lighting, vertical video."
            )

            result = fal_client.subscribe(
                "fal-ai/wan/v2.7/image-to-video",
                arguments={
                    "image_url": image_url,
                    "prompt": prompt,
                    "duration": 5,
                    "resolution": "720p",
                    "enable_safety_checker": True
                }
            )

            video_url = result["video"]["url"]

            video_response = requests.get(
                video_url,
                timeout=180
            )
            video_response.raise_for_status()

            video_bytes = video_response.content

        st.success("AI video created successfully!")
        st.video(video_bytes)

        st.download_button(
            "Download Test Video",
            data=video_bytes,
            file_name="assam_reel_test.mp4",
            mime="video/mp4",
            use_container_width=True
        )

    except Exception as e:
        st.error("Video generation failed.")
        st.caption(str(e))
