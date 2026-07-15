import streamlit as st
import requests
import time
import streamlit.components.v1 as components

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")
st.markdown("<style>#MainMenu {visibility: hidden;} footer {visibility: hidden;}</style>", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador")
if not slug: st.error("URL Inválida"); st.stop()

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
display = st.empty()
video_atual = ""

while True:
    try:
        response = requests.get(URL_STATUS, timeout=5)
        if response.status_code == 200:
            status = response.json()
            # Verificação de segurança: status tem de ser um dicionário e ter url_video
            if isinstance(status, dict) and status.get("url_video"):
                nova_url = status.get('url_video')
                
                if nova_url != video_atual:
                    video_atual = nova_url
                    # HTML COM DEBUG E DEBUGGER DE ERROS
                    components.html(f"""
                        <div style='text-align: center; background: black; height: 100vh; display: flex; flex-direction: column; align-items: center; justify-content: center;'>
                            <h1 style='color: yellow;'>SOLTA A VOZ: {status.get('cantor', 'CANTOR').upper()}</h1>
                            <video id="v1" width="800" autoplay playsinline style="border: 10px solid #FFD700; border-radius: 20px; background: #222;">
                                <source src="{nova_url}" type="video/mp4">
                                O seu navegador não suporta a reprodução deste vídeo.
                            </video>
                        </div>
                        <script>
                            var vid = document.getElementById('v1');
                            
                            // Log para saber qual o link que está a chegar
                            console.log("Tentando carregar: {nova_url}");

                            vid.onerror = function() {{ 
                                console.error("Erro ao carregar o vídeo! Verifique se o link é público."); 
                            }};

                            function tentarPlay() {{
                                vid.muted = true;
                                vid.play().then(() => {{
                                    console.log("Play iniciado");
                                    setTimeout(() => {{ vid.muted = false; }}, 1000);
                                }}).catch(e => {{
                                    console.warn("Autoplay bloqueado, aguardando clique...");
                                }});
                            }}
                            tentarPlay();
                            
                            // Clique global para forçar arranque
                            document.body.addEventListener('click', () => {{ vid.play(); vid.muted = false; }});
                            
                            // Monitoramento de Comandos
                            setInterval(() => {{
                                fetch('{URL_STATUS}').then(r => r.json()).then(data => {{
                                    if(data.comando === 'pause') vid.pause();
                                    if(data.comando === 'play') vid.play();
                                    if(data.comando === 'voltar') vid.currentTime -= 10;
                                    if(data.comando === 'avancar') vid.currentTime += 10;
                                }});
                            }}, 1000);
                        </script>
                    """, height=800)
            else:
                display.markdown("<h1 style='text-align: center; color: white; margin-top: 200px;'>AGUARDANDO MÚSICA...</h1>", unsafe_allow_html=True)
    except: 
        display.warning("Conectando ao servidor...")
    time.sleep(2)
