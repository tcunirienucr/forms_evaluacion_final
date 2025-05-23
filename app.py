import streamlit as st
import pandas as pd
import os
import re
from datetime import datetime
from openpyxl import load_workbook

st.title("📋 Formulario de Evaluación Final del Curso: Excel Intermedio")
st.subheader("Le agradecemos que complete el siguiente formulario con honestidad y claridad. Sus aportes serán sumamente útiles para el enriquecimiento de nuestros cursos")

def validar_correo(correo):
    return re.match(r"[^@]+@[^@]+\.[^@]+", correo)

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

# Inicializar session_state para inputs si no existen
campos = {
    "nombre": "", "edad": 0, "correo": "", "comentario": "",
    "provincia": "", "canton": "", "distrito": "", "grupo": "", "asististe": "Seleccione...", "motivo_ausencia": [],
    "clase_favorita": "", "clase_menos_gusto": "", "recomendaciones": "", "experiencia": "",
    "calificacion": 5, "interes_cursos": [], "otro_curso": ""
}
for key, default in campos.items():
    if key not in st.session_state:
        st.session_state[key] = default
        
if "form_enviado" not in st.session_state:
    st.session_state["form_enviado"] = False

# ✅ Verificación temprana de envío
if st.session_state["form_enviado"]:
    st.success("✅ ¡Gracias por enviar tu respuesta!")
    st.write("Podés cerrar esta ventana o volver más tarde si querés enviar otro formulario.")
    st.stop()

# Campos del formulario
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
    options=["Seleccione...", "Si", "No"],
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

archivo = "respuestas.xlsx"

col1, col2 = st.columns(2)

with col1:
    if st.button("Enviar"):
        # Validaciones
        if not nombre.strip():
            st.error("Por favor ingresa tu nombre completo.")
        elif not validar_correo(correo):
            st.error("Por favor ingresa un correo válido.")
        elif not provincia or not canton or not distrito:
            st.error("Por favor selecciona provincia, cantón y distrito.")
        elif not grupo:
            st.error("Por favor selecciona el grupo.")
        elif asististe == "Seleccione...":
            st.error("Por favor indica si asististe a las cuatro clases.")
        elif not motivo_ausencia:
            st.error("Por favor selecciona el motivo de ausencia.")
        elif not clase_favorita.strip():
            st.error("Por favor escribe cuál fue tu clase favorita.")
        elif not clase_menos_gusto.strip():
            st.error("Por favor escribe cuál fue la clase que menos te gustó.")
        elif not recomendaciones.strip():
            st.error("Por favor escribe tus recomendaciones.")
        elif not experiencia.strip():
            st.error("Por favor escribe tu experiencia general del curso.")
        else:
            nueva_respuesta = pd.DataFrame({
                'Nombre': [nombre],
                'Edad': [edad],
                'Correo': [correo],
                'Grupo': [grupo],
                'Asistió a todas las clases': [asististe],
                'Motivo de ausencia': [", ".join(motivo_ausencia)],
                'Clase favorita': [clase_favorita],
                'Clase que menos gustó': [clase_menos_gusto],
                'Recomendaciones': [recomendaciones],
                'Experiencia general': [experiencia],
                'Calificación curso': [calificacion],
                'Interés en otros cursos': [", ".join(interes_cursos) if interes_cursos else ""],
                'Otro curso deseado': [otro_curso],
                'Provincia': [provincia],
                'Cantón': [canton],
                'Distrito': [distrito],
                'Fecha': [datetime.now().strftime("%Y-%m-%d %H:%M:%S")]
            })

            # Guardar respuesta en archivo .xlsx
            if not os.path.exists(archivo):
                with pd.ExcelWriter(archivo, engine='openpyxl') as writer:
                    nueva_respuesta.to_excel(writer, index=False, sheet_name='Respuestas')
            else:
                existing_df = pd.read_excel(archivo)
                with pd.ExcelWriter(archivo, engine='openpyxl', mode='a', if_sheet_exists='overlay') as writer:
                    nueva_respuesta.to_excel(writer, index=False, header=False, startrow=len(existing_df) + 1, sheet_name='Respuestas')

            st.session_state["form_enviado"] = True

            # Limpiar campos del formulario
            for key in campos.keys():
                st.session_state[key] = campos[key]

            st.experimental_rerun()

if st.checkbox("Mostrar respuestas"):
    user = st.text_input("Usuario")
    password = st.text_input("Contraseña", type="password")

    usuario_correcto = "admin"
    contraseña_correcta = st.secrets["CONTRASENA_ADMIN"]

    if user == usuario_correcto and password == contraseña_correcta:
        if os.path.exists(archivo):
            st.write(pd.read_excel(archivo))
        else:
            st.write("Aún no hay respuestas.")
    else:
        st.warning("❌ Usuario o contraseña incorrectos")
