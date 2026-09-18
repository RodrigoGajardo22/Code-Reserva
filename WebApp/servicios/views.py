import io
from io import BytesIO
from datetime import timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from django.http import FileResponse, HttpResponse
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.utils import timezone
from .forms import (
    ServicioForm,
    ReservaForm,
    ClienteForm,
    CoordinadorForm,
    EmpleadoForm,
    SolicitudReservaForm,
    AtenderSolicitudForm,
)
from .models import (
    Servicio,
    Cliente,
    ReservaServicio,
    Coordinador,
    Empleado,
    SolicitudReserva,
)
from .base_views import BajaLogicaView, RestaurarView


# ---------------- Acceso ----------------

def ingresar(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        usuario = authenticate(request, username=username, password=password)
        if usuario is not None:
            login(request, usuario)
            return redirect('dashboard')

        messages.error(request, 'Legajo o contraseña incorrectos.')

    return render(request, 'login.html')


def salir(request):
    logout(request)
    return redirect('home')


# ---------------- Home público (cliente) ----------------

def home(request):
    servicios = Servicio.objects.filter(activo=True)

    return render(request, 'home.html', {
        'servicios': servicios,
    })


# ---------------- Panel interno (empleado) ----------------

@login_required(login_url='ingresar')
def dashboard(request):
    hoy = timezone.localdate()
    servicios = Servicio.objects.filter(activo=True)

    reservas_hoy = ReservaServicio.objects.filter(fecha_servicio=hoy).count()
    reservas_proximas = ReservaServicio.objects.filter(
        fecha_servicio__gte=hoy,
        fecha_servicio__lte=hoy + timedelta(days=7),
    ).count()

    clientes_activos = Cliente.objects.filter(activo=True).count()
    personal_disponible = (
        Coordinador.objects.filter(activo=True).count()
        + Empleado.objects.filter(activo=True).count()
    )
    solicitudes_pendientes = SolicitudReserva.objects.filter(estado=SolicitudReserva.ESTADO_PENDIENTE).count()

    context = {
        'servicios': servicios,
        'reservas_hoy': reservas_hoy,
        'reservas_proximas': reservas_proximas,
        'servicios_activos': servicios.count(),
        'clientes_activos': clientes_activos,
        'personal_disponible': personal_disponible,
        'solicitudes_pendientes': solicitudes_pendientes,
    }
    return render(request, 'dashboard.html', context)


# ---------------- Servicio ----------------

@login_required(login_url='ingresar')
def listar_servicios(request):
    buscar = request.GET.get('buscar', '').strip()

    servicios = Servicio.objects.filter(activo=True)

    if buscar:
        palabras = buscar.split()

        for palabra in palabras:
            servicios = servicios.filter(
                Q(nombre__icontains=palabra)
            )

    return render(request, 'servicios/listar.html', {
        'servicios': servicios,
        'buscar': buscar,
    })


@login_required(login_url='ingresar')
def crear_servicio(request):
    if request.method == 'POST':
        form = ServicioForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio creado correctamente.')
            return redirect('servicios')
    else:
        form = ServicioForm()
    return render(request, 'servicios/form.html', {'form': form})


@login_required(login_url='ingresar')
def editar_servicio(request, pk):
    servicio = get_object_or_404(Servicio, pk=pk)
    if request.method == 'POST':
        form = ServicioForm(request.POST, instance=servicio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio actualizado correctamente.')
            return redirect('servicios')
    else:
        form = ServicioForm(instance=servicio)
    return render(request, 'servicios/form.html', {'form': form, 'servicio': servicio})


@login_required(login_url='ingresar')
def listar_inactivos(request):
    buscar = request.GET.get('buscar', '').strip()

    servicios = Servicio.objects.filter(activo=False)

    if buscar:
        palabras = buscar.split()

        for palabra in palabras:
            servicios = servicios.filter(
                Q(nombre__icontains=palabra)
            )

    return render(request, 'servicios/inactivos.html', {
        'servicios': servicios,
        'buscar': buscar,
    })

class BajaServicio(BajaLogicaView):
    model = Servicio
    success_url = 'servicios'
class RestaurarServicio(RestaurarView):
    model = Servicio
    success_url = 'servicios_inactivos'


# ---------------- Cliente ----------------

@login_required(login_url='ingresar')
def listar_clientes(request):
    buscar = request.GET.get('buscar', '').strip()

    clientes = Cliente.objects.filter(activo=True)

    if buscar:
        palabras = buscar.split()

        for palabra in palabras:
            clientes = clientes.filter(
                Q(nombre__icontains=palabra) |
                Q(apellido__icontains=palabra) |
                Q(numero_documento__icontains=palabra)
            )

    return render(request, 'clientes/listar.html', {
        'clientes': clientes,
        'buscar': buscar,
    })


@login_required(login_url='ingresar')
def crear_cliente(request):
    if request.method == 'POST':
        form = ClienteForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente agregado correctamente.')
            return redirect('clientes')
    else:
        form = ClienteForm()
    return render(request, 'clientes/form.html', {'form': form})


@login_required(login_url='ingresar')
def editar_cliente(request, pk):
    cliente = get_object_or_404(Cliente, pk=pk)
    if request.method == 'POST':
        form = ClienteForm(request.POST, instance=cliente)
        if form.is_valid():
            form.save()
            messages.success(request, 'Cliente actualizado correctamente.')
            return redirect('clientes')
    else:
        form = ClienteForm(instance=cliente)
    return render(request, 'clientes/form.html', {'form': form, 'cliente': cliente})


class BajaCliente(BajaLogicaView):
    model = Cliente
    success_url = 'clientes'


@login_required(login_url='ingresar')
def listar_clientes_inactivos(request):
    buscar = request.GET.get('buscar', '').strip()

    clientes = Cliente.objects.filter(activo=False)

    if buscar:
        palabras = buscar.split()

        for palabra in palabras:
            clientes = clientes.filter(
                Q(nombre__icontains=palabra) |
                Q(apellido__icontains=palabra) |
                Q(numero_documento__icontains=palabra)
            )

    return render(request, 'clientes/inactivos.html', {
        'clientes': clientes,
        'buscar': buscar,
    })


class RestaurarCliente(RestaurarView):
    model = Cliente
    success_url = 'clientes_inactivos'


# ---------------- Reserva Servicio ----------------

@login_required(login_url='ingresar')
def listar_reservas(request):
    buscar = request.GET.get('buscar', '').strip()

    reservas = ReservaServicio.objects.filter()
    if buscar:
        palabras = buscar.split()

        for palabra in palabras:
            reservas = reservas.filter(
                Q(fecha_reserva__icontains=palabra)
            )

    return render(request, 'reservas/listar.html', {
        'reservas': reservas,
        'buscar': buscar,
    })


@login_required(login_url='ingresar')
def crear_reserva(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva Exitosa')
            return redirect('reservas')
    else:
        form = ReservaForm()
    return render(request, 'reservas/form.html', {'form': form})


@login_required(login_url='ingresar')
def editar_reserva(request, pk):
    reserva = get_object_or_404(ReservaServicio, pk=pk)
    form = ReservaForm(request.POST or None, instance=reserva)
    if form.is_valid():
        form.save()
        messages.success(request, "Reserva Actualizada")
        return redirect('reservas')
    return render(request, 'reservas/form.html', {'form': form})


@login_required(login_url='ingresar')
def eliminar_reserva(request, pk):
    reserva = get_object_or_404(ReservaServicio, pk=pk)
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, "Reserva eliminada")
        return redirect('reservas')


def datos_reserva(request, pk):
    reserva = get_object_or_404(ReservaServicio, pk=pk)

    cliente = reserva.cliente
    empleado = reserva.empleado
    coordinador = reserva.coordinador
    servicio = reserva.servicio
    fecha_servicio = reserva.fecha_servicio
    fecha_reserva = reserva.fecha_reserva

    info = [
        ("Cliente:", f"{cliente.nombre} {cliente.apellido}"),
        ("DNI:", f"{cliente.numero_documento}"),
        ("Servicio:", f"{servicio.nombre}"),
        ("Empleado:", f"{empleado.nombre} {empleado.apellido}"),
        ("DNI:", f"{empleado.numero_documento}"),
        ("Coordinador:", f"{coordinador.nombre} {coordinador.apellido}"),
        ("DNI:", f"{coordinador.numero_documento}"),
        ("Fecha del servicio:", fecha_servicio),
        ("Fecha de reserva:", fecha_reserva),
    ]

    buffer = BytesIO()

    datos = canvas.Canvas(buffer, pagesize=A4)

    ancho, alto = A4

    color_principal = colors.HexColor("#14344e")
    color_secundario = colors.HexColor("#F4F3FF")
    color_texto = colors.HexColor("#333333")
    color_gris = colors.HexColor("#777777")

    # --------------------------------------------------
    # ENCABEZADO
    # --------------------------------------------------

    datos.setFillColor(color_principal)
    datos.rect(
        0,
        alto - 100,
        ancho,
        100,
        fill=1,
        stroke=0
    )

    datos.setFillColor(colors.white)
    datos.setFont("Helvetica-Bold", 24)
    datos.drawString(
        50,
        alto - 55,
        "DATOS DE LA RESERVA"
    )

    datos.setFont("Helvetica", 10)
    # --------------------------------------------------
    # TÍTULO
    # --------------------------------------------------
    y = alto - 140

    datos.setFillColor(color_texto)
    datos.setFont("Helvetica-Bold", 16)
    datos.drawString(
        50,
        y,
        "Datos de la reserva"
    )

    # Línea decorativa

    datos.setStrokeColor(color_principal)
    datos.setLineWidth(2)
    datos.line(
        50,
        y - 10,
        ancho - 50,
        y - 10
    )

    # --------------------------------------------------
    # CAJA DE INFORMACIÓN
    # --------------------------------------------------

    y -= 50

    datos.setFillColor(color_secundario)

    info_amplitud = 0
    for etiqueta, valor in info:
        info_amplitud += 30

    datos.roundRect(
        50,
        y - 15 - info_amplitud,
        ancho - 100,
        info_amplitud,
        10,
        fill=1,
        stroke=0
    )


    # --------------------------------------------------
    # DATOS
    # --------------------------------------------------

    x_label = 70
    x_value = 210

    datos.setFont("Helvetica-Bold", 11)
    datos.setFillColor(color_texto)

    posicion_y = y - 35

    for etiqueta, valor in info:

        datos.setFillColor(color_gris)
        datos.setFont("Helvetica-Bold", 10)
        datos.drawString(
            x_label,
            posicion_y,
            etiqueta
        )

        datos.setFillColor(color_texto)
        datos.setFont("Helvetica", 10)
        datos.drawString(
            x_value,
            posicion_y,
            str(valor)
        )

        posicion_y -= 30

    # --------------------------------------------------
    # MENSAJE FINAL
    # --------------------------------------------------

    datos.setFillColor(color_principal)
    datos.setFont("Helvetica-Bold", 12)

    datos.drawCentredString(
        ancho / 2,
        180,
        "¡Gracias por confiar en nosotros!"
    )

    datos.setFillColor(color_gris)
    datos.setFont("Helvetica", 9)

    datos.drawCentredString(
        ancho / 2,
        160,
        "Conserve este archivo para revisar los datos de su reserva."
    )

    # --------------------------------------------------
    # PIE DE PÁGINA
    # --------------------------------------------------

    datos.setStrokeColor(colors.lightgrey)
    datos.line(
        50,
        100,
        ancho - 50,
        100
    )

    datos.setFillColor(color_gris)
    datos.setFont("Helvetica", 8)

    datos.drawCentredString(
        ancho / 2,
        80,
        "CodeReserva - Sistemas & Apps"
    )

    # --------------------------------------------------
    # GENERAR PDF
    # --------------------------------------------------

    datos.showPage()
    datos.save()

    buffer.seek(0)

    response = HttpResponse(
        buffer,
        content_type="application/pdf"
    )

    response["Content-Disposition"] = (
        f'attachment; filename="reserva_{reserva.cliente.nombre}_{reserva.cliente.apellido}_{fecha_servicio}.pdf"'
    )

    return response


# ---------------- Solicitudes de reserva (cliente) ----------------

def solicitud_reserva(request):
    servicio_id = request.GET.get('servicio')
    initial = {}
    if servicio_id:
        servicio = Servicio.objects.filter(activo=True, pk=servicio_id).first()
        if servicio:
            initial['servicio'] = servicio

    if request.method == 'POST':
        form = SolicitudReservaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                '¡Gracias! Recibimos tu solicitud. Un integrante de nuestro equipo te va a contactar para confirmar la reserva.',
            )
            return redirect('home')
    else:
        form = SolicitudReservaForm(initial=initial)

    return render(request, 'reservas/solicitar.html', {'form': form})


def consulta_reserva(request):
    solicitudes = None
    reservas = None
    dni = None

    if request.method == 'POST':
        dni = request.POST.get('numero_documento', '').strip()
        if dni:
            try:
                dni_int = int(dni)
            except ValueError:
                dni_int = None

            if dni_int is not None:
                solicitudes = SolicitudReserva.objects.filter(
                    numero_documento=dni_int
                ).exclude(
                    estado=SolicitudReserva.ESTADO_ACEPTADA
                ).order_by('-fecha_registro')

                reservas = ReservaServicio.objects.filter(
                    cliente__numero_documento=dni_int
                ).order_by('-fecha_servicio')

    return render(request, 'reservas/consultar.html', {
        'solicitudes': solicitudes,
        'reservas': reservas,
        'dni': dni,
    })


@login_required(login_url='ingresar')
def listar_solicitudes(request):
    pendientes = SolicitudReserva.objects.filter(
        estado=SolicitudReserva.ESTADO_PENDIENTE
    ).order_by('-fecha_registro')

    historial = SolicitudReserva.objects.exclude(
        estado=SolicitudReserva.ESTADO_PENDIENTE
    ).order_by('-fecha_registro')

    return render(request, 'solicitudes/listar.html', {
        'pendientes': pendientes,
        'historial': historial,
    })


@login_required(login_url='ingresar')
def rechazar_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudReserva, pk=pk)

    if request.method == 'POST':
        if solicitud.estado != SolicitudReserva.ESTADO_PENDIENTE:
            messages.info(request, 'Esta solicitud ya no está pendiente.')
            return redirect('solicitudes')

        solicitud.estado = SolicitudReserva.ESTADO_RECHAZADA
        solicitud.save()

        messages.success(
            request,
            f'Solicitud de {solicitud.nombre} {solicitud.apellido} rechazada.',
        )
        return redirect('solicitudes')

    return redirect('solicitudes')


