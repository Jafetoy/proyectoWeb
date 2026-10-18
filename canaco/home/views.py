from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.db.models import F
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from .models import Perfil, Publicacion, Categoria, Archivo, GaleriaPublicacion, Comentario

# Create your views here.
def es_operador(user):
    return user.is_authenticated and user.is_active and (user.is_staff or user.is_superuser)


def operador_required(view_func):
    return user_passes_test(es_operador, login_url='home:login')(view_func)


def guardar_archivo(archivo, user):
    return Archivo.objects.create(
        nombre=archivo.name,
        nombre_temporal=archivo.name,
        ruta=archivo,
        tipo=getattr(archivo, 'content_type', ''),
        tamano=archivo.size,
        fk_user=user,
    )


def index(request):
    publicaciones = Publicacion.objects.filter(
        estado=Publicacion.ESTADO_PUBLICADO
    ).select_related('categoria', 'autor', 'imagen_portada').order_by('-createdat')
    return render(request, 'home/index.html', {
        'destacada': publicaciones.first(),
        'publicaciones': publicaciones[:6],
        'categorias': Categoria.objects.all().order_by('nombre'),
    })

def base(request):
    return render(request, 'home/base.html')

def categoria(request, pk=None):
    categoria_seleccionada = get_object_or_404(Categoria, pk=pk) if pk else None
    publicaciones = Publicacion.objects.filter(
        estado=Publicacion.ESTADO_PUBLICADO
    ).select_related('categoria', 'autor', 'imagen_portada').order_by('-createdat')
    if categoria_seleccionada:
        publicaciones = publicaciones.filter(categoria=categoria_seleccionada)
    return render(request, 'home/categoria.html', {
        'categoria': categoria_seleccionada,
        'categorias': Categoria.objects.all().order_by('nombre'),
        'publicaciones': publicaciones,
    })

def contactanos(request):
    return render(request, 'home/contactanos.html')

@operador_required
def crear_publicacion(request):
    if request.method == 'POST':
        titulo = request.POST.get('titulo', '').strip()
        resumen = request.POST.get('resumen', '').strip()
        contenido = request.POST.get('contenido', '').strip()
        categoria_id = request.POST.get('categoria')
        estado = request.POST.get('estado', Publicacion.ESTADO_BORRADOR)

        autor = request.user
        categoria = Categoria.objects.filter(id=categoria_id).first() if categoria_id else None

        publicacion = Publicacion.objects.create(
            titulo=titulo,
            resumen=resumen,
            contenido=contenido,
            categoria=categoria,
            autor=autor,
            estado=estado
        )

        portada = request.FILES.get('imagen_portada')
        if portada:
            publicacion.imagen_portada = guardar_archivo(portada, autor)
            publicacion.save()

        for foto in request.FILES.getlist('galeria'):
            GaleriaPublicacion.objects.create(
                publicacion=publicacion,
                archivo=guardar_archivo(foto, autor),
            )

        messages.success(request, 'Publicación creada exitosamente.')
        return redirect('home:crud_noticias')

    categorias = Categoria.objects.all()
    return render(request, 'home/crear_publicacion.html', {'categorias': categorias})

crear_publicaciones = crear_publicacion

def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        rol = request.POST.get('rol')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Ese usuario ya está registrado. Intenta de nuevo.')
            return redirect('home:crear_usuario')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('home:crear_usuario')

        usuario = User.objects.create_user(
            username=username,
            email=email,
            first_name=first_name,
            last_name=' '.join(filter(None, [apellido_paterno, apellido_materno])),
            password=password1
        )

        usuario.is_staff = rol in ['editor', 'administrador']
        usuario.is_superuser = (rol == 'administrador')
        usuario.save()

        perfil, _ = Perfil.objects.get_or_create(user=usuario)
        perfil.apellido_paterno = apellido_paterno
        perfil.apellido_materno = apellido_materno
        perfil.save()

        messages.success(request, 'Usuario creado exitosamente.')
        return redirect('home:crud_usuarios')

    return render(request, 'home/crear_usuario.html')


def crud_cambiar_contraseña(request):
    if request.method == 'POST':
        current_password = request.POST.get('current_password', '')
        new_password1 = request.POST.get('new_password1', '')
        new_password2 = request.POST.get('new_password2', '')

        if not request.user.check_password(current_password):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return redirect('home:crud_cambiar_contraseña')

        if new_password1 != new_password2:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return redirect('home:crud_cambiar_contraseña')

        request.user.set_password(new_password1)
        request.user.save()
        messages.success(request, 'Contraseña cambiada exitosamente.')
        return redirect('home:perfil')
    return render(request, 'home/crud_cambiar_contraseña.html')


