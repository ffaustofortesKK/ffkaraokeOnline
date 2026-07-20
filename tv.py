import streamlit as st
import requests
import time

st.set_page_config(page_title="FF KARAOKE - TV", layout="wide")

st.markdown("""
    <style>
        .stApp { background: black; }
        #MainMenu {visibility: hidden;} footer {visibility: hidden;}
        .cantor-style { color: white; font-weight: bold; text-shadow: 3px 3px 6px #000; }
        .musica-style { color: yellow; font-weight: bold; text-shadow: 2px 2px 4px #000; }
        .destaque-container { 
            display: flex; 
            justify-content: center; 
            align-items: center; 
            flex-direction: column; 
            height: 60vh; 
            text-align: center;
            border: 5px solid #d4af37;
            border-radius: 20px;
            background: linear-gradient(135deg, #141416 0%, #1a1a1e 100%);
            margin: 20px auto;
            width: 85%;
            box-shadow: 0px 0px 30px rgba(212, 175, 55, 0.3);
        }
        .fila-container { 
            background: rgba(20,20,22,0.9); 
            padding: 20px; 
            border-radius: 15px; 
            color: white; 
            width: 85%; 
            margin: 10px auto;
            border: 1px solid #333333;
        }
    </style>
""", unsafe_allow_html=True)

params = st.query_params
slug = params.get("prestador", "geral")

# URLs unificadas em sintonia com o painel de controlo desktop e cliente
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"
URL_PEDIDOS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos.json"

# Buscar dados em tempo real
try:
    res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}", timeout=5).json() or {}
    res_pedidos = requests.get(f"{URL_PEDIDOS}?nocache={time.time()}", timeout=5).json() or {}
except:
    res_status = {}
    res_pedidos = {}

comando = res_status.get("comando")
cantor_atual = str(res_status.get("cantor", "")).upper()
musica_atual = str(res_status.get("musica", "")).upper()

# 1. ESTADO DE REPRODUÇÃO / CANTO A DECORRER
if comando in ["play", "aguardando_play"]:
    st.markdown(f"""
        <div class="destaque-container">
            <h2 style="color: #d4af37; font-family: Arial, sans-serif; letter-spacing: 2px; margin-bottom: 10px;">🎤 NO PALCO AGORA</h2>
            <h1 class="cantor-style" style="font-size: 50px; margin: 10px 0;">{cantor_atual if cantor_atual else "CANTOR"}</h1>
            <h3 class="musica-style" style="font-size: 30px; margin: 5px 0;">{musica_atual if musica_atual else "A PREPARAR..."}</h3>
            <p style="color: #00ffcc; font-size: 18px; margin-top: 15px; font-weight: bold;">(Acompanhe o vídeo no ecrã principal do espaço)</p>
        </div>
    """, unsafe_allow_html=True)

# 2. CABEÇALHO PADRÃO QUANDO NÃO HÁ NINGUÉM NO PALCO
else:
    st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="color: white; font-family: 'Arial Black', sans-serif; font-size: 45px; text-shadow: 2px 2px 4px #000;">FF KARAOKE</h1>
            <p style="color: #d4af37; font-size: 20px; font-weight: bold;">Escolha a sua música no telemóvel e prepare a voz!</p>
        </div>
    """, unsafe_allow_html=True)

# 3. LISTA DA FILA DE ESPERA
if res_pedidos:
    st.markdown("<div class='fila-container'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color: #d4af37; margin-bottom: 15px;'>📋 Fila de Espera Atual:</h3>", unsafe_allow_html=True)
    pedidos_lista = list(res_pedidos.items())
    for i, (p_id, p) in enumerate(pedidos_lista, 1):
        st.markdown(f"#### {i}. <span class='cantor-style'>{p.get('cantor')}</span> — <span class='musica-style'>{p.get('musica')}</span>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# Atualização automática contínua
time.sleep(2)
st.rerun()
