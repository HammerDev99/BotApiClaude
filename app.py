import streamlit as st
import requests
import json
import os
from typing import Dict, Any
import time
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="LLM Chat Interface",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Configuración de la API
API_CONFIG = {
    "anthropic": {
        "url": "https://api.anthropic.com/v1/messages",
        "headers": {
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
            "x-api-key": ""
        },
        "model": "claude-3-haiku-20240307"
    },
    "openai": {
        "url": "https://api.openai.com/v1/chat/completions",
        "headers": {
            "Content-Type": "application/json",
            "Authorization": "Bearer "
        },
        "model": "gpt-3.5-turbo"
    }
}

def initialize_session_state():
    """Inicializa las variables de sesión"""
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'api_provider' not in st.session_state:
        st.session_state.api_provider = "anthropic"
    if 'api_key' not in st.session_state:
        # Intentar cargar la API key desde las variables de entorno
        if st.session_state.get('api_provider', 'anthropic') == 'anthropic':
            st.session_state.api_key = os.getenv('ANTHROPIC_API_KEY', '')
        else:
            st.session_state.api_key = os.getenv('OPENAI_API_KEY', '')

def make_api_request(provider: str, api_key: str, message: str) -> Dict[str, Any]:
    """Realiza una petición a la API del LLM"""
    config = API_CONFIG[provider]
    
    if provider == "anthropic":
        headers = config["headers"].copy()
        headers["x-api-key"] = api_key
        
        payload = {
            "model": config["model"],
            "max_tokens": 1000,
            "messages": [{"role": "user", "content": message}]
        }
    
    elif provider == "openai":
        headers = config["headers"].copy()
        headers["Authorization"] = f"Bearer {api_key}"
        
        payload = {
            "model": config["model"],
            "messages": [{"role": "user", "content": message}],
            "max_tokens": 1000
        }
    
    try:
        # Debug info
        st.write(f"🔍 **Debug:** Enviando request a {config['url']}")
        st.write(f"🔍 **Model:** {config['model']}")
        
        response = requests.post(
            config["url"],
            headers=headers,
            json=payload,
            timeout=30
        )
        
        # Debug response
        st.write(f"🔍 **Status Code:** {response.status_code}")
        
        if response.status_code != 200:
            error_detail = response.text
            st.error(f"API Error: {response.status_code}")
            st.code(error_detail)
            return {"success": False, "error": f"HTTP {response.status_code}: {error_detail}"}
        
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    
    except requests.exceptions.RequestException as e:
        st.error(f"Request Exception: {str(e)}")
        return {"success": False, "error": str(e)}
    except Exception as e:
        st.error(f"Unexpected Error: {str(e)}")
        return {"success": False, "error": str(e)}

def extract_response_text(provider: str, response_data: Dict[str, Any]) -> str:
    """Extrae el texto de respuesta según el proveedor"""
    try:
        if provider == "anthropic":
            return response_data["content"][0]["text"]
        elif provider == "openai":
            return response_data["choices"][0]["message"]["content"]
    except KeyError:
        return "Error: Formato de respuesta inesperado"

def main():
    """Función principal de la aplicación"""
    initialize_session_state()
    
    st.title("🤖 LLM Chat Interface")
    st.markdown("---")
    
    # Sidebar para configuración
    with st.sidebar:
        st.header("⚙️ Configuración")
        
        # Selector de proveedor
        provider = st.selectbox(
            "Proveedor LLM",
            ["anthropic", "openai"],
            index=0,  # Forzar anthropic por defecto
            help="Anthropic configurado con tu API key"
        )
        
        # Cargar API key automáticamente desde .env
        if provider == "anthropic":
            api_key = os.getenv('ANTHROPIC_API_KEY', '')
        elif provider == "openai":
            api_key = os.getenv('OPENAI_API_KEY', '')
        
        # Validar API key silenciosamente
        if not api_key or api_key in ["your_anthropic_api_key_here", "your_openai_api_key_here"]:
            st.error(f"❌ No se encontró API Key válida para {provider}")
            if provider == "anthropic":
                st.info("Configura ANTHROPIC_API_KEY en el archivo .env")
            else:
                st.info("Configura OPENAI_API_KEY en el archivo .env")
            # Opción manual como fallback
            api_key = st.text_input(
                "API Key (fallback)",
                type="password",
                help="Ingresa manualmente tu API key solo si no está en .env"
            )
        
        # Botón para limpiar chat
        if st.button("🗑️ Limpiar Chat"):
            st.session_state.messages = []
            st.rerun()
        
        # Información del modelo
        st.markdown("---")
        st.markdown("**Modelo actual:**")
        st.code(API_CONFIG[provider]["model"])
        
        # Actualizar session state
        st.session_state.api_provider = provider
        st.session_state.api_key = api_key
    
    # Área principal del chat
    chat_container = st.container()
    
    # Mostrar mensajes del chat
    with chat_container:
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
    
    # Input del usuario
    if prompt := st.chat_input("Escribe tu mensaje aquí..."):
        # Validar API key
        if not api_key:
            st.error("Por favor, ingresa tu API key en la configuración lateral.")
            return
        
        # Agregar mensaje del usuario
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Mostrar mensaje del usuario
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Mostrar mensaje del asistente
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Mostrar spinner mientras se procesa
            with st.spinner("Procesando..."):
                response = make_api_request(provider, api_key, prompt)
            
            if response["success"]:
                response_text = extract_response_text(provider, response["data"])
                message_placeholder.markdown(response_text)
                
                # Agregar respuesta al historial
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": response_text
                })
            else:
                error_message = f"Error: {response['error']}"
                message_placeholder.markdown(error_message)
                
                # Agregar error al historial
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": error_message
                })

if __name__ == "__main__":
    main()