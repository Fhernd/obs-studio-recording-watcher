# 1. Introducción

Aplicación para monitorear la carpeta de grabaciones de la aplicación *OBS Studio*.

# 2. Requerimientos

Para el correcto funcionamiento de la aplicación, se necesitan los siguientes componentes:

- **Python**: Se requiere tener Python instalado en el sistema. La aplicación es compatible con Python 3.6 o superior.
- **Librería de WebSocket para OBS Studio**: Es necesario instalar una librería que permita la comunicación a través de WebSocket con OBS Studio. Se recomienda utilizar `obs-websocket-py`, que es una librería de Python específica para este propósito.

# 3. Creación y activación de un ambiente virtual

## 3.1 Linux y macOS

1. **Creación del ambiente virtual:**

   Abre una terminal y navega hasta el directorio del proyecto. Luego, ejecuta el siguiente comando para crear un ambiente virtual llamado `venv`:

   ```bash
   python3 -m venv venv
   ```

`source venv/bin/activate`

## 3.2 Windows

   Abre una terminal y navega hasta el directorio del proyecto. Luego, ejecuta el siguiente comando para crear un ambiente virtual llamado `venv`:

   ```bash
   python -m venv venv
   ```

`.\venv\Scripts\activate`
