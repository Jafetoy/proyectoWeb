"""
URL configuration for canaco project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LogoutView
from home import views
import os
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test

from home.models import Perfil

urlpatterns = [
    path('', include('home.urls')),
    path('admin/', admin.site.urls),
    path("login", auth_views.LoginView.as_view(template_name='home/login.html'), name="login"),
    path("logout/", LogoutView.as_view(next_page='home:login'), name="logout"),
    path("sign_up", views.sign_up, name="sign_up"),
    path("crud_usuarios/crear", views.crear_usuario, name="crear_usuario"),
    path("crud_usuarios/<int:pk>/editar", views.editar_usuario, name="editar_usuario"),
    path("crud_usuarios/<int:pk>/bloquear", views.bloquear_usuario, name="bloquear_usuario"),
    path("crud_usuarios/<int:pk>/eliminar", views.eliminar_usuario, name="eliminar_usuario"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

def es_operador(user):
    return user.is_authenticated and user.is_staff and user.is_active

operador_required = user_passes_test(es_operador)

def sign_up(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('home:sign_up')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El nombre de usuario ya está en uso.')
            return redirect('home:sign_up')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'El correo electrónico ya está registrado.')
            return redirect('home:sign_up')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = ' '.join(filter(None, [apellido_paterno, apellido_materno]))
        user.save()

        perfil, _ = Perfil.objects.get_or_create(user=user)
        perfil.apellido_paterno = apellido_paterno
        perfil.apellido_materno = apellido_materno
        perfil.save()

        messages.success(request, 'Tu cuenta ha sido creada con éxito. Ahora puedes iniciar sesión.')
        return redirect('home:login')

    return render(request, 'home/sign_up.html')


@login_required
def crud_perfil(request):
    user = request.user
    perfil, _ = Perfil.objects.get_or_create(user=user)

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        foto = request.FILES.get('foto')

        if not username:
            messages.error(request, 'El usuario es obligatorio.')
            return redirect('home:crud_perfil')

        if User.objects.filter(username=username).exclude(pk=user.pk).exists():
            messages.error(request, 'Ese nombre de usuario ya está en uso.')
            return redirect('home:crud_perfil')

        user.username = username
        if email:
            user.email = email
        user.first_name = first_name
        user.last_name = ' '.join(filter(None, [apellido_paterno, apellido_materno]))
        user.save()

        perfil.apellido_paterno = apellido_paterno
        perfil.apellido_materno = apellido_materno

        if foto:
            if perfil.foto_perfil:
                archivo_anterior = perfil.foto_perfil
                if hasattr(archivo_anterior, 'path') and os.path.exists(archivo_anterior.path):
                    os.remove(archivo_anterior.path)
            perfil.foto_perfil = foto

        perfil.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('home:perfil')

    return render(request, 'home/crud_perfil.html', {'perfil_usuario': perfil})


@login_required
def crud_cambiar_contrasena(request):
    if request.method == 'POST':
        actual = request.POST.get('actual')
        nueva = request.POST.get('nueva')
        confirmar = request.POST.get('confirmar')
        user = request.user

        if not user.check_password(actual):
            messages.error(request, 'La contraseña actual es incorrecta.')
            return redirect('home:crud_cambiar_contrasena')

        if nueva != confirmar:
            messages.error(request, 'Las nuevas contraseñas no coinciden.')
            return redirect('home:crud_cambiar_contrasena')

        user.set_password(nueva)
        user.save()
        update_session_auth_hash(request, user)
        messages.success(request, 'Contraseña actualizada correctamente.')
        return redirect('home:crud_cambiar_contrasena')

    return render(request, 'home/crud_cambiar_contrasena.html')


@operador_required
def crud_usuarios(request):
    for usuario in User.objects.all():
        Perfil.objects.get_or_create(user=usuario)
    usuarios = User.objects.select_related('perfil').order_by('date_joined')
    return render(request, 'home/crud_usuarios.html', {'usuarios': usuarios})


@operador_required
def crear_usuario(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        apellido_paterno = request.POST.get('apellido_paterno', '').strip()
        apellido_materno = request.POST.get('apellido_materno', '').strip()
        password1 = request.POST.get('password1', '')
        password2 = request.POST.get('password2', '')

        if not username or not password1:
            messages.error(request, 'Usuario y contraseña son obligatorios.')
            return redirect('home:crear_usuario')

        if password1 != password2:
            messages.error(request, 'Las contraseñas no coinciden.')
            return redirect('home:crear_usuario')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'El usuario ya existe.')
            return redirect('home:crear_usuario')

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.first_name = first_name
        user.last_name = ' '.join(filter(None, [apellido_paterno, apellido_materno]))
        
        rol = request.POST.get('rol')
        user.is_staff = rol in ['editor', 'administrador']
        user.is_superuser = (rol == 'administrador')
        user.save()

        perfil, _ = Perfil.objects.get_or_create(user=user)
        perfil.apellido_paterno = apellido_paterno
        perfil.apellido_materno = apellido_materno
        perfil.save()

        messages.success(request, 'Usuario creado correctamente.')
        return redirect('home:crud_usuarios')

    return render(request, 'home/crear_usuario.html')