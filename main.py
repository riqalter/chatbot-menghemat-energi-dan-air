import os
import random
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
    "temperature": 0.7,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE",
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE",
    },
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction="Anda adalah asisten yang ahli dalam memberikan rekomendasi, tips dan saran untuk menghemat energi dan air di rumah tangga. Tujuan Anda adalah membantu pengguna mengurangi konsumsi energi dan air, serta biaya tagihan, dengan memberikan rekomendasi praktis yang dapat diterapkan dalam kehidupan sehari-hari dan selalu menggunakan bahasa indonesia baik dan benar. Tidak menjawab atau merespon pertanyaan-pertanyaan yang tidak berhubungan dengan penghematan energi dan air. Anda diperbolehkan menggunakan emoji.",
)

# Pertanyaan terkait penghematan energi dan air di industri dan rumah tangga
questions = [
    "Apa saja langkah-langkah sederhana yang dapat diambil untuk menghemat energi di rumah?",
    "Bagaimana penggunaan peralatan elektronik hemat energi dapat mengurangi konsumsi listrik?",
    "Mengapa penting untuk mematikan lampu saat tidak digunakan?",
    "Bagaimana pengaturan suhu AC yang optimal dapat menghemat energi?",
    "Apa peran lampu LED dalam penghematan energi dibandingkan dengan lampu pijar?",
    "Bagaimana cara mengoptimalkan penggunaan mesin cuci untuk menghemat energi?",
    "Apa keuntungan menggunakan peralatan dapur hemat energi?",
    "Bagaimana insulasi rumah yang baik dapat membantu dalam penghematan energi?",
    "Apa manfaat menggunakan termostat pintar di rumah?",
    "Bagaimana caranya menghemat energi saat memasak?",
    "Bagaimana audit energi dapat membantu perusahaan dalam mengidentifikasi peluang penghematan energi?",
    "Apa saja teknologi terbaru yang dapat diterapkan industri untuk menghemat energi?",
    "Bagaimana manajemen energi yang baik dapat meningkatkan efisiensi operasional di industri?",
    "Apa peran sumber energi terbarukan dalam penghematan energi di industri?",
    "Bagaimana penggunaan sistem pencahayaan cerdas dapat mengurangi konsumsi energi di fasilitas industri?",
    "Apa manfaat dari pemeliharaan rutin peralatan industri untuk penghematan energi?",
    "Bagaimana peran kontrol otomatis dalam penghematan energi di industri?",
    "Bagaimana cara mengurangi konsumsi energi di proses pendinginan industri?",
    "Apa pentingnya pelatihan karyawan mengenai praktik penghematan energi di tempat kerja?",
    "Bagaimana penerapan prinsip lean manufacturing dapat membantu dalam penghematan energi?",
    "Apa saja langkah-langkah yang dapat diambil untuk menghemat air di kamar mandi?",
    "Bagaimana cara mengurangi penggunaan air saat mencuci piring?",
    "Apa keuntungan menggunakan perangkat hemat air di rumah?",
    "Bagaimana mengurangi penggunaan air untuk penyiraman taman?",
    "Apa pentingnya memeriksa dan memperbaiki kebocoran pipa air di rumah?",
    "Bagaimana penggunaan toilet dual flush dapat menghemat air?",
    "Bagaimana cara menghemat air saat mencuci pakaian?",
    "Apa manfaat memasang shower head hemat air?",
    "Bagaimana mengoptimalkan penggunaan air hujan untuk kebutuhan rumah tangga?",
    "Apa peran kesadaran keluarga dalam penghematan air?",
    "Bagaimana audit penggunaan air dapat membantu industri mengidentifikasi peluang penghematan air?",
    "Apa saja teknologi terbaru yang dapat diterapkan untuk menghemat air di industri?",
    "Bagaimana sistem pengolahan air limbah dapat membantu dalam penghematan air di industri?",
    "Apa manfaat dari penggunaan air daur ulang di proses industri?",
    "Bagaimana cara mengurangi konsumsi air dalam proses pendinginan industri?",
    "Apa pentingnya pelatihan karyawan mengenai praktik penghematan air di tempat kerja?",
    "Bagaimana penerapan prinsip green manufacturing dapat membantu dalam penghematan air?",
    "Apa peran sensor otomatis dalam penghematan air di industri?",
    "Bagaimana cara mengoptimalkan penggunaan air dalam proses pembersihan di industri?",
    "Bagaimana pemeliharaan rutin peralatan dapat mengurangi pemborosan air di industri?",
    "Apa peran inovasi teknologi dalam penghematan air di industri?",
    "Bagaimana mengimplementasikan program penghematan air secara efektif di industri?"
]

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "random_questions" not in st.session_state:
    st.session_state.random_questions = random.sample(questions, 5)

st.title("Chatbot Rekomendasi Hemat Energi dan Air di Industri Dan Rumah Tangga 🏡💡💧")

if "selected_question" in st.session_state and st.session_state.send_question:
    st.chat_message("user").markdown(st.session_state.selected_question)
    response = st.session_state.chat.send_message(st.session_state.selected_question)
    with st.chat_message("assistant"):
        st.markdown(response.text)
    st.session_state.send_question = False  # Reset flag setelah mengirim pertanyaan
    st.session_state.selected_question = None  # Reset selected_question setelah mengirim

def role_to_streamlit(role):
    if role == "model":
        return "assistant"
    else:
        return role

if prompt := st.chat_input("Silahkan tulis pertanyaan anda disini..."):
    st.chat_message("user").markdown(prompt)
    response = st.session_state.chat.send_message(prompt)
    with st.chat_message("assistant"):
        st.markdown(response.text)

# Fungsi untuk menampilkan tombol pertanyaan acak
def display_random_question_buttons():
    st.write("### Rekomendasi Pertanyaan:")
    random_questions = st.session_state.random_questions
    for question in random_questions:
        if st.button(question):
            st.session_state.selected_question = question
            st.session_state.send_question = True

# Tombol untuk mengacak ulang pertanyaan
if st.button("Randomize Questions"):
    st.session_state.random_questions = random.sample(questions, 5)

# Menampilkan tombol pertanyaan acak di atas kotak input
display_random_question_buttons()

