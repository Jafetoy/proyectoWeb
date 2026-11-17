import importlib
from datetime import timedelta
from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, RequestFactory, TestCase, override_settings
from django.urls import clear_url_caches, reverse
from django.utils import timezone
from .context_processors import global_categorias
from .models import Archivo, Categoria, Comentario, GaleriaPublicacion, Perfil, Publicacion


class CrearUsuarioTests(TestCase):
	def setUp(self):
		self.operador = User.objects.create_superuser(
			username='administrador_usuarios',
			email='administrador@example.com',
			password='ClaveSegura123!',
		)
		self.client.force_login(self.operador)

	def test_crea_usuario_y_actualiza_perfil_generado_por_senal(self):
		response = self.client.post(reverse('home:crear_usuario'), {
			'username': 'nuevo_usuario_test',
			'email': 'nuevo@example.com',
			'first_name': 'Usuario',
			'apellido_paterno': 'Paterno',
			'apellido_materno': 'Materno',
			'password1': 'ClaveSegura123!',
			'password2': 'ClaveSegura123!',
			'rol': 'colaborador',
		})

		self.assertRedirects(response, reverse('home:crud_usuarios'))
		usuario = User.objects.get(username='nuevo_usuario_test')
		perfil = Perfil.objects.get(user=usuario)
		self.assertEqual(perfil.apellido_paterno, 'Paterno')
		self.assertEqual(perfil.apellido_materno, 'Materno')
		self.assertEqual(Perfil.objects.filter(user=usuario).count(), 1)

	def test_muestra_mensaje_si_el_usuario_ya_esta_registrado(self):
		User.objects.create_user(username='usuario_existente', password='ClaveSegura123!')

		response = self.client.post(reverse('home:crear_usuario'), {
			'username': 'usuario_existente',
			'email': 'otro@example.com',
			'password1': 'ClaveSegura123!',
			'password2': 'ClaveSegura123!',
		}, follow=True)

		self.assertContains(response, 'Ese usuario ya está registrado. Intenta de nuevo.')
		self.assertEqual(User.objects.filter(username='usuario_existente').count(), 1)


