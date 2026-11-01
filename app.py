
import streamlit as st
import numpy as np
import tempfile
import os
import shutil

from io import BytesIO
from PIL import Image, ImageFilter, ImageEnhance
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip


st.set_page_config(
    page_title="Assam Reel AI",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Assam Reel AI")
st.caption("Create Cinematic Assamese Reels")
st.divider()

photo = st.file_uploader(
    "Upload Photo",
    type=["jpg", "jpeg", "png"]
)

song = st.file_uploader(
    "Upload Assamese Song",
    type=["mp3", "wav", "m4a"]
)

duration_option = st.selectbox(
    "Reel Duration",
    ["30 Seconds", "1 Minute"]
)

requested_duration = 30 if duration_option == "30 Seconds" else 60

effect = st.selectbox(
    "Camera Animation",
    ["Zoom In", "Zoom Out", "Pan Left", "Pan Right"]
)

background_style = st.selectbox(
    "Background Style",
    ["Natural", "Blur", "Dreamy"]
)

mood = st.selectbox(
    "Reel Theme",
    ["Bihu", "Kathak", "Romantic", "Happy", "Emotional", "Cinematic"]
)

if photo:
    st.image(photo, caption="Photo Preview", width="stretch")

if song:
    st.audio(song)

st.write("Video Format: Vertical 9:16 | 720 × 1280")


def make_reel(photo_data, song_data):

    temp_dir = tempfile.mkdtemp(prefix="assam_reel_")
    audio_path = os.path.join(temp_dir, "song.mp3")
    output_path = os.path.join(temp_dir, "reel.mp4")

    clips = []

    try:
        image = Image.open(
            BytesIO(photo_data)
        ).convert("RGB")

        with open(audio_path, "wb") as f:
            f.write(song_data)

        audio = AudioFileClip(audio_path)
        clips.append(audio)

        duration = min(requested_duration, audio.duration)

        if duration <= 0:
            raise ValueError("Audio duration is invalid.")

        audio = audio.subclipped(0, duration)

        # Create background
        bg = image.resize(
            (720, 1280),
            Image.Resampling.LANCZOS
        )

        if background_style == "Blur":
            bg = bg.filter(ImageFilter.GaussianBlur(25))
        elif background_style == "Dreamy":
            bg = bg.filter(ImageFilter.GaussianBlur(12))
            bg = ImageEnhance.Brightness(bg).enhance(1.12)

        # Fit foreground image
        ratio = max(720 / image.width, 1280 / image.height)

        resized = image.resize(
            (int(image.width * ratio), int(image.height * ratio)),
            Image.Resampling.LANCZOS
        )

        left = (resized.width - 720) // 2
        top = (resized.height - 1280) // 2

        foreground = resized.crop(
            (left, top, left + 720, top + 1280)
        )

        # Mood adjustments
        if mood == "Romantic":
            foreground = ImageEnhance.Color(foreground).enhance(1.15)
            foreground = ImageEnhance.Brightness(foreground).enhance(1.06)

        elif mood == "Happy" or mood == "Bihu":
            foreground = ImageEnhance.Color(foreground).enhance(1.30)
            foreground = ImageEnhance.Contrast(foreground).enhance(1.08)

        elif mood == "Emotional":
            foreground = ImageEnhance.Color(foreground).enhance(0.65)
            foreground = ImageEnhance.Contrast(foreground).enhance(1.12)

        elif mood == "Kathak":
            foreground = ImageEnhance.Color(foreground).enhance(1.12)
            foreground = ImageEnhance.Contrast(foreground).enhance(1.08)

        # Video clips
        background = ImageClip(
            np.array(bg)
        ).with_duration(duration)

        clips.append(background)

        base = ImageClip(
            np.array(foreground)
        ).with_duration(duration)

        clips.append(base)

        if effect == "Zoom In":
            animated = base.resized(
                lambda t: 1 + 0.12 * t / duration
            ).with_position("center")

        elif effect == "Zoom Out":
            animated = base.resized(
                lambda t: 1.12 - 0.12 * t / duration
            ).with_position("center")

        elif effect == "Pan Left":
            animated = base.resized(1.08).with_position(
                lambda t: (
                    -38 * t / duration,
                    -51 * t / duration
                )
            )

        else:
            animated = base.resized(1.08).with_position(
                lambda t: (
                    -38 + 38 * t / duration,
                    -51 + 51 * t / duration
                )
            )

        clips.append(animated)

        video = CompositeVideoClip(
            [background, animated],
            size=(720, 1280)
        ).with_duration(duration)

        clips.append(video)

        final_video = video.with_audio(audio)
        clips.append(final_video)

        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            logger=None
        )

        with open(output_path, "rb") as f:
            video_bytes = f.read()

        if not video_bytes:
            raise RuntimeError("Video export failed.")

        return video_bytes, duration

    finally:
        for clip in reversed(clips):
            try:
                clip.close()
            except Exception:
                pass

        shutil.rmtree(temp_dir, ignore_errors=True)


if st.button("✨ GENERATE MY REEL", width="stretch"):

    if photo is None or song is None:
        st.warning("Please upload both photo and song.")

    else:
        try:
            with st.spinner("Creating your cinematic reel..."):

                video_bytes, actual_duration = make_reel(
                    photo.getvalue(),
                    song.getvalue()
                )

            st.success(
                f"Your reel is ready! {actual_duration:.1f} seconds"
            )

            st.video(video_bytes)

            st.download_button(
                "⬇️ Download MP4",
                data=video_bytes,
                file_name="Assam_Reel_AI.mp4",
                mime="video/mp4",
                width="stretch"
            )

        except Exception as e:
            st.error("Reel generation failed.")
            st.exception(e)
