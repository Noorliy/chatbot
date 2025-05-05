import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient
import google.generativeai as genai
import os

# --- Konfigurasi API Gemini ---
GOOGLE_API_KEY = "AIzaSyANGSidhWqegFOjCKm5JGeqmMbgrVJ7Z20"  # Ganti dengan API key Gemini kamu
genai.configure(api_key=GOOGLE_API_KEY)

# --- Inisialisasi model Gemini ---
@st.cache_resource
def load_gemini_model():
    try:
        return genai.GenerativeModel('gemini-1.5-flash')
    except Exception as e:
        st.error(f"Error saat inisialisasi Gemini: {e}")
        return None

# --- Koneksi MongoDB ---
client = MongoClient("mongodb+srv://SIC6:jmCISIocH7HxL6xg@cluster0.qvi1yfs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Pureindivisum"]
collection = db["Byunum"]

# --- Navigasi Sidebar ---
st.sidebar.title("Navigasi")
page = st.sidebar.radio("Pilih Halaman:", ["Dashboard", "Chatbot Gemini"])

# --- Halaman Dashboard ---
if page == "Dashboard":
    st.title("📊 Grafik Sensor: TDS, Turbidity, dan pH")

    data = list(collection.find({}, {"_id": 0}))
    if data:
        df = pd.DataFrame(data)
        sensor_columns = [col for col in ["tds", "turbidity", "ph"] if col in df.columns]

        if sensor_columns:
            df["index"] = range(len(df))
            st.subheader("Grafik Sensor")
            fig = px.line(df, x="index", y=sensor_columns, title="Grafik TDS, Turbidity, dan pH")
            st.plotly_chart(fig)
        else:
            st.warning("Data tidak memiliki kolom TDS, Turbidity, atau pH.")
    else:
        st.warning("Belum ada data di MongoDB.")

# --- Halaman Chatbot Gemini ---
elif page == "Chatbot Gemini":
    st.title("🤖 Chatbot Cerdas (Gemini AI + MongoDB)")

    model = load_gemini_model()

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    prompt = st.chat_input("Tanyakan apa saja...")
    if prompt:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.spinner("Gemini sedang menjawab..."):
            try:
                response = model.generate_content(prompt)
                answer = response.text
            except Exception as e:
                answer = f"Error: {e}"

        st.session_state.messages.append({"role": "assistant", "content": answer})
        with st.chat_message("assistant"):
            st.markdown(answer)
