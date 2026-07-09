import streamlit as st
import requests

# CONFIGURAÇÃO
URL_FIREBASE = "https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos.json"

st.set_page_config(page_title="FF KARAOKE CLOUD", layout="centered")

st.title("🎤 FF KARAOKE - Pedidos")

nome = st.text_input("Seu Nome:")
musica = st.text_input("Nome da Música:")

if st.button("Enviar Pedido"):
    if nome and musica:
        payload = {"cantor": nome, "musica": musica, "estado": "Pendente"}
        requests.post(URL_FIREBASE, json=payload)
        st.success(f"Pedido de {musica} enviado!")
    else:
        st.error("Preencha o nome e a música.")
