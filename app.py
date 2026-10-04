import os
import streamlit as st
from google import genai

# Page setup with a clean layout
st.set_page_config(
    page_title="MeetAI - Meeting Notes Summarizer",
    page_icon="🎙️",
    layout="centered",
)

# Custom CSS to make the UI look modern and clean
st.markdown(
    """
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 8px;
        font-weight: bold;
        height: 45px;
    }
    .css-1r6slb0 {
        padding: 20px;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# Header Section
st.title("🎙️ MeetAI")
st.markdown(
    "Transform your meeting recordings and transcripts into structured, actionable"
    " summaries instantly using Gemini."
)
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
  st.header("⚙️ Settings")
  api_key = st.text_input("Gemini API Key", type="password")
  st.markdown("[Get a Free Gemini Key](https://aistudio.google.com/)")
  st.info(
      "🔒 Your key is secure and only used for your session-free of cost via"
      " Google AI Studio."
  )

# Tabs for input selection
tab1, tab2 = st.tabs(["📝 Paste Transcript", "🎧 Upload Audio Recording"])

input_content = None
content_type = None

with tab1:
  st.markdown("### Paste Meeting Notes")
  transcript_text = st.text_area(
      "Paste your text below:",
      height=180,
      placeholder=(
          "Speaker 1: Let's review our timeline...\nSpeaker 2: The database"
          " migration is complete."
      ),
  )
  if transcript_text:
    input_content = transcript_text
    content_type = "text"

with tab2:
  st.markdown("### Upload Audio File")
  audio_file = st.file_uploader(
      "Choose an audio file", type=["mp3", "wav", "m4a", "aac"]
  )
  if audio_file:
    st.audio(audio_file)  # Lets you play the audio right in the app!
    input_content = audio_file
    content_type = "audio"

st.markdown("---")

# Action Button
if st.button("✨ Generate MeetAI Summary", type="primary"):
  if not api_key:
    st.error("⚠️ Please enter your Gemini API Key in the sidebar first.")
  elif not input_content:
    st.warning(
        "⚠️ Please provide a text transcript or upload an audio file before"
        " generating."
    )
  else:
    try:
      client = genai.Client(api_key=api_key)

      with st.spinner("🤖 MeetAI is analyzing your meeting... Please wait."):
        prompt = (
            "You are an expert executive meeting assistant. Analyze the"
            " provided meeting content and generate a clean, well-formatted"
            " report containing:\n"
            "1. **Executive Summary**: A concise high-level overview.\n"
            "2. **Key Discussion Points**: Bullet points of main topics"
            " covered.\n"
            "3. **Action Items**: Specific tasks assigned with owners (if"
            " mentioned).\n"
            "4. **Next Steps**: Follow-up tasks or timelines."
        )

        if content_type == "text":
          response = client.models.generate_content(
              model="gemini-2.5-flash", contents=[prompt, input_content]
          )
        elif content_type == "audio":
          temp_path = f"temp_{audio_file.name}"
          with open(temp_path, "wb") as f:
            f.write(audio_file.getbuffer())

          with st.spinner("Uploading audio to Gemini..."):
            uploaded_file = client.files.upload(file=temp_path)

          response = client.models.generate_content(
              model="gemini-2.5-flash", contents=[uploaded_file, prompt]
          )

          if os.path.exists(temp_path):
            os.remove(temp_path)

        # Display Output inside a nice clean container
        st.success("🎉 Summary Generated Successfully!")
        st.markdown("### 📋 Meeting Insights")
        st.markdown(response.text)

    except Exception as e:
      st.error(f"❌ An error occurred: {e}")