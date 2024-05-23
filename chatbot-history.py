import os
import random
import streamlit as st
import google.generativeai as genai
from dotenv import load_dotenv
from passlib.hash import pbkdf2_sha256
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

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

# confifugure turso api key

turso_key = os.environ.get("TURSO_AUTH_TOKEN")
turso_key_sudo = ""

if turso_key:
    turso_key_sudo = turso_key
else:
    if "turso_key" in st.secrets:
        turso_key_sudo = st.secrets["turso_key"]
    else:
        st.error("API Key belum diatur. Silahkan atur API Key di file .env atau Secrets di Streamlit Sharing.")

turso_db_url = os.environ.get("TURSO_DATABASE_URL")
turso_db_url_sudo = ""

if turso_db_url:
    turso_db_url_sudo = turso_db_url
else:
    if "turso_db_url" in st.secrets:
        turso_db_url_sudo = st.secrets["turso_db_url"]
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
    system_instruction=("Anda adalah asisten yang ahli dalam memberikan rekomendasi, tips dan saran untuk menghemat energi dan air di rumah tangga dan bidang industri. Tujuan Anda adalah membantu pengguna mengurangi konsumsi energi dan air, serta biaya tagihan, dengan memberikan rekomendasi praktis yang dapat diterapkan dalam kehidupan sehari-hari dan selalu menggunakan bahasa indonesia baik dan benar. Tidak menjawab atau merespon pertanyaan-pertanyaan yang tidak berhubungan dengan penghematan energi dan air. Anda diperbolehkan menggunakan emoji."),
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

# SQLAlchemy setup
dbUrl = f"sqlite+{turso_db_url_sudo}/?authToken={turso_key_sudo}&secure=true"

engine = create_engine(dbUrl, connect_args={'check_same_thread': False}, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    messages = relationship("Message", back_populates="user")

class Message(Base):
    __tablename__ = 'messages'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = relationship("User", back_populates="messages")

Base.metadata.create_all(bind=engine)

# Functions for user authentication
def hash_password(password):
    return pbkdf2_sha256.hash(password)

def check_password(password, hashed):
    return pbkdf2_sha256.verify(password, hashed)

# Functions for user management
def register_user(db, name, email, password):
    hashed_password = hash_password(password)
    new_user = User(name=name, email=email, password=hashed_password)
    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except:
        db.rollback()
        return None

def login_user(db, email, password):
    user = db.query(User).filter(User.email == email).first()
    if user and check_password(password, user.password):
        return user
    return None

def save_message(db, user_id, message, response):
    if message and response:  # Ensure message and response are not None
        new_message = Message(user_id=user_id, message=message, response=response)
        db.add(new_message)
        db.commit()

def get_message_history(db, user_id):
    messages = db.query(Message).filter(Message.user_id == user_id).order_by(Message.timestamp.asc()).all()
    return [(message.message, message.response) for message in messages]

def clear_message_history(db, user_id):
    db.query(Message).filter(Message.user_id == user_id).delete()
    db.commit()

# Initialize session state
if "chat" not in st.session_state:
    st.session_state.chat = None
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
        db = SessionLocal()
        user = register_user(db, name, email, password)
        if user:
            st.success("Registration successful. Please login.")
        else:
            st.error("Email already exists.")
        db.close()
def show_login_form():
    st.subheader("Login")
    email = st.text_input("Email", key="login_email")
    password = st.text_input("Password", type="password", key="login_password")
    if st.button("Login", key="login_button"):
        db = SessionLocal()
        user = login_user(db, email, password)
        if user:
            st.session_state.user = {"id": user.id, "name": user.name}
            st.success(f"Welcome {user.name}!, Click the login button again to start chatting.")
            st.session_state.chat = model.start_chat(history=[])
        else:
            st.error("Invalid credentials. Please try again.")
        db.close()

def show_chat_interface():
    st.title("GreenergyAI: Solusi Efisiensi Energi dan Air 💡💧")

    db = SessionLocal()
    if "selected_question" in st.session_state and st.session_state.send_question:
        st.chat_message("user").markdown(st.session_state.selected_question)
        response = st.session_state.chat.send_message(st.session_state.selected_question)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        st.session_state.send_question = False  # Reset flag setelah mengirim pertanyaan
        st.session_state.selected_question = None  # Reset selected_question setelah mengirim

        # Save message and response
        save_message(db, st.session_state.user["id"], st.session_state.selected_question, response.text)

    if prompt := st.chat_input("Silahkan tulis pertanyaan anda disini..."):
        st.chat_message("user").markdown(prompt)
        response = st.session_state.chat.send_message(prompt)
        with st.chat_message("assistant"):
            st.markdown(response.text)
        
        # Save message and response
        save_message(db, st.session_state.user["id"], prompt, response.text)

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

    # Tombol untuk mereset riwayat chat
    if st.button("Reset Chat History", key="reset_chat_history"):
        clear_message_history(db, st.session_state.user["id"])
        st.success("Chat history has been reset.")

    # Menampilkan tombol pertanyaan acak di atas kotak input
    display_random_question_buttons()

    # Show message history
    st.subheader("Message History")
    history = get_message_history(db, st.session_state.user["id"])
    for message, response in history:
        st.write(f"**You:** {message}")
        st.write(f"**Assistant:** {response}")

    db.close()

# Main interface
if st.session_state.user is None:
    st.sidebar.title("User Authentication")
    show_login_form()
    st.sidebar.markdown("---")
    show_register_form()
else:
    show_chat_interface()
