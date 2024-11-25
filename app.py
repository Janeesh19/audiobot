import os
import streamlit as st
from langchain_groq import ChatGroq
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from google.cloud import texttospeech
import tempfile
import speech_recognition as sr

# Set up API keys and environment variables
GROQ_API_KEY = "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"
GOOGLE_APPLICATION_CREDENTIALS_CONTENT = """
{
  "type": "service_account",
  "project_id": "singular-arbor-423304-q9",
  "private_key_id": "56027426289130b0a408e25f05dfdf6396cafad0",
  "private_key": "-----BEGIN PRIVATE KEY-----\\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCixqPsIeSC3hQs\\nqY8y2oBMaeHeG+0Xxwvs2xXwF22nK5KhhgTuBhOZd28K181Wcj2HDQM0h/5t7eTI\\n9edN8/rSeNeylYpSlUmLywP3XcFQ132toz8mNOyWvVA4ZtccYzWMDLmMUmuyCvb9\\npvZVR4sB2R87T6Fvyc7DWCab1qzE3+TG5qYSRQTLwJQ1/X3IxJnyeEWJnJo8YWeA\\nGxH+wAszEZGPUsXAgUFQF3sGWqfTLW0bSv9XUCfuQONwve7fObCeeJ2o1kCFqqPB\\n0vmJDQHKgGNzlDYAWNOHHk+i/wja7q2ZAF518L142LRbH00h0pGEQLl/a5cw9P0k\\ntqol2iMPAgMBAAECggEAP/X+A5Ntz16kXshh1IG3WE9iyXv/thAox3FvNWB/Xejp\\nPT8EQONyYCNmJsSVkxpgwuiCEeo+N8P62lyF/0OXk4yYdTv9lmXC+INVk6XriHCk\\nmc5DyieRr8nD8+W1MRpquBVn85OPbe6RDyrEMM5j+N3wP8YSkXKjJG9G/IVmbhVL\\ngkatJTHI/W81YNFkj2TEHyOFZWRIVllyx1nksrBI6zDWCYEViKSMka7mmdauoR3D\\nX/MeZb2LxzCGdoLrS0EVGw+mVRn9qXxdF3T3kQw+ttsbbxqSVZAwN7oyID1K/Pmj\\n7JoaQPn8DM3xKcD0Ta8538/dkm64ZxF1aEshnYhMAQKBgQDYp04KHIdT9aPfuKB7\\niUemjBG1SGlT/KkhqWDlgTHSiHmj6JYqPai0rTcBWAUat2fpXtR/e5myYxgX2gnM\\nPWDeSC6Eze615LHmyoy0AcfipIz0QsTyOpyQ21M98MO3HNH23xtFJtBhfFRtXpKe\\nWCHtLqkTxvjsY8svWHu1ctwFwQKBgQDAVnLW2f8UpsqGXQH5uw+lBrt0QHfFOohi\\nx2lVUntCBB/UQjjrQqVw0a8qTg2S6oAKzBC4ZNvm0tnEmY2L3Zu9nl+2/Rkjr2zx\\nQdniiThmS3hNcurEXhXpC0g6Oy8y8VyQzxGlU7Jm5MwwzSFCkGUYS6JUf/DFJajD\\n6z2kDSh8zwKBgQCDbEHXumSRFsIYtTuMlMMFEZSwXkOecfb6929S6SMa7jSzrCRj\\nbVHIgAaM5yL5iOYc16yZxJWAc8IqvdYRse3wCONHJlC2wAr20Em37BifsGfcyCAG\\nPG27JYCCY2mly3LGiaJWOWxQpoXkbmkMarPx18sytxFK/GJFzywD7q/vQQKBgEp8\\nMBUMb0BsJ1pJgo5X5wMdzFKE9N0ogdDfMOed/aXfOwRUcP6K3M8IJTHY8GDI97U2\\nufLu/EoztanxXWOg+sNAJgkTkzzCnwn/WoXkZjcXWwuDSW+qkAmkGOCUMv8jgZmC\\n126TLy+xw3HSvuKsULpL8B2RPojawLS+0SxK/Db5AoGBAJymsdz6wtbdGbcXL27K\\nD9n4fDgSaCgkKnC3ZYprwDFPUzn2NsVAHq6bh54AS8ElBpCHvRXF6AVmPDmTokTB\\njsWVdrYXb9Vc2QxsVVbxgw2DdOLGO4XwIT8ANB85UwnQESrK924ZelxYDXzFEMaf\\nVAT3614X5OHFZW4un5l5KicO\\n-----END PRIVATE KEY-----\\n",
  "client_email": "tts-account@singular-arbor-423304-q9.iam.gserviceaccount.com",
  "client_id": "116350455014152767014",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/tts-account%40singular-arbor-423304-q9.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}
"""

