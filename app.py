import streamlit as st
import requests
import json
import os
from typing import Dict, Any
import time

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
            "x-api-key": ""
        },
        "model": "claude-3-sonnet-20240229"
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
        st.session_state.api_key = ""

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
        response = requests.post(
            config["url"],
            headers=headers,
            json=payload,
            timeout=30
        )
        response.raise_for_status()
        return {"success": True, "data": response.json()}
    
    except requests.exceptions.RequestException as e:
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
            index=0 if st.session_state.api_provider == "anthropic" else 1
        )
        
        # Input para API key
        api_key = st.text_input(
            "API Key",
            type="password",
            value=st.session_state.api_key,
            help="Ingresa tu API key del proveedor seleccionado"
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