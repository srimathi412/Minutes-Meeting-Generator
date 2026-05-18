import os
import tempfile
import time
import re
# pyrefly: ignore [missing-import]
from groq import Groq, RateLimitError
from dotenv import load_dotenv
# pyrefly: ignore [missing-import]
from pydub import AudioSegment

# System FFmpeg is expected to be available

env_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env')
load_dotenv(dotenv_path=env_path, override=True)

class FFmpegMissingException(Exception):
    """Exception raised when FFmpeg is missing from the system."""
    pass

def split_audio(audio_path):
    """Splits audio into 5-minute chunks if duration > 10 minutes OR file size > 20MB."""
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at path: {audio_path}")
        
    file_size = os.path.getsize(audio_path)
    size_limit = 20 * 1024 * 1024 # 20MB limit
    
    try:
        # pyrefly: ignore [missing-import]
        from pydub.utils import which
        if not which("ffmpeg") and not which("ffmpeg.exe"):
            raise FFmpegMissingException("FFmpeg is not available. Please install FFmpeg.")
    except Exception:
        raise FFmpegMissingException("FFmpeg is not available. Please install FFmpeg.")
        
    try:
        audio = AudioSegment.from_file(audio_path)
    except Exception as e:
        raise Exception(f"Failed to read audio file: {str(e)}")
            
    duration_ms = len(audio)
    duration_mins = duration_ms / (1000 * 60)
    
    if duration_mins > 10 or file_size > size_limit:
        chunk_length_ms = 5 * 60 * 1000 # 5 minutes in milliseconds
        chunks = [audio[i:i + chunk_length_ms] for i in range(0, duration_ms, chunk_length_ms)]
        
        chunk_paths = []
        for idx, chunk in enumerate(chunks):
            # Downsample chunk to mono, 16kHz for optimization
            optimized_chunk = chunk.set_frame_rate(16000).set_channels(1)
            
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_chunk_file:
                tmp_chunk_path = tmp_chunk_file.name
                
            optimized_chunk.export(tmp_chunk_path, format="wav")
            chunk_paths.append(tmp_chunk_path)
            
        return chunk_paths, True
    else:
        return [audio_path], False

