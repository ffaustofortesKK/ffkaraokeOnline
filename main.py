import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
URL_FIREBASE_TOKENS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/tokens.json"
URL_FIREBASE_PEDIDOS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos.json"
URL_FIREBASE_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"
URL_FIREBASE_SOLICITACOES = "https://grupoffkaraoke-default-rtdb.firebaseio.com/solicitacoes.json"
URL_SOM_PALMAS = "https://www.soundjay.com/misc/sounds/applause-2.mp3"

# --- FUNÇÃO DE VALIDAÇÃO ---
def validar_senha_no_firebase(nome, senha_input):
    try:
        if nome == "ADMIN": return True 
        resp = requests.get(URL_FIREBASE_TOKENS)
        dados = resp.json()
        if dados and nome in dados:
            token_data = dados[nome]
            if token_data.get('senha') == senha_input:
                expira = datetime.datetime.fromisoformat(token_data.get('expira'))
                if datetime.datetime.now() < expira:
                    return True
        return False
    except: return False

# --- LÓGICA DE ESTADO ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

# --- INTERFACE DE LOGIN ---
if not st.session_state.autenticado:
    st.subheader("🔑 Acesso ao Karaoke")
    nome_usuario = st.text_input("Nome:")
    senha_usuario = st.text_input("Código de Acesso:", type="password")
    
    if st.button("Entrar"):
        if validar_senha_no_firebase(nome_usuario, senha_usuario):
            st.session_state.nome = nome_usuario
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Código inválido ou expirado!")
            if st.button("Solicitar Acesso"):
                requests.post(URL_FIREBASE_SOLICITACOES, 
                              json={"usuario": nome_usuario, "timestamp": str(datetime.datetime.now())})
                st.info("Pedido enviado! Aguarde o operador.")
else:
    # --- PAINEL DO OPERADOR (ADMIN) ---
    if st.session_state.nome == "ADMIN":
        st.header("⚙️ Painel do Operador")
        
        # Mostrar Solicitações
        st.subheader("📩 Solicitações de Acesso")
        req_solic = requests.get(URL_FIREBASE_SOLICITACOES).json()
        st.write(req_solic if req_solic else "Nenhuma solicitação.")
        
        # Mostrar Pedidos
        st.subheader("🎵 Fila de Músicas")
        req_pedidos = requests.get(URL_FIREBASE_PEDIDOS).json()
        st.write(req_pedidos if req_pedidos else "Fila vazia.")
        
        if st.button("Limpar Tudo"):
            requests.delete(URL_FIREBASE_SOLICITACOES)
            requests.delete(URL_FIREBASE_PEDIDOS)
            st.rerun()
    
    # --- APP DO CLIENTE ---
    else:
        st.title(f"Bem-vindo, {st.session_state.nome}!")
        busca = st.text_input("🔍 Pesquisar Música:")
        if busca:
            try:
                resp = requests.get(URL_FIREBASE_CATALOGO, timeout=5)
                dados = resp.json()
                cat = list(dados.keys()) if isinstance(dados, dict) else dados
                resultados = [m for m in cat if busca.lower() in m.lower()]
                escolha = st.selectbox("Selecione:", resultados)
                if escolha and st.button("Confirmar Pedido"):
                    requests.post(URL_FIREBASE_PEDIDOS, json={"cantor": st.session_state.nome, "musica": escolha})
                    st.audio(URL_SOM_PALMAS, autoplay=True)
                    st.success("Pedido enviado!")
            except: st.error("Erro ao carregar catálogo.")
