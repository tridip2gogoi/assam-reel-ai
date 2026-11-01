import streamlit as st
import numpy as np
import tempfile
import os

from PIL import Image, ImageFilter
from moviepy import ImageClip, AudioFileClip, CompositeVideoClip

st.set_page_config(
    page_title="Assam Reel AI",
    page_icon="🎬",
    layout="centered"
)

st.title("🎬 Assam Reel AI")
st.caption("Create Your Cinematic Reel")

st.divider()

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

requested_duration = 30 if duration_option == "30 Seconds" else 60

effect = st.selectbox(
    "Cinematic Camera Effect",
    ["Zoom In", "Zoom Out", "Pan Left", "Pan Right"]
)

background = st.selectbox(
    "Background Style",
    ["Natural", "Blur Background", "Dreamy Background"]
)

mood = st.selectbox(
    "Reel Theme",
    ["Bihu", "Romantic", "Emotional", "Happy", "Kathak", "Cinematic"]
)

if photo:
    st.image(photo, caption="Your Photo", use_container_width=True)

if song:
    st.audio(song)

st.write("Video Format: 9:16 Vertical | 720 × 1280")

def make_reel(photo_bytes, song_bytes):

    temp_files = []
    audio = None
    video = None
    final = None

    try:
        image = Image.open(photo_bytes).convert("RGB")

        # Create vertical background
        bg = image.resize(
            (720, 1280),
            Image.Resampling.LANCZOS
        )

        if background == "Blur Background":
            bg = bg.filter(ImageFilter.GaussianBlur(28))

        elif background == "Dreamy Background":
            bg = bg.filter(ImageFilter.GaussianBlur(12))

        # Fit photo into vertical frame
        ratio = max(
            720 / image.width,
            1280 / image.height
        )

        new_size = (
            int(image.width * ratio),
            int(image.height * ratio)
        )

        foreground = image.resize(
            new_size,
            Image.Resampling.LANCZOS
        )

        left = (foreground.width - 720) // 2
        top = (foreground.height - 1280) // 2

        foreground = foreground.crop(
            (left, top, left + 720, top + 1280)
        )

        # Save temporary files
        bg_file = tempfile.NamedTemporaryFile(
            suffix=".jpg", delete=False
        )
        bg_path = bg_file.name
        bg_file.close()

        song_file = tempfile.NamedTemporaryFile(
            suffix=".mp3", delete=False
        )
        song_path = song_file.name
        song_file.close()

        output_file = tempfile.NamedTemporaryFile(
            suffix=".mp4", delete=False
        )
        output_path = output_file.name
        output_file.close()

        temp_files.extend([bg_path, song_path, output_path])

        bg.save(bg_path)

        with open(song_path, "wb") as f:
            f.write(song_bytes)

        # Read audio duration
        audio = AudioFileClip(str(song_path))

        duration = min(requested_duration, audio.duration)

        if duration <= 0:
            raise ValueError("The uploaded song has no usable audio.")

        audio = audio.subclipped(0, duration)

        # Create animated photo
        base = ImageClip(
            np.array(foreground)
        ).with_duration(duration)

        if effect == "Zoom In":
            animated = base.resized(
                lambda t: 1 + 0.12 * t / duration
            ).with_position("center")

        elif effect == "Zoom Out":
            animated = base.resized(
                lambda t: 1.12 - 0.12 * t / duration
            ).with_position("center")

        elif effect == "Pan Left":
            animated = base.with_position(
                lambda t: (-40 * t / duration, 0)
            )

        else:
            animated = base.with_position(
                lambda t: (40 * t / duration, 0)
            )

        background_clip = ImageClip(
            np.array(bg)
        ).with_duration(duration)

        video = CompositeVideoClip(
            [background_clip, animated],
            size=(720, 1280)
        )

        final = video.with_audio(audio)

        final.write_videofile(
            output_path,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            preset="ultrafast",
            logger=None
        )

        with open(output_path, "rb") as f:
            video_bytes = f.read()

        return video_bytes, duration

    finally:
        for clip in [final, video, audio]:
            if clip is not None:
                try:
                    clip.close()
                except Exception:
                    pass

        for path in temp_files:
            try:
                if os.path.exists(path):
                    os.remove(path)
            except OSError:
                pass


if st.button("✨ GENERATE MY REEL", use_container_width=True):

    if not photo or not song:
        st.warning("Please upload both Photo and Song.")

    else:
        try:
            with st.spinner("Creating your cinematic reel..."):

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
                use_container_width=True
            )

        except Exception as error:
            st.error("Reel generation failed.")
            st.code(str(error))
