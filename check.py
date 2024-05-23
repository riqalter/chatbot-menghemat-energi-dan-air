# import os
# import streamlit as st
# from dotenv import load_dotenv
# from sqlalchemy import create_engine

# load_dotenv()

# # confifugure turso api key

# turso_key = os.environ.get("TURSO_AUTH_TOKEN")
# turso_key_sudo = ""

# if turso_key:
#     turso_key_sudo = turso_key
# else:
#     if "turso_key" in st.secrets:
#         turso_key_sudo = st.secrets["turso_key"]
#     else:
#         st.error("API Key belum diatur. Silahkan atur API Key di file .env atau Secrets di Streamlit Sharing.")

# turso_db_url = os.environ.get("TURSO_DATABASE_URL")
# turso_db_url_sudo = ""

# if turso_db_url:
#     turso_db_url_sudo = turso_db_url
# else:
#     if "turso_db_url" in st.secrets:
#         turso_db_url_sudo = st.secrets["turso_db_url"]
#     else:
#         st.error("API Key belum diatur. Silahkan atur API Key di file .env atau Secrets di Streamlit Sharing.")

# # create engine
# dbUrl = f"sqlite+{turso_db_url_sudo}/?authToken={turso_key_sudo}&secure=true"

# engine = create_engine(dbUrl, connect_args={'check_same_thread': False}, echo=True)

import os
from dotenv import load_dotenv
from sqlalchemy import create_engine

load_dotenv()

TURSO_DATABASE_URL = os.environ.get("TURSO_DATABASE_URL")
TURSO_AUTH_TOKEN = os.environ.get("TURSO_AUTH_TOKEN")

dbUrl = f"sqlite+{TURSO_DATABASE_URL}/?authToken={TURSO_AUTH_TOKEN}&secure=true"

engine = create_engine(dbUrl, connect_args={'check_same_thread': False}, echo=True)

