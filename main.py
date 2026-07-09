import streamlit as st
import requests
import datetime
import time

BASE_URL = "https://grupoffkaraoke-default-rtdb.firebaseio.com"
URL_SOLICITACOES = f"{BASE_URL}/solicitacoes.json"
URL_TOKENS = f"{BASE_URL}/tokens.json"

if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- FUNÇÃO ADMIN ---
def painel_admin():
    st.header("⚙️ Painel do Operador")
    if st.button("🔄 Atualizar Lista"): st.rerun()
    
    solics = requests.get(URL_SOLICITACOES).json()
    if not solics:
        st.write("Nenhuma solicitação.")
        return

    for key, info in solics.items():
        usuario = info.get('usuario')
        estado = info.get('estado', 'Pendente')
        
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(f"👤 {usuario} - **{estado}**")
        
        if estado == "Pendente":
            if col2.button("✅ Aprovar", key=f"apr_{key}"):
                expira = (datetime.datetime.now() + datetime.timedelta(hours=3)).isoformat()
                requests.patch(f"{BASE_URL}/tokens/{usuario}.json", json={"senha": "123", "expira": expira})
                requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Aprovado"})
                st.rerun()
            if col3.button("❌ Recusar", key=f"rec_{key}"):
                requests.patch(f"{URL_SOLICITACOES}/{key}.json", json={"estado": "Recusado"})
                st.rerun()

# --- FUNÇÃO CLIENTE ---
def area_cliente():
    if not st.session_state.autenticado:
        st.subheader("🔑 Acesso ao Karaoke")
        nome = st.text_input("Seu Nome:")
        if st.button("Solicitar Acesso"):
            requests.post(URL_SOLICITACOES, json={"usuario": nome, "estado": "Pendente"})
            st.session_state.nome_temp = nome
            st.session_state.aguardando = True
            st.rerun()

        if st.session_state.get('aguardando'):
            st.info(f"Aguardando aprovação para {st.session_state.nome_temp}...")
            # O cliente verifica o estado a cada 3 segundos
            time.sleep(3)
            solics = requests.get(URL_SOLICITACOES).json()
            for key, info in (solics or {}).items():
                if info.get('usuario') == st.session_state.nome_temp:
                    if info.get('estado') == "Aprovado":
                        st.session_state.autenticado = True
                        st.session_state.nome = st.session_state.nome_temp
                        st.session_state.aguardando = False
                        st.rerun()
                    elif info.get('estado') == "Recusado":
                        st.error("Pedido recusado.")
                        st.session_state.aguardando = False
    else:
        # Acesso Aprovado - Mostrar contador
        token_data = requests.get(f"{URL_TOKENS}/{st.session_state.nome}.json").json()
        if not token_data: st.error("Erro no token."); return
        
        expira = datetime.datetime.fromisoformat(token_data.get('expira'))
        if datetime.datetime.now() > expira:
            st.error("Tempo esgotado!"); st.session_state.autenticado = False
        else:
            st.success(f"Bem-vindo, {st.session_state.nome}!")
            resta = expira - datetime.datetime.now()
            st.metric("Tempo restante", str(resta).split('.')[0])
            st.button("Sair", on_click=lambda: st.session_state.update(autenticado=False))

# --- LÓGICA PRINCIPAL ---
if st.session_state.get('nome') == "ADMIN": painel_admin()
else: area_cliente()
