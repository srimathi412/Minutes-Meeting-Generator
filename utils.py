import os
import tempfile

def save_uploaded_file(uploaded_file):
    """Saves a Streamlit UploadedFile to a temporary file and returns the path."""
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[1]) as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            return tmp_file.name
    except Exception as e:
        print(f"Error saving file: {e}")
        return None

def delete_temp_file(file_path):
    """Deletes a temporary file."""
    try:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
    except Exception as e:
        print(f"Error deleting file: {e}")
