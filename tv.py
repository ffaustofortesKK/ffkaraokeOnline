import streamlit as st
import requests
import time
import streamlit.components.v1 as components

params = st.query_params
slug = params.get("prestador")
URL_STATUS = f"https://grupoffkaraoke-default-rtdb.firebaseio.com/status_{slug}.json"

res_status = requests.get(f"{URL_STATUS}?nocache={time.time()}").json() or {}
comando = res_status.get("comando")

if comando == "play":
    url = res_status.get("url_video")
    components.html(f'<video autoplay src="{url}" width="100%"></video>', height=500)
elif comando == "aguardando_play":
    st.title(f"VEZ DE: {res_status.get('cantor')}")
    st.subheader("Aguardando o cantor carregar no telemóvel...")
else:
    st.title("FF KARAOKE")
time.sleep(2); st.rerun()
