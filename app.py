
import streamlit as st

st.set_page_config(
    page_title="Assam Reel AI",
    page_icon="🎵",
    layout="centered"
)

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #130d29, #30204c);
    color: white;
}
h1 {
    color: #f0abfc;
    text-align: center;
}
</style>
""", unsafe_allow_html=True)

st.title("🎵 Assam Reel AI")
st.write("আপোনাৰ Photo, আপোনাৰ গান, আপোনাৰ Reel")

st.divider()

st.header("✨ Create Your Reel")

photo = st.file_uploader(
    "1. Upload Your Photo",
    type=["jpg", "jpeg", "png"]
)

song = st.file_uploader(
    "2. Upload Assamese Song",
    type=["mp3", "wav", "m4a"]
)

duration = st.selectbox(
    "3. Select Reel Duration",
    ["30 Seconds", "1 Minute"]
)

st.write("Video Format: 9:16 Vertical")

if photo:
    st.image(photo, caption="Your Photo", use_container_width=True)

if song:
    st.audio(song)

if st.button("✨ GENERATE MY REEL", use_container_width=True):
    if photo is None or song is None:
        st.warning("Please upload your photo and song first.")
    else:
        st.success("Photo and song uploaded successfully!")
        st.info("AI video generation will be connected in the next step.")
