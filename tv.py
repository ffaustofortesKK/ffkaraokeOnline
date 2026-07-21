import streamlit as st
import requests
import time
import cloudinary
import cloudinary.search
import random

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
            background: black; display: flex; flex-direction: column; justify-content: center; align-items: center; z-index: 9999; 
        }
        
        /* Custom Controls Overlay para o vídeo em tela cheia */
        .custom-controls {
            position: absolute;
            bottom: 20px;
            width: 80%;
            background: rgba(0, 0, 0, 0.7);
            padding: 15px;
            border-radius: 10px;
            display: flex;
            align-items: center;
            gap: 15px;
            z-index: 10000;
            box-shadow: 0 4px 15px rgba(0,0,0,0.5);
        }
        .custom-controls button {
            background: #ffd700;
            border: none;
            color: black;
            font-weight: bold;
            padding: 8px 15px;
            border-radius: 5px;
            cursor: pointer;
            font-size: 1rem;
        }
        .custom-controls button:hover {
            background: #ffc700;
        }
        .custom-controls input[type=range] {
            cursor: pointer;
            accent-color: #ffd700;
        }
        .time-display {
            color: white;
            font-family: monospace;
            font-size: 1rem;
            min-width: 100px;
            text-align: center;
        }
        
        /* Caixa exata com 430x306px e borda amarela */
        .video-clipe-box { 
            width: 430px; 
            height: 306px;
            background: black; 
            padding: 0px; 
            border-radius: 4px; 
            border: 2px solid #ffd700; 
            overflow: hidden;
            display: flex;
            justify-content: center;
            align-items: center;
        }

        .video-clipe-box video {
            width: 100%;
            height: 100%;
            object-fit: fill; 
        }
        
        .contador-box { font-size: 8rem; color: yellow; font-weight: bold; text-shadow: 0 0 20px red; text-align: center; }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos_{slug}.json"

# Buscar dados do Firebase
try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_status = {}
    res_pedidos = {}

comando = res_status.get("comando")
url_video = res_status.get("url_video")

# Função para encontrar os vídeos da pasta "video_clipes"
def obter_video_clipe_da_pasta():
    try:
        search_result = cloudinary.search.Search()\
            .expression('folder=video_clipes AND resource_type:video')\
            .max_results(50)\
            .execute()
        
        lista = search_result.get('resources', [])
        if lista:
            return random.choice(lista)['secure_url']
    except Exception as e:
        print("Erro na busca avançada Cloudinary:", e)
    
    try:
        fallback = cloudinary.api.resources(type="upload", resource_type="video", max_results=50)
        geral = fallback.get('resources', [])
        if geral:
            return random.choice(geral)['secure_url']
    except:
        pass
        
    return None