def transcribe_audio(audio_file_path, progress_callback=None):
    """Transcribes audio using Groq's Whisper API.
    Supports comma-separated GROQ_API_KEYS for automatic key rotation to bypass rate limits.
    """
    # pyrefly: ignore [missing-import]
    import streamlit as st
    api_key_str = os.getenv("GROQ_API_KEY")

    if not api_key_str:
        try:
            api_key_str = st.secrets["GROQ_API_KEY"]
        except Exception:
            api_key_str = None

    if not api_key_str:
        raise ValueError(
            "Groq API Key not configured."
        )

    api_keys = [
        k.strip()
        for k in api_key_str.split(",")
        if k.strip()
    ]
        
    if progress_callback:
        progress_callback("Splitting audio...", 0, 0)
        
    chunk_paths, is_temp = split_audio(audio_file_path)
    total_chunks = len(chunk_paths)
    
    transcripts = []
    current_key_idx = 0
    
    try:
        for idx, chunk_path in enumerate(chunk_paths):
            if progress_callback:
                progress_callback(f"Processing chunk {idx + 1} of {total_chunks}...", idx + 1, total_chunks)
                
            chunk_text = None
            attempts_with_keys = 0
            
            while chunk_text is None:
                current_api_key = api_keys[current_key_idx]
                client = Groq(api_key=current_api_key)
                
                try:
                    chunk_text = _transcribe_file_directly(client, chunk_path)
                except RateLimitError as e:
                    # Swapping to next key if multiple keys are provided
                    if len(api_keys) > 1 and attempts_with_keys < len(api_keys) - 1:
                        current_key_idx = (current_key_idx + 1) % len(api_keys)
                        attempts_with_keys += 1
                        if progress_callback:
                            progress_callback(
                                f"🔄 Rate limit hit! Swapping to API key {current_key_idx + 1} immediately...",
                                idx + 1,
                                total_chunks
                            )
                        time.sleep(1) # Small pause before trying next key
                        continue
                    else:
                        # Fallback countdown if all keys are exhausted or only 1 key exists
                        err_msg = str(e)
                        wait_seconds = 10.0
                        min_match = re.search(r'(\d+)\s*m', err_msg)
                        sec_match = re.search(r'(\d+(\.\d+)?)\s*s', err_msg)
                        
                        if min_match and sec_match:
                            wait_seconds = int(min_match.group(1)) * 60 + float(sec_match.group(1))
                        elif sec_match:
                            wait_seconds = float(sec_match.group(1))
                            
                        wait_seconds = min(wait_seconds + 2.0, 180.0)
                        
                        if progress_callback:
                            for remaining in range(int(wait_seconds), 0, -1):
                                progress_callback(
                                    f"⚠️ Rate Limit Reached! Resuming in {remaining}s (Chunk {idx + 1} of {total_chunks})",
                                    idx + 1,
                                    total_chunks
                                )
                                time.sleep(1)
                        else:
                            time.sleep(wait_seconds)
                        attempts_with_keys = 0 # Reset attempts after wait
            
            if is_temp:
                start_min = idx * 5
                end_min = start_min + 5
                if idx == total_chunks - 1:
                    try:
                        audio = AudioSegment.from_file(audio_file_path)
                        end_min = len(audio) / (1000 * 60)
                    except Exception:
                        pass
                timestamp_str = f"[{int(start_min):02d}:00 - {int(end_min):02d}:{int((end_min % 1)*60):02d}]"
                transcripts.append(f"{timestamp_str}\n{chunk_text}\n")
            else:
                transcripts.append(chunk_text)
                
        if progress_callback:
            progress_callback("Combining transcript...", total_chunks, total_chunks)
            
        return "\n".join(transcripts)
        
    finally:
        if is_temp:
            for path in chunk_paths:
                if os.path.exists(path):
                    try:
                        os.remove(path)
                    except Exception:
                        pass

def _transcribe_file_directly_with_retry(client, file_path, progress_callback=None, current_chunk=0, total_chunks=0):
    """Transcribes a single audio file, automatically retrying with a countdown if rate limited."""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            return _transcribe_file_directly(client, file_path)
        except RateLimitError as e:
            err_msg = str(e)
            # Default pause time in case parsing fails
            wait_seconds = 10.0
            
            # Match minute and second structures (e.g. "2m9.5s" or "45s")
            min_match = re.search(r'(\d+)\s*m', err_msg)
            sec_match = re.search(r'(\d+(\.\d+)?)\s*s', err_msg)
            
            if min_match and sec_match:
                wait_seconds = int(min_match.group(1)) * 60 + float(sec_match.group(1))
            elif sec_match:
                wait_seconds = float(sec_match.group(1))
                
            # Add small padding buffer (e.g., 2 seconds) and limit maximum sleep
            wait_seconds = min(wait_seconds + 2.0, 180.0)
            
            if attempt < max_retries - 1:
                if progress_callback:
                    # Provide a live countdown inside the Streamlit status message
                    for remaining in range(int(wait_seconds), 0, -1):
                        progress_callback(
                            f"⚠️ Rate Limit Reached! Respecting Groq API limit... Resuming in {remaining}s (Chunk {current_chunk} of {total_chunks})",
                            current_chunk,
                            total_chunks
                        )
                        time.sleep(1)
                else:
                    time.sleep(wait_seconds)
            else:
                # Re-raise error if all retries are exhausted
                raise e

def _transcribe_file_directly(client, file_path):
    """Transcribes a single audio file directly using Groq's Whisper API."""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Audio file not found: {file_path}")
        
    with open(file_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
          file=(os.path.basename(file_path), file.read()),
          model="whisper-large-v3",
          response_format="text",
          language="en"
        )
    return transcription
