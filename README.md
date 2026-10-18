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

## Roles

| Rol | Permisos |
|---|---|
| **Superadmin** | Gestiona usuarios, publica, edita y borra noticias, y modera o elimina comentarios |
| **Usuario** | Consulta noticias y comenta |

## Variables de entorno

La conexión a la base de datos se configura desde `docker-compose.yml`:

| Variable | Descripción |
|---|---|
| `DB_NAME` | Nombre de la base de datos |
| `DB_USER` | Usuario de MySQL |
| `DB_PASSWORD` | Contraseña del usuario |
| `DB_HOST` | Host de la base de datos (`db`) |
| `DB_PORT` | Puerto de MySQL (`3306`) |

## Autor

**Jairo de la Fuente** · Desarrollador Web · Villahermosa, MX

[GitHub](https://github.com/Jafetoy) · [Email](mailto:jafet05.com@gmail.com)
