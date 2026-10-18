from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path
from home import views
from home.models import Perfil

app_name = "home"

urlpatterns = [
    path("", views.index, name="index"),
    path("base/", views.base, name="base"),
    path("categoria/", views.categoria, name="categoria"),
    path("contactanos/", views.contactanos, name="contactanos"),
    path("categoria/<int:pk>/", views.categoria, name="categoria_detalle"),
    path("crear-publicacion/", views.crear_publicacion, name="crear_publicacion"),
    path("crear-publicaciones/", views.crear_publicacion, name="crear_publicaciones"),
    path("crear-usuario/", views.crear_usuario, name="crear_usuario"),
    path("crud-cambiar-contraseña/", views.crud_cambiar_contraseña, name="crud_cambiar_contraseña"),
    path("crud-categorias/", views.crud_categorias, name="crud_categorias"),
    path("crud-comentarios/<int:pk>/aprobar/", views.aprobar_comentario, name="aprobar_comentario"),
    path("crud-comentarios/<int:pk>/bloquear/", views.bloquear_comentario, name="bloquear_comentario"),
    path("crud-comentarios/<int:pk>/eliminar/", views.eliminar_comentario, name="eliminar_comentario"),
    path("crud-comentarios/", views.crud_comentarios, name="crud_comentarios"),
    path("crud-noticias/", views.crud_noticias, name="crud_noticias"),
    path("crud-perfil/", views.crud_perfil, name="crud_perfil"),
    path("crud-usuarios/", views.crud_usuarios, name="crud_usuarios"),
    path("editar-categoria/<int:pk>/", views.editar_categoria, name="editar_categoria"),
    path("eliminar-categoria/<int:pk>/", views.eliminar_categoria, name="eliminar_categoria"),
    path("login/", auth_views.LoginView.as_view(template_name="home/login.html"), name="login"),
    path("logout/", LogoutView.as_view(next_page="home:index"), name="logout"),
    path("noticia/<int:pk>/", views.noticia, name="noticia_detalle"),
    path("noticia/", views.noticia, name="noticia"),
    path("perfil/", views.perfil, name="perfil"),
    path("editar-publicacion/<int:pk>/", views.editar_publicacion, name="editar_publicacion"),
    path("publicar-publicacion/<int:pk>/", views.cambiar_estado_publicacion, name="publicar_publicacion"),
    path("eliminar-publicacion/<int:pk>/", views.eliminar_publicacion, name="eliminar_publicacion"),
    path("editar-usuario/<int:pk>/", views.editar_usuario, name="editar_usuario"),
    path("bloquear-usuario/<int:pk>/", views.bloquear_usuario, name="bloquear_usuario"),
    path("eliminar-usuario/<int:pk>/", views.eliminar_usuario, name="eliminar_usuario"),
    path("sign-up/", views.sign_up, name="sign_up"),
]
