import streamlit as st
import requests
import datetime

# --- CONFIGURAÇÕES ---
URL_FIREBASE_TOKENS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/tokens.json"
URL_FIREBASE_PEDIDOS = "https://grupoffkaraoke-default-rtdb.firebaseio.com/pedidos.json"
URL_FIREBASE_CATALOGO = "https://grupoffkaraoke-default-rtdb.firebaseio.com/catalogo.json"
URL_FIREBASE_SOLICITACOES = "https://grupoffkaraoke-default-rtdb.firebaseio.com/solicitacoes.json"

# --- FUNÇÕES ---
def validar_senha_no_firebase(nome, senha_input):
    if nome == "ADMIN": return True
    try:
        resp = requests.get(URL_FIREBASE_TOKENS)
        dados = resp.json()
        if dados and nome in dados:
            if dados[nome].get('senha') == senha_input:
                expira = datetime.datetime.fromisoformat(dados[nome].get('expira'))
                return datetime.datetime.now() < expira
        return False
    except: return False

# --- INTERFACE ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.subheader("🔑 Acesso ao Karaoke")
    nome_usuario = st.text_input("Nome:")
    senha_usuario = st.text_input("Código de Acesso:", type="password")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Entrar"):
            if validar_senha_no_firebase(nome_usuario, senha_usuario):
                st.session_state.nome = nome_usuario
                st.session_state.autenticado = True
                st.rerun()
            else:
                st.error("Código inválido ou expirado!")
    with col2:
        if st.button("Registar / Solicitar Acesso"):
            if nome_usuario:
                requests.post(URL_FIREBASE_SOLICITACOES, 
                              json={"usuario": nome_usuario, "timestamp": str(datetime.datetime.now())})
                st.success("Pedido enviado! Aguarde o operador.")
            else:
                st.warning("Digite o seu nome primeiro!")
else:
    # --- PAINEL DO OPERADOR ---
    if st.session_state.nome == "ADMIN":
        st.header("⚙️ Painel do Operador")
        
        # Leitura forçada do Firebase para depuração
        st.subheader("📩 Solicitações")
        try:
            solics = requests.get(URL_FIREBASE_SOLICITACOES).json()
            st.write(solics if solics else "Nenhuma solicitação.")
        except: st.write("Erro ao ler solicitações.")
        
        st.subheader("🎵 Pedidos")
        try:
            peds = requests.get(URL_FIREBASE_PEDIDOS).json()
            st.write(peds if peds else "Fila vazia.")
        except: st.write("Erro ao ler pedidos.")
        
        if st.button("Limpar Tudo"):
            requests.delete(URL_FIREBASE_SOLICITACOES)
            requests.delete(URL_FIREBASE_PEDIDOS)
            st.rerun()
    else:
        # --- APP DO CLIENTE ---
        st.title(f"Bem-vindo, {st.session_state.nome}!")
        busca = st.text_input("🔍 Pesquisar Música:")
        if busca:
            # ... (código de busca que você já tinha)
