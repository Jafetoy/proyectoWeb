# Instrucciones de trabajo para Canaco

Canaco es una aplicación web de noticias construida con Python 3.11 y Django 4.2. Estas pautas aplican al repositorio completo; mantené los cambios acotados al objetivo solicitado.

## Estructura del proyecto

- `canaco/canaco/`: configuración del proyecto Django, rutas y puntos de entrada ASGI/WSGI.
- `canaco/home/`: aplicación principal; contiene modelos, vistas, rutas, pruebas y plantillas.
- `canaco/home/templates/home/`: plantillas HTML.
- `canaco/static/`: recursos estáticos del sitio.
- `canaco/media/`: archivos cargados por usuarios; no modificar ni incluir archivos existentes en cambios que no lo requieran.
- `design-system/`: recursos del sistema de diseño.

## Reglas de implementación

1. Seguí los patrones existentes de Django y reutilizá modelos, formularios, decoradores y utilidades antes de agregar otros.
2. Usá el ORM de Django para acceder a la base de datos. Si cambiás modelos, generá y revisá las migraciones correspondientes.
3. Conservá las verificaciones de autenticación y autorización. Las operaciones que cambian datos deben usar métodos HTTP apropiados y mantener la protección CSRF de Django.
4. No expongas secretos, contraseñas, datos personales ni contenido de `media/` en el código, los registros o las respuestas.
5. Mantené en español el texto visible para usuarios, con redacción clara y consistente con la interfaz existente.
6. Al cambiar comportamiento, agregá o actualizá pruebas en la aplicación afectada. Evitá refactorizaciones ajenas al pedido.
7. No edites archivos generados, bases de datos locales ni medios existentes salvo que el pedido lo requiera explícitamente.

## Verificación

Desde la raíz del repositorio, ejecutá las comprobaciones pertinentes:

```powershell
python .\canaco\manage.py check
python .\canaco\manage.py test
```

Si una comprobación no puede ejecutarse por dependencias o servicios externos, informá cuál falló y por qué; no afirmes que pasó.
