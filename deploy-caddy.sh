#!/bin/bash

# Script de despliegue para Ubuntu 20.04 LTS con Caddy
# Ejecutar con: sudo bash deploy-caddy.sh

set -e

echo "🚀 Iniciando despliegue de la aplicación Streamlit con Caddy..."

# Variables
APP_NAME="llm-chat-app"
APP_USER="streamlit"
APP_DIR="/opt/$APP_NAME"
PYTHON_VERSION="3.8"
CADDY_CONFIG_DIR="/etc/caddy"

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
apt install -y python3 python3-pip python3-venv debian-keyring debian-archive-keyring apt-transport-https ufw curl

# Instalar Caddy
print_status "Instalando Caddy..."
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy

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

# Configurar systemd service para la aplicación
print_status "Configurando servicio systemd para la aplicación..."
cp $APP_DIR/llm-chat-app.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable $APP_NAME

# Configurar Caddy
print_status "Configurando Caddy..."
mkdir -p $CADDY_CONFIG_DIR
mkdir -p /var/log/caddy

# Respaldar configuración existente si existe
if [ -f "$CADDY_CONFIG_DIR/Caddyfile" ]; then
    cp $CADDY_CONFIG_DIR/Caddyfile $CADDY_CONFIG_DIR/Caddyfile.backup.$(date +%Y%m%d_%H%M%S)
    print_warning "Configuración existente respaldada"
fi

# Copiar nueva configuración
cp $APP_DIR/Caddyfile $CADDY_CONFIG_DIR/Caddyfile
chown caddy:caddy $CADDY_CONFIG_DIR/Caddyfile
chown -R caddy:caddy /var/log/caddy

# Configurar firewall
print_status "Configurando firewall..."
ufw --force enable
ufw allow ssh
ufw allow 80
ufw allow 443
ufw allow 8501

# Iniciar servicios
print_status "Iniciando servicios..."
systemctl start $APP_NAME
systemctl enable caddy
systemctl restart caddy

# Verificar estado de los servicios
print_status "Verificando servicios..."
if systemctl is-active --quiet $APP_NAME; then
    print_status "✅ Servicio $APP_NAME está corriendo"
else
    print_error "❌ Servicio $APP_NAME no está corriendo"
    systemctl status $APP_NAME
fi

if systemctl is-active --quiet caddy; then
    print_status "✅ Servicio Caddy está corriendo"
else
    print_error "❌ Servicio Caddy no está corriendo"
    systemctl status caddy
fi

print_status "✅ Despliegue completado!"
print_warning "Pasos adicionales necesarios:"
echo "1. Configurar las API keys en $APP_DIR/.env"
echo "2. Editar el dominio en $CADDY_CONFIG_DIR/Caddyfile"
echo "3. Reiniciar los servicios: sudo systemctl restart $APP_NAME caddy"
echo "4. Verificar logs: sudo journalctl -u $APP_NAME -f"
echo "5. Verificar logs de Caddy: sudo journalctl -u caddy -f"

print_status "La aplicación estará disponible en: http://tu-dominio.com"
print_status "Caddy se encargará automáticamente de obtener certificados SSL"

# Comandos útiles
print_status "Comandos útiles:"
echo "- Ver logs de la app: sudo journalctl -u $APP_NAME -f"
echo "- Ver logs de Caddy: sudo journalctl -u caddy -f"
echo "- Reiniciar app: sudo systemctl restart $APP_NAME"
echo "- Reiniciar Caddy: sudo systemctl restart caddy"
echo "- Verificar configuración Caddy: sudo caddy validate --config $CADDY_CONFIG_DIR/Caddyfile"
echo "- Recargar configuración Caddy: sudo systemctl reload caddy"