import streamlit as st
import pandas as pd
import random
import unicodedata
import re
import time

# --------------------------
# CONFIGURACIÓN INICIAL
# --------------------------
st.set_page_config(page_title="Pasapalabra", page_icon="🧠")
st.title("🎮 Pasapalabra - Ciencia de Datos")

# --------------------------
# FUNCIONES DE SOPORTE
# --------------------------

# Normaliza texto para comparación flexible
def normalizar(texto):
    texto = texto.lower().strip()
    texto = unicodedata.normalize('NFD', texto)
    texto = texto.encode('ascii', 'ignore').decode("utf-8")
    texto = re.sub(r'[^a-z0-9]', '', texto)
    return texto

# Carga preguntas y selecciona una por letra
@st.cache_data
def cargar_preguntas():
    df = pd.read_csv("data/preguntas_pasapalabra_final.csv")
    letras = sorted(df["letra"].unique())
    preguntas = []
    for letra in letras:
        subset = df[df["letra"] == letra]
        if not subset.empty:
            pregunta = subset.sample(1).iloc[0]
            preguntas.append({
                "letra": letra,
                "definicion": pregunta["definicion"],
                "respuesta": pregunta["concepto"],
                "tipo": pregunta["tipo_letra"]
            })
    return preguntas

# --------------------------
# ESTADO DE SESIÓN
# --------------------------
if "preguntas" not in st.session_state:
    st.session_state.preguntas = cargar_preguntas()
    st.session_state.indice = 0
    st.session_state.puntaje = 0
    st.session_state.estados = {}
    for p in st.session_state.preguntas:
        st.session_state.estados[p["letra"]] = "pendiente"

if "inicio" not in st.session_state:
    st.session_state.inicio = time.time()

if "tiempo_restante" not in st.session_state:
    st.session_state.tiempo_restante = 150  # segundos

# --------------------------
# TEMPORIZADOR
# --------------------------
tiempo_transcurrido = time.time() - st.session_state.inicio
st.session_state.tiempo_restante = int(150 - tiempo_transcurrido)

if st.session_state.tiempo_restante > 0:
    st.markdown(f"⏱️ Tiempo restante: **{st.session_state.tiempo_restante}** segundos")
else:
    st.warning("⏰ ¡Se acabó el tiempo!")
    st.success("🎉 Juego terminado por tiempo")
    st.write(f"Puntaje final: **{st.session_state.puntaje} / {len(st.session_state.preguntas)}**")
    if st.button("Jugar otra vez"):
        st.session_state.clear()
        st.rerun()
    st.stop()

# --------------------------
# ROSCO VISUAL
# --------------------------
st.markdown("### 🔤 Estado del rosco")

estado_colores = {
    "pendiente": "gray",
    "correcto": "green",
    "incorrecto": "red",
    "pasapalabra": "orange"
}

cols = st.columns(13)
letras = sorted(st.session_state.estados.keys())

for i, letra in enumerate(letras):
    estado = st.session_state.estados[letra]
    color = estado_colores[estado]
    cols[i % 13].markdown(
        f"<div style='text-align:center; border-radius:50%; background:{color}; width:30px; height:30px; line-height:30px; color:white; font-weight:bold;'>{letra}</div>",
        unsafe_allow_html=True
    )

# --------------------------
# PREGUNTA ACTUAL
# --------------------------
preguntas = st.session_state.preguntas
indice = st.session_state.indice

if indice < len(preguntas):
    actual = preguntas[indice]
    letra = actual["letra"]
    tipo = actual["tipo"]
    definicion = actual["definicion"]
    respuesta_correcta = actual["respuesta"]

    st.markdown(f"### {'Con la letra' if tipo == 'empieza' else 'Contiene la letra'} **{letra}**")
    st.write(definicion)

    respuesta = st.text_input("Tu respuesta:", key=f"respuesta_{indice}")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Responder"):
            if normalizar(respuesta) == normalizar(respuesta_correcta):
                st.success("✅ ¡Correcto!")
                st.session_state.puntaje += 1
                st.session_state.estados[letra] = "correcto"
            else:
                st.error(f"❌ Incorrecto. La respuesta era: {respuesta_correcta}")
                st.session_state.estados[letra] = "incorrecto"
            st.session_state.indice += 1
            st.rerun()

    with col2:
        if st.button("Pasapalabra"):
            st.session_state.estados[letra] = "pasapalabra"
            st.session_state.preguntas.append(actual)
            st.session_state.indice += 1
            st.rerun()
else:
    st.success("🎉 ¡Juego terminado!")
    st.write(f"Puntaje final: **{st.session_state.puntaje} / {len(preguntas)}**")
    if st.button("Jugar otra vez"):
        st.session_state.clear()
        st.rerun()