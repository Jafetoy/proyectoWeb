from datetime import timedelta
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone
from .context_processors import global_categorias
from .models import Categoria, Comentario, Perfil, Publicacion


class CrearUsuarioTests(TestCase):
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
		self.assertContains(response, 'Noticia pública')
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
