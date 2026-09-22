
from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    path("", views.index, name="index"),
]

urlpatterns = [
    path("", views.base, name="base"),
]

urlpatterns = [
    path("", views.categoria, name="categoria"),
]

urlpatterns = [
    path("", views.contactanos, name="contactanos"),
]

urlpatterns = [
    path("", views.crear_publicaciones, name="crear_publicaciones"),
]

urlpatterns = [
    path("", views.crear_usuario, name="crear_usuario"),
]

urlpatterns = [
    path("", views.crear_cambiar_contraseña, name="crear_cambiar_contraseña"),
]

