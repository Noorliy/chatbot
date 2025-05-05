import streamlit as st
import pandas as pd
import plotly.express as px
from pymongo import MongoClient

# --- Koneksi MongoDB ---
client = MongoClient("mongodb+srv://SIC6:jmCISIocH7HxL6xg@cluster0.qvi1yfs.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
db = client["Pureindivisum"]
collection = db["Byunum"]

# --- Navigasi Sidebar ---
st.sidebar.title("Navigasi")
page = st.sidebar.radio("Pilih Halaman:", ["Dashboard", "Chatbot"])

# --- Dashboard Grafik ---
if page == "Dashboard":
    st.title("📊 Grafik Sensor Jarak & TDS")

    data = list(collection.find({}, {"_id": 0}))
    if data:
        df = pd.DataFrame(data)
        df["index"] = range(len(df))
        st.subheader("Grafik Jarak dan TDS")
        fig = px.line(df, x="index", y=["jarak", "tds"], title="Grafik Jarak & TDS Berdasarkan Urutan Data")
        st.plotly_chart(fig)
    else:
        st.warning("Belum ada data di MongoDB.")

# --- Chatbot ---
elif page == "Chatbot":
    st.title("🤖 Chatbot MongoDB + Streamlit")

    def chatbot_reply(user_input):
        user_input = user_input.lower()

        if "halo" in user_input:
            return "Halo juga! Ada yang bisa saya bantu?"

        elif "siapa kamu" in user_input:
            return "Saya adalah chatbot yang bisa membaca data dari MongoDB."

        elif "tds tertinggi" in user_input:
            data = list(collection.find({}, {"_id": 0, "tds": 1}))
            if data:
                max_tds = max(item["tds"] for item in data if "tds" in item)
                return f"TDS tertinggi yang tercatat adalah {max_tds}"
            else:
                return "Belum ada data TDS di database."

        elif "jarak terendah" in user_input:
            data = list(collection.find({}, {"_id": 0, "jarak": 1}))
            if data:
                min_jarak = min(item["jarak"] for item in data if "jarak" in item)
                return f"Jarak terendah yang tercatat adalah {min_jarak}"
            else:
                return "Belum ada data jarak di database."

        elif "terima kasih" in user_input:
            return "Sama-sama! Senang bisa membantu."

        else:
            return "Maaf, saya belum mengerti pertanyaan itu. Coba tanya tentang TDS atau jarak."

    # Session untuk histori chat
    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    user_input = st.chat_input("Ketik pertanyaanmu...")

    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        response = chatbot_reply(user_input)
        st.session_state.messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"):
            st.markdown(response)