class LaboratorioNoticiasTests(TestCase):
	def setUp(self):
		self.operador = User.objects.create_user(
			username='operador_laboratorio',
			password='ClaveSegura123!',
			is_staff=True,
		)
		self.client.force_login(self.operador)

	def test_operador_crea_edita_y_elimina_categoria(self):
		self.client.post(reverse('home:crud_categorias'), {'nombre': 'Tecnología'})
		categoria = Categoria.objects.get(nombre='Tecnología')
		self.assertEqual(categoria.fk_user, self.operador)

		self.client.post(
			reverse('home:editar_categoria', args=[categoria.pk]),
			{'nombre': 'Comercio'},
		)
		categoria.refresh_from_db()
		self.assertEqual(categoria.nombre, 'Comercio')

		self.client.post(reverse('home:eliminar_categoria', args=[categoria.pk]))
		self.assertFalse(Categoria.objects.filter(pk=categoria.pk).exists())

	def test_operador_modera_comentario(self):
		publicacion = Publicacion.objects.create(
			titulo='Noticia de prueba',
			resumen='Resumen',
			contenido='Contenido',
			autor=self.operador,
		)
		comentario = Comentario.objects.create(
			publicacion=publicacion,
			autor=self.operador,
			contenido='Comentario de prueba',
		)

		response = self.client.get(reverse('home:crud_comentarios'))
		self.assertContains(response, 'Comentario de prueba')
		self.client.post(reverse('home:aprobar_comentario', args=[comentario.pk]))
		comentario.refresh_from_db()
		self.assertEqual(comentario.estado, Comentario.ESTADO_APROBADO)

		self.client.post(reverse('home:bloquear_comentario', args=[comentario.pk]))
		comentario.refresh_from_db()
		self.assertEqual(comentario.estado, Comentario.ESTADO_BLOQUEADO)

		self.client.post(reverse('home:eliminar_comentario', args=[comentario.pk]))
		self.assertFalse(Comentario.objects.filter(pk=comentario.pk).exists())

	def test_operador_completa_crud_y_publicacion_de_noticia(self):
		categoria = Categoria.objects.create(nombre='Categoría noticias', fk_user=self.operador)
		response = self.client.post(reverse('home:crear_publicacion'), {
			'titulo': 'Noticia inicial',
			'resumen': 'Resumen inicial',
			'contenido': 'Contenido inicial',
			'categoria': categoria.pk,
			'estado': Publicacion.ESTADO_BORRADOR,
		})
		self.assertRedirects(response, reverse('home:crud_noticias'))
		publicacion = Publicacion.objects.get(titulo='Noticia inicial')
		self.assertEqual(publicacion.autor, self.operador)

		self.client.post(reverse('home:editar_publicacion', args=[publicacion.pk]), {
			'titulo': 'Noticia editada',
			'resumen': 'Resumen editado',
			'contenido': 'Contenido editado',
			'categoria': categoria.pk,
			'estado': Publicacion.ESTADO_BORRADOR,
		})
		publicacion.refresh_from_db()
		self.assertEqual(publicacion.titulo, 'Noticia editada')

		self.client.post(reverse('home:publicar_publicacion', args=[publicacion.pk]))
		publicacion.refresh_from_db()
		self.assertEqual(publicacion.estado, Publicacion.ESTADO_PUBLICADO)

		self.client.post(reverse('home:publicar_publicacion', args=[publicacion.pk]))
		publicacion.refresh_from_db()
		self.assertEqual(publicacion.estado, Publicacion.ESTADO_BORRADOR)

		self.client.post(reverse('home:eliminar_publicacion', args=[publicacion.pk]))
		self.assertFalse(Publicacion.objects.filter(pk=publicacion.pk).exists())

	def test_noticia_publicada_registra_visita_y_comentarios_pendientes(self):
		publicacion = Publicacion.objects.create(
			titulo='Noticia pública',
			resumen='Resumen público',
			contenido='Contenido público',
			autor=self.operador,
			estado=Publicacion.ESTADO_PUBLICADO,
		)

		self.client.logout()
		response = self.client.get(reverse('home:noticia_detalle', args=[publicacion.pk]))
		self.assertContains(response, publicacion.titulo)
		publicacion.refresh_from_db()
		self.assertEqual(publicacion.visitas, 0)

		visita_url = reverse('home:registrar_visita', args=[publicacion.pk])
		self.assertEqual(self.client.get(visita_url).status_code, 405)
		self.assertEqual(self.client.post(visita_url).status_code, 204)
		publicacion.refresh_from_db()
		self.assertEqual(publicacion.visitas, 1)

		lector = User.objects.create_user(username='lector_laboratorio', password='ClaveSegura123!')
		self.client.force_login(lector)
		self.client.post(
			reverse('home:noticia_detalle', args=[publicacion.pk]),
			{'contenido': 'Comentario pendiente'},
		)
		comentario = Comentario.objects.get(publicacion=publicacion, autor=lector)
		self.assertEqual(comentario.estado, Comentario.ESTADO_PENDIENTE)

		self.client.force_login(self.operador)
		self.client.post(reverse('home:aprobar_comentario', args=[comentario.pk]))
		self.client.logout()
		response = self.client.get(reverse('home:noticia_detalle', args=[publicacion.pk]))
		self.assertContains(response, 'Comentario pendiente')


class GlobalFooterContextTests(TestCase):
	def test_contexto_global_devuelve_tres_publicadas_y_categorias(self):
		categoria = Categoria.objects.create(nombre='Categoría global')
		ahora = timezone.now()
		publicaciones = []
		for indice in range(4):
			publicacion = Publicacion.objects.create(
				titulo=f'Noticia global {indice}',
				resumen='Resumen',
				contenido='Contenido',
				categoria=categoria,
				estado=Publicacion.ESTADO_PUBLICADO,
			)
			Publicacion.objects.filter(pk=publicacion.pk).update(
				createdat=ahora + timedelta(minutes=indice)
			)
			publicaciones.append(publicacion)

		Publicacion.objects.create(
			titulo='Borrador global',
			resumen='Resumen',
			contenido='Contenido',
			estado=Publicacion.ESTADO_BORRADOR,
		)
		contexto = global_categorias(RequestFactory().get('/'))

		self.assertEqual(
			list(contexto['global_recientes'].values_list('pk', flat=True)),
			[publicaciones[3].pk, publicaciones[2].pk, publicaciones[1].pk],
		)
		self.assertIn(categoria, contexto['global_categorias'])

		response = self.client.get(reverse('home:index'))
		footer = response.content.decode().split('<footer class="site-footer">', 1)[1].split('</footer>', 1)[0]
		self.assertIn(publicaciones[3].titulo, footer)
		self.assertIn(publicaciones[2].titulo, footer)
		self.assertIn(publicaciones[1].titulo, footer)
		self.assertNotIn(publicaciones[0].titulo, footer)


