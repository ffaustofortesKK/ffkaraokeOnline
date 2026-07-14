import streamlit as st
import requests
import time

# Configuração da página para modo tela cheia
st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

# Ocultar elementos padrão do Streamlit
st.markdown("""<style>
    #MainMenu {visibility: hidden;} 
    footer {visibility: hidden;}
    .video-container { text-align: center; margin-top: 20px; }
    video { width: 80%; border: 10px solid #FFD700; border-radius: 20px; }
</style>""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")

if not slug:
    st.error("ERRO: URL da TV inválida.")
    st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
display = st.empty()

while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            # Verificamos se há ação e se existe uma URL de vídeo
            if isinstance(status, dict) and status.get("acao") == "contagem":
                video_url = status.get('url_video', '') # O seu painel deve enviar esta chave
                
                display.markdown(f"""
                    <div class='video-container'>
                        <h1 style='color: yellow;'>SOLTA A VOZ: {status.get('cantor', '').upper()}</h1>
                        <video autoplay controls>
                            <source src="{video_url}" type="video/mp4">
                            Seu navegador não suporta vídeos.
                        </video>
                    </div>
                """, unsafe_allow_html=True)
                
                time.sleep(15) # Tempo do vídeo
                requests.put(URL_STATUS, json={"acao": "espera"})
                
            else:
                display.markdown("<h1 style='text-align: center; color: #555; margin-top: 200px;'>AGUARDANDO NOVO CANTOR...</h1>", unsafe_allow_html=True)
    except Exception as e:
        display.warning(f"Conexão instável...")
        
    time.sleep(2)
