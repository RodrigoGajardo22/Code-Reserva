from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Servicio,
    Cliente,
    Coordinador,
    Empleado,
    ReservaServicio,
    SolicitudReserva,
)


User = get_user_model()


class SeedCommandTest(TestCase):

    def test_seed_carga_datos_y_es_idempotente(self):
        call_command('seed')

        self.assertEqual(Servicio.objects.count(), 7)
        self.assertEqual(Cliente.objects.count(), 5)
        self.assertEqual(Coordinador.objects.count(), 3)
        self.assertEqual(Empleado.objects.count(), 4)

        call_command('seed')
        self.assertEqual(Servicio.objects.count(), 7)
        self.assertEqual(Cliente.objects.count(), 5)

    def test_seed_omite_si_ya_hay_datos(self):
        Servicio.objects.create(nombre='Propio', descripcion='d', precio='10')
        call_command('seed')
        self.assertEqual(Servicio.objects.count(), 1)
        self.assertFalse(Cliente.objects.exists())

    def test_seed_force_resiembra(self):
        Servicio.objects.create(nombre='Propio', descripcion='d', precio='10')
        call_command('seed', '--force')
        self.assertEqual(Servicio.objects.count(), 7)
        self.assertEqual(Cliente.objects.count(), 5)

    def test_seed_crea_usuarios_para_empleados_activos(self):
        call_command('seed')

        activos = Empleado.objects.filter(activo=True)
        self.assertEqual(activos.count(), 3)
        for empleado in activos:
            self.assertIsNotNone(empleado.usuario)
            self.assertEqual(empleado.usuario.username, str(empleado.numero_legajo))
            self.assertTrue(empleado.usuario.check_password(str(empleado.numero_documento)))

        inactivo = Empleado.objects.get(numero_legajo=4)
        self.assertIsNone(inactivo.usuario)


def _empleado_con_usuario(nombre='Emi', apellido='Ruiz', documento=5, legajo=1):
    empleado = Empleado.objects.create(
        nombre=nombre, apellido=apellido,
        numero_documento=documento, numero_legajo=legajo,
    )
    empleado.sincronizar_usuario()
    return empleado


class HomePublicaTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.servicio = Servicio.objects.create(nombre='Catering', descripcion='d', precio='100')
        Servicio.objects.create(nombre='Salón', descripcion='d', precio='300', activo=False)

    def test_home_muestra_solo_servicios_activos_sin_kpis(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Catering')
        self.assertNotContains(response, 'Salón')
        self.assertContains(response, 'Hacer una reserva')
        self.assertContains(response, 'Consultar reserva por DNI')
        self.assertNotContains(response, 'Reservas de hoy')

    def test_home_tiene_link_de_reserva_por_servicio(self):
        response = self.client.get(reverse('home'))
        self.assertContains(
            response,
            reverse('solicitud_reserva') + f'?servicio={self.servicio.pk}',
        )


class AccesoTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.empleado = _empleado_con_usuario()

    def test_anomino_no_accede_al_panel(self):
        response = self.client.get(reverse('dashboard'))
        self.assertRedirects(
            response,
            reverse('ingresar') + '?next=' + reverse('dashboard'),
        )

    def test_login_con_legajo_y_dni(self):
        response = self.client.post(reverse('ingresar'), {
            'username': str(self.empleado.numero_legajo),
            'password': str(self.empleado.numero_documento),
        })
        self.assertRedirects(response, reverse('dashboard'))

    def test_login_datos_incorrectos(self):
        response = self.client.post(reverse('ingresar'), {
            'username': str(self.empleado.numero_legajo),
            'password': '999999',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('_auth_user_id', self.client.session)

    def test_salir(self):
        self.client.login(
            username=str(self.empleado.numero_legajo),
            password=str(self.empleado.numero_documento),
        )
        response = self.client.get(reverse('salir'))
        self.assertRedirects(response, reverse('home'))
        self.assertNotIn('_auth_user_id', self.client.session)


class DashboardKpisTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.hoy = timezone.localdate()

        Servicio.objects.create(nombre='Catering', descripcion='d', precio='100')
        Servicio.objects.create(nombre='DJ', descripcion='d', precio='200')
        Servicio.objects.create(nombre='Salón', descripcion='d', precio='300', activo=False)

        cls.cliente = Cliente.objects.create(nombre='Ana', apellido='Gómez', numero_documento=1)
        Cliente.objects.create(nombre='Beto', apellido='Pérez', numero_documento=2, activo=False)

        cls.coordinador = Coordinador.objects.create(nombre='Carla', apellido='Díaz', numero_documento=3)
        Coordinador.objects.create(nombre='Ciro', apellido='López', numero_documento=4, activo=False)

        cls.empleado = _empleado_con_usuario()
        Empleado.objects.create(nombre='Eva', apellido='Sosa', numero_documento=6, numero_legajo=2, activo=False)

        cls.servicio = Servicio.objects.get(nombre='Catering')
        otro_servicio = Servicio.objects.get(nombre='DJ')

        def reserva(servicio, fecha):
            ReservaServicio.objects.create(
                cliente=cls.cliente,
                servicio=servicio,
                empleado=cls.empleado,
                coordinador=cls.coordinador,
                fecha_servicio=fecha,
            )

        reserva(cls.servicio, cls.hoy)
        reserva(otro_servicio, cls.hoy)
        reserva(cls.servicio, cls.hoy + timedelta(days=3))
        reserva(cls.servicio, cls.hoy + timedelta(days=30))

    def setUp(self):
        self.client.login(
            username=str(self.empleado.numero_legajo),
            password=str(self.empleado.numero_documento),
        )

    def test_kpis(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reservas de hoy')
        self.assertContains(response, 'Próximas reservas (7 días)')
        self.assertContains(response, 'Servicios activos')
        self.assertContains(response, 'Clientes activos')
        self.assertContains(response, 'Personal disponible')

    def test_conteos(self):
        response = self.client.get(reverse('dashboard'))
        context = response.context
        self.assertEqual(context['reservas_hoy'], 2)
        self.assertEqual(context['reservas_proximas'], 3)
        self.assertEqual(context['servicios_activos'], 2)
        self.assertEqual(context['clientes_activos'], 1)
        self.assertEqual(context['personal_disponible'], 2)
        self.assertEqual(context['solicitudes_pendientes'], 0)


class CRUDRequiereLoginTest(TestCase):

    def test_crear_servicio_requiere_login(self):
        response = self.client.get(reverse('servicio_nuevo'))
        self.assertRedirects(
            response,
            reverse('ingresar') + '?next=' + reverse('servicio_nuevo'),
        )

    def test_listar_clientes_requiere_login(self):
        response = self.client.get(reverse('clientes'))
        self.assertRedirects(
            response,
            reverse('ingresar') + '?next=' + reverse('clientes'),
        )


class ServicioViewsTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.empleado = _empleado_con_usuario()

    def setUp(self):
        self.client.login(
            username=str(self.empleado.numero_legajo),
            password=str(self.empleado.numero_documento),
        )

    def test_crear_servicio(self):
        response = self.client.post(reverse('servicio_nuevo'), {
            'nombre': 'Catering',
            'descripcion': 'Menú personalizado',
            'precio': '5000.00',
            'activo': 'on',
        })
        self.assertRedirects(response, reverse('servicios'))
        self.assertEqual(Servicio.objects.filter(activo=True).count(), 1)

    def test_listar_solo_activos(self):
        Servicio.objects.create(nombre='Activo', descripcion='d', precio='1')
        Servicio.objects.create(nombre='DesactivadoXYZ', descripcion='d', precio='1', activo=False)
        response = self.client.get(reverse('servicios'))
        self.assertContains(response, 'Activo')
        self.assertNotContains(response, 'DesactivadoXYZ')

    def test_editar_servicio(self):
        servicio = Servicio.objects.create(nombre='Salón', descripcion='d', precio='100')
        response = self.client.post(reverse('servicio_editar', args=[servicio.pk]), {
            'nombre': 'Salón Premium',
            'descripcion': 'd',
            'precio': '200',
            'activo': 'on',
        })
        self.assertRedirects(response, reverse('servicios'))
        servicio.refresh_from_db()
        self.assertEqual(servicio.nombre, 'Salón Premium')
        self.assertEqual(servicio.precio, 200)

    def test_baja_logica(self):
        servicio = Servicio.objects.create(nombre='Salón', descripcion='d', precio='100')
        response = self.client.post(reverse('servicio_eliminar', args=[servicio.pk]))
        self.assertRedirects(response, reverse('servicios'))
        servicio.refresh_from_db()
        self.assertFalse(servicio.activo)
        self.assertTrue(Servicio.objects.filter(pk=servicio.pk).exists())

    def test_listar_y_restaurar_inactivos(self):
        servicio = Servicio.objects.create(nombre='Salón', descripcion='d', precio='100', activo=False)
        response = self.client.get(reverse('servicios_inactivos'))
        self.assertContains(response, 'Salón')
        response = self.client.post(reverse('servicio_restaurar', args=[servicio.pk]))
        self.assertRedirects(response, reverse('servicios_inactivos'))
        servicio.refresh_from_db()
        self.assertTrue(servicio.activo)


class SolicitudReservaFlowTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.servicio = Servicio.objects.create(nombre='Catering', descripcion='d', precio='100')
        cls.empleado = _empleado_con_usuario()
        cls.coordinador = Coordinador.objects.create(nombre='Carla', apellido='Díaz', numero_documento=3)
        cls.mañana = timezone.localdate() + timedelta(days=1)

    def setUp(self):
        self.client.login(
            username=str(self.empleado.numero_legajo),
            password=str(self.empleado.numero_documento),
        )

    def test_cliente_puede_dejar_solicitud(self):
        self.client.logout()
        response = self.client.post(reverse('solicitud_reserva'), {
            'servicio': self.servicio.pk,
            'nombre': 'María',
            'apellido': 'González',
            'numero_documento': '30111222',
            'fecha_servicio': self.mañana.isoformat(),
        })
        self.assertRedirects(response, reverse('home'))
        solicitud = SolicitudReserva.objects.get()
        self.assertEqual(solicitud.estado, SolicitudReserva.ESTADO_PENDIENTE)
        self.assertEqual(solicitud.numero_documento, 30111222)

    def test_atender_solicitud_crea_reserva_y_cliente(self):
        solicitud = SolicitudReserva.objects.create(
            servicio=self.servicio,
            nombre='María',
            apellido='González',
            numero_documento='30111222',
            telefono=1151234567,
            email='maria@mail.com',
            fecha_servicio=self.mañana,
        )

        response = self.client.post(
            reverse('solicitud_atender', args=[solicitud.pk]),
            {
                'empleado': self.empleado.pk,
                'coordinador': self.coordinador.pk,
                'fecha_servicio': self.mañana.isoformat(),
            },
        )
        self.assertRedirects(response, reverse('solicitudes'))

        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, SolicitudReserva.ESTADO_ACEPTADA)
        self.assertIsNotNone(solicitud.reserva)

        cliente = Cliente.objects.get(numero_documento=30111222)
        self.assertEqual(cliente.nombre, 'María')
        reserva = ReservaServicio.objects.get()
        self.assertEqual(reserva.cliente, cliente)
        self.assertEqual(reserva.servicio, self.servicio)
        self.assertEqual(reserva.empleado, self.empleado)
        self.assertEqual(reserva.coordinador, self.coordinador)

    def test_atender_reutiliza_cliente_existente(self):
        cliente = Cliente.objects.create(
            nombre='Carlos', apellido='Pérez', numero_documento=25111222,
        )
        solicitud = SolicitudReserva.objects.create(
            servicio=self.servicio,
            nombre='Carlos',
            apellido='Pérez',
            numero_documento='25111222',
            fecha_servicio=self.mañana,
        )

        response = self.client.post(
            reverse('solicitud_atender', args=[solicitud.pk]),
            {
                'empleado': self.empleado.pk,
                'coordinador': self.coordinador.pk,
                'fecha_servicio': self.mañana.isoformat(),
            },
        )
        self.assertRedirects(response, reverse('solicitudes'))
        self.assertEqual(Cliente.objects.count(), 1)
        self.assertEqual(Cliente.objects.get().pk, cliente.pk)

    def test_atender_falla_si_servicio_ya_reservado_esa_fecha(self):
        cliente = Cliente.objects.create(nombre='Ana', apellido='Gómez', numero_documento=1)
        ReservaServicio.objects.create(
            cliente=cliente,
            servicio=self.servicio,
            empleado=self.empleado,
            coordinador=self.coordinador,
            fecha_servicio=self.mañana,
        )
        solicitud = SolicitudReserva.objects.create(
            servicio=self.servicio,
            nombre='María',
            apellido='González',
            numero_documento='30111222',
            fecha_servicio=self.mañana,
        )

        response = self.client.post(
            reverse('solicitud_atender', args=[solicitud.pk]),
            {
                'empleado': self.empleado.pk,
                'coordinador': self.coordinador.pk,
                'fecha_servicio': self.mañana.isoformat(),
            },
        )
        self.assertEqual(response.status_code, 200)
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, SolicitudReserva.ESTADO_PENDIENTE)
        self.assertEqual(ReservaServicio.objects.count(), 1)

    def test_rechazar_solicitud(self):
        solicitud = SolicitudReserva.objects.create(
            servicio=self.servicio,
            nombre='María',
            apellido='González',
            numero_documento='30111222',
            fecha_servicio=self.mañana,
        )

        response = self.client.post(reverse('solicitud_rechazar', args=[solicitud.pk]))
        self.assertRedirects(response, reverse('solicitudes'))

        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, SolicitudReserva.ESTADO_RECHAZADA)
        self.assertEqual(ReservaServicio.objects.count(), 0)

        pagina = self.client.get(reverse('solicitudes'))
        self.assertEqual(pagina.context['pendientes'].count(), 0)
        self.assertEqual(pagina.context['historial'].count(), 1)

    def test_no_se_puede_rechazar_dos_veces(self):
        solicitud = SolicitudReserva.objects.create(
            servicio=self.servicio,
            nombre='María',
            apellido='González',
            numero_documento='30111222',
            estado=SolicitudReserva.ESTADO_RECHAZADA,
        )

        self.client.post(reverse('solicitud_rechazar', args=[solicitud.pk]))
        solicitud.refresh_from_db()
        self.assertEqual(solicitud.estado, SolicitudReserva.ESTADO_RECHAZADA)

    def test_badge_solicitudes_pendientes(self):
        SolicitudReserva.objects.create(
            servicio=self.servicio,
            nombre='María',
            apellido='González',
            numero_documento='30111222',
        )
        SolicitudReserva.objects.create(
            servicio=self.servicio,
            nombre='Pedro',
            apellido='López',
            numero_documento='30111223',
        )

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            '<span class="badge rounded-pill bg-danger ms-1">2</span>',
            html=True,
        )

    def test_consulta_muestra_todos_los_estados(self):
        cliente = Cliente.objects.create(nombre='Ana', apellido='Gómez', numero_documento=30111222)
        reserva = ReservaServicio.objects.create(
            cliente=cliente,
            servicio=self.servicio,
            empleado=self.empleado,
            coordinador=self.coordinador,
            fecha_servicio=self.mañana,
        )
        SolicitudReserva.objects.create(
            servicio=self.servicio,
            nombre='María',
            apellido='González',
            numero_documento='30111222',
            fecha_servicio=self.mañana,
        )
        SolicitudReserva.objects.create(
            servicio=self.servicio,
            nombre='Pedro',
            apellido='López',
            numero_documento='30111222',
            estado=SolicitudReserva.ESTADO_RECHAZADA,
        )

        self.client.logout()
        response = self.client.post(reverse('consulta_reserva'), {
            'numero_documento': '30111222',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Aceptada')
        self.assertContains(response, 'Pendiente')
        self.assertContains(response, 'Rechazada')
        self.assertContains(response, reverse('reserva_imprimir', args=[reserva.pk]))

    def test_consulta_por_dni(self):
        cliente = Cliente.objects.create(nombre='Ana', apellido='Gómez', numero_documento=25111222)
        reserva = ReservaServicio.objects.create(
            cliente=cliente,
            servicio=self.servicio,
            empleado=self.empleado,
            coordinador=self.coordinador,
            fecha_servicio=self.mañana,
        )

        self.client.logout()
        response = self.client.post(reverse('consulta_reserva'), {
            'numero_documento': '25111222',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Catering')
        self.assertContains(response, reverse('reserva_imprimir', args=[reserva.pk]))

    def test_consulta_por_dni_sin_resultados(self):
        self.client.logout()
        response = self.client.post(reverse('consulta_reserva'), {
            'numero_documento': '99999999',
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No se encontraron reservas')