class PortadasTests(TestCase):
	def test_index_incluye_modal_de_bienvenida_y_su_script(self):
		response = self.client.get(reverse('home:index'))

		self.assertContains(response, 'id="modalBienvenida"')
		self.assertContains(response, 'data-welcome-modal')
		self.assertContains(response, reverse('home:categoria'))
		self.assertContains(response, 'js/welcome-modal.js')

	def test_index_muestra_las_cinco_publicaciones_mas_recientes(self):
		ahora = timezone.now()
		publicaciones = []
		for indice in range(6):
			publicacion = Publicacion.objects.create(
				titulo=f'Portada {indice}',
				resumen='Resumen',
				contenido='Contenido',
				estado=Publicacion.ESTADO_PUBLICADO,
			)
			Publicacion.objects.filter(pk=publicacion.pk).update(
				createdat=ahora + timedelta(minutes=indice)
			)
			publicaciones.append(publicacion)

		Publicacion.objects.create(
			titulo='Borrador fuera de portadas',
			resumen='Resumen',
			contenido='Contenido',
			estado=Publicacion.ESTADO_BORRADOR,
		)

		response = self.client.get(reverse('home:index'))

		self.assertEqual(
			list(response.context['portadas'].values_list('pk', flat=True)),
			[publicacion.pk for publicacion in reversed(publicaciones[1:])],
		)
		self.assertContains(response, publicaciones[5].titulo)
		self.assertNotContains(response, 'Borrador fuera de portadas')

	def test_index_admite_portadas_vacias(self):
		response = self.client.get(reverse('home:index'))

		self.assertEqual(list(response.context['portadas']), [])
		self.assertEqual(response.status_code, 200)


class GetSinMutacionesTests(TestCase):
	def setUp(self):
		self.operador = User.objects.create_superuser(
			username='operador_get',
			email='operador@example.com',
			password='ClaveSegura123!',
		)
		self.usuario = User.objects.create_user(
			username='usuario_sin_perfil',
			password='ClaveSegura123!',
		)
		Perfil.objects.filter(user=self.usuario).delete()

	def test_perfil_y_crud_perfil_no_crean_perfil_con_get(self):
		self.client.force_login(self.usuario)

		self.assertEqual(self.client.get(reverse('home:perfil')).status_code, 200)
		self.assertEqual(self.client.get(reverse('home:crud_perfil')).status_code, 200)
		self.assertFalse(Perfil.objects.filter(user=self.usuario).exists())

	def test_editar_usuario_no_crea_perfil_con_get(self):
		self.client.force_login(self.operador)

		response = self.client.get(reverse('home:editar_usuario', args=[self.usuario.pk]))

		self.assertEqual(response.status_code, 200)
		self.assertFalse(Perfil.objects.filter(user=self.usuario).exists())


class EditarUsuarioPasswordTests(TestCase):
	def setUp(self):
		self.operador = User.objects.create_superuser(
			username='administrador_password',
			email='admin@example.com',
			password='ClaveSegura123!',
		)
		self.usuario = User.objects.create_user(
			username='usuario_password',
			email='usuario@example.com',
			password='ClaveOriginal123!',
		)
		self.client.force_login(self.operador)

	def test_rechaza_password_que_no_supera_los_validadores(self):
		response = self.client.post(
			reverse('home:editar_usuario', args=[self.usuario.pk]),
			{
				'username': self.usuario.username,
				'email': self.usuario.email,
				'password1': '123',
				'password2': '123',
			},
		)

		self.assertRedirects(
			response,
			reverse('home:editar_usuario', args=[self.usuario.pk]),
		)
		self.usuario.refresh_from_db()
		self.assertTrue(self.usuario.check_password('ClaveOriginal123!'))


class PanelAjaxTemplatesTests(TestCase):
	def setUp(self):
		self.operador = User.objects.create_superuser(
			username='operador_ajax',
			email='operador_ajax@example.com',
			password='ClaveSegura123!',
		)
		self.usuario = User.objects.create_user(
			username='usuario_ajax',
			password='ClaveSegura123!',
		)
		self.categoria = Categoria.objects.create(nombre='Categoría AJAX')
		self.client.force_login(self.operador)

	def test_vistas_del_panel_crud_incluyen_el_contenedor_ajax(self):
		rutas = [
			reverse('home:crud_categorias'),
			reverse('home:crud_comentarios'),
			reverse('home:crud_usuarios'),
			reverse('home:crear_usuario'),
			reverse('home:editar_categoria', args=[self.categoria.pk]),
			reverse('home:editar_usuario', args=[self.usuario.pk]),
		]

		for ruta in rutas:
			with self.subTest(ruta=ruta):
				response = self.client.get(ruta)
				self.assertEqual(response.status_code, 200)
				self.assertContains(response, 'data-panel-ajax')
				self.assertContains(response, 'js/panel-ajax.js')

	def test_perfil_incluye_el_contenedor_ajax(self):
		for ruta in (reverse('home:perfil'), reverse('home:crud_perfil')):
			with self.subTest(ruta=ruta):
				response = self.client.get(ruta)
				self.assertEqual(response.status_code, 200)
				self.assertContains(response, 'data-panel-ajax')
				self.assertContains(response, 'js/panel-ajax.js')

	def test_comentarios_ajax_no_aparecen_como_texto_visible(self):
		rutas = [
			reverse('home:perfil'),
			reverse('home:crud_perfil'),
			reverse('home:crud_categorias'),
			reverse('home:crud_comentarios'),
			reverse('home:crud_usuarios'),
			reverse('home:crear_usuario'),
			reverse('home:editar_categoria', args=[self.categoria.pk]),
		]

		for ruta in rutas:
			with self.subTest(ruta=ruta):
				response = self.client.get(ruta)
				contenido = response.content.decode().lower()
				self.assertNotIn('//ajax', contenido)
				self.assertNotIn('//carga', contenido)
				self.assertNotIn('//seleccion', contenido)


