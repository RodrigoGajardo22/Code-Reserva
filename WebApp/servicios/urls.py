from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),

    # acceso
    path('ingresar/', views.ingresar, name='ingresar'),
    path('salir/', views.salir, name='salir'),

    # panel interno
    path('panel/', views.dashboard, name='dashboard'),

    # cliente (público)
    path('reservar/', views.solicitud_reserva, name='solicitud_reserva'),
    path('consultar/', views.consulta_reserva, name='consulta_reserva'),

    # solicitudes de reserva
    path('solicitudes/', views.listar_solicitudes, name='solicitudes'),
    path('solicitudes/atender/<int:pk>/', views.atender_solicitud, name='solicitud_atender'),
    path('solicitudes/rechazar/<int:pk>/', views.rechazar_solicitud, name='solicitud_rechazar'),

    # servicios
    path('servicios/', views.listar_servicios, name='servicios'),
    path('servicios/inactivos/', views.listar_inactivos, name='servicios_inactivos'),
    path('servicios/nuevo/', views.crear_servicio, name='servicio_nuevo'),
    path('servicios/editar/<int:pk>/', views.editar_servicio, name='servicio_editar'),
    path('servicios/eliminar/<int:pk>/', views.BajaServicio.as_view(), name='servicio_eliminar'),
    path('servicios/restaurar/<int:pk>/', views.RestaurarServicio.as_view(), name='servicio_restaurar'),

    # Reserva Servicio

    path('reservas/nueva/', views.crear_reserva, name='reserva_nuevo'),
    path('reservas/', views.listar_reservas, name='reservas'),
    path('reservas/editar/<int:pk>/', views.editar_reserva, name='reserva_editar'),
    path('reservas/eliminar/<int:pk>/', views.eliminar_reserva, name='reserva_eliminar'),
    path('reservas/imprimir/<int:pk>/', views.datos_reserva, name='reserva_imprimir'),


    # clientes
    path('clientes/', views.listar_clientes, name='clientes'),
    path('clientes/inactivos/', views.listar_clientes_inactivos, name='clientes_inactivos'),
    path('clientes/nuevo/', views.crear_cliente, name='cliente_nuevo'),
    path('clientes/editar/<int:pk>/', views.editar_cliente, name='cliente_editar'),
    path('clientes/eliminar/<int:pk>/', views.BajaCliente.as_view(), name='cliente_eliminar'),
    path('clientes/restaurar/<int:pk>/', views.RestaurarCliente.as_view(), name='cliente_restaurar'),

    # coordinadores
    path('coordinadores/', views.listar_coordinadores, name='coordinadores'),
    path('coordinadores/inactivos/', views.coordinadores_inactivos, name='coordinadores_inactivos'),
    path('coordinadores/nuevo/', views.agregar_coordinador, name='coordinador_nuevo'),
    path('coordinadores/editar/<int:pk>/', views.editar_coordinador, name='coordinador_editar'),
    path('coordinadores/eliminar/<int:pk>/', views.BajaCoordinador.as_view(), name='coordinador_eliminar'),
    path('coordinadores/restaurar/<int:pk>/', views.RestaurarCoordinador.as_view(), name='coordinador_restaurar'),

    # empleados
    path('empleados/', views.listar_empleados, name='empleados'),
    path('empleados/inactivos/', views.empleados_inactivos, name='empleados_inactivos'),
    path('empleados/editar/<int:pk>/', views.editar_empleado, name='empleado_editar'),
    path('empleados/eliminar/<int:pk>/', views.BajaEmpleado.as_view(), name='empleado_eliminar'),
    path('empleados/restaurar/<int:pk>/', views.RestaurarEmpleado.as_view(), name='empleado_restaurar'),

]
