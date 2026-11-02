# Desplegar Canaco en Azure con Docker y Nginx

Los archivos de producción ya están incluidos. Esta guía usa una **VM Ubuntu 24.04 LTS**, Nginx y Certbot en el host, y Django/Gunicorn y MySQL en Docker. No usa App Service ni Kubernetes. No se ha conectado a Azure ni creado recursos.

## 1. Qué está preparado

| Archivo | Función |
|---|---|
| `Dockerfile.production` | Python 3.11, build multietapa y Gunicorn sin privilegios. |
| `canaco/requirements-production.txt` | Dependencias de producción independientes del desarrollo. |
| `compose.production.yaml` | Web en loopback, MySQL privado, volúmenes y logs limitados. |
| `canaco/canaco/settings_production.py` | HTTPS, cookies seguras y secretos obligatorios. |
| `.env.production.example` | Plantilla sin secretos reales. |
| `deploy/nginx/canaco.bootstrap.conf` | Sitio inicial para emitir el certificado. |
| `deploy/nginx/canaco.conf` | Proxy HTTPS, estáticos y medios denegados por defecto. |
| `canaco/home/test_production.py` | Pruebas de configuración sin base de datos. |

Los settings y dependencias de desarrollo permanecen sin cambios. Producción utiliza su propio entorno con Django 5.2 LTS; el desarrollo sigue usando la versión original y no debe exponerse a Internet. Antes de publicar se necesita validar toda la aplicación con las dependencias de producción, no solo importar los settings.

```text
Internet -> Azure NSG 80/443 -> Nginx HTTPS -> 127.0.0.1:8000 -> Gunicorn
                                                                -> MySQL
```

Solo Nginx es público; SSH se limita a tu IP. MySQL no publica puertos. Una VM es un punto único de fallo: una base administrada y almacenamiento externo mejoran disponibilidad a cambio de costo y configuración adicional. Los volúmenes NO son respaldos.

**Medios:** `/media/` responde 404 deliberadamente para no publicar documentos personales. Antes de habilitarla clasifica su contenido. Para privados implementa entrega autenticada; solo si todos son públicos sustituye esa ubicación por `alias /srv/canaco/media/;` y añade cabeceras `X-Content-Type-Options nosniff` y `Content-Disposition attachment`. Las imágenes cargadas no se mostrarán hasta resolver esa política. No publiques toda la carpeta sin revisión.

## 2. Validar localmente

Desde la raíz, en PowerShell:

```powershell
python -B .\canaco\manage.py test home.test_production --settings=canaco.settings_test -v 2
python -B .\canaco\manage.py check --settings=canaco.settings_test
Push-Location .\canaco
python -B .\manage.py test --settings=canaco.settings_test
Pop-Location
docker compose --env-file .env.production.example -f compose.production.yaml config --quiet
docker build -f Dockerfile.production -t canaco-web:validation .
docker run --rm --entrypoint python canaco-web:validation manage.py test home.test_production --settings=canaco.settings_test -v 2
```

`canaco.settings_test` usa SQLite en memoria: estos comandos no leen ni escriben la base MySQL configurada para desarrollo o producción. La primera orden ejecuta únicamente las comprobaciones de configuración de producción. El bloque con `Push-Location` ejecuta el descubrimiento desde la raíz de Django y encuentra la suite completa, incluidas esas pruebas; lanzar el mismo comando desde la raíz del repositorio puede devolver cero pruebas. El comando `docker run` usa la misma prueba dentro de la imagen sin iniciar MySQL. Ejecuta además la suite contra MySQL solo en staging, con una cuenta autorizada a crear una base de pruebas desechable; nunca uses la cuenta ni los datos de producción. El entorno de ejemplo permite validar la estructura Compose, pero Django rechaza sus placeholders al arrancar. No levantes el Compose de producción localmente sin revisar sus rutas absolutas.

Las etiquetas base y las dependencias transitivas pueden cambiar: conserva la imagen validada y registra sus digest y versiones resueltas antes de un despliegue reproducible. Revalida periódicamente actualizaciones de seguridad.

## 3. Crear VM y DNS

Necesitas suscripción Azure, permisos, presupuesto aprobado, Azure CLI, SSH, clave propia y dominio. VM, disco, IP y respaldos generan costos: consulta los precios de tu región. Los comandos siguientes crean recursos facturables; sustitúyelos y revisa el resultado de cada uno antes de continuar.

En **PowerShell local**:

```powershell
az login
az account set --subscription "<SUBSCRIPTION_ID>"
$rg = "rg-canaco-prod"
$vm = "vm-canaco-prod"
$location = "<AZURE_REGION>"
$adminCidr = "<TU_IP_PUBLICA>/32"
az group create --name $rg --location $location
az network nsg create --resource-group $rg --name canaco-nsg
az network nsg rule create -g $rg --nsg-name canaco-nsg -n AllowSSH --priority 1000 --access Allow --protocol Tcp --direction Inbound --source-address-prefixes $adminCidr --destination-port-ranges 22
az network nsg rule create -g $rg --nsg-name canaco-nsg -n AllowWeb --priority 1010 --access Allow --protocol Tcp --direction Inbound --source-address-prefixes Internet --destination-port-ranges 80 443
az vm create -g $rg -n $vm --image Ubuntu2404 --size Standard_B2s --admin-username azureuser --ssh-key-values "$HOME/.ssh/id_ed25519.pub" --public-ip-sku Standard --public-ip-address-allocation static --nsg canaco-nsg --nsg-rule NONE --os-disk-size-gb 64
$ip = az vm show -g $rg -n $vm -d --query publicIps -o tsv
ssh -i "$HOME/.ssh/id_ed25519" "azureuser@$ip"
```

Verifica la huella SSH por un canal confiable. El tamaño es inicial: comprueba disponibilidad, memoria y carga. Crea un registro DNS A de tu dominio hacia la IP. Corrige o retira registros AAAA que no sirvan correctamente IPv6. Sustituye `noticias.example.com` en ambos archivos Nginx y en el entorno real.

## 4. Preparar Ubuntu y transferir la versión