class ArchivoDisplayUrlTests(TestCase):
    def test_usa_static_para_recursos_estaticos_y_ruta_protegida_para_subidas(self):
        estatico = Archivo(ruta='images/logo.png')
        subido = Archivo.objects.create(
            nombre='portada.jpg',
            nombre_temporal='portada.jpg',
            ruta='uploads/portada.jpg',
        )

        self.assertEqual(estatico.display_url, '/static/images/logo.png')
        self.assertEqual(
            subido.display_url,
            reverse('home:mostrar_imagen', args=[subido.pk]),
        )


class MostrarImagenTests(TestCase):
    def setUp(self):
        self.directorio_media = TemporaryDirectory()
        self.configuracion_media = override_settings(MEDIA_ROOT=self.directorio_media.name)
        self.configuracion_media.enable()
        self.addCleanup(self.directorio_media.cleanup)
        self.addCleanup(self.configuracion_media.disable)

        self.operador = User.objects.create_user(
            username='operador_imagenes',
            password='ClaveSegura123!',
            is_staff=True,
        )
        self.propietario = User.objects.create_user(
            username='propietario_imagen',
            password='ClaveSegura123!',
        )
        self.otro_usuario = User.objects.create_user(
            username='otro_usuario_imagen',
            password='ClaveSegura123!',
        )

    def crear_archivo(self, nombre='imagen.jpg', contenido=b'imagen'):
        return Archivo.objects.create(
            nombre=nombre,
            nombre_temporal=nombre,
            ruta=SimpleUploadedFile(nombre, contenido),
        )

    def test_imagen_publicada_es_publica(self):
        archivo = self.crear_archivo()
        Publicacion.objects.create(
            titulo='Noticia publicada',
            resumen='Resumen',
            contenido='Contenido',
            estado=Publicacion.ESTADO_PUBLICADO,
            imagen_portada=archivo,
        )

        response = self.client.get(reverse('home:mostrar_imagen', args=[archivo.pk]))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'image/jpeg')
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        b''.join(response.streaming_content)

    def test_operador_puede_ver_portada_y_galeria_de_borrador(self):
        portada = self.crear_archivo('portada.jpg')
        galeria = self.crear_archivo('galeria.png')
        publicacion = Publicacion.objects.create(
            titulo='Borrador privado',
            resumen='Resumen',
            contenido='Contenido',
            estado=Publicacion.ESTADO_BORRADOR,
            imagen_portada=portada,
        )
        GaleriaPublicacion.objects.create(publicacion=publicacion, archivo=galeria)
        self.client.force_login(self.operador)

        for archivo in (portada, galeria):
            with self.subTest(archivo=archivo.nombre):
                response = self.client.get(reverse('home:mostrar_imagen', args=[archivo.pk]))
                self.assertEqual(response.status_code, 200)
                b''.join(response.streaming_content)

    def test_borrador_no_es_publico(self):
        archivo = self.crear_archivo()
        Publicacion.objects.create(
            titulo='Borrador privado',
            resumen='Resumen',
            contenido='Contenido',
            estado=Publicacion.ESTADO_BORRADOR,
            imagen_portada=archivo,
        )

        response = self.client.get(reverse('home:mostrar_imagen', args=[archivo.pk]))

        self.assertEqual(response.status_code, 404)

    def test_media_root_no_expone_archivos_por_ruta_directa(self):
        archivo = self.crear_archivo('privada.jpg')

        from canaco import urls as project_urls

        try:
            with override_settings(DEBUG=True):
                clear_url_caches()
                importlib.reload(project_urls)
                response = self.client.get(f'/media/{archivo.ruta.name}')
                if response.streaming:
                    b''.join(response.streaming_content)
        finally:
            clear_url_caches()
            importlib.reload(project_urls)

        self.assertEqual(response.status_code, 404)

    def test_foto_de_perfil_solo_es_visible_para_su_propietario(self):
        archivo = self.crear_archivo()
        perfil = Perfil.objects.get(user=self.propietario)
        perfil.foto_perfil = archivo
        perfil.save(update_fields=['foto_perfil'])

        self.client.force_login(self.otro_usuario)
        self.assertEqual(
            self.client.get(reverse('home:mostrar_imagen', args=[archivo.pk])).status_code,
            404,
        )

        self.client.force_login(self.propietario)
        response = self.client.get(reverse('home:mostrar_imagen', args=[archivo.pk]))
        self.assertEqual(response.status_code, 200)
        b''.join(response.streaming_content)

    def test_rechaza_formatos_no_permitidos_y_archivos_inexistentes(self):
        formato_invalido = self.crear_archivo('documento.txt', b'texto')
        archivo_inexistente = Archivo.objects.create(
            nombre='inexistente.jpg',
            nombre_temporal='inexistente.jpg',
            ruta='uploads/inexistente.jpg',
        )
        for archivo in (formato_invalido, archivo_inexistente):
            Publicacion.objects.create(
                titulo=f'Publicacion {archivo.pk}',
                resumen='Resumen',
                contenido='Contenido',
                estado=Publicacion.ESTADO_PUBLICADO,
                imagen_portada=archivo,
            )

        self.assertEqual(
            self.client.get(reverse('home:mostrar_imagen', args=[formato_invalido.pk])).status_code,
            404,
        )
        self.assertEqual(
            self.client.get(reverse('home:mostrar_imagen', args=[archivo_inexistente.pk])).status_code,
            404,
        )


