import streamlit as st
import requests
import time
import cloudinary
import cloudinary.api
import random
import json

# Configuração Cloudinary
cloudinary.config(cloud_name="yhwgjh7g", api_key="347924379441394", api_secret="_gzZOnOmzIk6dlmferYm6ck8S08")

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""
    <style>
        .stApp { background: black; margin: 0; padding: 0; overflow: hidden; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
        .cantor-style { color: white; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        
        .video-container { 
            position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; 
            background: black; display: flex; justify-content: center; align-items: center; z-index: 9999; 
        }
        .video-container video { 
            width: 100vw; height: 100vh; object-fit: contain; background: black; 
        }
        
        /* Contratos e barra flutuante sobre o vídeo clipe */
        .video-clipe-fullscreen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: black;
            z-index: 9999;
            display: flex;
            justify-content: center;
            align-items: center;
            overflow: hidden;
        }

        .video-clipe-fullscreen video {
            width: 100vw;
            height: 100vh;
            object-fit: cover;
            background: black;
        }

        .controlo-flutuante {
            position: absolute;
            bottom: 30px;
            left: 50%;
            transform: translateX(-50%);
            background: rgba(0, 0, 0, 0.75);
            padding: 12px 25px;
            border-radius: 40px;
            display: flex;
            align-items: center;
            gap: 20px;
            z-index: 10000;
            border: 1px solid rgba(255, 255, 255, 0.2);
            backdrop-filter: blur(5px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.8);
            opacity: 0.2;
            transition: opacity 0.3s ease;
        }

        .video-clipe-fullscreen:hover .controlo-flutuante {
            opacity: 1;
        }

        .btn-vid {
            background: #222;
            color: white;
            border: 1px solid #555;
            padding: 8px 16px;
            border-radius: 20px;
            cursor: pointer;
            font-weight: bold;
            font-size: 14px;
            transition: background 0.2s;
        }

        .btn-vid:hover {
            background: #e50914;
            border-color: #e50914;
        }

        .progresso-barra {
            appearance: none;
            -webkit-appearance: none;
            width: 300px;
            height: 6px;
            border-radius: 3px;
            background: #555;
            outline: none;
            cursor: pointer;
        }

        .progresso-barra::-webkit-slider-thumb {
            -webkit-appearance: none;
            appearance: none;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: #ffff00;
            cursor: pointer;
        }

        .contador-box { font-size: 8rem; color: yellow; font-weight: bold; text-shadow: 0 0 20px red; text-align: center; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=3).json() or {}
except:
    res_status = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

@st.cache_data(ttl=120)
def obter_todos_videos_da_pasta():
    urls = []
    try:
        fallback = cloudinary.api.resources(type="upload", resource_type="video", max_results=100)
        geral = fallback.get('resources', [])
        for item in geral:
            public_id = item.get('public_id', '')
            if 'video_clipes' in public_id or not urls:
                urls.append(item['secure_url'])
    except Exception as e:
        print("Erro ao buscar vídeos no Cloudinary:", e)
    return urls

# 1. EXIBIÇÃO DO VÍDEO DE KARAOKE EM TELA TOTAL
if comando == "play":
    if url_video:
        st.markdown(f"""
            <div class="video-container" id="container-video">
                <video id="karaoke-video" autoplay playsinline>
                    <source src="{url_video}" type="video/mp4">
                    O seu navegador não suporta reprodução de vídeo.
                </video>
            </div>
            <script>
                const vid = document.getElementById('karaoke-video');
                let fechado = false;
                
                function fecharKaraoke() {{
                    if (fechado) return;
                    fechado = true;

                    fetch('{URL_STATUS}', {{
                        method: 'PATCH',
                        headers: {{ 'Content-Type': 'application/json' }},
                        body: JSON.stringify({{ comando: '', url_video: '', musica: '', cantor: '' }})
                    }}).finally(() => {{
                        window.location.reload();
                    }});
                }}

                vid.play().catch(error => {{
                    vid.muted = true;
                    vid.play();
                }});

                vid.onended = function() {{ fecharKaraoke(); }};
                vid.ontimeupdate = function() {{
                    if (vid.duration && !isNaN(vid.duration)) {{
                        if (vid.currentTime >= (vid.duration - 0.4)) {{ fecharKaraoke(); }}
                    }}
                }};
            </script>
        """, unsafe_allow_html=True)

        while True:
            time.sleep(1)
            try:
                check_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=3).json() or {}
                if check_status.get("comando") != "play":
                    st.rerun()
            except:
                pass
    else:
        st.error("⚠️ Comando 'play' recebido, mas o link do vídeo está vazio.")
        time.sleep(2)
        requests.patch(URL_STATUS, json={"comando": ""})
        st.rerun()