# 1. EXIBIÇÃO DO VÍDEO DE KARAOKE EM TELA CHEIA COM CONTROLES CUSTOMIZADOS DE SOM, SEEKBAR E PRÓXIMA MÚSICA
if comando == "play":
    if url_video:
        st.markdown(f"""
            <div class="video-container" id="container-video">
                <video id="karaoke-video" playsinline>
                    <source src="{url_video}" type="video/mp4">
                    O seu navegador não suporta reprodução de vídeo.
                </video>
                
                <div class="custom-controls" id="controls-bar">
                    <button id="btn-play-pause" onclick="togglePlayPause()">⏸️ Pausa</button>
                    <span id="current-time" class="time-display">00:00 / 00:00</span>
                    <input type="range" id="seek-bar" value="0" min="0" max="100" step="0.1" style="flex-grow: 1;" oninput="mudarProgresso(this.value)">
                    <span style="color: white; font-weight: bold;">🔊 Som</span>
                    <input type="range" id="volume-bar" min="0" max="1" step="0.05" value="1" style="width: 100px;" oninput="mudarVolume(this.value)">
                    <button onclick="proximaMusicaForçada()" style="background: #ff4444; color: white;">⏭️ Avançar</button>
                </div>
            </div>
            
            <script>
                const vid = document.getElementById('karaoke-video');
                const seekBar = document.getElementById('seek-bar');
                const volumeBar = document.getElementById('volume-bar');
                const timeDisplay = document.getElementById('current-time');
                const btnPlayPause = document.getElementById('btn-play-pause');

                // Tenta iniciar a reprodução com som ativado por padrão
                vid.muted = false;
                vid.play().catch(error => {
                    console.log("Autoplay com som bloqueado pelo navegador, tentando com mudo automático...", error);
                    vid.muted = true;
                    vid.play();
                    volumeBar.value = 0;
                });

                function formatarTempo(segundos) {
                    let m = Math.floor(segundos / 60);
                    let s = Math.floor(segundos % 60);
                    return (m < 10 ? "0" + m : m) + ":" + (s < 10 ? "0" + s : s);
                }

                vid.ontimeupdate = function() {
                    if (vid.duration) {
                        let progressoPercentual = (vid.currentTime / vid.duration) * 100;
                        seekBar.value = progressoPercentual;
                        timeDisplay.innerText = formatarTempo(vid.currentTime) + " / " + formatarTempo(vid.duration);
                    }
                };

                function togglePlayPause() {
                    if (vid.paused) {
                        vid.play();
                        btnPlayPause.innerText = "⏸️ Pausa";
                    } else {
                        vid.pause();
                        btnPlayPause.innerText = "▶️ Play";
                    }
                }

                function mudarProgresso(valor) {
                    if (vid.duration) {
                        let tempoNovo = (valor * vid.duration) / 100;
                        vid.currentTime = tempoNovo;
                    }
                }

                function mudarVolume(valor) {
                    vid.volume = valor;
                    vid.muted = (valor == 0);
                }

                function proximaMusicaForçada() {
                    fetch('{URL_STATUS}', {
                        method: 'PATCH',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({{ comando: 'fim', url_video: '', musica: '', cantor: '' }})
                    }).then(() => {
                        window.location.reload();
                    });
                }

                vid.onended = function() {
                    proximaMusicaForçada();
                };
            </script>
        """, unsafe_allow_html=True)

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

# 2. CONTAGEM DECRESCENTE (3, 2, 1, 0) ANTES DE ABRIR O KARAOKE
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

# 3. TELA PRINCIPAL: FILA DE ESPERA À ESQUERDA E VÍDEO CLIPE EM MINIATURA À DIREITA
else:
    cl1, cl2 = st.columns([1.4, 1.2])

    with cl1:
        st.markdown("<h1 style='color:gold; font-size: 2.2rem; margin-bottom: 15px;'>🎤 FILA DE ESPERA</h1>", unsafe_allow_html=True)
        
        if res_pedidos:
            pedidos_lista = list(res_pedidos.items())
            contador_exibicao = 1
            for p_id, p in pedidos_lista:
                if not str(p.get('musica', '')).startswith("PEDIDO:"):
                    st.markdown(f"<h3 style='margin: 10px 0; font-size: 1.3rem;'>{contador_exibicao}. <span class='cantor-style'>{str(p.get('cantor')).upper()}</span> ➔ <span class='musica-style'>{str(p.get('musica')).upper()}</span></h3>", unsafe_allow_html=True)
                    contador_exibicao += 1
            if contador_exibicao == 1:
                st.info("Ainda sem cantores na fila.")
        else:
            st.info("A fila está vazia. Envie músicas pelo telemóvel!")

    with cl2:
        st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
        
        url_clipe = obter_video_clipe_da_pasta()
        if url_clipe:
            # ID único e chave de controle para forçar o recarregamento limpo e evitar sobreposição de vídeos duplicados
            video_id_unico = f"vid_{abs(hash(url_clipe))}"
            st.markdown(f"""
                <div class="video-clipe-box">
                    <video id="{video_id_unico}" autoplay muted loop playsinline>
                        <source src="{url_clipe}" type="video/mp4">
                        Seu navegador não suporta vídeo.
                    </video>
                </div>
                <script>
                    // Força o reset de qualquer stream órfão para garantir que apenas um vídeo toque
                    const vElement = document.getElementById('{video_id_unico}');
                    if (vElement) {{
                        vElement.currentTime = 0;
                        vElement.play().catch(e => console.log("Autoplay bloqueado:", e));
                    }}
                </script>
            """, unsafe_allow_html=True)
        else:
            st.warning("Nenhum vídeo encontrado.")

    time.sleep(5)
    st.rerun()