@operador_required
def crud_categorias(request):
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            Categoria.objects.create(nombre=nombre, fk_user=request.user)
            messages.success(request, 'Categoría agregada correctamente.')
            return redirect('home:crud_categorias')
        messages.error(request, 'El nombre de la categoría no puede estar vacío.')

    categorias = Categoria.objects.select_related('fk_user').order_by('-createdat')
    return render(request, 'home/crud_categorias.html', {'categorias': categorias})

@operador_required
def crud_comentarios(request):
    comentarios = Comentario.objects.select_related(
        'publicacion', 'autor'
    ).order_by('-createdat')
    return render(request, 'home/crud_comentarios.html', {'comentarios': comentarios})

@operador_required
@require_POST
def aprobar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    comentario.estado = Comentario.ESTADO_APROBADO
    comentario.save(update_fields=['estado', 'updatedat'])
    messages.success(request, 'Comentario aprobado.')
    return redirect('home:crud_comentarios')


@operador_required
@require_POST
def bloquear_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    comentario.estado = Comentario.ESTADO_BLOQUEADO
    comentario.save(update_fields=['estado', 'updatedat'])
    messages.success(request, 'Comentario bloqueado.')
    return redirect('home:crud_comentarios')


@operador_required
@require_POST
def eliminar_comentario(request, pk):
    comentario = get_object_or_404(Comentario, pk=pk)
    comentario.delete()
    messages.success(request, 'Comentario eliminado.')
    return redirect('home:crud_comentarios')


@operador_required
def crud_noticias(request):
    publicaciones = Publicacion.objects.select_related('autor', 'categoria').order_by('-createdat')
    return render(request, 'home/crud_noticias.html', {'publicaciones': publicaciones})

@operador_required
def editar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == 'POST':
        publicacion.titulo = request.POST.get('titulo', publicacion.titulo).strip()
        publicacion.resumen = request.POST.get('resumen', publicacion.resumen).strip()
        publicacion.contenido = request.POST.get('contenido', publicacion.contenido).strip()

        categoria_id = request.POST.get('categoria')
        publicacion.categoria = Categoria.objects.filter(id=categoria_id).first() if categoria_id else None
        publicacion.estado = request.POST.get('estado', publicacion.estado)

        portada = request.FILES.get('imagen_portada')
        if portada:
            publicacion.imagen_portada = guardar_archivo(portada, request.user)

        for foto in request.FILES.getlist('galeria'):
            GaleriaPublicacion.objects.create(
                publicacion=publicacion,
                archivo=guardar_archivo(foto, request.user),
            )

        publicacion.save()
        messages.success(request, 'Publicación actualizada correctamente.')
        return redirect('home:crud_noticias')

    categorias = Categoria.objects.all()
    return render(request, 'home/crear_publicacion.html', {
        'publicacion': publicacion,
        'categorias': categorias
    })

@operador_required
@require_POST
def cambiar_estado_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if publicacion.estado == Publicacion.ESTADO_PUBLICADO:
        publicacion.estado = Publicacion.ESTADO_BORRADOR
        messages.info(request, f'La publicación "{publicacion.titulo}" ahora está en borrador.')
    else:
        publicacion.estado = Publicacion.ESTADO_PUBLICADO
        messages.success(request, f'La publicación "{publicacion.titulo}" ha sido publicada.')
    publicacion.save()
    return redirect('home:crud_noticias')

publicar_publicacion = cambiar_estado_publicacion

@operador_required
@require_POST
def eliminar_publicacion(request, pk):
    publicacion = get_object_or_404(Publicacion, pk=pk)
    if request.method == 'POST':
        publicacion.delete()
        messages.success(request, 'Publicación eliminada correctamente.')
    return redirect('home:crud_noticias')

def crud_usuarios(request):
    usuarios = User.objects.all().order_by('-date_joined')
    return render(request, 'home/crud_usuarios.html', {'usuarios': usuarios})

@operador_required
def editar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        nombre = request.POST.get('nombre', '').strip()
        if nombre:
            from django.utils import timezone
            categoria.nombre = nombre
            categoria.updatedat = timezone.now()
            categoria.save()
            messages.success(request, 'Categoría actualizada exitosamente.')
            return redirect('home:crud_categorias')
        else:
            messages.error(request, 'El nombre de la categoría no puede estar vacío.')
    return render(request, 'home/editar_categoria.html', {'categoria': categoria})

@operador_required
@require_POST
def eliminar_categoria(request, pk):
    categoria = get_object_or_404(Categoria, pk=pk)
    if request.method == 'POST':
        categoria.delete()
        messages.success(request, 'Categoría eliminada correctamente.')
    return redirect('home:crud_categorias')

def login(request):
    return render(request, 'home/login.html')

