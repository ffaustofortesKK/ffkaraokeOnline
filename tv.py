import streamlit as st
import requests
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""<style>
    #MainMenu {visibility: hidden; display: none;} 
    footer {visibility: hidden; display: none;}
    .video-container { text-align: center; margin-top: 50px; }
</style>""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")

if not slug:
    st.error("ERRO: URL da TV inválida.")
    st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
display = st.empty()

# Variável para controlar o vídeo atual
video_atual = ""

while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            status = response.json()
            
            if isinstance(status, dict) and status.get("acao") == "contagem":
                nova_url = status.get('url_video', '')
                
                # Só desenha se for um vídeo novo ou se o vídeo ainda não estiver a tocar
                if nova_url and (nova_url != video_atual):
                    video_atual = nova_url
                    
                    components.html(f"""
                        <div style='text-align: center;'>
                            <h1 style='color: yellow; font-family: sans-serif;'>SOLTA A VOZ: {status.get('cantor', '').upper()}</h1>
                            <video id="v1" width="800" autoplay playsinline style="border: 10px solid #FFD700; border-radius: 20px; background: black;">
                                <source src="{nova_url}" type="video/mp4">
                            </video>
                        </div>
                        <script>
                            var vid = document.getElementById('v1');
                            
                            // Tenta dar play forçado
                            vid.muted = true; 
                            vid.play();
                            
                            // Tenta tirar o mute após 1 segundo
                            setTimeout(() => {{ vid.muted = false; }}, 1000);
                            
                            // Quando o vídeo acabar, recarrega a página para limpar o ecrã
                            vid.onended = function() {{
                                window.location.reload();
                            }};
                            
                            // Gatilho de segurança: qualquer clique na tela força o play
                            document.body.onclick = function() {{ vid.play(); }};
                        </script>
                    """, height=700)
                
            else:
                # Se não há acção de contagem, limpa a variável e mostra o texto
                video_atual = ""
                display.markdown("<h1 style='text-align: center; color: #555; margin-top: 200px;'>AGUARDANDO NOVO CANTOR...</h1>", unsafe_allow_html=True)
                
    except Exception:
        display.warning("Aguardando conexão...")
        
    time.sleep(2)