@login_required(login_url='ingresar')
def atender_solicitud(request, pk):
    solicitud = get_object_or_404(SolicitudReserva, pk=pk)

    if solicitud.estado != SolicitudReserva.ESTADO_PENDIENTE:
        messages.info(request, 'Esta solicitud ya no está pendiente.')
        return redirect('solicitudes')

    empleado_actual = None
    try:
        empleado_actual = request.user.empleado
    except Empleado.DoesNotExist:
        pass

    initial = {
        'fecha_servicio': solicitud.fecha_servicio or timezone.localdate(),
    }
    if empleado_actual is not None and empleado_actual.activo:
        initial['empleado'] = empleado_actual

    if request.method == 'POST':
        form = AtenderSolicitudForm(request.POST, initial=initial)
        if form.is_valid():
            servicio = solicitud.servicio
            empleado = form.cleaned_data['empleado']
            coordinador = form.cleaned_data['coordinador']
            fecha_servicio = form.cleaned_data['fecha_servicio']

            cliente = Cliente.objects.filter(numero_documento=solicitud.numero_documento).first()
            cliente_creado = False
            if cliente is None:
                cliente = Cliente(
                    nombre=solicitud.nombre,
                    apellido=solicitud.apellido,
                    numero_documento=solicitud.numero_documento,
                    telefono=solicitud.telefono,
                    email=solicitud.email,
                    activo=True,
                )
                cliente.save()
                cliente_creado = True

            reserva = ReservaServicio(
                cliente=cliente,
                servicio=servicio,
                empleado=empleado,
                coordinador=coordinador,
                fecha_servicio=fecha_servicio,
            )

            try:
                reserva.full_clean()
                reserva.save()
            except ValidationError as error:
                for message in error.messages:
                    messages.error(request, message)
                return render(request, 'solicitudes/atender.html', {
                    'form': form,
                    'solicitud': solicitud,
                })

            solicitud.estado = SolicitudReserva.ESTADO_ACEPTADA
            solicitud.reserva = reserva
            solicitud.save()

            if cliente_creado:
                messages.success(
                    request,
                    f'Solicitud atendida: se creó la reserva y el cliente {cliente.nombre} {cliente.apellido} (DNI {cliente.numero_documento}) automáticamente.',
                )
            else:
                messages.success(request, 'Solicitud atendida: reserva creada correctamente.')

            return redirect('solicitudes')
    else:
        form = AtenderSolicitudForm(initial=initial)

    return render(request, 'solicitudes/atender.html', {
        'form': form,
        'solicitud': solicitud,
    })


