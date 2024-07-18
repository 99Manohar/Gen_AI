import streamlit as st
from dotenv import load_dotenv
import os
import google.generativeai as genai
from youtube_transcript_api import YouTubeTranscriptApi
from fpdf import FPDF

# Load environment variables
load_dotenv()

# Configure Google GenerativeAI
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Prompt for user input
prompt = """You are YouTube video summarizer and professional content writer. You will be taking the transcript text
and summarizing the entire video and providing the important summary in bullet points and some paragraphs
within your limit. Also use some bold fonts and add some tables for better representation generate some images if you have okay!. Please provide the summary of the text given here : """

# Function to extract transcript from YouTube video
def extract_transcript_details(youtube_video_url):
    try:
        video_id = youtube_video_url.split("=")[1]
        transcript_text = YouTubeTranscriptApi.get_transcript(video_id)
        transcript = " ".join([i["text"] for i in transcript_text])
        return transcript
    except Exception as e:
        st.error(f"Error extracting transcript: {str(e)}")
        return None

# Function to generate summary using Gemini Pro
def generate_gemini_content(transcript_text, prompt):
    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(prompt + transcript_text)
        return response.text
    except Exception as e:
        st.error(f"Error generating content: {str(e)}")
        return None

# Function to convert text to PDF
def text_to_pdf(text, pdf_filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    for line in text.split('\n'):
        pdf.multi_cell(0, 10, line)
    pdf.output(pdf_filename)

# Streamlit UI
st.title("YouTube Transcript to Detailed Notes Converter")
youtube_link = st.text_input("Enter YouTube Video Link:")

if youtube_link:
    video_id = youtube_link.split("=")[1]
    st.image(f"http://img.youtube.com/vi/{video_id}/0.jpg", use_column_width=True)

if st.button("Get Detailed Notes"):
    transcript_text = extract_transcript_details(youtube_link)

    if transcript_text:
        summary = generate_gemini_content(transcript_text, prompt)

        if summary:
            st.markdown("## Detailed Notes:")
            video_summary = summary
            st.write(video_summary)

            # Convert summary to PDF and allow download
            pdf_filename = "video_summary.pdf"
            text_to_pdf(video_summary, pdf_filename)
            with open(pdf_filename, "rb") as file:
                st.download_button(
                    label="Download Summary as PDF",
                    data=file,
                    file_name=pdf_filename,
                    mime="application/pdf"
                )
