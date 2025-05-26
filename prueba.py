# streamlit_app.py

import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os
import re
from datetime import datetime
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
#Conectar a la hoja de Google.

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

json_creds = st.secrets["connections"]["gsheets"]
creds_dict = json.loads(json_creds)  # convertir string JSON a dict

creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)

sh = client.open('Formularios de evaluación final').worksheet('prueba2')

#Función para validar correo
def validar_correo(correo):
    return re.match(r"[^@]+@[^@]+\.[^@]+", correo)
#Función para organizar provincia, cantón, distrito
@st.cache_data
def cargar_ubicaciones(ruta):
    df = pd.read_excel(ruta)
    df['Provincia'] = df['Provincia'].str.strip()
    df['Cantón'] = df['Cantón'].str.strip()
    df['Distrito'] = df['Distrito'].str.strip()
    return df

archivo_ubicaciones = "división_territorial_CR.xlsx"
if not os.path.exists(archivo_ubicaciones):
    st.error("Archivo de ubicaciones no encontrado. Por favor, sube el archivo 'ubicaciones.xlsx' con las columnas Provincia, Cantón y Distrito.")
    st.stop()

df_ubicaciones = cargar_ubicaciones(archivo_ubicaciones)

#Contenido del formulario
st.title("📋 Formulario de Evaluación Final del Curso: Excel Intermedio")
st.subheader("Le agradecemos que complete el siguiente formulario con honestidad y claridad. Sus aportes serán sumamente útiles para el enriquecimiento de nuestros cursos")

st.write("Datos actuales en la hoja:")
st.write(df)

#Contenido del formulario
nombre = st.text_input("Nombre completo", key="nombre")
edad = st.number_input("Edad", 0, 120, key="edad")
correo = st.text_input("Correo electrónico", key="correo")
grupo = st.selectbox(
    "¿Cuál es el número de grupo donde te inscribiste? *",
    options=["", "Grupo 01: martes", "Grupo 02: jueves", "ACTIM"],
    key="grupo"
)
asististe = st.radio(
    "¿Asististe a las cuatro clases? *",
    options=["Si", "No"],
    key="asististe"
)
motivo_ausencia = st.multiselect(
    "Si faltaste a algunas de las clases, ¿por qué fue? *",
    options=[
        "Tuve problemas de internet",
        "Tuve que atender otras situaciones",
        "Sentía que las clases no me eran útiles",
        "No entendía la materia",
        "No me gustaban las clases",
        "El horario me resultaba muy incómodo",
        "No falté a ninguna clase",
        "Otros"
    ],
    key="motivo_ausencia"
)
clase_favorita = st.text_area("¿Cuál de las clases te gustó más? Porfa contanos por qué *", key="clase_favorita")
clase_menos_gusto = st.text_area("¿Cuál de las clases te gustó menos? Porfa contanos por qué *", key="clase_menos_gusto")
recomendaciones = st.text_area("¿Qué recomendaciones nos harías para el futuro? *", key="recomendaciones")
experiencia = st.text_area("¿Podrías escribir unas pocas líneas comentándonos tu experiencia y resumiéndonos cuál ha sido tu apreciación general del curso? *", key="experiencia")
calificacion = st.slider(
    "En general, ¿qué calificación le das al curso? Donde 1 es la peor nota y 10 es la mejor nota o excelente",
    1, 10,
    step=1,
    format="%d",
    key="calificacion"
)
interes_cursos = st.multiselect(
    "Interés por otros cursos que impartimos y que no hayas llevado (puedes llenar todas las que gustes).",
    options=[
        "Economía para la Vida para menores de 20 años",
        "Redacción Consciente",
        "Economía para entender el Mercado y la Sociedad",
        "Indicadores Macroeconómicos",
        "Ninguno"
    ],
    key="interes_cursos"
)
otro_curso = st.text_input("¿Qué otro curso te gustaría recibir de manera virtual?", key="otro_curso")

# Select provincia
provincias = df_ubicaciones['Provincia'].unique()
provincia = st.selectbox("Provincia", options=[""] + list(provincias), key="provincia")

# Select cantón según provincia
if provincia:
    cantones = df_ubicaciones[df_ubicaciones['Provincia'] == provincia]['Cantón'].unique()
else:
    cantones = []
canton = st.selectbox("Cantón", options=[""] + list(cantones), key="canton")

# Select distrito según cantón
if canton:
    distritos = df_ubicaciones[(df_ubicaciones['Provincia'] == provincia) & (df_ubicaciones['Cantón'] == canton)]['Distrito'].unique()
else:
    distritos = []
distrito = st.selectbox("Distrito", options=[""] + list(distritos), key="distrito")

#Revisar envío
if st.button("Enviar formulario"):
# Validaciones
    if not nombre.strip():
        st.warning("Por favor ingresa tu nombre completo.")
    elif not validar_correo(correo):
        st.warning("Por favor ingresa un correo válido.")
    elif not provincia or not canton or not distrito:
        st.warning("Por favor selecciona provincia, cantón y distrito.")
    elif not grupo:
        st.warning("Por favor selecciona el grupo.")
    elif asististe == "Seleccione...":
        st.warning("Por favor indica si asististe a las cuatro clases.")
    elif not motivo_ausencia:
        st.warning("Por favor selecciona el motivo de ausencia.")
    elif not clase_favorita.strip():
        st.warning("Por favor escribe cuál fue tu clase favorita.")
    elif not clase_menos_gusto.strip():
        st.warning("Por favor escribe cuál fue la clase que menos te gustó.")
    elif not recomendaciones.strip():
        st.warning("Por favor escribe tus recomendaciones.")
    elif not experiencia.strip():
        st.warning("Por favor escribe tu experiencia general del curso.")
    else:
        nueva_fila=[nombre, edad, correo, grupo, asististe, motivo_ausencia, clase_favorita, clase_menos_gusto, recomendaciones, experiencia, calificacion, interes_cursos, otro_curso, provincia, canton, distrito[
        sh.append_row(nueva_fila)



    
