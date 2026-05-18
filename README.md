# MinuteMind AI

MinuteMind AI converts meeting audio into smart notes and summaries using Whisper, LangChain, and Groq LLM.

## Setup Instructions

1.  **Clone or create the project.**
2.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configure API Key:**
    *   Open the `.env` file.
    *   Replace `your_api_key_here` with your actual Groq API key.
4.  **Run the application:**
    ```bash
    streamlit run app.py
    ```
5.  **Use the app:**
    *   Upload a `.mp3` or `.wav` file.
    *   Click "Process Audio".
    *   View the summary, key points, action items, and MoM.
    *   Download the PDF report.