class RegistroPublicoTests(TestCase):
    def test_registro_crea_usuario_y_actualiza_el_perfil_generado(self):
        response = self.client.post(reverse('home:sign_up'), {
            'username': 'registro_publico',
            'email': 'registro@example.com',
            'first_name': 'Registro',
            'apellido_paterno': 'Paterno',
            'apellido_materno': 'Materno',
            'password1': 'ClaveSegura123!',
            'password2': 'ClaveSegura123!',
        })

        self.assertRedirects(response, reverse('home:login'))
        usuario = User.objects.get(username='registro_publico')
        perfil = Perfil.objects.get(user=usuario)
        self.assertEqual(usuario.email, 'registro@example.com')
        self.assertEqual(usuario.last_name, 'Paterno Materno')
        self.assertEqual(perfil.apellido_paterno, 'Paterno')
        self.assertEqual(perfil.apellido_materno, 'Materno')
        self.assertEqual(Perfil.objects.filter(user=usuario).count(), 1)

    def test_registro_rechaza_contrasenas_distintas_sin_crear_usuario(self):
        response = self.client.post(reverse('home:sign_up'), {
            'username': 'registro_invalido',
            'email': 'invalido@example.com',
            'password1': 'ClaveSegura123!',
            'password2': 'OtraClaveSegura123!',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Las contraseñas no coinciden.')
        self.assertFalse(User.objects.filter(username='registro_invalido').exists())


class PrivacidadTests(TestCase):
    def test_pagina_de_privacidad_es_publica(self):
        response = self.client.get(reverse('home:privacidad'))

        self.assertEqual(response.status_code, 200)


class LogoutTests(TestCase):
    def setUp(self):
        self.usuario = User.objects.create_user(
            username='usuario_logout',
            password='ClaveSegura123!',
        )

    def test_logout_rechaza_get_sin_cerrar_la_sesion(self):
        self.client.force_login(self.usuario)

        response = self.client.get(reverse('home:logout'))

        self.assertEqual(response.status_code, 405)
        self.assertEqual(int(self.client.session['_auth_user_id']), self.usuario.pk)

    def test_logout_acepta_post_y_cierra_la_sesion(self):
        self.client.force_login(self.usuario)

        response = self.client.post(reverse('home:logout'))

        self.assertRedirects(response, reverse('home:index'))
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_logout_post_conserva_proteccion_csrf(self):
        cliente_csrf = Client(enforce_csrf_checks=True)
        cliente_csrf.force_login(self.usuario)

        response = cliente_csrf.post(reverse('home:logout'))

        self.assertEqual(response.status_code, 403)
        self.assertEqual(int(cliente_csrf.session['_auth_user_id']), self.usuario.pk)
