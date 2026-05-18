# MinuteMind AI
MinuteMind AI is an innovative system designed to transform meeting audio into valuable, actionable insights. By leveraging the power of Whisper for audio transcription, LangChain for intelligent processing, and Groq LLM for advanced natural language understanding, this platform generates comprehensive meeting summaries, key discussion points, action items, and minutes of meeting (MoM).

## Project Overview
The primary goal of MinuteMind AI is to streamline the process of meeting note-taking and summary generation. By automating these tasks, the system saves time and enhances productivity for meeting participants and organizers alike. The system's core functionality revolves around uploading meeting audio files, which are then processed to extract meaningful information.

## Problem Statement & Goals
In many professional settings, meetings are a crucial component of collaboration and decision-making. However, manually taking notes during meetings can be time-consuming and often leads to incomplete or inaccurate records. The main problem addressed by MinuteMind AI is the need for an efficient, reliable method to capture and summarize meeting discussions. The system aims to provide a user-friendly interface for uploading audio files and generating detailed, structured summaries.

## Domain Concept Explanation
The core domain concept in MinuteMind AI is the transformation of unstructured meeting audio into structured, actionable data. This involves several key steps:
- **Audio Transcription**: The process of converting spoken words in audio files into text.
- **Natural Language Processing (NLP)**: Analyzing the transcribed text to identify key points, actions, and summaries.
- **Large Language Model (LLM) Integration**: Utilizing advanced LLMs like Groq to enhance the accuracy and relevance of the generated summaries and insights.

## Solution Approach
MinuteMind AI solves the problem of manual meeting note-taking by providing an automated, AI-driven solution. The system's approach involves:
1. **Audio Upload**: Users upload their meeting audio files through a Streamlit-based interface.
2. **Transcription and Processing**: The uploaded audio is transcribed using Whisper, and the transcript is then processed using LangChain and Groq LLM to generate summaries, key points, and action items.
3. **PDF Generation**: A custom PDF generator creates a detailed meeting report, including the transcript, summary, key points, action items, and MoM.

## Technical Architecture
```markdown
+---------------+
|  Frontend   |
+---------------+
           |
           |
           v
+---------------+
|  Streamlit  |
|  (App.py)     |
+---------------+
           |
           |
           v
+---------------+
|  Business    |
|  Logic (LLM  |
|  Processor)  |
+---------------+
           |
           |
           v
+---------------+
|  LLM (Groq)   |
|  Integration  |
+---------------+
           |
           |
           v
+---------------+
|  PDF Generator|
|  (FPDF)       |
+---------------+
           |
           |
           v
+---------------+
|  Database     |
|  (Temp Files)  |
+---------------+
```
The system's architecture is designed to be modular, with each component serving a specific purpose:
- **Frontend**: Handles user interaction, including audio file uploads and display of generated summaries.
- **Streamlit (App.py)**: Acts as the backend for the frontend, managing the workflow and interactions between different components.
- **Business Logic (LLM Processor)**: Responsible for processing the audio transcript using LangChain and Groq LLM.
- **LLM (Groq) Integration**: Provides the advanced NLP capabilities for generating summaries and insights.
- **PDF Generator (FPDF)**: Creates detailed meeting reports based on the generated summaries and transcripts.
- **Database (Temp Files)**: Temporarily stores uploaded audio files and generated reports.

## Key Components & Implementation Details
- **app.py**: The main application file, responsible for handling user interactions, audio uploads, and the display of generated summaries.
- **llm_processor.py**: Contains the business logic for processing audio transcripts using LangChain and Groq LLM.
- **pdf_generator.py**: Defines the functionality for generating PDF meeting reports.
- **speech_module.py**: Handles audio transcription using Whisper and provides functionality for splitting large audio files into manageable chunks.
- **utils.py**: Offers utility functions for saving uploaded files and deleting temporary files.

## System Logic / Analytics Insights
The system's logic revolves around the following workflow:
1. **Audio Upload**: The user uploads a meeting audio file.
2. **Transcription**: The audio file is transcribed using Whisper.
3. **LLM Processing**: The transcript is processed using LangChain and Groq LLM to generate summaries, key points, and action items.
4. **PDF Generation**: A PDF meeting report is generated based on the processed transcript and summaries.
5. **Report Display**: The user can view and download the generated PDF report.

## Usage / Workflow
To use MinuteMind AI, follow these steps:
1. Upload your meeting audio file through the Streamlit interface.
2. Click the "Process Audio" button to initiate transcription and LLM processing.
3. View the generated summaries, key points, and action items.
4. Download the detailed PDF meeting report.

## Folder Structure
```markdown
MinuteMindAI/
├── app.py
├── llm_processor.py
├── pdf_generator.py
├── speech_module.py
├── utils.py
├── requirements.txt
├── meeting_report.pdf
├── __pycache__
└── .env
```
The repository is structured to keep related components together, with the main application logic in `app.py` and supporting modules in separate files.

## Installation & Setup
To install and set up MinuteMind AI, run the following commands:
```bash
pip install -r requirements.txt
streamlit run app.py
```
Ensure you have the necessary dependencies installed, including Streamlit, OpenAI Whisper, LangChain, and Groq LLM. Also, configure your Groq API key in the `.env` file.

## Real-World Applications
MinuteMind AI can be applied in various professional settings where meetings are frequent, such as:
- Corporate meetings for decision-making and project updates.
- Academic meetings for research discussions and collaboration.
- Government meetings for policy discussions and public hearings.

## Future Enhancements
To further enhance MinuteMind AI, consider the following improvements:
- **Multi-Language Support**: Integrate support for transcribing and processing audio files in multiple languages.
- **Customizable Summaries**: Allow users to customize the structure and content of generated summaries.
- **Integration with Calendar Apps**: Integrate MinuteMind AI with popular calendar apps to automatically generate meeting summaries.
