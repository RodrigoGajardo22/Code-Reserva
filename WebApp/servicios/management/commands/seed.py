from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError

from servicios.models import Servicio, Cliente, Coordinador, Empleado

SERVICIOS = [
    {
        'nombre': 'Desarrollo web a medida',
        'descripcion': 'Sitios y aplicaciones web desarrollados a medida, listos para escalar con tu negocio.',
        'precio': '300000.00',
    },
    {
        'nombre': 'Apps móviles',
        'descripcion': 'Aplicaciones para iOS y Android: desde la idea hasta la publicación en las tiendas.',
        'precio': '350000.00',
    },
    {
        'nombre': 'Sistemas de gestión',
        'descripcion': 'Software a medida para administrar ventas, stock, clientes y equipos de trabajo.',
        'precio': '400000.00',
    },
    {
        'nombre': 'E-commerce',
        'descripcion': 'Tienda online con medios de pago, logística y panel de administración integrados.',
        'precio': '280000.00',
    },
    {
        'nombre': 'Cloud y DevOps',
        'descripcion': 'Infraestructura en la nube, despliegues automatizados y monitoreo de tus aplicaciones.',
        'precio': '200000.00',
    },
    {
        'nombre': 'Soporte y mantenimiento',
        'descripcion': 'Mantenimiento evolutivo y soporte técnico continuo para tus sistemas.',
        'precio': '90000.00',
    },
]

CLIENTES = [
    {'nombre': 'María', 'apellido': 'González', 'numero_documento': 30111222, 'telefono': 1151234567, 'email': 'mariagonzalez@mail.com'},
    {'nombre': 'Jorge', 'apellido': 'Pérez', 'numero_documento': 30111223, 'telefono': 1151234568, 'email': 'jorgeperez@mail.com'},
    {'nombre': 'Lucía', 'apellido': 'Fernández', 'numero_documento': 30111224, 'telefono': 1151234569, 'email': 'luciafernandez@mail.com'},
    {'nombre': 'Martín', 'apellido': 'Rodríguez', 'numero_documento': 30111225, 'telefono': 1151234570, 'email': 'martinrodriguez@mail.com'},
]

COORDINADORES = [
    {'nombre': 'Ana', 'apellido': 'López', 'numero_documento': 25111222},
    {'nombre': 'Carlos', 'apellido': 'Martínez', 'numero_documento': 25111223},
]

EMPLEADOS = [
    {'nombre': 'Pedro', 'apellido': 'Sánchez', 'numero_documento': 27111222, 'numero_legajo': 1},
    {'nombre': 'Laura', 'apellido': 'Romero', 'numero_documento': 27111223, 'numero_legajo': 2},
    {'nombre': 'Diego', 'apellido': 'Torres', 'numero_documento': 27111224, 'numero_legajo': 3},
]


def _hay_datos():
    return (
        Servicio.objects.exists()
        or Cliente.objects.exists()
        or Coordinador.objects.exists()
        or Empleado.objects.exists()
    )


def seedear():
    Servicio.objects.create(
        nombre='Página institucional básica',
        descripcion='Sitio estático simple de una sola sección. (Dado de baja)',
        precio='50000.00',
        activo=False,
    )
    for datos in SERVICIOS:
        Servicio.objects.create(**datos)

    for datos in CLIENTES:
        Cliente.objects.create(**datos)
    Cliente.objects.create(
        nombre='Elena', apellido='García', numero_documento=30111226,
        telefono=1151234571, email='elenagarcia@mail.com', activo=False,
    )

    for datos in COORDINADORES:
        Coordinador.objects.create(**datos)
    Coordinador.objects.create(
        nombre='Silvia', apellido='Díaz', numero_documento=25111224, activo=False,
    )

    for datos in EMPLEADOS:
        empleado = Empleado.objects.create(**datos)
        empleado.sincronizar_usuario()
    Empleado.objects.create(
        nombre='Nicolás', apellido='Álvarez', numero_documento=27111225,
        numero_legajo=4, activo=False,
    )


class Command(BaseCommand):
    help = 'Sembra datos de ejemplo (servicios, clientes, coordinadores y empleados).'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Borra los datos existentes de estas tablas antes de sembrar.',
        )

    def handle(self, *args, **options):
        if options['force']:
            # Los empleados crean su usuario de acceso con username = legajo (número).
            # Se eliminan también los que quedaron huérfanos de seeds anteriores
            # (el usuario se desvincula al borrar al empleado).
            User = get_user_model()
            User.objects.filter(username__regex=r'^\d+$').delete()
            Servicio.objects.all().delete()
            Cliente.objects.all().delete()
            Coordinador.objects.all().delete()
            Empleado.objects.all().delete()
            self.stdout.write(self.style.WARNING('Datos anteriores eliminados.'))

        if _hay_datos():
            self.stdout.write(self.style.NOTICE('Ya hay datos cargados, seed omitido.'))
            return

        try:
            seedear()
        except Exception as e:
            raise CommandError(f'Error al sembrar datos: {e}')

        self.stdout.write(self.style.SUCCESS('Seed completado: datos de ejemplo cargados.'))
