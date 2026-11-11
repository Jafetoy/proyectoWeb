import mimetypes

from django.db.models import Q
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404

from .models import Archivo, Perfil, Publicacion
from .views import es_operador


TIPOS_PERMITIDOS = {
    "image/jpeg",
    "image/png",
    "image/webp",
    "image/gif",
    "image/avif",
    "image/heic",
}


def mostrar_imagen(request, pk):
    archivo = get_object_or_404(Archivo, pk=pk)

    publicaciones = Publicacion.objects.filter(
        Q(imagen_portada_id=pk) | Q(galeria__archivo_id=pk)
    ).distinct()
    es_imagen_publica = publicaciones.filter(
        estado=Publicacion.ESTADO_PUBLICADO,
    ).exists()
    es_imagen_de_operador = es_operador(request.user) and publicaciones.exists()

    # Fotografías personales: acceso solo del propietario
    es_foto_propia = (
        request.user.is_authenticated
        and Perfil.objects.filter(
            user_id=request.user.pk,
            foto_perfil_id=pk,
        ).exists()
    )

    if not (
        es_imagen_publica
        or es_imagen_de_operador
        or es_foto_propia
    ):
        raise Http404("Imagen no disponible")

    if not archivo.ruta:
        raise Http404("Archivo no disponible")

    tipo, _ = mimetypes.guess_type(archivo.ruta.name)

    if tipo not in TIPOS_PERMITIDOS:
        raise Http404("Formato no permitido")

    try:
        respuesta = FileResponse(
            archivo.ruta.open("rb"),
            content_type=tipo,
        )
    except (OSError, ValueError):
        raise Http404("Archivo no encontrado")

    respuesta["Cache-Control"] = "private, no-store"
    respuesta["X-Content-Type-Options"] = "nosniff"

    return respuesta
