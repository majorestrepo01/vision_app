import os
import base64
import streamlit as st
from openai import OpenAI

# 1. Configuración de la página
st.set_page_config(
    page_title="Análisis de Imagen IA",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS ligeros
st.markdown("""
    <style>
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
    }
    </style>
""", unsafe_allow_html=True)

# Función para codificar la imagen en base64
def encode_image(image_file):
    return base64.b64encode(image_file.getvalue()).decode("utf-8")

# 2. Barra lateral para configuración
with st.sidebar:
    st.title("⚙️ Configuración")
    st.caption("Inserta tu API Key para activar las funciones de análisis visual.")
    
    ke = st.text_input('Clave API de OpenAI', type="password", help="Tu API Key no se guarda en ningún servidor.")
    
    if ke:
        os.environ['OPENAI_API_KEY'] = ke
        st.success("API Key cargada", icon="✅")
    else:
        st.warning("Ingresa tu API Key de OpenAI para comenzar", icon="🔑")
        
    st.markdown("---")
    st.caption("Powered by `gpt-4o` 🚀")

# 3. Panel Principal
st.title("Visión por Computadora con IA 🤖🖼️")
st.write("Sube cualquier imagen para obtener un análisis descriptivo detallado o haz preguntas específicas sobre ella.")

st.markdown("---")

# Layout de 2 columnas principales
col_left, col_right = st.columns([1, 1], gap="large")

with col_left:
    st.subheader("1. Cargar Imagen")
    uploaded_file = st.file_uploader(
        "Selecciona una imagen (JPG, PNG, JPEG)", 
        type=["jpg", "png", "jpeg"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.image(uploaded_file, caption=uploaded_file.name, use_container_width=True)

with col_right:
    st.subheader("2. Opciones de Análisis")
    
    # Toggle para agregar contexto o pregunta específica
    show_details = st.toggle("¿Quieres hacer una pregunta específica?", value=False)

    additional_details = ""
    if show_details:
        additional_details = st.text_area(
            "Pregunta o contexto adicional:",
            placeholder="Ej. ¿Qué marca es la computadora que aparece sobre la mesa?",
            height=100
        )

    st.markdown("<br>", unsafe_allow_html=True)
    analyze_button = st.button("🚀 Analizar Imagen", type="primary")

# 4. Procesamiento y Resultado
if analyze_button:
    if not ke:
        st.error("Por favor ingresa tu API Key en la barra lateral antes de continuar.")
    elif not uploaded_file:
        st.warning("Por favor sube una imagen primero.")
    else:
        st.markdown("---")
        st.subheader("3. Resultado del Análisis")
        
        # Inicializar cliente de OpenAI
        client = OpenAI(api_key=ke)

        with st.spinner("Analizando imagen..."):
            try:
                base64_image = encode_image(uploaded_file)

                # Construcción del prompt
                prompt_text = "Describe lo que ves en la imagen detalladamente en español."
                if show_details and additional_details.strip():
                    prompt_text = f"Responde a la siguiente pregunta/contexto sobre la imagen en español: {additional_details}"

                messages = [
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt_text},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}"
                                }
                            },
                        ],
                    }
                ]

                # Contenedor para mostrar la respuesta en tiempo real
                response_container = st.container()
                with response_container:
                    message_placeholder = st.empty()
                    full_response = ""

                    for completion in client.chat.completions.create(
                        model="gpt-4o",
                        messages=messages,
                        max_tokens=1200,
                        stream=True
                    ):
                        if completion.choices[0].delta.content is not None:
                            full_response += completion.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")

                    message_placeholder.markdown(full_response)

            except Exception as e:
                st.error(f"Error al procesar la solicitud: {str(e)}")
