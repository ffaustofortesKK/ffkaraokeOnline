import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")
st.markdown("""<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")

if not slug:
    st.error("URL da TV inválida.")
    st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
display = st.empty()

while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            if isinstance(status, dict) and status.get("acao") == "contagem":
                # AQUI É ONDE O VÍDEO APARECE
                # Se o sinal do Firebase incluir uma URL de vídeo, ele reproduz
                video_url = status.get('video_url', 'https://www.youtube.com/watch?v=dQw4w9WgXcQ') # Exemplo
                
                display.markdown(f"## Cantando: {status.get('musica')}")
                st.video(video_url) # O componente de vídeo do Streamlit
                
                time.sleep(20) # Tempo do vídeo
                requests.put(URL_STATUS, json={"acao": "espera"})
            else:
                display.markdown("<h1 style='text-align: center;'>AGUARDANDO...</h1>")
        
    except Exception as e:
        st.warning("Conexão instável...")
    time.sleep(2)
