# Spicy Sweet - Gestión de Inventario

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Python](https://www.python.org/downloads/)

## Instrucciones para ejecutar el proyecto

### 1. Configurar Docker Compose

1. Abre una terminal o símbolo del sistema.
2. Navega a la carpeta donde se encuentra el archivo `docker-compose.yml`.
3. Ejecuta el siguiente comando para levantar los servicios en segundo plano:

    ```sh
    docker-compose up -d
    ```

### 2. Instalar dependencias de Python

Es recomendable, aunque no necesario, crear un entorno virtual antes de instalar las dependencias.

1. Abre una terminal o símbolo del sistema.
2. Navega a la carpeta raíz del proyecto.
3. (Opcional) Crea un entorno virtual:

    ```sh
    python -m venv env
    source env/bin/activate   # En Linux/Mac
    env\Scripts\activate      # En Windows
    ```

4. Instala las dependencias listadas en `requirements.txt`:

    ```sh
    pip install -r requirements.txt
    ```

### 3. Ejecutar el proyecto

1. Asegúrate de estar en la carpeta raíz del proyecto.
2. Ejecuta el archivo principal del proyecto:

    ```sh
    python myproject.py
    ```

¡Listo! Ahora deberías tener el proyecto Spicy Sweet ejecutándose.
