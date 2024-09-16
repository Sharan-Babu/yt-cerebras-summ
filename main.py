import streamlit as st
import os
from youtube_transcript_api import YouTubeTranscriptApi
from cerebras.cloud.sdk import Cerebras

# Set up Cerebras API client
cerebras_api_key = st.secrets["cerebras_api_key"]
client = Cerebras(api_key=cerebras_api_key)

st.set_page_config(page_title="Yt Cerebras Summarizer",page_icon="▶️")


def get_youtube_id(url):
    """Extract YouTube video ID from URL"""
    if "youtu.be" in url:
        return url.split("/")[-1]
    elif "youtube.com" in url:
        return url.split("v=")[1].split("&")[0]
    else:
        return None

def get_transcript(video_id):
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        formatted_transcript = ""
        for entry in transcript:
            start_seconds = entry['start']
            minutes = int(start_seconds // 60)
            seconds = int(start_seconds % 60)
            formatted_transcript += f"[{minutes:02d}:{seconds:02d}] {entry['text']} "
        return formatted_transcript.strip()
    except Exception as e:
        st.error(f"Error fetching transcript: {str(e)}")
        return None

def summarize_text(text):
    """Summarize text using Cerebras API"""
    prompt = f"""Summarize the following YouTube video transcript. Provide a concise summary, followed by key chapters along with start timestamps. The transcript includes timestamps for each text chunk.

Transcript:
{text}

Summary:
"""

    try:
        response = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3.1-70b",
            max_tokens=2000,
            temperature=0
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Error in summarization: {str(e)}")
        return None

# Streamlit UI
st.title("YouTube Video Summarizer")

url = st.text_input("Enter YouTube Video URL:")
submit_button = st.button("Summarize")

if submit_button and url:
    video_id = get_youtube_id(url)
    if video_id:
        # Embed YouTube video
        st.header("Video")
        st.video(f"https://www.youtube.com/watch?v={video_id}")
        
        transcript = get_transcript(video_id)[:28000]
        #st.write(transcript)
        if transcript:
            with st.spinner("Summarizing video..."):
                summary = summarize_text(transcript)
                if summary:
                    st.subheader("Summary and Key Chapters:")
                    st.write(summary)
        else:
            st.warning("Couldn't fetch the transcript. Please try another video.")
    else:
        st.warning("Invalid YouTube URL. Please enter a valid URL.")