# 2. CONTAGEM DECRESCENTE (3, 2, 1, 0)
elif comando == "aguardando_play":
    st.markdown(f"""
        <div style='text-align:center; padding:80px; color:white;'>
            <h1 style='font-size: 2.5rem; color: #00ff00;'>A CHAMAR AO PALCO:</h1>
            <h2 style='font-size: 3.5rem;' class="cantor-style">{str(res_status.get('cantor', '')).upper()}</h2>
            <h3 style='font-size: 2rem; color: yellow;'>{str(res_status.get('musica', '')).upper()}</h3>
            <hr style='width: 50%; margin: 20px auto; border-color: #444;'>
            <p style='font-size: 1.5rem; color: #ccc;'>O palco vai abrir em:</p>
        </div>
    """, unsafe_allow_html=True)
    
    placeholder_contagem = st.empty()
    for i in [3, 2, 1, 0]:
        placeholder_contagem.markdown(f'<div class="contador-box">{i}</div>', unsafe_allow_html=True)
        time.sleep(1)
    
    requests.patch(URL_STATUS, json={"comando": "play"})
    st.rerun()

# 3. TELA PRINCIPAL: VÍDEO CLIPE EM TELA CHEIA IMEDIATA COM CONTROLOS
else:
    lista_videos = obter_todos_videos_da_pasta()
    if lista_videos:
        random.shuffle(lista_videos)
        videos_json = json.dumps(lista_videos)
        
        st.markdown(f"""
            <div class="video-clipe-fullscreen">
                <video id="clipe-principal" autoplay playsinline></video>
                
                <div class="controlo-flutuante">
                    <button class="btn-vid" id="btn-play-pause">⏸️ Pausa</button>
                    <button class="btn-vid" id="btn-som">🔊 Som: ON</button>
                    <input type="range" id="barra-progresso" class="progresso-barra" value="0" min="0" max="100" step="0.1">
                </div>
            </div>
            
            <script>
                const listaUrls = {videos_json};
                let indiceAtual = 0;
                const v = document.getElementById('clipe-principal');
                const btnPlayPause = document.getElementById('btn-play-pause');
                const btnSom = document.getElementById('btn-som');
                const barraProgresso = document.getElementById('barra-progresso');
                
                function carregarProximoClipe() {{
                    if (indiceAtual >= listaUrls.length) {{
                        indiceAtual = 0;
                        listaUrls.sort(() => Math.random() - 0.5);
                    }}
                    v.src = listaUrls[indiceAtual++];
                    v.load();
                    v.play().catch(e => {{
                        v.muted = true;
                        v.play();
                        btnSom.innerText = "🔇 Som: OFF";
                    }});
                }}
                
                carregarProximoClipe();
                
                v.onended = function() {{
                    carregarProximoClipe();
                }};
                
                // Botão Play / Pause
                btnPlayPause.onclick = function() {{
                    if (v.paused) {{
                        v.play();
                        btnPlayPause.innerText = "⏸️ Pausa";
                    }} else {{
                        v.pause();
                        btnPlayPause.innerText = "▶️ Play";
                    }}
                }};
                
                // Botão Som Mudo / Com Som
                btnSom.onclick = function() {{
                    v.muted = !v.muted;
                    btnSom.innerText = v.muted ? "🔇 Som: OFF" : "🔊 Som: ON";
                }};
                
                // Atualizar Linha de Acompanhamento da Música
                v.ontimeupdate = function() {{
                    if (v.duration && !isNaN(v.duration)) {{
                        const percentual = (v.currentTime / v.duration) * 100;
                        barraProgresso.value = percentual;
                    }}
                }};
                
                // Permitir avançar/recuar clicando na barra de progresso
                barraProgresso.oninput = function() {{
                    if (v.duration && !isNaN(v.duration)) {{
                        const novoTempo = (barraProgresso.value / 100) * v.duration;
                        v.currentTime = novoTempo;
                    }}
                }};
                
                // Detetar imediatamente comando do microfone para abrir o palco de karaoke
                setInterval(() => {{
                    fetch('{URL_STATUS}?nocache=' + Date.now())
                        .then(res => res.json())
                        .then(data => {{
                            if (data && data.comando && data.comando !== "") {{
                                window.location.reload();
                            }}
                        }}).catch(err => {{}});
                }}, 1000);
            </script>
        """, unsafe_allow_html=True)
    else:
        st.warning("A carregar vídeos do Cloudinary ou pasta vazia...")
        time.sleep(2)
        st.rerun()
