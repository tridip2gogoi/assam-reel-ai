
import streamlit as st
import numpy as np
import tempfile
import os
import traceback

from pathlib import Path
from PIL import Image, ImageFilter
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip


# ---------------- PAGE SETTINGS ----------------

st.set_page_config(
    page_title="Assam Reel AI",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Assam Reel AI")
st.caption("Create Your Cinematic Reel")

st.divider()


# ---------------- USER INPUT ----------------

photo = st.file_uploader(
    "Upload Your Photo",
    type=["jpg", "jpeg", "png"]
)

song = st.file_uploader(
    "Upload Your Assamese Song",
    type=["mp3", "wav", "m4a"]
)

duration_option = st.selectbox(
    "Select Reel Duration",
    ["30 Seconds", "1 Minute"]
)

requested_duration = (
    30 if duration_option == "30 Seconds" else 60
)

effect = st.selectbox(
    "Cinematic Camera Effect",
    ["Zoom In", "Zoom Out", "Pan Left", "Pan Right"]
)

background_style = st.selectbox(
    "Background Style",
    ["Natural", "Blur Background", "Dreamy Background"]
)

mood = st.selectbox(
    "Reel Theme",
    ["Bihu", "Romantic", "Emotional", "Happy", "Kathak", "Cinematic"]
)


# ---------------- PREVIEW ----------------

if photo:
    st.image(
        photo,
        caption="Your Photo",
        width="stretch"
    )

if song:
    st.audio(song)

st.write("Video Format: 9:16 Vertical | 720 × 1280")


# ---------------- VIDEO GENERATOR ----------------

def make_reel(photo_data, song_data):

    temp_dir = tempfile.mkdtemp(prefix="assam_reel_")

    photo_path = os.path.join(temp_dir, "input_photo.jpg")
    audio_path = os.path.join(temp_dir, "input_audio")
    output_path = os.path.join(temp_dir, "output_reel.mp4")

    clips = []

    try:

        # Validate generated paths
        for file_path in [photo_path, audio_path, output_path]:
            if "\x00" in file_path:
                raise ValueError("Invalid temporary file path.")

        # Save uploaded photo
        image = Image.open(
            photo_data
        ).convert("RGB")

        image.save(photo_path, format="JPEG")

        # Save uploaded audio
        with open(audio_path, "wb") as file:
            file.write(song_data)

        if os.path.getsize(audio_path) == 0:
            raise ValueError("Uploaded audio file is empty.")

        # Read audio
        audio = AudioFileClip(str(Path(audio_path).resolve()))
        clips.append(audio)

        duration = min(
            float(requested_duration),
            float(audio.duration)
        )

        if duration <= 0:
            raise ValueError("Audio duration is invalid.")

        audio = audio.subclipped(0, duration)

        # Create vertical background
        background = image.resize(
            (720, 1280),
            Image.Resampling.LANCZOS
        )

        if background_style == "Blur Background":
            background = background.filter(
                ImageFilter.GaussianBlur(28)
            )

        elif background_style == "Dreamy Background":
            background = background.filter(
                ImageFilter.GaussianBlur(12)
            )

        # Fit main photo into vertical frame
        ratio = max(
            720 / image.width,
            1280 / image.height
        )

        new_width = int(image.width * ratio)
        new_height = int(image.height * ratio)

        foreground = image.resize(
            (new_width, new_height),
            Image.Resampling.LANCZOS
        )

        left = (foreground.width - 720) // 2
        top = (foreground.height - 1280) // 2

        foreground = foreground.crop(
            (left, top, left + 720, top + 1280)
        )

        # Background clip
        background_clip = ImageClip(
            np.array(background)
        ).with_duration(duration)

        clips.append(background_clip)

        # Main photo clip
        base = ImageClip(
            np.array(foreground)
        ).with_duration(duration)

        clips.append(base)

        # Camera effects
        if effect == "Zoom In":

            animated = base.resized(
                lambda t: 1.0 + 0.12 * t / duration
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

        # Combine video and audio
        video = CompositeVideoClip(
            [background_clip, animated],
            size=(720, 1280)
        ).with_duration(duration)

        clips.append(video)

        final_video = video.with_audio(audio)
        clips.append(final_video)

        # Export MP4
        final_video.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            logger=None
        )

        if not os.path.isfile(output_path):
            raise RuntimeError("MP4 file was not created.")

        with open(output_path, "rb") as file:
            result = file.read()

        if not result:
            raise RuntimeError("Generated video is empty.")

        return result, duration

    finally:

        # Close clips
        seen = set()

        for clip in reversed(clips):
            if id(clip) not in seen:
                seen.add(id(clip))
                try:
                    clip.close()
                except Exception:
                    pass

        # Remove temporary files
        import shutil
        shutil.rmtree(temp_dir, ignore_errors=True)


# ---------------- GENERATE BUTTON ----------------

if st.button(
    "✨ GENERATE MY REEL",
    width="stretch"
):

    if photo is None or song is None:

        st.warning(
            "Please upload both Photo and Song."
        )

    else:

        try:

            with st.spinner(
                "Creating your cinematic reel..."
            ):

                video_bytes, actual_duration = make_reel(
                    photo.getvalue(),
                    song.getvalue()
                )

            st.success(
                f"Your Reel is ready! Duration: {actual_duration:.1f} seconds"
            )

            st.video(video_bytes)

            st.download_button(
                "⬇️ Download MP4 Reel",
                data=video_bytes,
                file_name="Assam_Reel_AI.mp4",
                mime="video/mp4",
                width="stretch"
            )

        except Exception as error:

            st.error("Reel generation failed.")

            st.code(
                traceback.format_exc(),
                language="text"
            )
