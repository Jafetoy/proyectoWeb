FROM python:3.11-slim

# Evita que Python escriba archivos .pyc y fuerza salida sin buffer
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Instalar dependencias del sistema necesarias para mysqlclient
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias de Python
COPY requirements.txt /app/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copiar el código del proyecto
COPY . /app/

# Exponer el puerto de desarrollo de Django
EXPOSE 8000

# Ejecutar el servidor apuntando al archivo manage.py dentro de canaco/
CMD ["python", "canaco/manage.py", "runserver", "0.0.0.0:8000"]

