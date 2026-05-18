# pyrefly: ignore [missing-import]
import streamlit as st
import os
from dotenv import load_dotenv

from utils import save_uploaded_file, delete_temp_file
from speech_module import transcribe_audio, FFmpegMissingException
from llm_processor import process_transcript, parse_llm_output
from pdf_generator import generate_pdf

# Load environment variables (override allows dynamic hot-swapping of .env variables)
load_dotenv(override=True)

st.set_page_config(page_title="MinuteMind AI", page_icon="🎙️", layout="wide")

# Custom CSS for Premium UI
CSS_STYLE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&display=swap');

/* Font application globally */
html, body, [class*="css"], .stText, .stMarkdown, .stButton, .stTextInput, .stAudio, label {
    font-family: 'Outfit', sans-serif !important;
}

/* Main title styling */
.title-gradient {
    background: linear-gradient(135deg, #7F00FF 0%, #E100FF 50%, #00F2FE 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 3.5rem !important;
    font-weight: 800 !important;
    letter-spacing: -2px;
    margin-bottom: 0.1rem !important;
    text-align: center;
    animation: fadeIn 1s ease-in-out;
}

.subtitle-desc {
    color: #a0aec0 !important;
    font-size: 1.3rem !important;
    font-weight: 400 !important;
    margin-bottom: 2.5rem !important;
    text-align: center;
    letter-spacing: -0.2px;
    animation: fadeIn 1.2s ease-in-out;
}

/* Streamlit Container / Glassmorphism Cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: rgba(255, 255, 255, 0.02) !important;
    backdrop-filter: blur(20px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
    border: 1px solid rgba(255, 255, 255, 0.06) !important;
    border-radius: 20px !important;
    padding: 26px !important;
    box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.4) !important;
    margin-bottom: 24px !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    animation: slideUp 0.8s ease-out;
}

div[data-testid="stVerticalBlockBorderWrapper"]:hover {
    transform: translateY(-6px) !important;
    border-color: rgba(0, 242, 254, 0.35) !important;
    box-shadow: 0 16px 48px 0 rgba(0, 242, 254, 0.15) !important;
}

/* Card Header Stylings */
.card-header {
    font-size: 1.45rem !important;
    font-weight: 700 !important;
    margin-bottom: 18px !important;
    border-bottom: 1px solid rgba(255, 255, 255, 0.07) !important;
    padding-bottom: 10px !important;
    display: flex;
    align-items: center;
    gap: 10px;
}

.card-header-summary { color: #E100FF !important; }
.card-header-points { color: #00F2FE !important; }
.card-header-actions { color: #00FF87 !important; }
.card-header-mom { color: #FFB800 !important; }

/* Custom styled status indicators */
.status-indicator {
    background: rgba(0, 242, 254, 0.04) !important;
    border: 1px solid rgba(0, 242, 254, 0.15) !important;
    border-radius: 16px !important;
    padding: 18px !important;
    font-weight: 500 !important;
    color: #00f2fe !important;
    display: flex;
    align-items: center;
    gap: 14px;
    margin-bottom: 24px !important;
    animation: fadeIn 0.5s ease-out;
}

/* Dynamic Buttons */
div.stButton > button, div.stDownloadButton > button {
    background: linear-gradient(135deg, #7F00FF 0%, #E100FF 100%) !important;
    border: none !important;
    color: white !important;
    border-radius: 14px !important;
    padding: 14px 32px !important;
    font-size: 1.05rem !important;
    font-weight: 600 !important;
    box-shadow: 0 4px 20px rgba(225, 0, 255, 0.25) !important;
    transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1) !important;
    width: 100% !important;
}

div.stButton > button:hover, div.stDownloadButton > button:hover {
    transform: translateY(-2px) scale(1.01) !important;
    box-shadow: 0 8px 25px rgba(0, 242, 254, 0.4) !important;
    background: linear-gradient(135deg, #00F2FE 0%, #4FACFE 100%) !important;
    color: #121212 !important;
}

/* Styling alert boxes */
div[data-testid="stAlert"] {
    background: rgba(0, 242, 254, 0.05) !important;
    border: 1px solid rgba(0, 242, 254, 0.15) !important;
    border-radius: 16px !important;
    color: #00f2fe !important;
}

/* Keyframes */
@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes slideUp {
    from {
        opacity: 0;
        transform: translateY(30px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* Hide default streamlit layout structures */
#MainMenu {visibility: hidden;}
header {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""

# Inject Premium CSS Styles
st.markdown(CSS_STYLE, unsafe_allow_html=True)

# Custom Premium Header
st.markdown('<div class="title-gradient">🎙&nbsp; MinuteMind AI</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle-desc">Transform your meeting audio into high-fidelity notes and summaries instantly</div>', unsafe_allow_html=True)

# Check for API Key
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    try:
        api_key = st.secrets["GROQ_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("Please configure your Groq API Key in the `.env` file or Streamlit Secrets to continue.")
    st.stop()

uploaded_file = st.file_uploader("", type=['mp3', 'wav'])

if uploaded_file is not None:
    st.audio(uploaded_file)
    
    if st.button("Process Audio"):
        # Check for unsupported file types
        file_ext = os.path.splitext(uploaded_file.name)[1].lower()
        if file_ext not in ['.mp3', '.wav']:
            st.error("❌ Unsupported file type! Please upload only .mp3 or .wav files.")
            st.stop()
            
        progress_container = st.empty()
        
        # Step 1: Uploading...
        progress_container.markdown("""
            <div class="status-indicator">
                <span style="font-size: 1.5rem; animation: spin 2s linear infinite; display: inline-block;">⏳</span>
                <span>Uploading...</span>
            </div>
            <style>
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            </style>
        """, unsafe_allow_html=True)
        
        tmp_file_path = save_uploaded_file(uploaded_file)
            
        if tmp_file_path:
            try:
                # Progress callback to show splitting, transcribing, and combining
                def progress_cb(message, current, total):
                    progress_container.markdown(f"""
                        <div class="status-indicator">
                            <span style="font-size: 1.5rem; animation: spin 2s linear infinite; display: inline-block;">⏳</span>
                            <span>{message}</span>
                        </div>
                        <style>
                        @keyframes spin {{
                            0% {{ transform: rotate(0deg); }}
                            100% {{ transform: rotate(360deg); }}
                        }}
                        </style>
                    """, unsafe_allow_html=True)
                
                # Step 2: Speech to Text (splits, transcribes chunks in loop, combines)
                transcript = transcribe_audio(tmp_file_path, progress_callback=progress_cb)
                
                with st.expander("📝 View Full Transcript", expanded=False):
                    st.write(transcript)
                    
                # Step 3: Generating summary...
                progress_container.markdown("""
                    <div class="status-indicator">
                        <span style="font-size: 1.5rem; animation: spin 2s linear infinite; display: inline-block;">⏳</span>
                        <span>Generating summary...</span>
                    </div>
                """, unsafe_allow_html=True)
                
                llm_output = process_transcript(transcript)
                sections = parse_llm_output(llm_output)
                
                # Clear the progress display
                progress_container.empty()
                
                # Display Results
                st.success("✨ Processing complete! Here is your custom meeting summary:")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    with st.container(border=True):
                        st.markdown('<div class="card-header card-header-summary">📝 Meeting Summary</div>', unsafe_allow_html=True)
                        st.markdown(sections.get('summary', 'No summary generated.'))
                    
                    with st.container(border=True):
                        st.markdown('<div class="card-header card-header-points">💡 Key Discussion Points</div>', unsafe_allow_html=True)
                        st.markdown(sections.get('key_points', 'No key points generated.'))
                    
                with col2:
                    with st.container(border=True):
                        st.markdown('<div class="card-header card-header-actions">✅ Action Items</div>', unsafe_allow_html=True)
                        st.markdown(sections.get('action_items', 'No action items generated.'))
                    
                    with st.container(border=True):
                        st.markdown('<div class="card-header card-header-mom">📋 Minutes of Meeting</div>', unsafe_allow_html=True)
                        st.markdown(sections.get('mom', 'No MoM generated.'))
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # 4. Generate PDF
                pdf_path = generate_pdf(transcript, sections)
                
                with open(pdf_path, "rb") as pdf_file:
                    st.download_button(
                        label="📄 Download Meeting Report (PDF)",
                        data=pdf_file,
                        file_name="MinuteMind_Meeting_Report.pdf",
                        mime="application/pdf"
                    )
                    
            except FFmpegMissingException as e:
                progress_container.empty()
                st.error("⚠️ FFmpeg Missing!")
                st.markdown(
                    """
                    **MinuteMind AI requires FFmpeg to process and split large audio files.**
                    
                    Please install FFmpeg to resolve this:
                    
                    ### 💻 For Windows (Easiest Method):
                    1. Open your terminal or Command Prompt as Administrator and run:
                       ```powershell
                       winget install Gyan.FFmpeg
                       ```
                    2. **Restart** your terminal/editor/server so Python can detect the new system path.
                    
                    ---
                    *Note: For audio files under 20MB and under 10 minutes, the app will transcribe them directly without requiring FFmpeg.*
                    """
                )
            except FileNotFoundError as e:
                progress_container.empty()
                st.error(f"📁 File Not Found Error: The temporary audio file could not be accessed. Detail: {str(e)}")
            except ConnectionError as e:
                progress_container.empty()
                st.error(f"🌐 Connection Error: Failed to connect to Groq API. Please check your internet connection. Detail: {str(e)}")
            except TimeoutError as e:
                progress_container.empty()
                st.error(f"⏱️ Timeout Error: The request to Groq API timed out. Please try again. Detail: {str(e)}")
            except ValueError as e:
                progress_container.empty()
                st.error(f"❌ Value Error: {str(e)}")
            except Exception as e:
                progress_container.empty()
                if "rate_limit" in str(e).lower() or "429" in str(e):
                    st.error("⏳ Groq API Rate Limit Reached!")
                    st.markdown(
                        f"""
                        **You have reached Groq's hourly limit for transcription audio.**
                        
                        * **Details:** {str(e)}
                        * **What to do:** Groq's free tier has a limit of 120 minutes of audio per hour. Please wait a few minutes and try again!
                        """
                    )
                else:
                    st.error(f"An unexpected error occurred: {str(e)}")
            finally:
                # Clean up temp file
                delete_temp_file(tmp_file_path)
        else:
            st.error("Failed to save uploaded file.")
