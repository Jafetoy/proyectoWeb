# Canaco

Plataforma web para **publicar y administrar noticias**. Incluye un sistema de usuarios y un panel de control donde un superadministrador gestiona publicaciones, comentarios y cuentas.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-092E20?style=flat&logo=django&logoColor=white)
![MySQL](https://img.shields.io/badge/MySQL-8.0-4479A1?style=flat&logo=mysql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white)

## Características

- 📰 **Publicación de noticias:** crea, edita y elimina publicaciones.
- 💬 **Comentarios:** los usuarios pueden comentar las noticias y el administrador puede moderarlos y borrarlos.
- 👥 **Gestión de usuarios:** registro y creación de cuentas desde el panel de administración.
- 🛡️ **Control de superadmin:** el superadministrador tiene control total sobre usuarios, publicaciones y comentarios.

## Tecnologías

- **Backend:** Python 3.11 + Django
- **Base de datos:** MySQL 8.0
- **Contenedores:** Docker y Docker Compose

## Estructura del proyecto

```
proyectoWeb/
├── canaco/              # Proyecto Django (manage.py)
├── design-system/       # Sistema de diseño
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

## Requisitos

Para producción en Azure con Docker, Gunicorn, MySQL y Nginx, consulta
[la guía de despliegue](docs/despliegue-azure.md). Usa los archivos
`Dockerfile.production` y `compose.production.yaml`; los comandos de abajo
corresponden al entorno de desarrollo.

- [Docker](https://www.docker.com/) y Docker Compose

## Instalación y uso

1. Clona el repositorio:

```bash
   git clone https://github.com/Jafetoy/proyectoWeb.git
   cd proyectoWeb
```

2. Levanta los contenedores:

```bash
   docker compose up --build
```

3. En otra terminal, aplica las migraciones:

```bash
   docker compose exec web python canaco/manage.py migrate
```

4. Crea el superadministrador:

```bash
   docker compose exec web python canaco/manage.py createsuperuser
```

5. Abre la app en [http://localhost:8000](http://localhost:8000)

Para detener todo:

```bash
docker compose down
```

## Pruebas

La suite usa SQLite en memoria y no modifica MySQL:

```powershell
Push-Location .\canaco
python -B .\manage.py test --settings=canaco.settings_test
Pop-Location
```

Para ejecutar solo las comprobaciones de configuración de producción:

```powershell
python -B .\canaco\manage.py test home.test_production --settings=canaco.settings_test -v 2
```

## Roles

| Rol | Permisos |
|---|---|
| **Superadmin** | Gestiona usuarios, publica, edita y borra noticias, y modera o elimina comentarios |
| **Usuario** | Consulta noticias y comenta |

## Variables de entorno

La configuración local se carga desde el archivo `.env` ubicado en la raíz del
repositorio. El archivo está ignorado por Git y Docker; solamente se versiona
`.env.example` con valores de ejemplo.

Para preparar un entorno nuevo:

```powershell
Copy-Item .env.example .env
```

Generá valores distintos para `DJANGO_SECRET_KEY`, `MYSQL_PASSWORD` y
`MYSQL_ROOT_PASSWORD`. No reutilices contraseñas personales o de producción.

Variables disponibles:

| Variable | Descripción |
|---|---|
| `DJANGO_SECRET_KEY` | Clave criptográfica local de Django |
| `DJANGO_DEBUG` | Activa o desactiva el modo de depuración |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos separados por comas |
| `MYSQL_DATABASE` | Nombre de la base de datos local |
| `MYSQL_USER` | Usuario local de MySQL |
| `MYSQL_PASSWORD` | Contraseña del usuario local |
| `MYSQL_ROOT_PASSWORD` | Contraseña administrativa local de MySQL |
| `DB_HOST` | Host usado al ejecutar Django fuera de Docker |
| `DB_PORT` | Puerto de MySQL |

Los archivos Compose interpolan únicamente las variables que necesita cada
servicio y no contienen credenciales literales. Iniciá el entorno local desde
la raíz del repositorio:

```powershell
docker compose --env-file .env up -d
```

Para producción, copiá `.env.production.example` como `.env.production` en el
servidor y ejecutá Compose indicando el archivo:

```powershell
docker compose --env-file .env.production -f compose.production.yaml up -d --build
```

## Autor

**Jairo de la Fuente** · Desarrollador Web · Villahermosa, MX

[GitHub](https://github.com/Jafetoy) · [Email](mailto:jafet05.com@gmail.com)
