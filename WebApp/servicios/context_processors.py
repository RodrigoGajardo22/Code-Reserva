'''
    Aquí se definen los estilos de los elemenos que se utilizarán en la aplicación web.
'''
from .models import SolicitudReserva

ESTILOS = {
    'boton_confirmacion': 'btn btn-primary btn-sm',
    'boton_editar': 'btn btn-sm btn-outline-primary',
    'boton_eliminar': 'btn btn-sm btn-outline-danger',
    'boton_restaurar': 'btn btn-sm btn-success',
    'boton_nuevo': 'btn btn-primary',
    'boton_volver': 'btn btn-outline-secondary',
    'boton_admin': 'btn btn-outline-light btn-sm',
}


def estilos(request):
    return {'estilos': ESTILOS}


'''
    Ejemplo de uso:

    <button type="submit" class="{{ estilos.boton_eliminar }}" onclick="...">    
'''

#-------------------- NAVBAR --------------------
def navbar_menu(request):
    if request.user.is_authenticated:
        items = [
            {'title': 'Panel', 'url_name': 'dashboard'},
            {'title': 'Servicios', 'url_name': 'servicios'},
            {'title': 'Clientes', 'url_name': 'clientes'},
            {'title': 'Coordinadores', 'url_name': 'coordinadores'},
            {'title': 'Empleados', 'url_name': 'empleados'},
            {'title': 'Reservas', 'url_name': 'reservas'},
            {'title': 'Solicitudes', 'url_name': 'solicitudes'},
            {
                'title': 'API',
                'children': [
                    {'title': 'Documentación', 'url_name': 'swagger-ui'},
                    {'title': 'Descargar schema JSON', 'url_name': 'schema'},
                ],
            },
        ]

        pendientes = SolicitudReserva.objects.filter(
            estado=SolicitudReserva.ESTADO_PENDIENTE
        ).count()

        for item in items:
            if item.get('url_name') == 'solicitudes' and pendientes > 0:
                item['badge'] = pendientes
    else:
        items = [
            {'title': 'Inicio', 'url_name': 'home'},
            {'title': 'Hacer una reserva', 'url_name': 'solicitud_reserva'},
            {'title': 'Consultar reserva', 'url_name': 'consulta_reserva'},
        ]

    return {'nav_items': items}