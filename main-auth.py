import os
import sqlite3
import random
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256

load_dotenv()

# Configure the API key
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
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
]

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    safety_settings=safety_settings,
    generation_config=generation_config,
    system_instruction=(
        "Anda adalah asisten yang ahli dalam memberikan rekomendasi, tips dan saran untuk "
        "menghemat energi dan air di rumah tangga. Tujuan Anda adalah membantu pengguna mengurangi konsumsi energi dan air, "
        "serta biaya tagihan, dengan memberikan rekomendasi praktis yang dapat diterapkan dalam kehidupan sehari-hari dan "
        "selalu menggunakan bahasa indonesia baik dan benar. Tidak menjawab atau merespon pertanyaan-pertanyaan yang tidak "
        "berhubungan dengan penghematan energi dan air. Anda diperbolehkan menggunakan emoji."
    ),
)

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

# SQLite database setup
conn = sqlite3.connect('chatbot_users.db')
c = conn.cursor()

c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
''')
c.execute('''
    CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY,
        user_id INTEGER,
        message TEXT,
        response TEXT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')
conn.commit()

# Functions for user authentication
def hash_password(password):
    return pbkdf2_sha256.hash(password)

def check_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)

# Functions for user management
def register_user(name, email, password):
    hashed_password = hash_password(password)
    try:
        c.execute('INSERT INTO users (name, email, password) VALUES (?, ?, ?)', (name, email, hashed_password))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def login_user(email, password):
    c.execute('SELECT id, name, password FROM users WHERE email = ?', (email,))
    user = c.fetchone()
    if user and check_password(password, user[2]):
        return user[0], user[1]
    return None, None

def save_message(user_id, message, response):
    c.execute('INSERT INTO messages (user_id, message, response) VALUES (?, ?, ?)', (user_id, message, response))
    conn.commit()

def get_message_history(user_id):
    c.execute('SELECT message, response, timestamp FROM messages WHERE user_id = ? ORDER BY timestamp DESC', (user_id,))
    return c.fetchall()

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])
if "random_questions" not in st.session_state:
    st.session_state.random_questions = random.sample(questions, 5)
if "user" not in st.session_state:
    st.session_state.user = None

# User authentication
def show_register_form():
    st.subheader("Register")
    name = st.text_input("Name", key="register_name")
    email = st.text_input("Email", key="register_email")
    password = st.text_input("Password", type="password", key="register_password")
    if st.button("Register", key="register_button"):
        if register_user(name, email, password):
            st.success("Registration successful. Please login.")
        else:
            st.error("Email already exists.")

def show_login_form():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_button"):
        user_id, user_name = login_user(email, password)
        if user_id:
            st.session_state.user = {"id": user_id, "name": user_name}
            st.success(f"Welcome {user_name}!")
        else:
            st.error("Invalid credentials. Please try again.")

def show_chat_interface():
    st.title("Chatbot Rekomendasi Hemat Energi dan Air di Industri Dan Rumah Tangga 🏡💡💧")

    if "selected_question" in st.session_state and st.session_state.send_question:
        st.chat_message("user").markdown(st.session_state.selected_question)
        response = st.session_state.chat.send_message(st.session_state.selected_question)
        save_message(st.session_state.user["id"], st.session_state.selected_question, response.text)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.send_question = False  # Reset flag setelah mengirim pertanyaan
        st.session_state.selected_question = None  # Reset selected_question setelah mengirim
        # TODO: Save message and response FIXME
        # Save message and response
        save_message(st.session_state.user["id"], st.session_state.selected_question, response.text)

    if prompt := st.chat_input("Silahkan tulis pertanyaan anda disini..."):
        st.chat_message("user").markdown(prompt)
        response = st.session_state.chat.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Save message and response
        save_message(st.session_state.user["id"], prompt, response.text)

    # Fungsi untuk menampilkan tombol pertanyaan acak
    def display_random_question_buttons():
        st.write("### Rekomendasi Pertanyaan:")
        random_questions = st.session_state.random_questions
        for question in random_questions:
            if st.button(question, key=f"random_question_{question}"):
                st.session_state.selected_question = question
                st.session_state.send_question = True

    # Tombol untuk mengacak ulang pertanyaan
    if st.button("Randomize Questions", key="randomize_questions"):
        st.session_state.random_questions = random.sample(questions, 5)

    # Menampilkan tombol pertanyaan acak di atas kotak input
    display_random_question_buttons()

    # Show message history
    st.subheader("Message History")
    history = get_message_history(st.session_state.user["id"])
    for message, response, timestamp in history:
        st.write(f"{timestamp}:")
        st.write(f"**You:** {message}")
        st.write(f"**Assistant:** {response}")

# Main interface
if st.session_state.user is None:
    st.sidebar.title("User Authentication")
    show_login_form()
    st.sidebar.markdown("---")
    show_register_form()
else:
    show_chat_interface()