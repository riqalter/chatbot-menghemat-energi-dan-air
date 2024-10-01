"""
Install the Google AI Python SDK

$ pip install google-generativeai

See the getting started guide for more information:
https://ai.google.dev/gemini-api/docs/get-started/python
"""

import os

import google.generativeai as genai

genai.configure(api_key=os.environ["GOOGLE_GEMINI_KEY"])

# Create the model
# See https://ai.google.dev/api/python/google/generativeai/GenerativeModel
generation_config = {
  "temperature": 1,
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
  model_name="gemini-1.5-flash",
  safety_settings=safety_settings,
  generation_config=generation_config,
  system_instruction="Anda adalah asisten yang ahli dalam memberikan rekomendasi, tips dan saran untuk menghemat energi dan air di rumah tangga dan bidang industri. Tujuan Anda adalah membantu pengguna mengurangi konsumsi energi dan air, serta biaya tagihan, dengan memberikan rekomendasi praktis yang dapat diterapkan dalam kehidupan sehari-hari dan selalu menggunakan bahasa indonesia baik dan benar. Tidak menjawab atau merespon pertanyaan-pertanyaan yang tidak berhubungan dengan penghematan energi dan air. Anda diperbolehkan menggunakan emoji.",
)

chat_session = model.start_chat(
  history=[
  ]
)

response = chat_session.send_message("Apa saja langkah-langkah sederhana yang dapat diambil untuk menghemat energi di rumah?")

print(response.text)
print(chat_session.history)