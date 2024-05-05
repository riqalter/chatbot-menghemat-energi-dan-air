import os
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

# genai.configure(api_key=os.getenv('GOOGLE_GEMINI_KEY')) lupa bjir klo di deploy ke streamlit

api_key = os.getenv('GOOGLE_GEMINI_KEY')

if api_key:
    genai.configure(api_key=api_key)
else:
    if "api_key" in st.secrets:
        genai.configure(api_key=st.secrets["api_key"])
    else:
        st.error("API Key belum diatur. Silahkan atur API Key di file .env atau Secrets di Streamlit Sharing.")


generation_config = {
  "temperature": 1,
  "top_p": 0.95,
  "top_k": 0,
  "max_output_tokens": 8192,
}

safety_settings = [
  {
    "category": "HARM_CATEGORY_HARASSMENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_HATE_SPEECH",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
  {
    "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
    "threshold": "BLOCK_MEDIUM_AND_ABOVE"
  },
]

system_instruction = "Anda adalah asisten yang ahli dalam memberikan rekomendasi, tips dan saran untuk menghemat energi dan air di rumah tangga. Tujuan Anda adalah membantu pengguna mengurangi konsumsi energi dan air, serta biaya tagihan, dengan memberikan rekomendasi praktis yang dapat diterapkan dalam kehidupan sehari-hari dan selalu menggunakan bahasa indonesia baik dan benar. Tidak menjawab atau merespon pertanyaan-pertanyaan yang tidak berhubungan dengan penghematan energi dan air."

model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest",generation_config=generation_config,system_instruction=system_instruction,safety_settings=safety_settings)

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])

st.title("Chatbot Rekomendasi Hemat Energi dan Air di Rumah Tangga 🏡💡💧")

def role_to_streamlit(role):
    if role == "model":
        return "assistant"
    else:
        return role
    
for message in st.session_state.chat.history:
    with st.chat_message(role_to_streamlit(message.role)):
        st.markdown(message.parts[0].text)

if prompt := st.chat_input("Silahkan tulis pertanyaan anda disini..."):
    st.chat_message("user").markdown(prompt)
    response = st.session_state.chat.send_message(prompt)
    with st.chat_message("assistant"):
        st.markdown(response.text)

