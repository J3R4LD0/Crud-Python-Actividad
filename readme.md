# Requisitos para el Proyecto

- Tener **Docker** instalado en el sistema.
- Tener **Docker Compose** instalado (si no viene incluido con Docker).

# Pasos para la Instalación

1. Verificar el archivo `requirements.txt` para las dependencias:
   ```
   gradio==3.34.0
   redis==5.0.0
   pandas==1.5.3
   etc..
   ```

4. Construir y ejecutar los servicios con Docker Compose:
   ```bash
   docker-compose up --build
   ```

5. Acceder a la aplicación en:
   ```
   http://localhost:7860
   ```