# ---------------- Coordinador ----------------

@login_required(login_url='ingresar')
def agregar_coordinador(request):
    if request.method == 'POST':
        form = CoordinadorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coordinador agregado correctamente.')
            return redirect('coordinadores')
    else:
        form = CoordinadorForm()
    return render(request, 'coordinadores/form.html', {'form': form})


@login_required(login_url='ingresar')
def listar_coordinadores(request):
    buscar = request.GET.get('buscar', '').strip()

    coordinadores = Coordinador.objects.filter(activo=True)

    if buscar:
        palabras = buscar.split()

        for palabra in palabras:
            coordinadores = coordinadores.filter(
                Q(nombre__icontains=palabra) |
                Q(apellido__icontains=palabra) |
                Q(numero_documento__icontains=palabra)
            )

    return render(request, 'coordinadores/listar.html', {
        'coordinadores': coordinadores,
        'buscar': buscar,
    })


class BajaCoordinador(BajaLogicaView):
    model = Coordinador
    success_url = 'coordinadores'


class RestaurarCoordinador(RestaurarView):
    model = Coordinador
    success_url = 'coordinadores_inactivos'


@login_required(login_url='ingresar')
def coordinadores_inactivos(request):
    buscar = request.GET.get('buscar', '').strip()

    coordinadores = Coordinador.objects.filter(activo=False)

    if buscar:
        palabras = buscar.split()

        for palabra in palabras:
            coordinadores = coordinadores.filter(
                Q(nombre__icontains=palabra) |
                Q(apellido__icontains=palabra) |
                Q(numero_documento__icontains=palabra)
            )

    return render(request, 'coordinadores/inactivos.html', {
        'coordinadores': coordinadores,
        'buscar': buscar,
    })


