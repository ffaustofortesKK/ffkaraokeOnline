import streamlit as st
import requests
import datetime

# Função para validar a senha no Firebase
def validar_senha_no_firebase(nome, senha_input):
    try:
        # Busca tokens no seu Firebase
        resp = requests.get("https://grupoffkaraoke-default-rtdb.firebaseio.com/tokens.json")
        dados = resp.json()
        if dados and nome in dados:
            token_data = dados[nome]
            # Verifica se a senha bate e se não expirou
            if token_data['senha'] == senha_input:
                expira = datetime.datetime.fromisoformat(token_data['expira'])
                if datetime.datetime.now() < expira:
                    return True
        return False
    except:
        return False

# --- Lógica de Entrada ---
if 'autenticado' not in st.session_state: st.session_state.autenticado = False

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
                # Envia o nome para o nó 'solicitacoes' no Firebase
                requests.post("https://grupoffkaraoke-default-rtdb.firebaseio.com/solicitacoes.json", 
                              json={"usuario": nome_usuario, "timestamp": str(datetime.datetime.now())})
                st.info("Pedido enviado! Aguarde o operador gerar o seu código.")
else:
    # ... (AQUI VAI O SEU CÓDIGO DO KARAOKE QUE JÁ TEMOS)