def noticia(request, pk=None):
    if pk and es_operador(request.user):
        publicaciones = Publicacion.objects.all()
    else:
        publicaciones = Publicacion.objects.filter(estado=Publicacion.ESTADO_PUBLICADO)

    publicaciones = publicaciones.select_related('categoria', 'autor', 'imagen_portada')
    publicacion = (
        get_object_or_404(publicaciones, pk=pk)
        if pk
        else publicaciones.order_by('-createdat').first()
    )
    if not publicacion:
        messages.info(request, 'Todavía no hay noticias publicadas.')
        return redirect('home:index')

    Publicacion.objects.filter(pk=publicacion.pk).update(visitas=F('visitas') + 1)
    publicacion.refresh_from_db()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            messages.error(request, 'Debes iniciar sesión para comentar.')
            return redirect('home:login')
        contenido = request.POST.get('contenido', '').strip()
        if contenido:
            Comentario.objects.create(
                publicacion=publicacion,
                autor=request.user,
                contenido=contenido,
            )
            messages.success(request, 'Comentario enviado. Será visible cuando lo apruebe un operador.')
        else:
            messages.error(request, 'El comentario no puede estar vacío.')
        return redirect('home:noticia_detalle', pk=publicacion.pk)

    recientes = Publicacion.objects.filter(
        estado=Publicacion.ESTADO_PUBLICADO,
    ).exclude(pk=publicacion.pk).select_related('imagen_portada').order_by('-createdat')[:4]
    comentarios = publicacion.comentarios.filter(
        estado=Comentario.ESTADO_APROBADO,
    ).select_related('autor').order_by('-createdat')
    categorias = Categoria.objects.all().order_by('nombre')
    return render(request, 'home/noticia.html', {
        'publicacion': publicacion,
        'recientes': recientes,
        'comentarios': comentarios,
        'categorias': categorias,
    })

def sign_up(request):
    return render(request, 'home/sign_up.html')

def operador_required(view_func):
    es_operador = lambda user: user.is_authenticated and (
        user.is_staff or user.is_superuser
    )
    return user_passes_test(es_operador)(view_func)

@login_required
def perfil(request):
    perfil_usuario, _ = Perfil.objects.get_or_create(user=request.user)
    return render(request, 'home/perfil.html', {'perfil_usuario': perfil_usuario})

@login_required
def crud_perfil(request):
    perfil_usuario, _ = Perfil.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        user = request.user
        user.username = request.POST.get('username', user.username).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.first_name = request.POST.get('first_name', user.first_name).strip()

        perfil_usuario.apellido_paterno = request.POST.get('apellido_paterno', perfil_usuario.apellido_paterno).strip()
        perfil_usuario.apellido_materno = request.POST.get('apellido_materno', perfil_usuario.apellido_materno).strip()
        user.last_name = ' '.join(filter(None, [perfil_usuario.apellido_paterno, perfil_usuario.apellido_materno]))

        if 'foto' in request.FILES:
            foto = request.FILES['foto']
            archivo = Archivo.objects.create(
                nombre=foto.name,
                nombre_temporal=foto.name,
                ruta=foto,
                tipo=getattr(foto, 'content_type', ''),
                tamano=foto.size,
                fk_user=user
            )
            perfil_usuario.foto_perfil = archivo

        user.save()
        perfil_usuario.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('home:perfil')

    return render(request, 'home/crud_perfil.html', {'perfil_usuario': perfil_usuario})

@operador_required
def editar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    perfil, _ = Perfil.objects.get_or_create(user=usuario)

    if request.method == 'POST':
        usuario.username = request.POST.get('username', usuario.username).strip()
        usuario.email = request.POST.get('email', usuario.email).strip()
        usuario.first_name = request.POST.get('first_name', usuario.first_name).strip()
        
        perfil.apellido_paterno = request.POST.get('apellido_paterno', perfil.apellido_paterno).strip()
        perfil.apellido_materno = request.POST.get('apellido_materno', perfil.apellido_materno).strip()
        usuario.last_name = ' '.join(filter(None, [perfil.apellido_paterno, perfil.apellido_materno]))

        rol = request.POST.get('rol')
        if rol:
            usuario.is_staff = rol in ['editor', 'administrador']
            usuario.is_superuser = (rol == 'administrador')

        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')
        if password1 or password2:
            if password1 != password2:
                messages.error(request, 'Las contraseñas no coinciden.')
                return redirect('home:editar_usuario', pk=usuario.pk)
            usuario.set_password(password1)

        usuario.save()
        perfil.save()
        messages.success(request, 'Usuario actualizado correctamente.')
        return redirect('home:crud_usuarios')

    return render(request, 'home/crear_usuario.html', {
        'usuario_editado': usuario,
        'perfil_editado': perfil,
    })


@operador_required
def bloquear_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if usuario != request.user:
        usuario.is_active = not usuario.is_active
        usuario.save()
    return redirect('home:crud_usuarios')


@operador_required
def eliminar_usuario(request, pk):
    usuario = get_object_or_404(User, pk=pk)
    if request.method == 'POST' and usuario != request.user:
        usuario.delete()
    return redirect('home:crud_usuarios')