Instala Docker Engine y Compose desde el [repositorio APT oficial](https://docs.docker.com/engine/install/ubuntu/); no uses scripts descargados sin revisar. Los comandos siguientes son **Bash en la VM**:

```bash
sudo systemctl enable --now docker
sudo docker version
sudo docker compose version
sudo apt-get update
sudo apt-get install -y nginx certbot python3-certbot-nginx openssl
sudo systemctl enable --now nginx
sudo mkdir -p /opt/canaco /srv/canaco/static /srv/canaco/media
sudo chown "$USER:$USER" /opt/canaco
sudo chown -R 10001:10001 /srv/canaco/static /srv/canaco/media
sudo chmod 755 /srv/canaco /srv/canaco/static /srv/canaco/media
```

Usa `sudo docker`: el grupo Docker equivale a privilegios root. No uses permisos 777.

En tu equipo revisa y guarda en un commit los archivos que vas a desplegar, sin secretos, medios ni cambios ajenos. `git archive` solo incluye el commit, no archivos nuevos sin registrar. Después, en **PowerShell local**:

```powershell
git archive --format=tar --output="$env:TEMP/canaco-release.tar" HEAD
scp -i "$HOME/.ssh/id_ed25519" "$env:TEMP/canaco-release.tar" "azureuser@${ip}:/opt/canaco/release.tar"
```

Para la primera instalación, en la VM:

```bash
cd /opt/canaco
tar -xf release.tar
test -f compose.production.yaml && test -f canaco/canaco/settings_production.py
umask 077
cp .env.production.example .env.production
chmod 600 .env.production
nano .env.production
```

Completa `DJANGO_HOST` sin protocolo, puerto ni ruta. Reemplaza los tres valores `CHANGE_ME` por secretos distintos generados con `openssl rand -hex 32`. No reutilices claves de desarrollo ni guardes el entorno real en Git. Usa una etiqueta única en `RELEASE`. Compose interpola este archivo, pero no es un gestor de secretos: administradores Docker pueden leerlo. Para mayores requisitos evalúa Key Vault y entrega controlada de secretos.

## 5. Construir e inicializar

En cada sesión Bash define el atajo:

```bash
cd /opt/canaco
dc() { sudo docker compose --env-file .env.production -f compose.production.yaml "$@"; }
dc config --quiet
dc build web
dc up -d db
dc ps
```

Espera a que MySQL esté saludable. Para una **base nueva**, después de validar en staging:

```bash
dc run --rm web python manage.py check --deploy
dc run --rm web python manage.py migrate --plan
dc run --rm web python manage.py migrate
dc run --rm web python manage.py collectstatic --noinput
dc run --rm web python manage.py createsuperuser
dc up -d web
dc logs --tail=80 web
```

Revisa los avisos: HSTS está desactivado durante la puesta en marcha mediante `SECURE_HSTS_SECONDS = 0` en `canaco/canaco/settings_production.py`. Déjalo así durante el bootstrap. Después de comprobar el certificado, la redirección HTTPS y `certbot renew --dry-run`, cambia el valor primero a `3600`, reconstruye y despliega la imagen, y monitorea al menos una semana. Si no hay problemas, súbelo a `31536000` y vuelve a desplegar. Mantén `SECURE_HSTS_INCLUDE_SUBDOMAINS` y `SECURE_HSTS_PRELOAD` desactivados hasta verificar todos los subdominios y aceptar que esa política es difícil de revertir. Comprueba también que Nginx (`www-data`) pueda leer los estáticos.

**Datos existentes:** antes de migrar, ensaya la restauración lógica de MySQL y la copia autorizada de medios en un entorno aislado. No montes directamente un volumen MySQL 8.0 sobre 8.4. Migrar no importa usuarios ni noticias. Mantén un corte de escrituras al trasladar base y archivos. Cambiar `MYSQL_PASSWORD` en el entorno no rota una contraseña de un volumen inicializado: coordina su modificación en MySQL y en la aplicación.

## 6. Nginx y HTTPS

En la VM sustituye el dominio en ambos archivos. Instala primero **solo el bootstrap**, que responde 503 mientras se obtiene el certificado:

```bash
cd /opt/canaco
sudo cp deploy/nginx/canaco.bootstrap.conf /etc/nginx/sites-available/canaco
sudo ln -s /etc/nginx/sites-available/canaco /etc/nginx/sites-enabled/canaco
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d noticias.example.com --redirect
sudo certbot certificates
```

DNS y puerto 80 deben ser accesibles. Certbot pide correo y aceptación de términos. No fuerces renovaciones repetidas. Verifica que las rutas mostradas coincidan con el archivo final antes de activarlo:

```bash
sudo cp deploy/nginx/canaco.conf /etc/nginx/sites-available/canaco
sudo nginx -t && sudo systemctl reload nginx
sudo certbot renew --dry-run
systemctl list-timers --all | grep certbot
```

Debe existir renovación automática y recarga Nginx tras renovar; compruébalo y monitorea vencimientos. Repite la prueba tras cambiar el sitio. El proxy sobrescribe `X-Forwarded-Proto`; Gunicorn debe permanecer en loopback. El límite de carga inicial de 20 MB no sustituye validación de archivos en Django.

## 7. Verificación de publicación

```bash
dc ps
dc exec web python manage.py check --deploy
curl -I http://noticias.example.com
curl -I https://noticias.example.com
curl -I https://noticias.example.com/static/css/theme-custom.css
sudo ss -lntp
```

- HTTP redirige a HTTPS, certificado válido, sin 5xx, CSS responde 200.
- Verifica login/logout, CSRF, permisos y una publicación desde el navegador.
- Desde fuera comprueba que 3306 y 8000 NO sean accesibles.
- Recrea web con `dc up -d --force-recreate web` y verifica persistencia.
- Configura alertas de disponibilidad, memoria, CPU, disco, 5xx y presupuesto.

| Síntoma | Revisar |
|---|---|
| 502 | Logs de web, Gunicorn y enlace loopback. |
| DisallowedHost | Dominio y DNS; no usar `*`. |
| CSRF 403 | Origen HTTPS y proxy; no desactivar CSRF. |
| CSS 404 | `collectstatic`, alias y permisos. |
| Medios 404 | Bloqueo deliberado; clasificar antes de habilitar. |
| MySQL no conecta | Salud de db y credenciales almacenadas realmente. |

## 8. Respaldos, actualizaciones y recuperación

Define frecuencia, retención, cifrado y destino fuera de la VM. Incluye dump consistente de MySQL, medios, secretos y configuración Nginx. Para coherencia entre base y archivos, detén escrituras durante el respaldo o diseña una estrategia coordinada. No copies en caliente el directorio interno MySQL. Ensaya restauraciones aisladas; Azure Backup puede complementar, no sustituir esa prueba.

Para actualizar: valida el commit en staging, conserva la imagen anterior, bloquea escrituras y respalda. Transfiere el nuevo paquete a una carpeta de versión nueva para evitar archivos obsoletos. Copia secretos de forma restringida. Usa el mismo nombre Compose y montajes; cambia `RELEASE`, construye, revisa/aplica migraciones, recolecta estáticos, ejecuta `dc up -d web` y verifica antes de reabrir escrituras.

Para revertir código con esquema compatible, vuelve a la carpeta y etiqueta anteriores y ejecuta `dc up -d --no-build web`; restaura los estáticos de esa versión. Si el esquema es incompatible, aplica únicamente la reversión ensayada o restaura base y medios coordinadamente, con aprobación por pérdida de cambios posteriores al respaldo.

**Nunca ejecutes `docker compose down -v` en producción:** elimina los volúmenes de la base. No borres el grupo de recursos para reiniciar el sitio. Detener contenedores no elimina todos los costos Azure.

## Lista de salida

- [ ] Pruebas de aplicación con dependencias de producción y `check --deploy` revisados.
- [ ] Secretos nuevos fuera de Git e imágenes; respaldo y restauración probados.
- [ ] NSG restringido, HTTPS y renovación automática comprobados.
- [ ] Medios clasificados; permisos, formularios y estáticos comprobados.
- [ ] Monitoreo, presupuesto, responsable y recuperación definidos.

## Fuentes oficiales

Consultadas el 28 de octubre de 2026; revalida versiones y comandos antes de publicar.

- [Crear VM Linux](https://learn.microsoft.com/en-us/azure/virtual-machines/linux/quick-create-cli).
- [Docker en Ubuntu](https://docs.docker.com/engine/install/ubuntu/).
- [Soporte Django](https://www.djangoproject.com/download/) y [checklist de despliegue](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/).
- [Gunicorn](https://pypi.org/project/gunicorn/) y [django-mysql](https://django-mysql.readthedocs.io/en/latest/installation.html).
- [Proxy Nginx](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/) y [Certbot](https://eff-certbot.readthedocs.io/en/stable/using.html).
