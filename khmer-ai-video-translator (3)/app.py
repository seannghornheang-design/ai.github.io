import os
import streamlit as st
from translator import translate_video

st.set_page_config(page_title="Khmer AI Video Translator", page_icon="🇰🇭", layout="wide")
st.markdown("""
<style>
.stApp {background:#101827;color:#f5f7fb}
h1 {color:#28d6a0;text-align:center}
.subtitle {text-align:center;color:#b8c4d6}
.stButton>button {background:#16a36a;color:white;border-radius:10px;width:100%;height:48px}
</style>
""", unsafe_allow_html=True)

st.title("🇰🇭 Khmer AI Video Translator")
st.markdown('<p class="subtitle">បកប្រែសំឡេងវីដេអូ និងបង្កើត Subtitle ជាភាសាខ្មែរ</p>', unsafe_allow_html=True)
st.info("សូមប្រើតែវីដេអូដែលអ្នកមានសិទ្ធិប្រើប្រាស់។")

with st.sidebar:
    st.header("ការកំណត់សំឡេង")
    voice_mode = st.selectbox("សំឡេងអ្នកនិយាយ", ["ប្រុស → សំឡេងប្រុសខ្មែរ", "ស្រី → សំឡេងស្រីខ្មែរ"])
    burn_subtitles = st.checkbox("បញ្ចូល Subtitle ខ្មែរក្នុងវីដេអូ", value=True)

st.subheader("1. Upload វីដេអូ")
uploaded = st.file_uploader("ជ្រើសរើសវីដេអូ", type=["mp4","mov","mkv","webm"])
st.caption("កំណែដំបូងនេះប្រើ Upload វីដេអូ។ YouTube URL និងការសម្គាល់អ្នកនិយាយច្រើននាក់នឹងត្រូវបន្ថែមក្នុងជំហានបន្ទាប់។")

if st.button("🚀 បកប្រែជាភាសាខ្មែរ"):
    if uploaded is None:
        st.error("សូម Upload វីដេអូជាមុនសិន។")
    else:
        needed = ["OPENAI_API_KEY", "AZURE_SPEECH_KEY", "AZURE_SPEECH_REGION"]
        missing = [k for k in needed if not (st.secrets.get(k) or os.getenv(k))]
        if missing:
            st.error("សូមបញ្ចូល API credentials ក្នុង Streamlit Secrets: " + ", ".join(missing))
        else:
            try:
                voice = "km-KH-PisethNeural" if voice_mode.startswith("ប្រុស") else "km-KH-SreymomNeural"
                with st.spinner("កំពុងស្គាល់សំឡេង បកប្រែ និងបង្កើតសំឡេងខ្មែរ..."):
                    result = translate_video(uploaded.getvalue(), uploaded.name, voice, burn_subtitles)
                st.success("បកប្រែរួចរាល់!")
                st.video(result["video_path"])
                with open(result["video_path"], "rb") as f:
                    st.download_button("⬇️ Download វីដេអូ MP4", f, "khmer_translated.mp4", "video/mp4")
                with open(result["srt_path"], "rb") as f:
                    st.download_button("⬇️ Download Subtitle SRT", f, "khmer_subtitles.srt", "application/x-subrip")
            except Exception as e:
                st.error(f"មានបញ្ហា៖ {e}")
st.divider()
st.caption("Khmer AI Video Translator — MVP")
