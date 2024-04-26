import streamlit as st
from vertexai.preview.generative_models import GenerativeModel, Part
from langchain_google_vertexai import HarmBlockThreshold, HarmCategory, VertexAI
from vertexai import generative_models
import base64
from PIL import Image
import io
from utils.utils import get_gcs_location_for_query, download_blob, image_requested
from dotenv import load_dotenv
import os

load_dotenv()


st.title("Multimodal citations chatbot")

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_NONE,
    generative_models.HarmCategory.HARM_CATEGORY_UNSPECIFIED: generative_models.HarmBlockThreshold.BLOCK_NONE,
}

model = GenerativeModel(
    "gemini-1.5-pro-preview-0409",
    system_instruction="""Answer questions based on the information in the provided document.
If the user requests a chart responds normally and end your response saying 'Here is the chart:' in a new line.
Do not print anything after that.""",
)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat()


# Display chat messages from history on app rerun
for message in st.session_state.messages:
    if message["role"] == "image":
        image_bytes = download_blob(message["content"])
        image = Image.open(io.BytesIO(image_bytes))
        st.image(image, width=800)
        continue
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Type a message"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)
    # Display assistant response in chat message container
    with st.chat_message("assistant"):
        with st.spinner("Processing"):
            # in first interaction add PDF doc as context
            if len(st.session_state.messages) < 2:
                pdf_file = Part.from_uri(
                    os.getenv("DOC_LOCATION"), mime_type="application/pdf"
                )
                contents = [pdf_file, prompt]
                response = st.session_state.chat.send_message(
                    contents, safety_settings=safety_settings
                )
            else:
                response = st.session_state.chat.send_message(
                    prompt, safety_settings=safety_settings
                )
            st.markdown(response.text)
        st.session_state.messages.append(
            {"role": "assistant", "content": response.text}
        )

    if image_requested(prompt):
        st.session_state.messages.append(
            {"role": "image", "content": get_gcs_location_for_query(prompt)}
        )
    st.rerun()
