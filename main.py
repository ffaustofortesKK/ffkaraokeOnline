import streamlit as st
import requests
import datetime
import time

BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_SOLICITACOES = f"{BASE_URL}/solicitacoes.json"
URL_TOKENS = f"{BASE_URL}/tokens.json"

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- PAINEL DO ADMIN ---
if st.session_state.get('nome') == "ADMIN":
    st.header("⚙️ Painel de Aprovação")
    if st.button("🔄 Refresh"): st.rerun()
    
    solics = requests.get(URL_SOLICITACOES).json()
    if solics:
        for key, info in solics.items():
            # Filtra apenas pendentes para mostrar na lista
            estado = info.get('estado', 'Pendente')
            if estado == "Pendente":
                col1, col2, col3 = st.columns([2, 1, 1])
                col1.write(f"👤 {info['usuario']}")
                if col2.button("✅ Aprovar", key=f"apr_{key}"):
                    expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                    requests.patch(f"{BASE_URL}/tokens/{info['usuario']}.json", json={"senha": "123", "expira": expira})
                    requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Aprovado"})
                    st.rerun()
                if col3.button("❌ Recusar", key=f"rec_{key}"):
                    requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Recusado"})
                    st.rerun()
            else:
                st.write(f"✅ {info['usuario']} - {estado}")
    else: st.write("Nenhum pedido pendente.")

# --- ÁREA DO CLIENTE ---
elif not st.session_state.autenticado:
    st.subheader("🔑 Acesso ao Karaoke")
    nome = st.text_input("Seu Nome:")
    if st.button("Solicitar Acesso"):
        requests.post(URL_SOLICITACOES, json={"usuario": nome, "estado": "Pendente"})
        st.session_state.nome_temp = nome
        st.session_state.aguardando = True

    if st.session_state.get('aguardando'):
        st.info("Aguardando aprovação...")
        time.sleep(3)
        solics = requests.get(URL_SOLICITACOES).json()
        for key, info in (solics or {}).items():
            if info.get('usuario') == st.session_state.nome_temp:
                if info.get('estado') == "Aprovado":
                    st.session_state.autenticado = True
                    st.session_state.nome = st.session_state.nome_temp
                    st.rerun()
                elif info.get('estado') == "Recusado":
                    st.error("Pedido recusado.")
                    st.session_state.aguardando = False
else:
    # --- VERIFICAÇÃO DE TEMPO (3 HORAS) ---
    token_data = requests.get(f"{URL_TOKENS}/{st.session_state.nome}.json").json()
    expira = datetime.datetime.fromisoformat(token_data.get('expira', datetime.datetime.now().isoformat()))
    
    if datetime.datetime.now() > expira:
        st.error("Tempo esgotado! Seu acesso expirou.")
        if st.button("Sair"):
            st.session_state.autenticado = False
            st.rerun()
    else:
        st.success(f"Bem-vindo, {st.session_state.nome}!")
        tempo_restante = expira - datetime.datetime.now()
        st.write(f"⏱️ Tempo restante: {str(tempo_restante).split('.')[0]}")
