# LLM Chat App - Streamlit

Una aplicación web construida con Streamlit que permite interactuar con modelos de lenguaje como Claude (Anthropic) y GPT (OpenAI) a través de sus APIs.

## Características

- 🤖 Soporte para múltiples proveedores LLM (Anthropic Claude, OpenAI GPT)
- 💬 Interfaz de chat interactiva
- 🔧 Configuración fácil de API keys
- 📱 Diseño responsive
- 🚀 Listo para despliegue en producción

## Requisitos

- Python 3.8+
- Ubuntu 20.04 LTS (para despliegue)
- API keys de Anthropic y/o OpenAI

## Instalación Local

1. Clonar el repositorio:
```bash
git clone <tu-repositorio>
cd BotApiClaude
```

2. Crear entorno virtual:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno:
```bash
cp .env.example .env
# Editar .env con tus API keys
```

5. Ejecutar la aplicación:
```bash
streamlit run app.py
```

## Despliegue en Ubuntu 20.04

### Opción 1: Despliegue con Docker (Recomendado)

**Caso de uso:** Despliegue aislado y limpio usando contenedores Docker

1. **En tu máquina local - Actualizar y subir cambios:**
```bash
# Hacer cambios al código
git add .
git commit -m "Update application"
git push origin master
```

2. **En el VPS - Actualizar proyecto:**
```bash
cd ~/llm-chat-docker
git pull origin master
```

3. **En el VPS - Configurar variables de entorno:**
```bash
cp .env.example .env
nano .env
# Configurar ANTHROPIC_API_KEY y otras variables
```

4. **En el VPS - Construir y ejecutar contenedor:**
```bash
docker-compose up --build -d
```

5. **En el VPS - Configurar Caddy (solo la primera vez):**
```bash
sudo nano /etc/caddy/Caddyfile
```
Agregar configuración del chat:
```caddyfile
:80 {
    # Ruta para la aplicación LLM Chat (Docker)
    handle /chat/* {
        uri strip_prefix /chat
        reverse_proxy 127.0.0.1:8501
    }

    handle /chat {
        redir /chat/ 301
    }

    # Tu configuración existente del blog
    handle {
        root * /var/www/tu-blog
        file_server
        # resto de configuración...
    }
}
```

6. **En el VPS - Recargar Caddy:**
```bash
sudo systemctl reload caddy
```

**Resultado:** 
- Blog: `http://tu-ip/`
- App LLM: `http://tu-ip/chat/`

### Opción 2: Script Automático con Caddy

```bash
# Hacer el script ejecutable
chmod +x deploy-caddy.sh

# Ejecutar el script de despliegue con Caddy
sudo ./deploy-caddy.sh
```

### Opción 3: Script Automático con Nginx

```bash
# Hacer el script ejecutable
chmod +x deploy.sh

# Ejecutar el script de despliegue
sudo ./deploy.sh
```

### Opción 3: Despliegue en VPS con Blog Existente (Caddy)

**Caso de uso:** Ya tienes un blog funcionando con Caddy y quieres agregar la aplicación LLM en un subdirectorio `/chat`

1. **Crear directorio y clonar repositorio:**
```bash
sudo mkdir -p /opt/llm-chat-app
sudo chown webmaster:webmaster /opt/llm-chat-app
cd /opt/llm-chat-app
git clone https://github.com/tu-usuario/BotApiClaude.git .
```

2. **Configurar entorno virtual:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

3. **Configurar variables de entorno:**
```bash
cp .env.example .env
nano .env
# Configurar ANTHROPIC_API_KEY y STREAMLIT_SERVER_ADDRESS=127.0.0.1
```

4. **Crear servicio systemd:**
```bash
sudo nano /etc/systemd/system/llm-chat-app.service
```
Contenido:
```ini
[Unit]
Description=LLM Chat App - Streamlit Application
After=network.target

[Service]
Type=simple
User=webmaster
Group=webmaster
WorkingDirectory=/opt/llm-chat-app
Environment=PATH=/opt/llm-chat-app/venv/bin
ExecStart=/opt/llm-chat-app/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

5. **Habilitar y iniciar servicio:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable llm-chat-app
sudo systemctl start llm-chat-app
```

6. **Modificar Caddyfile existente:**
```bash
sudo nano /etc/caddy/Caddyfile
```
Agregar la configuración del chat antes del handle principal:
```caddyfile
:80 {
    # Ruta para la aplicación LLM Chat
    handle /chat* {
        uri strip_prefix /chat
        reverse_proxy 127.0.0.1:8501 {
            header_up Host localhost:8501
            header_up X-Real-IP {remote_host}
            header_up X-Forwarded-For {remote_host}
            header_up X-Forwarded-Proto {scheme}
            header_up Upgrade {>Upgrade}
            header_up Connection {>Connection}
        }
    }

    # Tu configuración existente del blog
    handle {
        root * /var/www/tu-blog
        file_server
        # resto de tu configuración...
    }
}
```

7. **Recargar Caddy:**
```bash
sudo systemctl reload caddy
```

**Resultado:** 
- Blog: `http://tu-ip/`
- App LLM: `http://tu-ip/chat/`

### Opción 4: Despliegue Manual con Caddy

1. **Actualizar sistema:**
```bash
sudo apt update && sudo apt upgrade -y
```

2. **Instalar Caddy:**
```bash
sudo apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | sudo gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | sudo tee /etc/apt/sources.list.d/caddy-stable.list
sudo apt update
sudo apt install -y caddy
```

3. **Instalar dependencias Python:**
```bash
sudo apt install -y python3 python3-pip python3-venv ufw
```

4. **Crear usuario para la aplicación:**
```bash
sudo useradd -m -s /bin/bash streamlit
```

