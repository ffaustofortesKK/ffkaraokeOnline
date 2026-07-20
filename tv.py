import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""
    <style>
        .stApp { background: black; margin: 0; padding: 0; overflow: hidden; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .cantor-style { color: white; font-weight: bold; text-shadow: 3px 3px 6px #000; }
        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .video-container { 
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
            background: black; display: flex; justify-content: center; align-items: center; z-index: 9999; 
        }
        video { width: 100vw; height: 100vh; object-fit: contain; background: black; }
        .fila-container { background: rgba(0,0,0,0.85); padding: 30px; border-radius: 15px; color: white; width: 85%; margin: 40px auto; border: 2px solid #333; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

# Buscar dados
try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_status = {}
    res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

# 1. EXIBIÇÃO DO VÍDEO EM TELA CHEIA E AUTOMÁTICO
if comando == "play":
    if url_video:
        st.markdown(f"""
            <div class="video-container" id="container-video">
                <video id="karaoke-video" autoplay playsinline controls>
                    <source src="{url_video}" type="video/mp4">
                    O seu navegador não suporta reprodução de vídeo.
                </video>
            </div>
            <script>
                const vid = document.getElementById('karaoke-video');
                
                // Força o play automático
                vid.play().catch(error => {{
                    console.log("Autoplay restrito, a tentar com mudo...", error);
                    vid.muted = true;
                    vid.play();
                }});

                // Quando o vídeo termina, limpa o estado na base de dados e volta à fila
                vid.onended = function() {{
                    fetch('{URL_STATUS}', {{
                        method: 'PATCH',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ comando: 'fim', url_video: '', musica: '', cantor: '' }})
                    }}).then(() => {{
                        window.location.reload();
                    }});
                }};
            </script>
        """, unsafe_allow_html=True)

        # Loop de sincronização em segundo plano
        while True:
            time.sleep(3)
            try:
                check_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
                if check_status.get("comando") != "play":
                    st.rerun()
            except:
                pass
    else:
        st.error("⚠️ Comando 'play' recebido, mas o link do vídeo está vazio.")
        time.sleep(3)
        requests.patch(URL_STATUS, json={"comando": "fim"})
        st.rerun()

# 2. VEZ DO CANTOR (AGUARDANDO START)
elif comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; padding:100px; color:white;'>
            <h1 style='font-size: 3rem;'>VEZ DE: <span class="cantor-style">{str(res_status.get('cantor', '')).upper()}</span></h1>
            <h2 style='font-size: 2.2rem; margin-top: 20px;'>Música: <span class="musica-style">{str(res_status.get('musica', '')).upper()}</span></h2>
            <h3 style="color: #00ff00; margin-top: 40px; font-size: 1.5rem;">A preparar o palco... O vídeo vai começar automaticamente!</h3>
        </div>
    """, unsafe_allow_html=True)
    time.sleep(2)
    st.rerun()

# 3. CABEÇALHO PADRÃO E FILA DE ESPERA (EXIBIDO QUANDO ACABA OU ESTÁ LIVRE)
else:
    st.markdown("<h1 style='text-align:center; color:gold; margin-top: 30px; font-size: 3rem;'>🎤 FF KARAOKE - FILA DE ESPERA</h1>", unsafe_allow_html=True)

    if res_pedidos:
        st.markdown("<div class='fila-container'>", unsafe_allow_html=True)
        st.markdown("<h2 style='color: #00ff00; border-bottom: 2px solid #444; padding-bottom: 10px;'>Próximos Cantores:</h2>", unsafe_allow_html=True)
        pedidos_lista = list(res_pedidos.items())
        
        for i, (p_id, p) in enumerate(pedidos_lista, 1):
            if not str(p.get('musica', '')).startswith("PEDIDO:"):
                st.markdown(f"<h3 style='margin: 15px 0;'>{i}. <span class='cantor-style'>{str(p.get('cantor')).upper()}</span> ➔ <span class='musica-style'>{str(p.get('musica')).upper()}</span></h3>", unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
            <div style='text-align:center; margin-top: 150px; color: #888;'>
                <h2>A fila está vazia. Peça a sua música através do telemóvel! 📱</h2>
            </div>
        """, unsafe_allow_html=True)
        
    time.sleep(3)
    st.rerun()
