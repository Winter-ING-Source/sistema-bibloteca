# 1. Usamos una imagen oficial ligera de Python
FROM python:3.11-slim

# 2. Instalamos los compiladores nativos del sistema operativo (SBCL y SWI-Prolog)
RUN apt-get update && apt-get install -y \
    sbcl \
    swi-prolog \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 3. Creamos el directorio de trabajo dentro del contenedor
WORKDIR /app

# 4. Instalamos las dependencias requeridas para Python y PostgreSQL
RUN pip install --no-cache-dir flask psycopg2-binary

# 5. Copiamos todos los archivos de nuestro proyecto al contenedor
COPY . .

# 6. Ejecutamos la aplicación
CMD ["python", "app.py"]