5. **Crear directorio de aplicación:**
```bash
sudo mkdir -p /opt/llm-chat-app
sudo chown streamlit:streamlit /opt/llm-chat-app
```

6. **Copiar archivos y configurar:**
```bash
sudo cp -r . /opt/llm-chat-app/
sudo chown -R streamlit:streamlit /opt/llm-chat-app
```

7. **Configurar entorno virtual:**
```bash
sudo -u streamlit python3 -m venv /opt/llm-chat-app/venv
sudo -u streamlit /opt/llm-chat-app/venv/bin/pip install -r /opt/llm-chat-app/requirements.txt
```

8. **Configurar systemd service:**
```bash
sudo cp llm-chat-app.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable llm-chat-app
sudo systemctl start llm-chat-app
```

9. **Configurar Caddy:**
```bash
sudo mkdir -p /etc/caddy /var/log/caddy
sudo cp Caddyfile /etc/caddy/Caddyfile
sudo chown caddy:caddy /etc/caddy/Caddyfile
sudo chown -R caddy:caddy /var/log/caddy
# Editar el dominio en el Caddyfile
sudo nano /etc/caddy/Caddyfile
sudo systemctl enable caddy
sudo systemctl start caddy
```

10. **Configurar firewall:**
```bash
sudo ufw enable
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
```

11. **Configurar variables de entorno:**
```bash
sudo cp /opt/llm-chat-app/.env.example /opt/llm-chat-app/.env
# Editar con tus API keys
sudo nano /opt/llm-chat-app/.env
```

## Configuración

### Variables de Entorno

Edita el archivo `.env` con tus API keys:

```env
ANTHROPIC_API_KEY=tu_clave_anthropic
OPENAI_API_KEY=tu_clave_openai
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_ADDRESS=0.0.0.0
```

### Caddy

Edita `Caddyfile` y cambia `tu-dominio.com` por tu dominio:

```caddyfile
tu-dominio.com {
    # configuración del proxy reverso
}
```

### Nginx (si usas nginx en lugar de Caddy)

Edita `nginx.conf` y cambia `tu-dominio.com` por tu dominio o IP:

```nginx
server_name tu-dominio.com;
```

## Comandos Útiles

### Para Docker (Opción 1 - Recomendado):
```bash
# Ver estado de contenedores
docker-compose ps

# Ver logs de la aplicación
docker logs llm-chat-app

# Reiniciar contenedor
docker-compose restart

# Detener contenedores
docker-compose down

# Reconstruir y reiniciar
docker-compose up --build -d

# Ver uso de recursos
docker stats llm-chat-app
```

### Para servicios systemd (Opciones 2-3):
```bash
# Verificar estado del servicio
sudo systemctl status llm-chat-app

# Ver logs
sudo journalctl -u llm-chat-app -f

# Reiniciar servicio
sudo systemctl restart llm-chat-app
```

### Comandos de Caddy:
```bash
# Verificar configuración
sudo caddy validate --config /etc/caddy/Caddyfile

# Recargar configuración
sudo systemctl reload caddy

# Ver logs de Caddy
sudo journalctl -u caddy -f

# Reiniciar Caddy
sudo systemctl restart caddy
```

## Solución de Problemas

### Docker (Opción 1):

**La aplicación no inicia:**
1. Verificar logs: `docker logs llm-chat-app`
2. Verificar contenedor: `docker-compose ps`
3. Verificar configuración: `docker-compose config`

**Error de conexión:**
1. Verificar que el contenedor esté corriendo: `docker-compose ps`
2. Verificar puerto: `docker port llm-chat-app`
3. Verificar red: `docker network ls`

**Error de API:**
1. Verificar variables de entorno: `docker exec llm-chat-app env | grep API`
2. Verificar archivo .env: `cat .env`
3. Verificar conectividad: `docker exec llm-chat-app curl -I https://api.anthropic.com`

### Servicios systemd (Opciones 2-3):

**La aplicación no inicia:**
1. Verificar logs: `sudo journalctl -u llm-chat-app -n 50`
2. Verificar permisos: `ls -la /opt/llm-chat-app/`
3. Verificar entorno virtual: `sudo -u streamlit /opt/llm-chat-app/venv/bin/python -c "import streamlit"`

**Error de conexión:**
1. Verificar que el servicio esté corriendo: `sudo systemctl status llm-chat-app`
2. Verificar puerto: `sudo netstat -tlnp | grep 8501`
3. Verificar firewall: `sudo ufw status`

**Error de API:**
1. Verificar API keys en `/opt/llm-chat-app/.env`
2. Verificar conectividad: `curl -I https://api.anthropic.com`

## Estructura del Proyecto

```
BotApiClaude/
├── app.py                 # Aplicación principal Streamlit
├── requirements.txt       # Dependencias Python
├── .env.example          # Ejemplo de variables de entorno
├── .streamlit/           # Configuración Streamlit
│   └── config.toml
├── Dockerfile            # Configuración Docker
├── docker-compose.yml    # Orquestación de contenedores
├── .dockerignore         # Archivos excluidos de Docker
├── deploy-caddy.sh       # Script de despliegue con Caddy
├── llm-chat-app.service  # Archivo de servicio systemd
├── Caddyfile            # Configuración Caddy standalone
└── README.md             # Este archivo
```

## Seguridad

- Las API keys se almacenan en variables de entorno
- Docker proporciona aislamiento de contenedores
- El servicio se ejecuta con usuario no privilegiado
- Caddy actúa como proxy reverso
- Caddy obtiene certificados SSL automáticamente
- Firewall configurado para permitir solo puertos necesarios
- Headers de seguridad configurados automáticamente
- Contenedores con acceso limitado al sistema host

## Contribuir

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request