# Write credentials to a temporary file
with tempfile.NamedTemporaryFile(delete=False, suffix=".json") as temp_cred_file:
    temp_cred_file.write(GOOGLE_APPLICATION_CREDENTIALS_CONTENT.encode())
    google_credentials_path = temp_cred_file.name

# Set the environment variable for Google credentials
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = google_credentials_path

# Initialize components
tts_client = texttospeech.TextToSpeechClient()
llm = ChatGroq(api_key=GROQ_API_KEY,temperature=0, model_name="mixtral-8x7b-32768")

# Load document content for context
document_content = """
Hyundai Creta is a premium SUV with cutting-edge technology, exceptional performance, and an attractive design. 
It comes with features like a panoramic sunroof, ventilated seats, and multiple driving modes. Powered by a choice of petrol and diesel engines, the Creta offers a balance of performance and efficiency.
"""

# Define prompt template
combined_prompt = f"""
Act as an expert telephone sales agent for Hyundai, focusing on selling the Hyundai Creta. Engage with potential customers professionally and effectively. Base all responses on the provided context. Follow these guidelines:

Greeting: Start with a brief, friendly introduction.
Response Style:
    For regular questions: Provide crisp, concise answers. Aim for responses under 25 words.
    For technical questions: Offer more detailed explanations. Limit responses to 2-3 sentences for moderately technical queries, and up to 5 sentences for highly technical questions.

Key Principles:
    Listen actively to identify customer needs.
    Match Creta features to customer requirements.
    Highlight Creta's value proposition succinctly.
    Address objections briefly but effectively.
    Guide interested customers to next steps concisely.

Technical Knowledge: For engine specifications, performance metrics, or advanced features, provide accurate, detailed information. Use layman's terms to explain complex features unless the customer demonstrates technical expertise.

Tone: Maintain a friendly, professional tone. Adjust to the customer's communication style.
Uncertainty Handling: If unsure about a specific detail, briefly acknowledge the need to verify the information.

Always focus exclusively on the Hyundai Creta. Prioritize being helpful, honest, and customer-oriented.

Context:
{document_content}
Question: {{question}}
Helpful Answer:"""

PROMPT = PromptTemplate(input_variables=["question"], template=combined_prompt)
llm_chain = LLMChain(llm=llm, prompt=PROMPT)

# Initialize chat history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Function to generate LLM response
def generate_response(prompt: str) -> str:
    response = llm_chain.run(question=prompt)
    return response

# Function for Text-to-Speech streaming
def text_to_speech_stream(text: str):
    chunks = text.split('. ')
    for chunk in chunks:
        if not chunk.strip():
            continue

        synthesis_input = texttospeech.SynthesisInput(text=chunk + '.')
        voice = texttospeech.VoiceSelectionParams(
            language_code="en-IN",
            ssml_gender=texttospeech.SsmlVoiceGender.NEUTRAL
        )
        audio_config = texttospeech.AudioConfig(audio_encoding=texttospeech.AudioEncoding.MP3)
        response = tts_client.synthesize_speech(
            input=synthesis_input, voice=voice, audio_config=audio_config
        )
        yield response.audio_content

# Function to save audio chunks to a temporary file for playback
def save_audio_to_file(audio_stream, suffix=".mp3"):
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_audio_file:
        for chunk in audio_stream:
            temp_audio_file.write(chunk)
        return temp_audio_file.name  # Return the file path

# Function for speech-to-text
def speech_to_text(audio_file_path):
    recognizer = sr.Recognizer()
    try:
        with sr.AudioFile(audio_file_path) as source:
            audio = recognizer.record(source)
            text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        return "Sorry, I could not understand the audio."
    except sr.RequestError:
        return "Error: Speech recognition service is unavailable."

# Streamlit interface
st.title("Hyundai Creta Sales Audiobot")
st.write("Record your audio query to interact with the bot!")

# Audio Recording
recorded_audio = st.audio_input("Record your voice message")

# Handle Audio Input
if recorded_audio:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_audio_file:
        temp_audio_file.write(recorded_audio.read())
        audio_file_path = temp_audio_file.name

    # Process audio
    with st.spinner("Processing your audio..."):
        user_query = speech_to_text(audio_file_path)

    if user_query:
        # Add user query to chat history
        st.session_state.chat_history.append({"role": "user", "content": user_query})

        # Generate bot response
        with st.spinner("Generating response..."):
            response = generate_response(user_query)
            audio_stream = text_to_speech_stream(response)

            # Save bot response audio
            bot_audio_path = save_audio_to_file(audio_stream)
            st.session_state.chat_history.append({"role": "bot", "content": response, "audio": bot_audio_path})

# Display chat history with bot's audio
st.write("### Chat History")
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.write(f"**You:** {message['content']}")
    else:
        st.write(f"**Bot:** {message['content']}")
        if message.get("audio"):
            with open(message["audio"], "rb") as audio_file:
                st.audio(audio_file.read(), format="audio/mp3")