@login_required(login_url='ingresar')
def editar_coordinador(request, pk):
    coordinador = get_object_or_404(Coordinador, pk=pk)
    if request.method == 'POST':
        form = CoordinadorForm(request.POST, instance=coordinador)
        if form.is_valid():
            form.save()
            messages.success(request, 'Coordinador actualizado correctamente.')
            return redirect('coordinadores')
    else:
        form = CoordinadorForm(instance=coordinador)
    return render(request, 'coordinadores/form.html', {'form': form, 'coordinador': coordinador})


# ---------------- Empleado ----------------

@login_required(login_url='ingresar')
def listar_empleados(request):
    buscar = request.GET.get('buscar', '').strip()

    empleados = Empleado.objects.filter(activo=True)

    if buscar:
        palabras = buscar.split()

        for palabra in palabras:
            empleados = empleados.filter(
                Q(nombre__icontains=palabra) |
                Q(apellido__icontains=palabra) |
                Q(numero_documento__icontains=palabra)
            )

    return render(request, 'empleados/listar.html', {
        'empleados': empleados,
        'buscar': buscar,
    })


class BajaEmpleado(BajaLogicaView):
    model = Empleado
    success_url = 'empleados'


class RestaurarEmpleado(RestaurarView):
    model = Empleado
    success_url = 'empleados_inactivos'


@login_required(login_url='ingresar')
def empleados_inactivos(request):
    buscar = request.GET.get('buscar', '').strip()

    empleados = Empleado.objects.filter(activo=False)

    if buscar:
        palabras = buscar.split()

        for palabra in palabras:
            empleados = empleados.filter(
                Q(nombre__icontains=palabra) |
                Q(apellido__icontains=palabra) |
                Q(numero_documento__icontains=palabra)
            )

    return render(request, 'empleados/inactivos.html', {
        'empleados': empleados,
        'buscar': buscar,
    })


@login_required(login_url='ingresar')
def editar_empleado(request, pk):
    empleado = get_object_or_404(Empleado, pk=pk)
    if request.method == 'POST':
        form = EmpleadoForm(request.POST, instance=empleado)
        if form.is_valid():
            form.save()
            empleado.sincronizar_usuario()
            messages.success(request, 'Empleado actualizado correctamente.')
            return redirect('empleados')
    else:
        form = EmpleadoForm(instance=empleado)
    return render(request, 'empleados/form.html', {'form': form, 'empleados': empleado})
