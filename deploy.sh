#!/bin/bash

# Script de despliegue para Ubuntu 20.04 LTS
# Ejecutar con: sudo bash deploy.sh

set -e

echo "🚀 Iniciando despliegue de la aplicación Streamlit..."

# Variables
APP_NAME="llm-chat-app"
APP_USER="streamlit"
APP_DIR="/opt/$APP_NAME"
PYTHON_VERSION="3.8"

# Colores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Verificar si se ejecuta como root
if [[ $EUID -ne 0 ]]; then
   print_error "Este script debe ejecutarse como root (sudo)"
   exit 1
fi

# Actualizar sistema
print_status "Actualizando sistema..."
apt update && apt upgrade -y

# Instalar dependencias del sistema
print_status "Instalando dependencias del sistema..."
apt install -y python3 python3-pip python3-venv nginx supervisor ufw

# Crear usuario para la aplicación
print_status "Creando usuario para la aplicación..."
if ! id "$APP_USER" &>/dev/null; then
    useradd -m -s /bin/bash $APP_USER
    print_status "Usuario $APP_USER creado"
else
    print_warning "Usuario $APP_USER ya existe"
fi

# Crear directorio de la aplicación
print_status "Creando directorio de la aplicación..."
mkdir -p $APP_DIR
chown $APP_USER:$APP_USER $APP_DIR

# Copiar archivos de la aplicación
print_status "Copiando archivos de la aplicación..."
cp -r . $APP_DIR/
chown -R $APP_USER:$APP_USER $APP_DIR

# Crear entorno virtual
print_status "Creando entorno virtual..."
sudo -u $APP_USER python3 -m venv $APP_DIR/venv

# Instalar dependencias de Python
print_status "Instalando dependencias de Python..."
sudo -u $APP_USER $APP_DIR/venv/bin/pip install --upgrade pip
sudo -u $APP_USER $APP_DIR/venv/bin/pip install -r $APP_DIR/requirements.txt

# Configurar variables de entorno
print_status "Configurando variables de entorno..."
if [ ! -f "$APP_DIR/.env" ]; then
    cp $APP_DIR/.env.example $APP_DIR/.env
    chown $APP_USER:$APP_USER $APP_DIR/.env
    print_warning "Archivo .env creado desde .env.example. Configura tus API keys."
fi

# Configurar firewall
print_status "Configurando firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8501

print_status "✅ Despliegue completado!"
print_warning "Pasos adicionales necesarios:"
echo "1. Configurar las API keys en $APP_DIR/.env"
echo "2. Configurar nginx: sudo systemctl enable nginx && sudo systemctl start nginx"
echo "3. Configurar supervisor: sudo systemctl enable supervisor && sudo systemctl start supervisor"
echo "4. Iniciar la aplicación: sudo systemctl start $APP_NAME"
echo "5. Habilitar inicio automático: sudo systemctl enable $APP_NAME"

print_status "La aplicación estará disponible en: http://tu-servidor:8501"